# Audit a formalized claim with source correspondence under review

The claim auditor checks a mathematical task explicitly supplied by a researcher. It preserves the supplied original source URL, location, exact excerpt and formalization note. It does not read entire papers automatically, infer an author's intended theorem, establish that a quotation is accurate, or announce errors in another researcher's work.

```sh
python anaxia.py audit examples/audit/synthetic-claims.json --output data/audits/tutorial
```

This example is deliberately synthetic and labeled `tutorial: true`. Its source is a tutorial document in this repository; it does not fabricate a quotation or a mistake in an arXiv paper. The first false inequality is refuted by an exact negative witness, while the other two elementary claims receive independently checked evidence.

## Manifest and supported statements

Use schema version 1 and between one and twenty claims. Each claim supplies:

| Field | Meaning |
| --- | --- |
| `id` | Unique safe output identifier |
| `source_url` | Original public arXiv paper or GitHub file/repository permalink |
| `source_location` | Page, equation, theorem, paragraph or source-file location |
| `source_excerpt` | Exact source text supplied by the researcher; retained unchanged in JSON with its SHA-256 |
| `formalization_note` | How variables, assumptions, quantifiers and domain in the source map to the JSON task |
| `task` | Task file relative to the manifest directory; escaping paths and resolved symlinks outside that directory are rejected |
| `backend` | `polynomial` or `modular` |

The polynomial backend checks the supplied nonnegativity statement on its explicit real or finite integer-box domain. A rational sum-of-squares identity may prove nonnegativity for all real assignments. An exact negative witness refutes that formal task. Finite enumeration verifies only the stated finite box. These proof scopes stay visible in every audit result.

The modular backend interprets its formal claim as **the submitted integer polynomial has no integer zero**. It can certify that claim by exhaustively checking all assignments modulo a small integer and finding no zero residue. It does not infer whether an original source asserts existence or nonexistence. A search without an obstruction remains inconclusive.

## Findings, corrections and review

`formal_claim_verified`, `formal_claim_refuted` and `inconclusive` describe the submitted formal task. Every source retains `source_claim_requires_review: true` and `source_correspondence: unreviewed`. The source excerpt itself is not authenticated by this command. A human must check the original paper, surrounding assumptions, definitions, quantifiers, revisions and the fidelity of the formalization before interpreting any result as a criticism of a paper.

After a polynomial counterexample, the auditor may try one candidate correction: add the magnitude of the negative witness value as a constant to the polynomial. This is retained as a verified formal proposal only if the exact solver and independent checker prove the resulting inequality within its explicit scope. Otherwise the result requests human revision of the inequality or domain. Even a verified replacement is a different mathematical statement; its relevance as a correction to the original source remains unreviewed.

The output directory contains `audit.json`, a readable `AUDIT.md`, and one JSON record per claim. Evidence records retain the original task, task-file hash, exact certificate or witness, verification result, source reference and proof scope. The auditor renders all outputs after validating every input and checking every result. It executes no source code or expressions from a manifest and makes no network request.

A checked formal claim is not automatically a novel theorem or a submission-ready paper. This workflow creates reviewable local evidence and proposals. It does not publish releases, deposit material on Zenodo, register a DOI, submit manuscripts, accuse authors or contact researchers.
