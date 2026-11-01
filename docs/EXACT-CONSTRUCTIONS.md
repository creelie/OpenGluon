# Exact constructions and proof obligations

OpenGluon connects concrete source trees to small, independently inspectable checks.

The new rational matrix checker constructs A = L D Lᵀ over Q, verifies the entire reconstruction independently, and requires D ≥ 0. Thus xᵀ A x is a sum of nonnegative squares for every real x. Singular positive semidefinite matrices are supported, and floating-point input is rejected.

```sh
python opengluon.py certify examples/rational-psd.json
```

The 14 construction routes cover Gram certificates, rank obstructions, finite-field traces, final-prime completion, reflexive descent chains, blow-up descent, block boundary response, non-escaping continuum observables, one-witness vacuum verification, skew-spectrum determinants, Clifford traces, monotone geometric support, costed deletion-contraction, and elimination with exceptional-locus accounting.

```sh
python opengluon.py routes Yang-Mills
python opengluon.py portfolio Lehmer
```

Every route lists its input, output, remaining obligations, failure check and source. A proposed technique is not treated as a discharged obligation. A source's claim of a theorem is not promoted to independent verification because it appears in an index. The checker added here certifies finite rational matrices; it does not close the Hodge, Lehmer, GSC or continuum Yang–Mills problems.
