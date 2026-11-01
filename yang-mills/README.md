# Yang–Mills mass gap: the cube estimate (D)

Research notes on one open step of a lattice approach to the Yang–Mills mass gap. Nothing here proves the mass gap.

## Context: where this work comes from

The work continues a research programme on the Yang–Mills mass gap whose paper and notes are public in the
repository [romanov360/4Y-M](https://github.com/romanov360/4Y-M), branch `claude/yang-mills-mass-gap-wf5h8x`. The
paper is `strong-coupling/forest/main.tex` (Bhattacharjee, Bhattacharya, Lockwood, *Explicit lattice Yang–Mills mass
gap for every compact simple group reducing the continuum gap to one cube*, not refereed). References below such as
"Theorem `chartdecay`" are the `\label` names in that file; each is described in words where it is used.

**The programme in one paragraph.**
- **Lattice gauge theory.** Yang–Mills theory is put on a four-dimensional lattice with spacing a. Each link carries a
  group element (for example in SU(2)), and the Wilson action weights each plaquette, the unit square of four links.
- **Proved so far.** A mass gap on the lattice at strong coupling (large spacing): for SU(2) up to β_W ≤ 0.351 and
  for SU(3) up to β_W ≤ 0.77.
- **The reduction.** The gap in the continuum (a → 0) is reduced to two statements:
  - **the cube estimate**: inside one cube of fixed physical size, with the block averages of the field held fixed,
    changing one link on the boundary moves the law of the cube only a little (a Dobrushin–Shlosman condition). It must
    hold uniformly as a → 0, that is, at weak coupling;
  - **existence**: a continuum limit satisfying the Osterwalder–Schrader axioms. This is essentially the Clay problem
    itself.

**The open steps of the cube estimate.** Several steps are proved, among them the quadratic (Gaussian) version at
every scale, one composition step, decay inside one calm fibre, and the rarity of large fields. Four steps are open:

| step | what it asks |
|---|---|
| **the cube coefficient** | turn the proved decay of correlations inside one fibre into a bound on the cube's response to a boundary change |
| **non-calm fibres** | control the field configurations that have no nearby small-field configuration |
| **harmless large fields** | show that rare regions of large field do not spoil the bound |
| **composition across scales** | combine the cube conditions at all scales into one statement (renormalisation group) |

**Other terms.**
- **Fibre.** The set of field configurations inside the cube with the given block averages and boundary.
- **Constrained law.** The Wilson measure restricted to one fibre.
- **Calm.** Every plaquette near the cube is within a tiny angle of the identity: the small-field regime.
- **Chart.** A coordinate patch of the fibre around a calm configuration. The paper proves that correlations decay
  exponentially there (Theorem `chartdecay`).
- **Cube coefficient.** The Wasserstein (W₁) distance between the cube's laws for two boundary conditions that differ at
  one link, divided by the size of that difference.

## Files

| file | content | status |
|---|---|---|
| `SURVEY.md` | literature (Bałaban/Dimock, W₁ Dobrushin, Bassalygo–Dobrushin, CCHS, Shen–Zhu–Zhu, Chatterjee, LGT in Lean, 2025–26), with what each means for the four open pieces in the glossary above | survey |
| `cube-coefficient/CALM_DATA.md` | the cube-coefficient step for calm boundary data: type-(a) exterior links proved with explicit constant C_* ≤ 7.4·10¹², uniform in β and n; type-(b) links reduced to one one-block large-field remainder; the constrained cube condition, conditionally, for cube side n ≳ 2.3·10¹⁵/α; the non-uniform off-chart term isolated as Conjecture L (harmlessness of large fields, in covariance form) | proved / reduced / conjectured, as marked in its §6 |
| `cube-coefficient/checks/geometry_checks.py` | enumeration of the block-tree geometry (link types, private links, counts), the lattice sum S(α), the constants | `python3 yang-mills/cube-coefficient/checks/geometry_checks.py` |

Nothing here proves the cube estimate or existence. The off-chart term of the cube-coefficient bound is not uniform along the weak-coupling tuning.
