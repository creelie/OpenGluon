# Tools and integrations

Anaxia has a small runnable core and a larger source workspace. A repository present on disk is a source checkout; it is not automatically an installed service, model, or mathematical verifier.

## Included and active

| Component | Current use | Requirements |
| --- | --- | --- |
| Research radar | GitHub and arXiv discovery plus configured mathematics community and blog feeds; snapshot and digest generation. | Python standard library; network access for live refresh. A GitHub token can increase API limits. |
| Resumable arXiv archive | Opt-in local metadata harvesting with progress state and search. | Network access for harvest; local storage. See [source guide](SOURCES.md). |
| Exact polynomial laboratory | Bounded integer search, quadratic SOS discovery, supplied SOS verification, exact counterexamples. | Python standard library. |
| Modular number theory | Exact modular obstructions for supported Diophantine equations. | Supported task format; bounded residue search. See [challenge guide](CHALLENGES.md). |
| Named conjecture challenges | Finite Collatz, Goldbach, Legendre, and Erdős–Straus experiments plus unsupported-goal cards. | Python standard library; explicit finite scope. |
| Local experiment queue | Automatically rerun registered local tasks, independently verify reports, and publish an experiment digest. | Supported formal JSON tasks registered in `config/research-tasks.json`; initial entries are tutorials. |
| Existing eBLLM bridge | Research portfolio, upstream inventory, construction-route cards, exact finite rational matrix certificates. | Initialized `engines/anaxia/` submodule; individual engine requirements apply. |
| Model connectors and reasoning loop | Local or cloud proposals, critic rounds, and exact checking of supported candidate certificates. | An available Ollama/llama.cpp service or your selected cloud provider credentials. See [model guide](MODELS.md). |

## Local and cloud model connections

Use Ollama for an installed local model, or an OpenAI-compatible server such as llama.cpp. Profiles in [`config/model-profiles.json`](../config/model-profiles.json) also support Anthropic, OpenAI, and Kimi. The [model guide](MODELS.md) documents endpoints, credentials, and model selection.

```sh
python anaxia.py models --provider ollama
python anaxia.py propose examples/quadratic-sos.json --provider ollama --model YOUR_MODEL_ID --output data/proposal.json
python anaxia.py reason examples/quadratic-sos.json --provider ollama --model YOUR_MODEL_ID --rounds 2 --output data/reasoning-report.json
```

Replace `YOUR_MODEL_ID` with an available model. Local services and model weights require their own setup. Cloud calls send the selected task and relevant reasoning context to the provider, use your credentials, and may incur charges. Keep credentials in environment variables or a secret manager.

Single proposals are saved as **unverified text**. The reasoning loop can extract a supported candidate certificate and ask the exact checker to verify it, recording unsuccessful attempts as well as successes. Model output is not executed as code. No model or paid API is needed for the exact local laboratory or discovery fixtures.

These connectors provide access to configured services; proprietary weights and private infrastructure remain with their providers. Source tools that interact with Claude have their own setup requirements.

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
