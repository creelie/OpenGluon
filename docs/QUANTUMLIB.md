# OpenGluon

A workspace containing all **17 public repositories** listed under [quantumlib](https://github.com/quantumlib) when this inventory was captured. Each project is a Git submodule pinned to an exact upstream commit, with a full local Git history. Archived repositories and organization configuration repositories are included.

## Clone the workspace

```sh
git clone --recurse-submodules https://github.com/creelie/OpenGluon.git
cd OpenGluon
```

For an existing checkout:

```sh
git submodule update --init --recursive
```

On Windows, enabling `git config --global core.longpaths true` may help with long upstream paths.

## Repository inventory

| Project | Local path | Pinned commit | Archived | Description |
| --- | --- | --- | --- | --- |
| [.allstar](https://github.com/quantumlib/.allstar) | `quantumlib/.allstar` | `7208ff64daa1` | Yes |  |
| [.github](https://github.com/quantumlib/.github) | `quantumlib/.github` | `b6845829c0c6` | No |  |
| [chromobius](https://github.com/quantumlib/chromobius) | `quantumlib/chromobius` | `c407dd3c8cba` | No | Open-source implementation of a Möbius decoder for color codes used in quantum error correction (QEC) |
| [Cirq](https://github.com/quantumlib/Cirq) | `quantumlib/Cirq` | `1fca7fb223b9` | No | Python framework for creating, editing, and running Noisy Intermediate-Scale Quantum (NISQ) circuits. |
| [OpenFermion](https://github.com/quantumlib/OpenFermion) | `quantumlib/OpenFermion` | `34adf3196cd5` | No | Python package for compiling and analyzing quantum algorithms to simulate electronic structures. |
| [OpenFermion-Cirq](https://github.com/quantumlib/OpenFermion-Cirq) | `quantumlib/OpenFermion-Cirq` | `655b00fee21c` | Yes | Quantum circuits for simulations of quantum chemistry and materials. |
| [OpenFermion-FQE](https://github.com/quantumlib/OpenFermion-FQE) | `quantumlib/OpenFermion-FQE` | `37d451e0611b` | No | The Fermionic Quantum Emulator (FQE) is a fermionic simulation research tool specializing in quantum circuits emulating fermion dynamics. |
| [OpenFermion-Psi4](https://github.com/quantumlib/OpenFermion-Psi4) | `quantumlib/OpenFermion-Psi4` | `36bd888b1b38` | No | OpenFermion plugin to interface with the electronic structure package Psi4. |
| [OpenFermion-PySCF](https://github.com/quantumlib/OpenFermion-PySCF) | `quantumlib/OpenFermion-PySCF` | `4a8675107544` | No | OpenFermion plugin to interface with the electronic structure package PySCF. |
| [qchack-2021-challenge](https://github.com/quantumlib/qchack-2021-challenge) | `quantumlib/qchack-2021-challenge` | `80c227033c1a` | Yes | The <G\|oogl\|e> challenge for Quantum Coalition Hackathon 2021 |
| [qsim](https://github.com/quantumlib/qsim) | `quantumlib/qsim` | `50cac4b3fa33` | No | Fast C++ and Python library for state-vector simulation of quantum circuits. |
| [Qualtran](https://github.com/quantumlib/Qualtran) | `quantumlib/Qualtran` | `9a0c11a4ee76` | No | Qᴜᴀʟᴛʀᴀɴ is a Python library for expressing and analyzing Fault Tolerant Quantum algorithms. |
| [ReCirq](https://github.com/quantumlib/ReCirq) | `quantumlib/ReCirq` | `c081606256e0` | No | Python modules for quantum computing applications and experiments using Cirq. Research using Cirq! |
| [Stim](https://github.com/quantumlib/Stim) | `quantumlib/Stim` | `ffe0d043598e` | No | A fast stabilizer circuit library. |
| [tesseract-decoder](https://github.com/quantumlib/tesseract-decoder) | `quantumlib/tesseract-decoder` | `54569b4af741` | No | Search-based decoder for quantum error correction (QEC) written in C++ and Python. |
| [TypedUnits](https://github.com/quantumlib/TypedUnits) | `quantumlib/TypedUnits` | `efc0bb4efd1e` | No | A fast units and dimensions library with support for static dimensionality checking and protobuffer serialization. |
| [unitary](https://github.com/quantumlib/unitary) | `quantumlib/unitary` | `a5eea27be2d7` | No | Open-source API library providing common operations for adding quantum behaviors to games. |

The complete commit IDs, upstream URLs, default branches, licenses reported by GitHub, and capture time are in [`quantumlib-lock.json`](quantumlib-lock.json). The inventory covers repositories owned by the quantumlib organization; projects linked from its profile but hosted under other owners are separate projects.

## Work with a project

Each upstream project retains its own build instructions, dependencies, tests, and license. Enter its directory and follow its documentation. Creating this workspace does not install dependencies or run upstream code.

To intentionally advance all projects to their upstream default branches, review the changes produced by:

```sh
git submodule update --remote --recursive
git diff --submodule=log
```

Commit updated submodule pointers only after reviewing them. Refresh `quantumlib-lock.json` to match any newly selected commits.

## Attribution and licensing

The upstream projects were created by their respective authors and contributors. Their original histories, copyright notices, licenses, and attribution remain in the submodules. OpenGluon is an independent collection maintained under the creelie account; it is not an official Google or quantumlib distribution. No new license is applied here to upstream material.

## Automatic upstream updates

[Sync quantumlib](https://github.com/creelie/OpenGluon/actions/workflows/sync-quantumlib.yml) runs hourly at minute 17 UTC and can also be started with **Actions → Sync quantumlib → Run workflow**. It checks all public repositories owned by quantumlib, advances submodule pins to their current default-branch commits, and refreshes the inventory. Newly discovered repositories are included automatically. Existing entries are retained if an upstream repository disappears, so an upstream removal never silently deletes a checkout.

The scheduled job reads GitHub metadata and updates Git links; it does not execute upstream code, install project dependencies, or rewrite upstream repositories. It uses the repository's built-in `GITHUB_TOKEN` with `contents: write`; no personal token or additional secret is required. GitHub may delay scheduled jobs or disable them after prolonged repository inactivity. Branch protection rules can prevent automatic pushes; use the workflow's manual run and logs to inspect failures.

The workflow updates the repository on GitHub. To bring an existing local checkout up to date:

```sh
git pull --ff-only
git submodule update --init --recursive
```
