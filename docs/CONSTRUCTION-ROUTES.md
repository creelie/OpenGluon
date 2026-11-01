# Construction routes

These are targeted ways to organize a mathematical attempt. A route is not a proof that its obligations have been discharged. Source links identify the related research or software; no claim of inventing classical techniques is made.

## Rational Gram and LDL certificates

**Input.** A finite symmetric rational matrix.

**Output.** A = L diag(d) L^T with d >= 0, independently reconstructed.

**Required checks.** Every entry is rational, with no rounded float conversion. Reconstruct the entire input matrix and check each diagonal sign.

**Failure test.** Positive diagonal entries alone do not imply positive semidefiniteness: [[1,2],[2,1]] is indefinite.

Sources: [EXACT-CERTIFICATES.md](https://github.com/creelie/eBLLM/blob/main/docs/EXACT-CERTIFICATES.md)

## Rank bounds for graph constructions

**Input.** A graph represented by a matrix whose support is its closed neighbourhood relation.

**Output.** Tensor-product rank bounds and a candidate extremal family.

**Required checks.** Verify the exact support pattern over a single common field. Supply a construction attaining the rank bound before claiming equality.

**Failure test.** An upper rank bound alone never proves a matching lower bound.

Sources: [Paper_1](https://github.com/creelie/Paper_1)

## Trace and kernel dimensions over finite fields

**Input.** A linearised polynomial over a specified finite field.

**Output.** Exact kernel conditions and a character-sum counting identity.

**Required checks.** Derive the kernel equivalence for every parameter. Check the small exceptional dimensions separately and justify the all-dimension estimate.

**Failure test.** Enumeration in small fields is not a proof for every odd extension degree.

Sources: [eConjectureWelchSumFree](https://github.com/creelie/eConjectureWelchSumFree)

## Exact final-prime completion

**Input.** An ordered prime prefix and exact divisibility equations.

**Output.** At most the explicitly derived candidate(s) for the next prime.

**Required checks.** Prove the algebraic reduction and all denominator/sign conditions. A full exclusion requires every possible prefix length, not a finite search cutoff.

**Failure test.** Millions of empty finite searches do not exclude unbounded numbers of prime factors.

Sources: [eLhmr](https://github.com/creelie/eLhmr)

## Certified reflexive descent chains

**Input.** Exact lattice vertices and a specified complete census.

**Output.** A replayable upper bound on shortest descent for each covered object.

**Required checks.** Certify each lattice cut and cover relation. Check complete census coverage, every row group, and any external completeness assumption.

**Failure test.** A maximum upper bound is not the exact maximum without a matching lower construction.

Sources: [seed](https://github.com/creelie/seed)

## Blow-up and finite-cover descent

**Input.** A proper algebraic map with explicit exceptional divisor and pullback/pushforward data.

**Output.** A transport statement for classes that are actually constructed.

**Required checks.** Track rational versus integral coefficients and every exceptional class. Provide an algebraic representative; do not replace it by a motivated or numerical class.

**Failure test.** Changing a variety or passing to a cover does not create an unconstructed algebraic representative.

Sources: [fermat-hodge-](https://github.com/creelie/fermat-hodge-)

## Rare-event boundary-response transfer

**Input.** Full and restricted block laws with a uniform response estimate.

**Output.** A two-sided error budget between their boundary influence coefficients.

**Required checks.** Bound derivatives or transport responses, not only bad-event probability. Prove a retained contraction margin uniformly along the physical tuning.

**Failure test.** A rare event can have a large derivative; deterministic gauge isometries preserve Wasserstein influence coefficients.

Sources: [4Y-M](https://github.com/creelie/4Y-M)

## Tightness with non-escaping observables

**Input.** Renormalized observables and a common state space at every cutoff.

**Output.** A candidate subsequential law with precisely stated moment transfers.

**Required checks.** Prove uniform moment/tree bounds and a nonzero fixed-distance observable. Establish uniqueness, locality, rotational invariance and the required positive physical gap.

**Failure test.** Unit normalization does not prevent mass from escaping to infinite physical energy.

Sources: [4Y-M](https://github.com/creelie/4Y-M)

## One-witness vacuum verification

**Input.** One explicit compactification and nine precisely formulated tests.

**Output.** A nine-entry obligation table for the same object.

**Required checks.** Use one common vacuum, not nine unrelated examples. Specify moduli stabilization, hierarchies and breaking tests and prove them.

**Failure test.** A geometric construction or vanishing index alone does not verify all physical conditions.

Sources: [geometric-selection-conjecture](https://github.com/creelie/geometric-selection-conjecture)

## Skew-spectrum determinant identities

**Input.** A real skew adjacency matrix with its exact nullspace.

**Output.** A paired-eigenvalue factorization and a rational-square candidate.

**Required checks.** Treat the zero eigenvalue and normalizing determinant explicitly. Justify the limiting product rather than extrapolating numerical values.

**Failure test.** A floating determinant near zero is not a proof of singularity.

Sources: [Paper_8](https://github.com/creelie/Paper_8)

## Clifford traces and graph invariants

**Input.** A fixed Clifford algebra convention and graph-state sum.

**Output.** An exact trace identity compatible with the four-term relation.

**Required checks.** Track normalizations, signs and exceptional specialization values. Prove the identity for arbitrary diagrams before using finite tests.

**Failure test.** Agreement on small chord diagrams alone does not prove an all-diagram identity.

Sources: [Paper_7](https://github.com/creelie/Paper_7)

## Finite support for monotone coverage

**Input.** A compact polytope and functions sharing a convex part with affine differences.

**Output.** A finite candidate support set reusable for monotone failure rules.

**Required checks.** Check the common convex-part hypothesis on every target face. A support theorem needs attainment and a matching design certificate for optimization.

**Failure test.** A finite grid need not contain the weakest coverage point.

Sources: [sensor-resilience-certificates](https://github.com/creelie/sensor-resilience-certificates)

## Deletion-contraction with an explicit cost ledger

**Input.** A graph or constraint family with a costed branching recurrence.

**Output.** An exact recurrence and a candidate subexponential algorithm on its proved parameter range.

**Required checks.** Solve the recurrence with all density/constraint parameters retained. Prove a reduction and worst-case bound before claiming a complexity separation.

**Failure test.** An exponent that grows with the number of constraints cannot be silently declared uniform.

Sources: [sympy](https://github.com/sympy/sympy)

## Elimination with exceptional-locus accounting

**Input.** An ideal over an exact field with stated denominators and exceptional sets.

**Output.** Elimination or saturation certificates for a specified algebraic implication.

**Required checks.** Retain every denominator-zero branch and distinguish radical from ordinary ideal membership. Give exact combination witnesses; analytic or arithmetic existence is a separate step.

**Failure test.** Dividing by a parameter can delete precisely the solutions one is trying to exclude.

Sources: [sympy](https://github.com/sympy/sympy), [flint](https://github.com/flintlib/flint)
