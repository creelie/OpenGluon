# Third-party sources

The 17 quantumlib projects, eBLLM/Anaxia, four mathematical libraries and two selected Harmonic repositories are separate Git submodules. Their original licenses, authors, copyright notices and histories remain intact. Inclusion does not transfer authorship to OpenGluon or change an upstream license.

The public research portfolio contains short attributed excerpts and links, not copies of entire third-party README files or proofs. A fork is explicitly identified in the index. Only public repository material is included.

The mathematical source libraries are leanprover-community/mathlib4, sympy/sympy, flintlib/flint and gap-system/gap. Read their license files at the pinned commits. The GitHub license label may be incomplete (for example NOASSERTION); the actual upstream notices govern.

Harmonic's `IMO2025` repository has no top-level license file at the captured commit. Its source remains an unmodified upstream checkout; OpenGluon's MIT license supplies no additional rights over it. The `aristotle` client has a proprietary license referring to the Aristotle API terms, alongside a separately MIT-licensed vendored tomli component. It is linked and cloned unmodified, not incorporated into OpenGluon's own Python package or relicensed. See [Harmonic tools](docs/HARMONIC.md) for the pinned scope and usage details.

The root MIT license applies to new OpenGluon integration code, documentation and artwork authored for this workspace. It does not relicense submodules, third-party quotations or research papers.
