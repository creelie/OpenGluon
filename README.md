<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="docs/assets/anaxia-hero.png">
  <img src="docs/assets/anaxia-hero.gif" alt="Anaxia — Mathematics, with evidence. An animated mathematical orbit connects discover, formalize, explore, critique and verify." width="100%">
</picture>

<p align="center">
  <a href="https://github.com/creelie/Anaxia/actions/workflows/checks.yml"><img src="https://github.com/creelie/Anaxia/actions/workflows/checks.yml/badge.svg" alt="Workspace checks"></a>
  <a href="https://github.com/creelie/Anaxia/actions/workflows/research-radar.yml"><img src="https://img.shields.io/badge/research_radar-hourly-68e3cb?style=flat-square&labelColor=101c32" alt="Research radar scheduled hourly"></a>
  <a href="docs/ANAXIA.md"><img src="https://img.shields.io/badge/verification-exact_rational-eec887?style=flat-square&labelColor=101c32" alt="Exact rational verification"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/project_code-MIT-9eafc8?style=flat-square&labelColor=101c32" alt="Project code MIT license"></a>
</p>

# Anaxia

**An open mathematics research workbench: discover questions, explore counterexamples, and verify evidence.**

Anaxia brings a continuously refreshed research radar together with exact computation and independently checkable certificates. Formerly **OpenGluon**, it retains the existing quantum and mathematics workspace while adding a focused path from a research lead to a precise, testable statement.

The research direction is ambitious: combine retrieval, explicit research stages, symbolic computation, counterexample search, and proof verification. The current release implements a bounded research workbench. It does not establish artificial superintelligence, human cognition, or a general method for solving arbitrary open conjectures.

<p align="center">
  <a href="#start-in-a-minute">Get started</a> ·
  <a href="docs/RESEARCH-RADAR.md">Live research digest</a> ·
  <a href="data/experiments/README.md">Experiment results</a> ·
  <a href="docs/ANAXIA.md">How it works</a> ·
  <a href="docs/INTEGRATIONS.md">Tools & integrations</a> ·
  <a href="docs/CONSTRUCTION-ROUTES.md">Construction routes</a>
</p>

## A research loop with inspectable results

| Discover | Formalize | Explore | Critique | Verify |
| :--- | :--- | :--- | :--- | :--- |
| Watch configured public GitHub sources and arXiv mathematics abstracts. | Translate a candidate into a supported JSON statement. | Search finite integer domains and construct quadratic SOS certificates. | Separate candidate claims, finite evidence, and global certificates. | Recompute exact rational identities and counterexamples. |
| Source IDs, versions, timestamps | Explicit variables and domains | Bounded, reproducible computation | Recorded stages and limitations | Independent certificate reconstruction |

The local discovery and verification tools use the Python standard library. They run without model weights or a paid API. Optional Claude proposals add language-model suggestions; the exact checker determines what the supported evidence establishes.

## Start in a minute

Python 3.10+ and Git are sufficient for the new local workbench. Submodules are optional for these commands.

```sh
git clone https://github.com/creelie/Anaxia.git
cd Anaxia

# Construct a certificate for a supported polynomial statement.
python anaxia.py solve examples/quadratic-sos.json --output data/demo-proof.json

# Verify the saved evidence independently.
python anaxia.py verify data/demo-proof.json

# Explore a finite domain, or find an exact counterexample.
python anaxia.py solve examples/bounded-polynomial.json
python anaxia.py solve examples/false-polynomial.json
```

For a higher-degree example with a supplied sum-of-squares certificate:

```sh
python anaxia.py solve examples/quartic-sos.json --output data/quartic-proof.json
python anaxia.py verify data/quartic-proof.json
```

| Result | Meaning |
| --- | --- |
| `exact_sos_verified` | Exact expansion verifies the polynomial equals a sum of squares with nonnegative rational weights. This establishes nonnegativity over the stated real variables. |
| `bounded_verified` | Every point in the specified finite integer box passes. The claim remains limited to that box. |
| `counterexample_verified` | An exact substitution violates the submitted statement. |
| `inconclusive` | The supported search did not establish a proof or counterexample. |

These statuses concern the submitted formal statement. A correct calculation does not establish that an informal paper was translated faithfully.

Register reviewed local tasks in [`config/research-tasks.json`](config/research-tasks.json), then run the queue:

```sh
python anaxia.py experiment --tasks config/research-tasks.json --output data/experiments
```

The hourly research-radar workflow reruns these registered tasks and independently verifies their reports. Read the [experiment digest](data/experiments/README.md) for scoped results. The initial four entries are tutorial examples, not new solutions to arXiv problems. The path from a radar lead to an automatic experiment is **literature review → faithful formalization → local task registry → exact computation and verification**.

## A research radar that updates this README

The radar monitors configured public GitHub owners, including **creelie**, discovers mathematical repositories through configurable search queries, and retrieves recent arXiv mathematics abstracts. Newly added public repositories enter the next successful owner refresh, within the configured pagination limit.

```sh
# Refresh from public services and regenerate the source-linked digest.
python anaxia.py radar refresh --output data/research-radar.json --digest docs/RESEARCH-RADAR.md --readme README.md

# Exercise the same pipeline with bundled fixtures, without network access.
python anaxia.py radar refresh --offline examples/radar-fixture.json --output data/radar-demo.json --digest data/radar-demo.md

python anaxia.py radar show
```

Configure scope and limits in [`config/research-watch.json`](config/research-watch.json). The **Research radar** GitHub Actions workflow polls hourly at minute 37 UTC and refreshes the digest and panel below. Coverage is a bounded sample of configured public sources; it does not capture everything published worldwide. Source failures are reported and previous successful source data is retained.

<!-- ANAXIA:RADAR:START -->

**Public metadata capture · 2026\-11\-14T14:18:03\+00:00**

| Repositories | Papers | Review candidates | Sources refreshed |
| ---: | ---: | ---: | ---: |
| 482 | 60 | 14 | 5 |

Configured, bounded searches; candidate language does not establish that a conjecture is open or solved.

Coverage: 0 source(s) stale/unavailable; 4 source(s) reached a limit or reported incomplete results.

**Latest review candidates**

- [$C^\{1,α\}$ Regularity of $W^\{2,2\}$ $Q$\-Valued Maps with Small Laplacian](https://arxiv.org/abs/2611.17317v1) — reported open candidate; review required.
- [On the maximum of Poissonian log\-correlated fields](https://arxiv.org/abs/2611.17236v1) — reported open candidate; review required.
- [Large diameter for $\(Δ\+2\)$\-colouring reconfiguration](https://arxiv.org/abs/2611.17022v1) — reported open candidate; review required.

[Full research radar](docs/RESEARCH-RADAR.md) · [Machine-readable snapshot](data/research-radar.json)

<!-- ANAXIA:RADAR:END -->

The detector flags phrases in abstracts as **reported open candidates**, retaining a source excerpt. This is a lead for review: the paper may prove the statement, discuss an old conjecture, or omit a later solution. A researcher must check current literature and encode the exact problem before the solver can work on it.

## Optional Claude proposals

Anaxia can request a proposal through Anthropic's official API using your own credentials and an explicitly selected model. Requests may incur provider charges. Credentials belong in environment variables, never in the repository.

```sh
# Set ANTHROPIC_API_KEY in your environment, then choose an available model ID.
python anaxia.py propose examples/quadratic-sos.json --model YOUR_MODEL_ID --output data/proposal.json
```

Proposals are **unverified suggestions**. They are not executed automatically and do not change a statement's proof status. See [integrations](docs/INTEGRATIONS.md) for the API boundary, source-only tools, and their requirements. This repository does not distribute Claude's proprietary model weights.

## A substantial source workspace

The original OpenGluon workspace remains available, with original upstream attribution, licenses, and pinned commits.

| Component | Role |
| --- | --- |
| `anaxia/` | New standard-library research radar and exact polynomial laboratory. |
| `engines/anaxia/` | Existing eBLLM engine, research portfolio, construction routes, and finite matrix certificates. |
| `mathematics/` | Lean mathlib, SymPy, FLINT, GAP, and selected Harmonic IMO examples. |
| `quantumlib/` | Pinned quantum software projects for circuits, simulation, chemistry, and decoding. |
| `engines/aristotle/` | Optional client for a hosted verification service; its own API and language support apply. |
| `engines/colibri/` | Source-only inference engine; install its dependencies and obtain compatible weights separately. |
| `engines/ai-memory/` | Source-only memory tooling, available for future integration. |
| `engines/claude-second-brain/` | Source-only knowledge-vault scaffold; requires its own setup. |

Source checkouts are not installed services or automatically connected solver backends. The [integration guide](docs/INTEGRATIONS.md) identifies the current boundary.

<details>
<summary><b>Initialize and inspect the original workspace</b></summary>

```sh
git submodule update --init --recursive
python anaxia.py doctor
python anaxia.py portfolio seed
python anaxia.py upstreams quantum
python anaxia.py routes Yang-Mills
python anaxia.py certify examples/rational-psd.json
```

The original `python opengluon.py ...` entry point remains available. The doctor checks source pins and checkout availability; it does not test every upstream dependency or theorem.

Source pins and inventory refreshes remain under the existing upstream synchronization workflow. The research radar adds a separate metadata discovery layer. Neither workflow runs newly discovered third-party code.

</details>

## Evidence before claims

Discovery records preserve their sources. Numerical or finite evidence stays finite. Model output stays unverified until checked. A supported exact polynomial certificate can establish its stated algebraic result; closing a named research conjecture additionally requires faithful formalization, complete hypotheses, and independent mathematical review.

Read the [architecture and task format](docs/ANAXIA.md), [verification notes](docs/VERIFICATION.md), [exact matrix constructions](docs/EXACT-CONSTRUCTIONS.md), and [Harmonic tool notes](docs/HARMONIC.md). Existing [research portfolios](docs/RESEARCH-PORTFOLIO.md) and [construction routes](docs/CONSTRUCTION-ROUTES.md) retain their stated assumptions.

## Development

```sh
python -m unittest discover -s tests -v
```

The core workbench has no required third-party Python dependencies. The optional artwork generator uses Pillow. See [`docs/assets/anaxia-hero.svg`](docs/assets/anaxia-hero.svg) for a scalable static version of the banner.

Maintained by **Deep Bhattacharjee**. Project code is MIT licensed; every upstream project retains its own authorship and license. Consult [contributors](CONTRIBUTORS.md), [third-party notices](THIRD_PARTY.md), [`quantumlib-lock.json`](quantumlib-lock.json), and [`toolkit-lock.json`](toolkit-lock.json) before reusing upstream material.
