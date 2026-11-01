# Exact rational positivity certificates

For a finite symmetric rational matrix A, the checker constructs a unit lower-triangular L and diagonal D. It then independently reconstructs every entry of A = L D L^T and checks every d_i >= 0. Hence for every real vector x,

    x^T A x = sum_i d_i ((L^T x)_i)^2 >= 0.

This is a classical LDL factorization, implemented here as a small exact certificate producer and a separate reconstruction verifier. The verifier can check a stored certificate without trusting the factorization algorithm. Rational strings such as "1/3" and integers are accepted. Floats are rejected. A zero pivot with a nonzero residual column is rejected; singular positive semidefinite matrices with zero rows or dependent columns are supported.

```sh
anaxia certify examples/rational-psd.json
```

The output contains L, D and rank. A successful certificate proves positivity of the supplied finite matrix. It does not prove a uniform bound for a matrix family, validate an analytic reduction, or imply a continuum quantum field theory. This revision does not supply a new Lean formalization of this checker.
