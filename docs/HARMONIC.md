# Harmonic sources in OpenGluon

Captured 1 November 2026. These are unmodified, full-history source checkouts maintained by their upstream authors.

| Upstream | Local path | Use in this workspace |
| --- | --- | --- |
| [harmonic-ai/IMO2025](https://github.com/harmonic-ai/IMO2025) | `mathematics/harmonic-imo2025` | Worked examples of precise definitions, auxiliary lemmas, explicit constructions, invariants and formal proof organization. |
| [harmonic-ai/aristotle](https://github.com/harmonic-ai/aristotle) | `engines/aristotle` | Optional client for the hosted Aristotle service, potentially useful for verifying C or hardware implementations of a finite mathematical checker. |

Exact commits and upstream branches are in [the toolkit lock](../toolkit-lock.json). The normal hourly toolkit synchronization includes both selected repositories. It changes source pins without running the code or submitting any files to a service.

## Scope of the current Aristotle client

At commit `52e3639009b4afd9f09982bbd17e8ebc0cb1b80f`, the client README says that the service verifies Verilog and C, and Rust for accounts with that feature. It explicitly states that it does **not** verify pure mathematics or Lean-only projects. The repository is a client, not the trained model or a local theorem-proving runtime.

The client can upload a project and spend account credits when a run starts. No client installation, account login, file upload or API run was performed for this integration. Use the pinned upstream documentation to review a particular submission before starting one. Credentials do not belong in OpenGluon.

## Reading and checking the IMO examples

The source requests `leanprover/lean4:v4.20.0-rc5` and matching mathlib. It should be built in its own Lake project rather than mixed into the current mathlib checkout.

```sh
cd mathematics/harmonic-imo2025
lake exe cache get
lake build
```

These commands can download the specified toolchain and dependencies. They were not run in this integration: the required release-candidate toolchain was not installed locally. Source integrity and commit pins were checked instead. A successful build would still need an audit of the actual theorem statements, dependencies and admissions.

The snapshot includes proof files for Problems 1, 3, 4 and 5, a text file for Problem 2, and `StatementOnly_*.lean` templates, including Problem 6. The templates contain `sorry`; their presence or a successful permissive build must not be reported as a proof of all six problems. The umbrella file also imports statement templates. This distinction matters when extracting examples for new formalizations.

For a research proof, first fix the statement, prove the missing mathematical step, then formalize and inspect its axioms. Source examples can help with the formalization; they do not supply an argument for an unrelated open conjecture.

## Selection and attribution

The organization's other two public repositories at inspection were `pbcc` (a Protocol Buffers implementation) and `python-memtools` (a memory debugger). They were not cloned because the current mathematical proof work has no identified need for them.

Harmonic retains authorship and all upstream rights. The IMO snapshot has no top-level license file. Aristotle's client uses its own proprietary API license, with a separately MIT-licensed vendored component. OpenGluon's MIT license does not replace either source's terms. No upstream files were edited.
