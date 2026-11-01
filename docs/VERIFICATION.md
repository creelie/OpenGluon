# Verification of this integration

1 November 2026.

- All 17 public quantumlib repositories were cloned with full Git history. Each head commit and non-shallow state was checked; `git fsck --connectivity-only` passed in every clone.
- FLINT, SymPy, GAP and Lean mathlib were added as pinned source submodules. These initial external checkouts are shallow; their dependencies were not installed and their upstream test suites were not run.
- The initial 144 public creelie repositories was queried for its current commit, README and latest stable release. 130 READMEs and 74 releases were initially available. The expanded public watch now includes 145 creelie repositories and 3,513 repositories in total across google, google-deepmind, quantumlib and creelie. No private content is included. Reading metadata and source claims is not independent mathematical verification.
- The expanded Anaxia Python suite completed 326 tests, with one skipped. Sixteen new tests cover exact rational certificates, tampering, singular matrices, invalid floating input, Gram-matrix constructions and source-scope records.
- Five OpenGluon tests passed, including a genuine Git-index update without an upstream checkout, no-op preservation, path validation and retention of absent upstreams.
- A wheel was built for Anaxia to check that the new package modules and source data are included. The original Lean, C, C++, Julia and full research-paper proof audits were not rerun for this integration.
- The source-refresh tests also cover managed-workspace self-trigger prevention and detecting a release without a new code push.
- README GIFs were generated locally, checked for multiple frames, and visually inspected. A static reduced-motion image is provided.

The rational checker establishes positivity of a supplied finite rational matrix by independently reconstructing its LDL factorization. It supplies no missing universal, analytic or continuum proof by itself.
