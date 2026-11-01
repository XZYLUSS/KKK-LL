#!/usr/bin/env python3
"""Deterministically build the P01B2A.1.2 HTML/PDF presentation and contract."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import tempfile
from html import escape
from pathlib import Path

import pypdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, ByteStringObject

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "docs/TOP00_Topology_and_Scope_Lock.md",
    ROOT / "docs/G01_CP2_Cubed_Product_Geometry_Lock.md",
    ROOT / "docs/P01B2_CURV_Stage_A_Exact_Reduction.md",
    ROOT / "docs/PROJECT_MEMORY_ROADMAP_v3_TOP00_G01_P01B2A_1_2.md",
)
HTML_NAME = "TOP00_G01_P01B2_CURV_Stage_A_1_2.html"
PDF_NAME = "TOP00_G01_P01B2_CURV_Stage_A_1_2.pdf"
CONTRACT_NAME = "presentation_contract.json"

EXPECTED = {
    "python": "3.12.13",
    "pypdf": "6.10.0",
    "pandoc": "pandoc 3.1.3",
    "pdflatex": "pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian)",
    "pdfinfo": "pdfinfo version 26.05.0",
    "pdftoppm": "pdftoppm version 26.05.0",
}

CSS = r"""
:root{--ink:#18251f;--green:#173f32;--gold:#b07d12;--paper:#fffdf8;--soft:#f1eadb;--red:#8a2e26;}
*{box-sizing:border-box}body{margin:0 auto;max-width:1120px;padding:42px 58px;background:var(--paper);color:var(--ink);font:16px/1.55 Georgia,'Times New Roman',serif}
h1,h2,h3{font-family:Arial,Helvetica,sans-serif;color:var(--green);line-height:1.2}h1{font-size:34px;border-bottom:4px solid var(--gold);padding-bottom:12px}h2{font-size:25px;margin-top:38px;border-bottom:1px solid #c8b98e;padding-bottom:7px}h3{font-size:19px;margin-top:26px}
code,pre{font-family:'Courier New',monospace}code{background:#eee8da;padding:1px 4px;border-radius:3px}pre{background:#16261f;color:#f8f2df;padding:16px;overflow:auto;border-radius:5px}
table{border-collapse:collapse;width:100%;margin:18px 0;font-size:14px}th,td{border:1px solid #b9aa82;padding:8px 10px;vertical-align:top}th{background:#e9dfc8;color:#173f32;text-align:left}
.title{background:var(--green);color:#fff;padding:30px 36px;margin:-42px -58px 34px}.title h1{color:#fff;border:0;margin:0}.title p{color:#e9dfc8;margin:8px 0 0;font-family:Arial,Helvetica,sans-serif}
.status{border-left:6px solid var(--gold);background:var(--soft);padding:14px 18px;margin:20px 0}.status strong{color:var(--red)}
math{font-size:1.04em}a{color:#235e82}footer{margin-top:50px;border-top:1px solid #c8b98e;padding-top:12px;color:#6a665c;font-size:12px}.pagebreak{page-break-before:always}
"""

LATEX_HEADER = r"""
\usepackage{fancyhdr}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{mathrsfs}
\definecolor{KKKGreen}{HTML}{173F32}
\definecolor{KKKGold}{HTML}{9A6B0B}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{KKKGreen} KKK-LL Roadmap v3}
\fancyhead[R]{\small\color{KKKGold} TOP00 / G01 / P01B2A.1.2}
\cfoot{\thepage}
\fancypagestyle{plain}{\fancyhf{}\fancyhead[L]{\small\color{KKKGreen} KKK-LL Roadmap v3}\fancyhead[R]{\small\color{KKKGold} Curved branch correction}\cfoot{\thepage}}
\setlength{\headheight}{14pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.28em}
\setcounter{secnumdepth}{0}
"""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def version(args: list[str]) -> str:
    run = subprocess.run(args, text=True, capture_output=True, check=True)
    return (run.stdout or run.stderr).splitlines()[0].strip()


def combined_markdown() -> str:
    sections = []
    for source in SOURCES:
        text = source.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        sections.append(text)
    return "\n\\newpage\n\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    html_path = args.output_dir / HTML_NAME
    pdf_path = args.output_dir / PDF_NAME
    contract_path = args.output_dir / CONTRACT_NAME

    actual = {
        "python": platform.python_version(),
        "pypdf": pypdf.__version__,
        "pandoc": version(["pandoc", "--version"]),
        "pdflatex": version(["pdflatex", "--version"]),
        "pdfinfo": version(["pdfinfo", "-v"]),
        "pdftoppm": version(["pdftoppm", "-v"]),
    }
    if platform.python_implementation() != "CPython" or actual != EXPECTED:
        raise RuntimeError(f"wrong rendering runtime: {actual}")

    combined = combined_markdown()
    required = (
        "topology-changing",
        "I_0^{(A)}",
        "C_6=(4\\pi)^6 6!",
        "Complete homogeneous acceleration map",
        "D^{1/2}MD^{-1/2}",
        "249{,}573",
        "Q_{15}",
        "arbitrary-",
        "P01C-CURV remains blocked",
    )
    missing = [fact for fact in required if fact not in combined]
    if missing:
        raise RuntimeError(f"authoritative sources missing facts: {missing}")
    if "\\!-!" in combined:
        raise RuntimeError("invalid branch-hyphen TeX remains in authoritative sources")
    source_hashes = {source.name: sha256(source.read_bytes()) for source in SOURCES}
    combined_hash = sha256(combined.encode("utf-8"))

    env = os.environ.copy()
    env.update({"SOURCE_DATE_EPOCH": "1786320000", "TZ": "UTC", "LC_ALL": "C.UTF-8"})
    with tempfile.TemporaryDirectory(prefix="kkk-ll-p01b2a1-render-") as name:
        tmp = Path(name)
        markdown = tmp / "combined.md"
        markdown.write_text(combined, encoding="utf-8")
        body_path = tmp / "body.html"
        raw_pdf = tmp / "pandoc-output.pdf"
        subprocess.run([
            "pandoc", str(markdown),
            "--from=markdown+tex_math_single_backslash+raw_tex",
            "--to=html5", "--mathml", "--output", str(body_path),
        ], cwd=ROOT, env=env, check=True)
        body = body_path.read_text(encoding="utf-8").replace(
            "\\newpage", '<div class="pagebreak"></div>'
        )
        html_path.write_text(
            "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"/>"
            '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
            f'<meta name="kkk-ll-combined-source-sha256" content="{combined_hash}"/>'
            "<title>KKK-LL TOP00 / G01 / P01B2A.1.2</title>"
            f"<style>{CSS}</style></head><body>"
            '<div class="title"><h1>KKK-LL Curved-Branch Entry</h1>'
            '<p>TOP00 topology lock - G01 product geometry - frozen P01B2A.1.2</p></div>'
            '<div class="status"><strong>Disposition:</strong> exact Stage A passed; '
            'the corrected equal-internal-radius rho=1 finite sample has no joint '
            'stability pass; the full equal-radius and unequal-radius branches remain '
            'open; P01C-CURV remains blocked.</div>'
            f"{body}<footer>Generated from four authenticated Markdown sources. "
            f"Combined SHA-256: {escape(combined_hash)}</footer></body></html>\n",
            encoding="utf-8",
        )

        header = tmp / "header.tex"
        header.write_text(LATEX_HEADER, encoding="utf-8")
        subprocess.run([
            "pandoc", str(markdown),
            "--from=markdown+tex_math_single_backslash+raw_tex",
            "--standalone", "--pdf-engine=pdflatex",
            "--metadata=title:KKK-LL TOP00, G01, and P01B2A.1.2",
            "--metadata=author:Shubham Kumar",
            "--variable=papersize:a4", "--variable=geometry:margin=19mm",
            "--variable=fontsize:9pt", "--variable=colorlinks:true",
            "--variable=urlcolor:blue", "--include-in-header", str(header),
            "--output", str(raw_pdf),
        ], cwd=ROOT, env=env, check=True)

        # pdfTeX's trailer identifier is not stable across separate invocations,
        # even under SOURCE_DATE_EPOCH.  Rewrite the file once and bind both ID
        # entries to the authoritative combined-source digest so the release can
        # require a byte-identical presentation rebuild.
        reader = PdfReader(raw_pdf, strict=True)
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        stable_id = bytes.fromhex(combined_hash[:32])
        writer._ID = ArrayObject((ByteStringObject(stable_id), ByteStringObject(stable_id)))
        with pdf_path.open("wb") as handle:
            writer.write(handle)

        reader = PdfReader(pdf_path, strict=True)
        pages = len(reader.pages)
        if pages < 11:
            raise RuntimeError(f"unexpectedly short PDF: {pages} pages")
        render_prefix = tmp / "page"
        subprocess.run([
            "pdftoppm", "-png", "-r", "160", str(pdf_path), str(render_prefix)
        ], check=True)
        rendered = sorted(tmp.glob("page-*.png"))
        if len(rendered) != pages or any(path.stat().st_size < 1000 for path in rendered):
            raise RuntimeError("PDF raster preflight failed")

    contract = {
        "status": "PASS",
        "revision": "TOP00-G01-P01B2A.1.2",
        "sources": source_hashes,
        "combined_source_sha256": combined_hash,
        "html_sha256": sha256(html_path.read_bytes()),
        "pdf_sha256": sha256(pdf_path.read_bytes()),
        "pdf_pages": pages,
        "visual_preflight": "rendered all pages at 160 dpi",
        "runtime": actual,
        "offline_html": not bool(re.search(
            r"<(?:link|script|img)[^>]+(?:src|href)=[\"'](?:https?:)?//|@import",
            html_path.read_text(encoding="utf-8"),
            re.I,
        )),
    }
    if not contract["offline_html"]:
        raise RuntimeError("HTML contains a remote dependency")
    contract_path.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(contract, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
