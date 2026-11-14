# Coefficient growth in reciprocal fractional-part approximation

Approximating the constant function in the reciprocal dictionary requires growing coefficient mass. The bound below makes this necessary condition quantitative and applies to every finitely supported coefficient vector. It does not prove the existence of a convergent sequence. [Source dictionary and finite Gram checks](https://github.com/creelie/nyman-beurling-approximation)

## Setup and result

For integers $q\ge1$ and $n\ge2$, write $f_n(q)=\{q/n\}$. Given a finitely supported real or complex sequence $(c_n)_{n\ge2}$, put

$$
e(q)=1-\sum_{n\ge2}c_n f_n(q),\qquad
\varepsilon^2=\sum_{q\ge1}\frac{|e(q)|^2}{q(q+1)},\qquad A=\sum_{n\ge2}|c_n|.
$$

The weights are the lengths of the intervals $(1/(q+1),1/q]$ in $(0,1)$. Therefore $\varepsilon$ is exactly the $L^2(0,1)$ error for the step functions $t\mapsto\{\lfloor1/t\rfloor/n\}$, up to endpoint conventions of measure zero. The argument applies directly to this norm and uses no equivalence with a different approximation space.

Write $\mu$ for the Möbius function and $\sigma(n)=\sum_{d\mid n}d$. Then for every $n\ge2$,

$$
|c_n+\mu(n)|\le2\varepsilon\sigma(n).
$$

For every integer $m\ge2$, this implies

$$
A\ge\sum_{n=2}^{m}\mu(n)^2-\min(2\varepsilon m^2,\varepsilon m\sqrt{4m+1}).
$$

In particular, $0<\varepsilon\le1/100$ implies $A\ge 1/(1000\varepsilon^2)$, and at least $1/(1000\varepsilon^2)$ distinct coefficients are nonzero. The same lower bound holds for the number of nonzero coefficients at squarefree indices up to $\lfloor1/(145\varepsilon^2)\rfloor$. Every sequence with error tending to zero must therefore converge coefficient by coefficient to $-\mu(n)$ and have unbounded total coefficient mass. This rules out approximation with a uniform $\ell^1$ bound on these coefficients. The sign convention comes from approximating $+1$ by $+\{q/n\}$.

## Proof

Set $e(0)=0$ for the difference calculation and write $S=\sum_{n\ge2}c_n/n$. For $q\ge1$, direct subtraction of fractional parts gives

$$
e(q)-e(q-1)=\mathbf1_{q=1}-S+\sum_{n\mid q,\ n\ge2}c_n.
$$

Multiply by $\mu(n/q)$, sum over $q\mid n$, and use $\sum_{d\mid k}\mu(d)=0$ for $k>1$. The constant term disappears for $n>1$, and the result is

$$
c_n+\mu(n)=\sum_{d\mid n}\mu(n/d)\,[e(d)-e(d-1)].
$$

The weighted norm gives $|e(d)|\le\varepsilon\sqrt{d(d+1)}$. With $e(0)=0$, the two consecutive evaluation bounds sum to at most $2\varepsilon d$, since $\sqrt{d(d+1)}+\sqrt{d(d-1)}\le2d$ by concavity of the square root. This proves the coordinate estimate. Sum $|c_n|\ge |\mu(n)|-2\varepsilon\sigma(n)$ and use $\sum_{n\le m}\sigma(n)=\sum_{d\le m}d\lfloor m/d\rfloor\le m^2$.

For the stronger aggregate estimate, sum the inversion identities before bounding the evaluations. Each difference at index $d$ occurs at most $\lfloor m/d\rfloor$ times. The coefficient of $|e(q)|$ after the triangle inequality is therefore at most $b_q=m/q+m/(q+1)$ for $1\le q\le m$, where the second term may overcount the last coordinate. Weighted Cauchy–Schwarz gives

$$
\sum_{n=2}^{m}|c_n+\mu(n)|\le\varepsilon\left(\sum_{q=1}^m b_q^2q(q+1)\right)^{1/2}
=\varepsilon m\sqrt{4m+1-\frac1{m+1}}
\le\varepsilon m\sqrt{4m+1}.
$$

The equality follows from $(2q+1)^2/[q(q+1)]=4+1/[q(q+1)]$ and telescoping the last term.

At least $m/3$ integers up to $m$ are squarefree. Indeed, a nonsquarefree integer is divisible by $k^2$ for some $k\ge2$. The union bound counts at most $m\sum_{k\ge2} k^{-2}<2m/3$. The last inequality follows by summing $k=2,3,4,5$ and bounding the tail by $\sum_{k\ge6}1/(k(k-1))=1/5$. Choose $m=\lfloor1/(145\varepsilon^2)\rfloor$. Since $\varepsilon^2(4m+1)\le4/145+1/10000<1/36$, the aggregate discrepancy is at most $m/6$. Thus $A\ge m/6-1\ge1/(870\varepsilon^2)-7/6\ge1/(1000\varepsilon^2)$ in the stated range. An error of zero is impossible for a finitely supported vector because the inversion formula would force $c_p=1$ for every prime $p$.

To count nonzero coefficients, note that each squarefree index $2\le n\le m$ with $c_n=0$ contributes exactly $1$ to $\sum_{n=2}^m|c_n+\mu(n)|$. With the same choice of $m$, at most $m/6$ such indices are omitted. Thus at least $m/6-1$ squarefree indices have nonzero coefficients, proving the stated count independently of how large the coefficients are at the indices retained.

The coordinate limit is consistent with the known role of Möbius coefficients in this dictionary. The explicit coefficient-mass inequality is a necessary condition for the particular norm above and supplies no zero-free half-plane. [Báez-Duarte on the arithmetic approach](https://arxiv.org/abs/math/0011254) · [Pointwise uniqueness of Möbius coefficients](https://arxiv.org/abs/2607.12084)

## Relation to Báez-Duarte's criterion

Write $\rho_n(t)=\{1/(nt)\}$ for $t>0$. On $(0,1]$, $\rho_n(t)-\rho_1(t)/n=\{\lfloor1/t\rfloor/n\}$, since adding the fractional part of $1/t$ divided by $n$ cannot cross the next integer. On $[1,\infty)$ the difference is zero. Thus an approximation in the step dictionary extends to the same approximation of $\mathbf1_{(0,1]}$ in $L^2(0,\infty)$ using finite linear combinations of the $\rho_n$.

Conversely, given such a linear combination $\sum_{n\ge1}a_n\rho_n$ of error $\delta$, put $s=\sum_n a_n/n$. On $[1,\infty)$ the combination agrees almost everywhere with $s/t$, so $|s|\le\delta$. Subtracting $s\rho_1$ preserves the coefficients with $n\ge2$ and expresses the result in the step dictionary, with error at most $(1+\|\rho_1\|_2)\delta\le(1+\sqrt2)\delta$. Therefore arbitrarily accurate approximation in the displayed norm is equivalent to the Riemann hypothesis by Báez-Duarte's criterion. The coefficient bound also applies, up to this constant in the error, to the integer dilations with $n\ge2$ in that criterion. [Báez-Duarte, Theorem 1.1](https://arxiv.org/abs/math/0202141)

## Exact arithmetic replay

Run `python scripts/check_rh_reciprocal_coefficients.py` from the repository root. It verifies the difference and inversion identities on rational test vectors, checks the required arithmetic counts, and checks the coefficient estimate using finite partial sums of the squared error. The proof above supplies the statements for arbitrary finite supports and the full squared norm.

A local-model attempt on 14 November 2026 proposed an aggregate lower bound with the inequality reversed. The zero coefficient vector refutes that proposed bound. It has $e(q)=1$ for $q\ge1$ and $\varepsilon^2=\sum_{q\ge1}1/[q(q+1)]=1$. At $m=2$, the aggregate discrepancy is $1$, while $3\varepsilon m^{3/2}=6\sqrt2>1$. The replay checks this comparison after squaring, using exact integers. The model's proposed reversal is rejected.
