<p align="center">
  <b>English</b> · <a href="docs/i18n/README.hi.md">हिन्दी</a> · <a href="docs/i18n/README.bn.md">বাংলা</a> · <a href="docs/i18n/README.es.md">Español</a> · <a href="docs/i18n/README.fr.md">Français</a> · <a href="docs/i18n/README.zh-CN.md">简体中文</a>
</p>

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="docs/assets/anaxia-hero.png">
  <img src="docs/assets/anaxia-hero.gif" alt="Anaxia — Explore boldly. Verify exactly. A bright mathematical orbit connects discovery, formalization, proposals, critique and exact verification." width="100%">
</picture>

<p align="center">
  <a href="https://github.com/creelie/Anaxia/actions/workflows/checks.yml"><img src="https://github.com/creelie/Anaxia/actions/workflows/checks.yml/badge.svg" alt="Workspace checks"></a>
  <a href="docs/MODELS.md"><img src="https://img.shields.io/badge/models-local_+_cloud-087f6b?style=flat-square&labelColor=edf5f1" alt="Local and cloud model connections"></a>
  <a href="docs/SOURCES.md"><img src="https://img.shields.io/badge/research-hourly_refresh-287caa?style=flat-square&labelColor=edf5f9" alt="Research sources refresh hourly"></a>
  <a href="docs/ANAXIA.md"><img src="https://img.shields.io/badge/certificates-exact_rational-bc4b3e?style=flat-square&labelColor=fff1ec" alt="Exact rational certificate verification"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-536b79?style=flat-square&labelColor=f4f3ef" alt="Project code MIT license"></a>
</p>

# Anaxia

**An open research engine for mathematical discovery. Explore boldly. Verify exactly.**

Anaxia combines a living research radar, local and cloud model connections, iterative proposal and critique, exact certificate checks, and repeatable conjecture experiments. It extends the original **OpenGluon** workspace with a practical research loop: **discover → formalize → propose → critique → verify → record**.

Use local models through Ollama or a llama.cpp server, or connect an available Claude, OpenAI, or Kimi model with your own API credentials. Keep every mathematical conclusion attached to its statement, domain, computation, and verification result.

<p align="center">
  <a href="#get-started">Get started</a> ·
  <a href="docs/MODELS.md">Model connections</a> ·
  <a href="docs/RESEARCH-RADAR.md">Research radar</a> ·
  <a href="docs/CHALLENGES.md">Conjecture challenges</a> ·
  <a href="docs/CAMPAIGNS.md">Continuing attempts</a> ·
  <a href="docs/PAPER-AUDIT.md">Paper audits</a> ·
  <a href="data/experiments/README.md">Experiment results</a> ·
  <a href="docs/ANAXIA.md">Architecture</a>
</p>

## Built for a complete research loop

| Capability | What runs today |
| --- | --- |
| **Research discovery** | Configured GitHub owners and mathematics searches; arXiv abstracts; MathOverflow, Mathematics Stack Exchange, and selected mathematics blogs. Source links and freshness remain visible. |
| **Local + cloud models** | Explicit provider profiles for Ollama, llama.cpp, Claude, OpenAI, and Kimi. Choose your model and endpoint; local services and weights have their own setup. |
| **Iterative reasoning** | Bounded proposer/critic rounds can suggest SOS certificates; the exact checker accepts or rejects their algebraic identities. |
| **Exact mathematics** | Rational sum-of-squares certificates, exact real sign decisions for supported univariate polynomials, modular obstruction proofs, and counterexamples. |
| **Conjecture experiments** | Reproducible bounded challenges for Collatz, Goldbach, Legendre, and Erdős–Straus, plus explicit target cards for larger open problems. |
| **Research memory** | Versioned snapshots, a resumable opt-in arXiv metadata archive, registered local tasks, saved reports, and source commit pins. |

The new core uses Python's standard library. Local exact experiments need no model, API key, or paid request. A model proposal becomes mathematical evidence only after the relevant exact check succeeds.

## Get started

Python 3.10+ and Git are sufficient for the local core. Submodules are optional for these commands.

```sh
git clone https://github.com/creelie/Anaxia.git
cd Anaxia

# Discover an exact quadratic sum-of-squares certificate.
python anaxia.py solve examples/quadratic-sos.json --output data/demo-proof.json
python anaxia.py verify data/demo-proof.json

# Decide global nonnegativity of a univariate polynomial by exact Sturm counts.
python anaxia.py solve examples/univariate-sturm.json --output data/univariate-proof.json
python anaxia.py verify data/univariate-proof.json

# Explore finite evidence and exact counterexamples.
python anaxia.py solve examples/bounded-polynomial.json
python anaxia.py solve examples/false-polynomial.json

# Run the registered experiment queue and independent checks.
python anaxia.py experiment --tasks config/research-tasks.json --output data/experiments
```

For a supplied higher-degree identity, run [`examples/quartic-sos.json`](examples/quartic-sos.json). For named conjecture experiments, see the [challenge guide and current results](docs/CHALLENGES.md). Tutorial examples and finite checks retain their scope; they are not presented as new solutions to open conjectures.

```sh
# Run a bounded suite of named conjecture experiments.
python anaxia.py challenge run --profile quick --output data/challenges

# Prove a supported Diophantine impossibility by exact modular obstruction.
python anaxia.py diophantine examples/modular-obstruction.json --output data/modular-proof.json
```

The modular backend can prove that a submitted equation has no integer solution when every residue class is excluded for a selected modulus. The conclusion applies to that equation; the [challenge guide](docs/CHALLENGES.md) explains each backend's scope.

## Run a model-assisted research session

Start an Ollama service with a model you have installed, then select its model ID:

```sh
python anaxia.py reason examples/quadratic-sos.json --provider ollama --model YOUR_MODEL_ID --rounds 2 --output data/reasoning-report.json
```

The loop records proposals, critiques, and exact certificate checks. An unsuccessful round remains an unsuccessful attempt. Run one proposal with `propose`, or choose another configured provider; the [model guide](docs/MODELS.md) gives endpoint, credential, and request-limit details.

The [continuing campaign](docs/CAMPAIGNS.md) uses saved GitHub and arXiv context to revisit Hodge, Yang–Mills, Riemann, and both D4 targets. The [first attempt ledger](data/campaign/README.md) records the strategies and their proof status. For a claim in a specific paper, the [audit workflow](docs/PAPER-AUDIT.md) checks the formalized statement and saves its exact source location alongside the evidence.

Cloud requests use your credentials and may incur provider charges. A local server keeps model inference on the machine where that server runs. No proprietary model weights are included.

## Follow research as it develops

The radar refreshes configured public sources and updates this README. It watches newly added public repositories under **creelie** within configured page limits, alongside broader mathematics searches and selected community feeds.

```sh
python anaxia.py radar refresh --output data/research-radar.json --digest docs/RESEARCH-RADAR.md --readme README.md
python anaxia.py radar show

# Exercise the discovery pipeline without network access.
python anaxia.py radar refresh --offline examples/radar-fixture.json --output data/radar-demo.json --digest data/radar-demo.md
```

The **Research radar** workflow polls hourly at minute 37 UTC and reruns registered experiments. Sources, coverage caps, and feed behavior are documented in the [source guide](docs/SOURCES.md) and [`config/research-watch.json`](config/research-watch.json). Failed sources retain their last successful data where available.

<!-- ANAXIA:RADAR:START -->

**Public metadata capture · 2026\-11\-14T14:54:24\+00:00**

| Repositories | Papers | Community questions | Blog posts | Review candidates | Sources refreshed |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 481 | 111 | 80 | 16 | 14 | 10 |

Configured, bounded sources; candidate language and community answer flags do not establish that a conjecture is open or solved.

Coverage: 0 source(s) stale/unavailable; 9 source(s) reached a limit or reported incomplete results.

**Latest review candidates**

- [$C^\{1,α\}$ Regularity of $W^\{2,2\}$ $Q$\-Valued Maps with Small Laplacian](https://arxiv.org/abs/2611.17317v1) — reported open candidate; review required.
- [On the maximum of Poissonian log\-correlated fields](https://arxiv.org/abs/2611.17236v1) — reported open candidate; review required.
- [Large diameter for $\(Δ\+2\)$\-colouring reconfiguration](https://arxiv.org/abs/2611.17022v1) — reported open candidate; review required.

[Full research radar](docs/RESEARCH-RADAR.md) · [Machine-readable snapshot](data/research-radar.json)

<!-- ANAXIA:RADAR:END -->

Candidate detection keeps source excerpts for review. A candidate label does not establish that a question remains open. The bridge to an automatic experiment is **current-literature review → faithful formalization → local task registry → exact computation and verification**.

## Build a resumable arXiv metadata archive

Opt in to a bounded harvesting run, then resume it with the same command:

```sh
python anaxia.py archive harvest --max-pages 1 --set math
python anaxia.py archive status
python anaxia.py archive search "sum of squares" --limit 20
```

Omit `--set math` to select all subjects. This is a metadata archive with a resumable cursor, not a claim that the entire arXiv is already indexed or that every paper has been read. See [sources and archive storage](docs/SOURCES.md).

## Evidence you can inspect

| Result | What it establishes |
| --- | --- |
| `exact_sos_verified` | Exact expansion verifies a polynomial as a sum of squares with nonnegative rational weights, proving its stated real nonnegativity. |
| `exact_univariate_verified` / `exact_univariate_refuted` | Exact polynomial arithmetic and Sturm root counts decide the stated univariate nonnegativity claim over all reals. |
| `bounded_verified` | Exhaustive success on the specified finite domain only. |
| `counterexample_verified` | An exact substitution refutes the submitted formal statement. |
| `inconclusive` | The supported attempt did not establish a proof or checked counterexample. |

Read [how the laboratory verifies evidence](docs/ANAXIA.md), the [challenge status notes](docs/CHALLENGES.md), and the [experiment digest](data/experiments/README.md). Closing an open research conjecture requires a faithful statement, complete proof, and independent mathematical review. Anaxia records the work needed to assess such a claim.

## The source workspace

The original quantum and mathematics workspace remains available with upstream attribution, licenses, and pinned revisions.

| Component | Role |
| --- | --- |
| `anaxia/` | Research feeds, model connections, iterative reasoning, exact laboratory, and experiment runners. |
| `engines/anaxia/` | Existing eBLLM portfolio, construction-route cards, and finite matrix certificates. |
| `mathematics/` | Lean mathlib, SymPy, FLINT, GAP, and selected Harmonic examples. |
| `quantumlib/` | Pinned quantum software for circuits, simulation, chemistry, and decoding. |
| `engines/colibri/` | Source-only inference engine; dependencies and compatible weights are separate. |
| `engines/ai-memory/` · `engines/claude-second-brain/` | Source-only memory tooling and a knowledge-vault scaffold. |
| `engines/aristotle/` | Optional hosted-verification client with its own supported targets and API terms. |

A source checkout is not an installed backend. See [integration status](docs/INTEGRATIONS.md) before setting up a tool.

<details>
<summary><b>Initialize the existing workspace</b></summary>

```sh
git submodule update --init --recursive
python anaxia.py doctor
python anaxia.py portfolio seed
python anaxia.py upstreams quantum
python anaxia.py routes Yang-Mills
python anaxia.py certify examples/rational-psd.json
```

The original `python opengluon.py ...` entry point remains available. The doctor checks checkout availability and recorded pins. Upstream synchronization tracks selected source revisions; it does not execute newly discovered code or independently verify upstream mathematical claims.

</details>

## Develop and contribute

```sh
python -m unittest discover -s tests -v
```

Start with the [architecture](docs/ANAXIA.md), [model guide](docs/MODELS.md), [source guide](docs/SOURCES.md), and [verification notes](docs/VERIFICATION.md). The bright animated banner has a reduced-motion PNG fallback and a [static SVG companion](docs/assets/anaxia-hero.svg).

Maintained by **Deep Bhattacharjee**. Project code is MIT licensed; upstream projects retain their authorship and licenses. See [contributors](CONTRIBUTORS.md), [third-party notices](THIRD_PARTY.md), [`toolkit-lock.json`](toolkit-lock.json), and [`quantumlib-lock.json`](quantumlib-lock.json).
