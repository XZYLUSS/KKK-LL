# KKK-LL TOP00 / G01 / P01B.2-CURV Stage A - P01B2A.1.3

This corrected release follows the P01B.1 No-Go Revision v3 roadmap:

```text
P01A-G6.1.1 FROZEN
  -> P01B.1-FLAT COMPLETE / SCOPED NO-GO
  -> TOP00 COMPLETE
  -> G01 COMPLETE
  -> P01B.2-CURV STAGE A EXACT REDUCTION PASSED
  -> P01B2A.1.3 RHO=1 CONTROLLED SLICE: FROZEN NO PASS
  -X-> P01C-CURV
```

P01B2A.1.3 supersedes v1 and the release-held P01B2A.1/P01B2A.1.1/P01B2A.1.2
archives as the immutable parent. It contains:

- the frozen Cauchy-topology and claim-boundary contract;
- exact unequal-radius product geometry for `(CP2)^3`;
- the exact lapse equation, four block equations, fixed-point coefficient
  system, and complete `120 x 120` homogeneous acceleration map for local
  Lovelock orders `alpha_0,...,alpha_7`;
- the order-eight Euler boundary transgression plus executable total-derivative
  and isotropic regressions;
- the corrected weighted trace map `B=sqrt(D) M invsqrt(D)`,
  `D=diag(3,4,4,4)`, with Einstein spectrum `{-1,-1,-1,14}`;
- exact double-form first derivatives, enforced condition/constraint/leakage
  gates, the corrected four-million-sample evidence, and the 27-point repair
  certificate;
- deterministic evidence and presentation builders, runtime enforcement,
  negative controls, scientific source mutations, and a fresh-extraction
  freeze wrapper;
- the fail-closed P01B.1.3 ancestor reseal, explicit audit supersession ledger,
  active-text integrity gate, and authenticated pinned-runtime transcript.

The primary replay from an extracted package root is:

```bash
python3.12 -B verification/freeze_wrapper.py --archive KKK_LL_TOP00_G01_P01B2A_1_3_Release_Harness_Corrected_Freeze_Grade.zip
```

For a bounded structural replay that does not regenerate the four-million-point
scan or rebuild the presentation, run:

```bash
python3.12 -B verification/verify_release.py --fast
```

The numerical conclusion is deliberately narrow: no jointly stable point was
found among the declared four million coupling vectors on the
equal-internal-radius slice `rho=H_star^2/y=1`.  This is not a no-go theorem, not
the full equal-radius family, and not an unequal-radius scan.  Homogeneous
Einstein-sign acceleration inertia is only a necessary kinetic-sign diagnostic;
the physical ghost verdict awaits constraint- and gauge-reduced residues.

The Stage-A HTML/PDF scientific presentation is retained byte-identically from
P01B2A.1.2. P01B2A.1.3 changes only the release harness, ancestry governance,
canonical memory, and hotfix ledger.

The next authorized calculation remains inside P01B.2-CURV: arbitrary-ratio
equal-radius regression followed by unequal radii, physical tensor/radion/vector
residues, determinant margins, and stability.  P01C-CURV remains blocked.
