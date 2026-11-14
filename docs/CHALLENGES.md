# Challenge experiments and closure requirements

The challenge suite tests exact finite assertions, checks a known geometric construction, and records the proof obligations for the requested general conjectures. It does not assign a difficulty score or interpret a small test as a Fields Medal result.

```sh
python anaxia.py challenge run --profile standard --output data/challenges
python anaxia.py challenge verify data/challenges/d4-kissing.json
python anaxia.py diophantine examples/modular-obstruction.json --output data/modular-proof.json
python anaxia.py diophantine data/modular-proof.json --verify
```

## Executable experiments

| Problem | Standard experiment | What is established |
| --- | --- | --- |
| Collatz | Starting integers 1 through 10,000, with explicit iteration and arithmetic budgets | Each retained path is recomputed and ends at 1. A budget failure is inconclusive. |
| Even Goldbach | Even integers 4 through 10,000 | An exact pair of primes is independently checked for each integer. |
| Legendre | Integers 1 through 500 | A prime strictly between consecutive squares is checked by exact trial division. |
| Erdos-Straus | Integers 2 through 200 | Positive denominators satisfy the unit-fraction equation by an exact integer identity. |
| D4 kissing construction | All 24 roots and all 276 pairs | Every norm squared is 2 and every distinct squared distance is at least 2. Scaling gives a kissing configuration. |
| Elementary Diophantine example | All assignments modulo 4 for `x^2+y^2-3` | The residue 0 is impossible, proving no integer solution for this particular equation. This is a known elementary fact. |

The first four experiments establish only their stated finite ranges. These ranges are deliberately modest capability tests, not new computational records. The modular checker can establish a universal statement because every integer assignment maps to a checked residue assignment; its verifier enumerates the residues independently and checks the exact claim.

## Requested full-closure targets

| Target | Requirement beyond the current tests |
| --- | --- |
| [Hodge](https://www.claymath.org/millennium/hodge-conjecture/) | A proof for all varieties and codimensions in the statement. Finite linear algebra or a special family is insufficient. |
| [Yang-Mills](https://www.claymath.org/millennium/yang-mills-the-maths-gap/) | A nontrivial four-dimensional continuum construction, all required axioms, and a positive physical mass gap. A finite lattice gap is insufficient. |
| [Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/) | Every nontrivial zero, including unbounded heights. No finite search closes the universal statement. |
| [Reflexive descent D4](https://github.com/creelie/seed) | Correct cover relations, complete classification coverage, and bounds at most 24 to establish the proposed upper bound. Matching bounds are needed for an exact value. The source repository reports `22 <= D4 <= 50`; that source claim is not a new independent audit here. |
| D4 kissing configuration | The known optimum 24 is attributed to [Musin](https://arxiv.org/abs/math/0309430). [De Laat, Leijenhorst and de Muinck Keizer](https://arxiv.org/abs/2404.18794) prove uniqueness up to isometry. Anaxia verifies the 24-point construction. |
| Four-dimensional sphere packing | Bound the density by $\pi^2/16$ for unrestricted packings. The stronger local approach would bound the volume of every saturated packing's unit-ball Voronoi cells by 8 from below. The sharp [fixed-grid results](D4-GRID-PACKINGS.md), [partial-contact classification](D4-PARTIAL-CONTACTS.md), and [radial-shell bound](D4-RADIAL-SHELL.md) each cover specified configurations. |

The executable targets and their sources are registered in [`config/challenge-targets.json`](../config/challenge-targets.json), with results in the [generated assessment](../data/challenges/README.md). Local model [campaigns](CAMPAIGNS.md) can revisit those targets with new repository and arXiv context. Research notes track the [Riemann coefficient bound](RH-RECIPROCAL-COEFFICIENTS.md), the [conditional Yang–Mills estimate](YANG-MILLS-ONE-SCALE.md), and the [Hodge spreading criterion](HODGE-DEGREE-OBSTRUCTION.md).

For the proposed descent bound of 24, the pinned census gives **358,101,083** polytopes across **64,022** point-count pairs whose raw pair bound exceeds 24. This measures where the pair-bound method alone needs a stronger certificate. The same computation reproduces the source's count of **92,422,743** at threshold 50. Run `python scripts/measure_d4_coverage.py` with the pinned engine initialized to reproduce the counts and see the census hash. [Coverage record](../data/d4-coverage.json).

## Papers and publication

A proposed correction needs the exact source claim, a faithful formalization, independently checked evidence, and a review of its hypotheses. A new closure manuscript additionally needs a complete proof and an originality/literature check. The current challenge run has zero newly verified global conjecture closures, so it generates no closure paper. A separate methods and proof-artifact repository may document reproducible results without calling them conjecture solutions.

No command here creates a GitHub release, Zenodo record, DOI, or external submission.
