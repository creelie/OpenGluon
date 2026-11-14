# Third-party sources

The 17 quantumlib projects, eBLLM/Anaxia, four mathematical libraries and two selected Harmonic repositories are separate Git submodules. Their original licenses, authors, copyright notices and histories remain intact. Inclusion does not transfer authorship to OpenGluon or change an upstream license.

The public research portfolio contains short attributed excerpts and links, not copies of entire third-party README files or proofs. A fork is explicitly identified in the index. Only public repository material is included.

The mathematical source libraries are leanprover-community/mathlib4, sympy/sympy, flintlib/flint and gap-system/gap. Read their license files at the pinned commits. The GitHub license label may be incomplete (for example NOASSERTION); the actual upstream notices govern.

Harmonic's `IMO2025` repository has no top-level license file at the captured commit. Its source remains an unmodified upstream checkout; OpenGluon's MIT license supplies no additional rights over it. The `aristotle` client has a proprietary license referring to the Aristotle API terms, alongside a separately MIT-licensed vendored tomli component. It is linked and cloned unmodified, not incorporated into OpenGluon's own Python package or relicensed. See [Harmonic tools](docs/HARMONIC.md) for the pinned scope and usage details.

Anaxia adds three source-only submodules from the maintainer's public forks: `creelie/colibri` (Apache-2.0), `creelie/ai-memory` (MIT), and `creelie/claude-second-brain` (MIT). Their original license files remain in their source directories. They are pinned in `toolkit-lock.json`, are not installed or executed by discovery, and require their own dependencies and setup. The knowledge-vault scaffold does not contain Claude's proprietary model or weights.

The optional Claude adapter calls Anthropic's official API only when explicitly invoked with the user's credentials. Anthropic's API terms and charges apply; no provider model is copied or relicensed.

The root MIT license applies to new OpenGluon/Anaxia integration code, documentation and artwork authored for this workspace. It does not relicense submodules, third-party quotations or research papers.
