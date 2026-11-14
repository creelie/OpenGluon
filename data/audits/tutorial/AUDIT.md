# Synthetic tutorial claim audit

Every result concerns a submitted JSON statement and its stated domain. Source correspondence remains **unreviewed**. A negative witness is not, by itself, evidence that the cited paper is wrong.

| Claim | Formal result | Source correspondence |
| --- | --- | --- |
| synthetic\-refutation | formal_claim_refuted | unreviewed |
| synthetic\-sos | formal_claim_verified | unreviewed |
| synthetic\-modular | formal_claim_verified | unreviewed |

## synthetic\-refutation

[Original source](https://github.com/creelie/Anaxia/blob/main/examples/audit/tutorial-source.md) · Synthetic tutorial statement 1

**Supplied source excerpt** (JSON preserves the exact original string and its SHA-256):

> For every real x, x squared minus one is nonnegative.

**Formalization note:** Synthetic test input: interpret this as x^2 \- 1 &gt;= 0 on the real domain. This is not a claim extracted from an arXiv paper.

**Formal statement kind:** `polynomial_nonnegative_on_task_domain`

**Result:** `formal_claim_refuted`

**Evidence scope:** The supplied nonnegativity statement is false on its stated domain.

[Exact task, evidence and independent check](synthetic-refutation.json)

**Source correspondence:** unreviewed; human literature and formalization review is required.

**Proposed correction:** `add_constant_to_polynomial` · `formal_proposal_verified_source_correspondence_unreviewed`

Polynomial is nonnegative for every real assignment.

This proves a different explicitly stated inequality. Whether it is a relevant correction to the source remains unreviewed.

## synthetic\-sos

[Original source](https://github.com/creelie/Anaxia/blob/main/examples/audit/tutorial-source.md) · Synthetic tutorial statement 2

**Supplied source excerpt** (JSON preserves the exact original string and its SHA-256):

> For every real x, x squared plus one is nonnegative.

**Formalization note:** Synthetic test input: x^2 \+ 1 &gt;= 0 for every real x.

**Formal statement kind:** `polynomial_nonnegative_on_task_domain`

**Result:** `formal_claim_verified`

**Evidence scope:** Polynomial is nonnegative for every real assignment.

[Exact task, evidence and independent check](synthetic-sos.json)

**Source correspondence:** unreviewed; human literature and formalization review is required.

## synthetic\-modular

[Original source](https://github.com/creelie/Anaxia/blob/main/examples/audit/tutorial-source.md) · Synthetic tutorial statement 3

**Supplied source excerpt** (JSON preserves the exact original string and its SHA-256):

> There is no integer x for which x squared plus one equals zero.

**Formalization note:** Synthetic test input: the modular backend audits the no\-integer\-zero claim, not an assertion of root existence.

**Formal statement kind:** `integer_polynomial_has_no_integer_zero`

**Result:** `formal_claim_verified`

**Evidence scope:** The submitted integer polynomial has no zero at any integer assignment.

[Exact task, evidence and independent check](synthetic-modular.json)

**Source correspondence:** unreviewed; human literature and formalization review is required.
