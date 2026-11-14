# What finitely many Euclidean time samples can establish about a gap

An exact positive-spectrum example shows that even noiseless Euclidean correlators at any prescribed finite list of integer multiples of a time step can agree for a gapped model and a gapless model. The gapless model has no extra zero-energy eigenvector. This identifies a limitation of finite correlator measurements. The conditional theorem in the linked Yang–Mills work assumes additional control of the state count and a continuum limit, so the example does not contradict it. [Jaffe–Witten problem statement](https://www.claymath.org/wp-content/uploads/2022/06/yangmills.pdf) · [Yang–Mills research and Theorem F](https://github.com/creelie/4Y-M)

## Constructing the two spectral measures

Fix an integer $m\ge1$. Choose distinct nodes $q_0,\ldots,q_m\in(0,1/2)$ and give them equal weights $b=1/(m+1)$. Call the resulting probability measure $\nu_0$. Define a second probability measure

$$
\eta=\sum_{n=2}^{\infty}2^{1-n}\delta_{1-2^{-n}}.
$$

Write $\ell_i(q)=\prod_{j\ne i}(q-q_j)/(q_i-q_j)$ and $A_i=\int \ell_i\,d\eta$. For $0\le k\le m$, Lagrange interpolation gives $q^k=\sum_i q_i^k\ell_i(q)$. Integrating shows that $\int q^k\,d\eta=\sum_i q_i^k A_i$. Since these are finitely many finite real numbers, choose $e>0$ so small that $b-eA_i\ge b/2$ for every $i$. Set

$$
\nu_1=\sum_{i=0}^m (b-eA_i)\delta_{q_i}+e\eta.
$$

Both measures are positive and their moments agree for every $k=0,\ldots,m$. The moment at zero ensures that $\nu_1$ also has mass one. With rational $q_i$, the moments of $\eta$ are rational, by the binomial formula and a geometric series:

$$
\int q^k\,d\eta=\sum_{j=0}^{k}(-1)^j\binom{k}{j}\frac{2\,2^{-2(j+1)}}{1-2^{-(j+1)}}.
$$

## Spectral interpretation and the missing estimate

For each $\nu$ use the Hilbert space $\mathbb C\oplus L^2(\nu)$, with Hamiltonian zero on the vacuum summand and multiplication by $-\log q$ on the second summand. Use the unit vector $v=(0,1)$. Its Euclidean correlator is $\langle v,e^{-tH}v\rangle=\int q^t\,d\nu(q)$. The two correlators agree at $t=0,1,\ldots,m$. Rescaling $H$ handles any common time step. The first Hamiltonian has gap greater than $\log 2$. The second has positive eigenvalues tending to zero, with no atom at $q=1$, so its vacuum is unique and its gap is zero.

Positivity does give a test using *all* integer times. If $\int q^k\,d\nu(q)\le C e^{-k\Delta}$ for every $k\ge1$, any positive mass on $q\ge e^{-\Delta}+d$ for $d>0$ would violate the bound as $k\to\infty$. Thus the vector's spectral measure is supported on energies at least $\Delta$. Extending this reasoning to the Hamiltonian requires such estimates on a dense set of vacuum-orthogonal vectors. Applying it to Yang–Mills also requires constructing the physical continuum Hilbert space and Hamiltonian.

Run `python scripts/check_thermal_gap_identifiability.py` for an exact replay at 12 sample counts. These abstract positive spectral measures are mathematical controls for the inference from samples. They are not gauge-theory constructions.
