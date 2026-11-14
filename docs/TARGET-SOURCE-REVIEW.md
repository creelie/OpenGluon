# Target source review: scope and checked evidence

Reviewed on 2026-11-14. This is a limited reading of public source statements and a comparison with Anaxia's executable evidence. It is not a referee report, an assertion of a paper error, or a new full proof. GitHub commit identities below were checked against the live API; no upstream repository was modified.

## Reflexive descent

Source: [creelie/seed README at 5e5f514](https://github.com/creelie/seed/blob/5e5f514e449324993636a1146df863c7ee4dbcb7/README.md).

The README reports `22 ≤ D_4 ≤ 50` and explicitly leaves the exact value of `D_4` open. It describes lower-bound certificates and a classification-scale replay supporting the upper bound. Its older `346` upper bound is marked superseded. These are statements about the source's reported results, not results reproduced by Anaxia during this review.

Checked here: the current README's distinction between its bounds and the open exact value. Not checked here: the full classification, all cover relations, its large certificate replay, the manuscript's lemmas, or the logical coverage of its Lean supplement. A small arithmetic task or a sample descent cannot supply those missing universal/classification obligations. Anaxia's target card therefore remains inconclusive rather than assigning a new exact value.

## Yang–Mills

Source: [creelie/4Y-M README at 2e36be0](https://github.com/creelie/4Y-M/blob/2e36be0f89e50aeabeb3844418cf9ad58b1e7fd9/README.md).

The README separates claimed strong-coupling lattice results and a conditional continuum implication from unresolved weak-coupling estimates, the Wightman limit and the Clay problem. In particular, its Theorem F is described with hypotheses about a Wightman limit and a one-scale partition-function bound. This review does not replace those hypotheses with a proved continuum construction.

Checked here: the scope and conditional wording of that current README. Not checked here: the manuscript proof, its axioms and assumptions, all Lean dependencies, Julia computations, construction of the continuum limit, or a physical mass-gap theorem. Repository badges and finite checks do not independently establish those steps. No contradiction or paper error was established by this review.

## D₄ kissing configuration: source theorem versus construction

Source: de Laat, Leijenhorst and de Muinck Keizer, [arXiv:2404.18794v1, Section 5.1](https://arxiv.org/html/2404.18794v1#S5.SS1). Its two theorem statements are:

- Theorem 5.2: “The D₄ root system is an optimal spherical code.”
- Theorem 5.3: “The D₄ root system is the unique optimal kissing configuration in R⁴ up to isometry.”

The paper's argument uses an exact semidefinite certificate, its constraints, and an equality-case analysis. Its verification discussion describes rigorous positivity checks and rational affine-constraint checks. Those ingredients quantify beyond the particular 24 vectors constructed by Anaxia.

Anaxia independently checks the 24 integer roots, their squared norms and all 276 pairwise squared distances. After scaling, this provides a valid 24-point kissing construction and hence a lower bound. It does not supply the universal upper bound or classify every optimal configuration. Consequently, the local result is `exact_configuration_verified`, with `global_closure: false` and `new_result: false`. The source theorem and the weaker local construction are compatible; the construction neither refutes the paper nor reproduces its full proof. The paper's certificate and complete argument were not independently rerun in this review.

## Challenge-verifier review

The finite challenge witnesses were checked against their mathematical predicates: Collatz paths terminate at 1, Goldbach witnesses are prime pairs with the required sum, Legendre witnesses are primes strictly between consecutive squares, and Erdős–Straus witnesses satisfy an exact positive-denominator identity. Their proof scopes cover only their declared finite domains.

The verifier now also rejects changed proof scopes, novelty/publication flags, unsupported closure fields, boolean schema versions, altered stored verification summaries, forged statuses and invalid declared domain bounds. Regression tests recheck serialized challenge reports as well as deliberately modified evidence. These checks strengthen the interpretation of local reports; they do not extend the mathematics to any unbounded conjecture.

No release, Zenodo deposit, DOI registration, submission, author contact or public accusation was performed as part of this review.
