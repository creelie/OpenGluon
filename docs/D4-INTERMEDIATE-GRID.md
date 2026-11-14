# Sharp packing density at the intermediate D4 grid scale

Let $D_4=\{x\in\mathbb Z^4:\sum_i x_i\text{ is even}\}$. Fix $\sqrt{2/3}\leq\mu<1$ and restrict the centers of unit balls to a translate of $\mu D_4$. The sharp upper density among all such packings, including nonperiodic subsets, is

$$\frac{\pi^2}{36\mu^4}.$$

At $\mu=\sqrt{2/3}$ this agrees with the density $\pi^2/16$ of the usual scaled $D_4$ packing. The restriction to a fixed grid is essential to the argument. [Other fixed-grid regimes and the local Voronoi bound](D4-GRID-PACKINGS.md)

## Weighted lattice graph

After undoing the scale and translation, the allowed center sets are the independent sets of a graph on $D_4$. Its edges are differences of squared norm 2 or 4. Indeed, squared norms in $D_4$ are even, both squared distances 2 and 4 give overlapping unit balls at this scale, and squared distance 6 is allowed even at the left endpoint.

Assign weight 2 to the 24 displacement vectors of squared norm 2 and weight 1 to the 24 of squared norm 4. The resulting symmetric adjacency operator has row sum 72. On any even torus $D_4/n\mathbb Z^4$ with $n\ge6$, the characters diagonalize this operator. Every character on the even-sum subgroup of $(\mathbb Z/n\mathbb Z)^4$ is a restriction of an ambient character, so set $t_i=\cos(2\pi k_i/n)$ for an ambient frequency $k$. The eigenvalue is

$$\lambda(t)=8\sum_{i<j}t_i t_j+4\sum_i t_i^2-8+16\prod_i t_i
            =4\Bigl(\sum_i t_i\Bigr)^2+16\prod_i t_i-8.$$

The norm-2 vectors have two signed unit coordinates and contribute the first term. The norm-4 vectors are the eight signed coordinate doubles and the sixteen all-sign vectors, giving the remaining terms.

## Exact spectral minimum

The inequality $\lambda\ge-9$ holds on the whole cube $[-1,1]^4$. For nonnegative product the displayed expression is at least $-8$. Otherwise permutation and simultaneous negation allow $t=(x,y,z,-w)$ with $x,y,z,w\in[0,1]$. Put $q=x+y+z$. By AM–GM, $xyz\le q^3/27$. For $q\le1$ we have

$$\lambda+9=1+4(q-w)^2-16xyzw\ge1-16/27>0.$$

For $1\le q\le3$, both $(q-w)^2$ and $-q^3w$ are nonincreasing in $w\in[0,1]$, so

$$\lambda+9\ge1+4(q-1)^2-\frac{16q^3}{27}
             =\frac{(2q-3)^2(15-4q)}{27}\ge0.$$

At $t=(1/2,1/2,1/2,-1)$ equality holds. These cosines are realized on the torus of period six.

## From the spectral bound to arbitrary subsets

On an even torus of period at least six, let $f$ be the indicator of an independent set, $\alpha$ its fraction of vertices, $N$ the number of vertices, and write $f=\alpha\mathbf1+g$ with $\sum_i g_i=0$. The weighted adjacency matrix $A$ gives

$$0=f^TAf=72\alpha^2N+g^TAg
  \ge72\alpha^2N-9\|g\|^2=9\alpha(9\alpha-1)N.$$

Hence $\alpha\le1/9$. An arbitrary independent set restricted to an integer cube of side $L$ injects into the even torus of least even period $n\ge L+4$ by reduction modulo $n$. There are no artificial adjacencies across the torus boundary, because a forbidden displacement has each coordinate of absolute value at most 2, and every coordinate difference in the cube has absolute value at most $L-1$. The bound is therefore at most $n^4/18$ sites, uniformly over integer translates of the cube. Tiling space by these cubes bounds the count in large balls by the number of cubes that intersect them. Letting the ball radius tend to infinity and then $L$ tend to infinity gives an upper center density of $1/18$ per unscaled volume, uniformly over translated balls. Scaling gives $1/(18\mu^4)$. Unit balls have volume $\pi^2/2$, and moving the window boundary by one unit covers the contributions of balls that meet it. This gives the stated upper density.

## Equality construction

The integer linear map

$$T(a,b,c,d)=(a-b-c,\;a+b+d,\;a+c-d,\;-b+c+d)$$

satisfies $T^{\mathsf T}T=3I$. Each column sum is odd, so it sends $D_4$ into $D_4$. It multiplies lengths by $\sqrt3$ and multiplies covolume by $|\det T|=9$. Thus $T(D_4)$ has index 9, minimum squared distance 6, and covolume 18. The scaled lattice $\mu T(D_4)$ is an admissible packing with the required density. On the six-period torus it occupies exactly 72 of 648 sites.

Run `python scripts/verify_d4_intermediate_grid.py` for an exact replay of the lattice similarity, its period-six density and edge constraints, the attaining Fourier mode, and the cubic factorization. The inequalities and passage to arbitrary subsets are proved above. [Verification data](../data/d4-intermediate-grid.json)
