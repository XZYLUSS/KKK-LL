# P01B2A.1.3 release-harness hotfix ledger

## Disposition

The P01B2A.1.2 scientific kernel, exact equations, three evidence files, HTML,
and 12-page PDF are preserved unchanged. P01B2A.1.2 is historical HOLD because
its mutation specimens used the wrong root name and its fresh-extraction
wrapper accepted files outside the authenticated release root.

P01B2A.1.3 changes only the release envelope and active ancestor governance.

## Corrections

| Review finding | P01B2A.1.3 enforcement |
|---|---|
| Mutated copies were named `release`, so the unmodified specimen already failed | Every copy retains `SOURCE.name`; an unmodified copied tree must pass before any mutation |
| No archive baseline preceded destructive mutations | A deterministic unmodified archive must pass the exact namespace validator before mutations begin |
| Files outside the sole release root were accepted | Every ZIP member must lie below the exact root `KKK_LL_TOP00_G01_P01B2A_1_3`; the member set must equal the rooted manifest set exactly |
| Extra top-level member was not tested | `UNAUTHENTICATED_TOP_LEVEL.txt` is inserted as an explicit destructive mutation and must be rejected |
| Candidate hash and byte-count claims were only mutually cross-locked | Raw self-referential claims are removed; content digest and byte count are independently recomputed from every payload except the manifest/transcript self-cycle |
| Candidate filename accepted any `.zip` suffix | The transcript requires the exact candidate name `KKK_LL_TOP00_G01_P01B2A_1_3_candidate.zip` |
| P01B.1.2 had the analogous coordinated-metadata limitation | P01B.1.3 applies the same baseline, namespace, content-binding, and mutation requirements |
| Supersession metadata omitted P01B2A.1.1 | `release_record.json` now names P01B2A.1.1 explicitly |

## Scientific statement preserved

The only numerical conclusion remains:

> No jointly stable point was found among the declared 4,000,000 coupling
> vectors on the equal-internal-radius \(\rho=1\) slice after all enforced
> necessary homogeneous inertia, Planck-sign, conditioning,
> constraint-gradient, leakage, and tangent-stability gates.

This is not an all-coupling theorem, not the complete equal-radius family, and
not an unequal-radius result. P01C-CURV remains blocked.

