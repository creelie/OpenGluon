# Verification of this integration

1 November 2026.

- All 17 public quantumlib repositories were cloned with full Git history. Each head commit and non-shallow state was checked; `git fsck --connectivity-only` passed in every clone.
- FLINT, SymPy, GAP and Lean mathlib were added as pinned source submodules. These initial external checkouts are shallow; their dependencies were not installed and their upstream test suites were not run.
- The initial 144 public creelie repositories was queried for its current commit, README and latest stable release. 130 READMEs and 74 releases were initially available. The expanded public watch now includes 145 creelie repositories and 3,513 repositories in total across google, google-deepmind, quantumlib and creelie. No private content is included. Reading metadata and source claims is not independent mathematical verification.
- The expanded Anaxia Python suite completed 326 tests, with one skipped. Sixteen new tests cover exact rational certificates, tampering, singular matrices, invalid floating input, Gram-matrix constructions and source-scope records.
- Five OpenGluon tests passed, including a genuine Git-index update without an upstream checkout, no-op preservation, path validation and retention of absent upstreams.
- A wheel was built for Anaxia to check that the new package modules and source data are included. The configured Python 3.9/3.12/3.13, C, C++, Julia, Lean and example-run jobs subsequently passed in [Anaxia CI](https://github.com/creelie/eBLLM/actions/runs/41313421362). The full research-paper proof audits were not rerun.
- The source-refresh tests also cover managed-workspace self-trigger prevention and detecting a release without a new code push.
- README GIFs were generated locally, checked for multiple frames, and visually inspected. A static reduced-motion image is provided.

The rational checker establishes positivity of a supplied finite rational matrix by independently reconstructing its LDL factorization. It supplies no missing universal, analytic or continuum proof by itself.

Both stages of the live automatic pipeline were tested successfully: [Anaxia source refresh](https://github.com/creelie/eBLLM/actions/runs/41313617205), then [OpenGluon sync](https://github.com/creelie/OpenGluon/actions/runs/41313944700). The second job imported Anaxia commit `9ef0454294c8dd293f1ce9c51f7937fbc785bd97`. All 22 local submodule heads match their published lock files.

The later Harmonic integration adds two unmodified full-history clones: `harmonic-ai/IMO2025` at `72b62405a176a7eaeadb335a7fa6ee80b6667161` and `harmonic-ai/aristotle` at `52e3639009b4afd9f09982bbd17e8ebc0cb1b80f`. `git fsck --connectivity-only` passed in both. All 24 source checkouts match the revised lock files, and the five synchronization tests passed again. The selected sources are included in the existing toolkit sync configuration. No Aristotle API job was submitted. The IMO project was inspected but not rebuilt; its required Lean `v4.20.0-rc5` toolchain is not installed here. [The scope notes](HARMONIC.md) distinguish proof files from statement templates containing admissions.
