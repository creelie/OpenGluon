# Tools and integrations

Anaxia has a small runnable core and a larger source workspace. A repository present on disk is a source checkout; it is not automatically an installed service, model, or mathematical verifier.

## Included and active

| Component | Current use | Requirements |
| --- | --- | --- |
| Research radar | Public GitHub metadata and arXiv abstract discovery; snapshot and digest generation. | Python standard library; network access for live refresh. A GitHub token can increase API limits. |
| Exact polynomial laboratory | Bounded integer search, quadratic SOS discovery, supplied SOS verification, exact counterexamples. | Python standard library. |
| Local experiment queue | Automatically rerun registered local tasks, independently verify reports, and publish an experiment digest. | Supported formal JSON tasks registered in `config/research-tasks.json`; initial entries are tutorials. |
| Existing eBLLM bridge | Research portfolio, upstream inventory, construction-route cards, exact finite rational matrix certificates. | Initialized `engines/anaxia/` submodule; individual engine requirements apply. |
| Claude proposal adapter | Optional task proposals saved as unverified text. | Your `ANTHROPIC_API_KEY`, an explicitly selected available model, network access, and any applicable API charges. |

## Optional Claude connection

Set `ANTHROPIC_API_KEY` in your local environment or secret manager. Choose a model ID available to your Anthropic account, then run:

```sh
python anaxia.py propose examples/quadratic-sos.json --model YOUR_MODEL_ID --output data/proposal.json
```

The adapter uses the [official Anthropic Messages API](https://platform.claude.com/docs/en/api/messages). It sends the selected task to the provider. Do not submit confidential material unless you intend to share it with that provider under your account's terms.

The saved response is an **unverified proposal**. It is not executed as code and does not authorize tool use or promote a statement to a proven status. Translate any useful suggestion into a supported task or certificate and check it with the laboratory. No API request is needed for local solving or discovery fixtures.

This repository does not contain Claude's proprietary weights, private infrastructure, or an independently reproduced Claude model. Source tools that interact with Claude have their own setup requirements and do not change that boundary.

## Source-only components

These checkouts preserve upstream authorship, licenses, and commit pins. Consult their README files before installation or use.

| Path | Intended role | Current boundary |
| --- | --- | --- |
| `engines/colibri/` | Inference-engine source. | Dependencies and compatible model weights must be obtained separately. No automatic inference or solver connection. |
| `engines/ai-memory/` | Memory tooling source. | Available for future integration; no automatic ingestion or memory service setup. |
| `engines/claude-second-brain/` | Knowledge-vault scaffold. | Requires its own configuration; no proprietary Claude model or autonomous research service is included. |
| `engines/aristotle/` | Optional hosted verification client. | The provider's supported targets, credentials, API terms, and charges apply. See [Harmonic notes](HARMONIC.md). |
| `mathematics/mathlib4/` | Lean formal mathematics library. | Use the pinned Lean toolchain and explicitly build/check a proof project. It is not invoked by the polynomial laboratory. |
| `mathematics/sympy/` | Symbolic computation source. | Install and integrate separately; the core laboratory currently uses its own exact rational operations. |
| `mathematics/flint/` | Exact and rigorous arithmetic source. | Requires its own native build/dependencies. |
| `mathematics/gap/` | Computational algebra source. | Requires its own runtime/setup. |
| `mathematics/harmonic-imo2025/` | Captured Lean examples. | Templates and completed proofs must be distinguished; use the original toolchain. |
| `quantumlib/` | Pinned quantum software sources. | Each project has separate dependencies and capabilities. |

Initialize source checkouts only when needed:

```sh
git submodule update --init --recursive
python anaxia.py doctor
```

The doctor reports missing or drifted pins. It does not install dependencies, download model weights, or establish the mathematical correctness of upstream claims.

## Adding more tools

Use the radar to discover candidates, then review their license, maintenance status, runtime needs, and intended interface. Add a source checkout with a pinned revision and preserve its notices. Installing a backend and connecting it to the solver are separate development steps that require tests of its actual behavior.

New public repositories under a watched owner can appear in the metadata inventory without being cloned or executed. This keeps discovery useful while preserving a reproducible source workspace.

See [third-party notices](../THIRD_PARTY.md), [`toolkit-lock.json`](../toolkit-lock.json), and [`quantumlib-lock.json`](../quantumlib-lock.json) for the authoritative source records.
