# Anaxia registered experiments

Deterministic results from explicitly registered, local, formalized tasks. Discovery does not automatically translate or solve an arXiv conjecture.

| Task | Type | Result | Evidence |
| --- | --- | --- | --- |
| quadratic-sos | Tutorial example | `exact_sos_verified` | [JSON](quadratic-sos.json) |
| quartic-sos | Tutorial example | `exact_sos_verified` | [JSON](quartic-sos.json) |
| univariate-sturm | Tutorial example | `exact_univariate_verified` | [JSON](univariate-sturm.json) |
| bounded-polynomial | Tutorial example | `bounded_verified` | [JSON](bounded-polynomial.json) |
| false-polynomial | Tutorial example | `counterexample_verified` | [JSON](false-polynomial.json) |

Global nonnegativity can follow from an exact rational SOS identity or a univariate Sturm calculation. Finite integer checks retain their finite scope. Counterexamples are evaluated exactly. An inconclusive result makes no proof claim.

- **quadratic-sos**: Automatic rational quadratic SOS discovery; tutorial example.
- **quartic-sos**: Independently verify a supplied quartic SOS identity; tutorial example.
- **univariate-sturm**: Decide the global statement by exact real root counting; tutorial example.
- **bounded-polynomial**: Finite integer-box verification; tutorial example.
- **false-polynomial**: Exact counterexample search; tutorial example.
