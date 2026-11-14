# The 24-cell bound for packings on a fixed D4 grid

Let $D_4=\{z\in\mathbb Z^4:\sum_i z_i\text{ is even}\}$, with minimum nonzero squared norm 2. Consider a packing of unit balls with centers selected from a translate of this grid. The center set can be nonperiodic.

**Fixed-grid result.** Every center's Voronoi cell has volume at least 8. At a center $c$, equality holds exactly when the other centers include $c\pm 2e_i$ for all four coordinates and all 16 points $c+(\pm1,\pm1,\pm1,\pm1)$. The largest upper density in this class is $\pi^2/16$.

This addresses a restricted case of the four-dimensional 24-cell problem. The companion research distinguishes previously reported results for two lattice translates from the general problem. [Two-translate paper and artifacts](https://github.com/creelie/eD424) · [Current Voronoi-cell research and residual cases](https://github.com/creelie/d4-voronoi-cells)

## Proof of the local bound

Translate a center to zero and use the reference polytope

$$
P=\{x\in\mathbb R^4: |x_i|\leq1,\ \textstyle\sum_i |x_i|\leq2\}.
$$

In each orthant, the absolute coordinates form a cube clipped by $\sum_i |x_i|\leq2$. A vertex in this clipped cube is binary. If two coordinates were fractional, one could vary them in opposite directions. If only one were fractional, it would either vary freely or be forced to an integer by the active sum bound. Thus the orthant vertices have at most two ones. Each one-coordinate vector is the midpoint of two signed two-coordinate vectors, and zero is the midpoint of opposite roots. Therefore $P$ is the convex hull of the 24 vectors $\pm e_i\pm e_j$ with $i<j$. The map $x\mapsto(1,1,1,1)-x$ exchanges the two halves of the unit cube cut by $\sum_i x_i=2$. All 16 orthants contribute volume $1/2$, so $\operatorname{vol}P=8$.

For any other center $y\in D_4$, write $a\ge b$ for its two largest absolute coordinates. The support of $P$ in direction $y$ is $a+b$. The bisector inequality for $y$ is $2x\cdot y\le \|y\|^2$. If $\|y\|^2\ge 8$, Cauchy–Schwarz gives

$$
2(a+b)\le 2\sqrt2\,\|y\|\le \|y\|^2.
$$

The remaining squared norms are 4 and 6, since the packing gives $\|y\|^2\ge4$ and parity makes squared norms even. The absolute-coordinate patterns of squared norm 4 are $(2,0,0,0)$ and $(1,1,1,1)$. The squared-norm-6 pattern is $(2,1,1,0)$. In all three cases $2(a+b)\le \|y\|^2$, so $P$ lies in the Voronoi cell.

The 24 listed neighbors define precisely the coordinate and sign inequalities of $P$. If a listed neighbor $y_0$ is absent, $x_0=y_0/2$ belongs to its boundary plane and has norm 1. It satisfies all the other neighboring-center inequalities of squared norm 4 strictly by Cauchy–Schwarz, whose equality at the bound requires $y=y_0$. There are finitely many such neighbors. The inequalities from all more distant neighbors hold throughout the ball of radius $\sqrt6/2>1$ by Cauchy–Schwarz. A sufficiently small open neighborhood of $x_0$ is therefore in the Voronoi cell and extends outside $P$, giving strictly larger volume.

## Sharp density by grid spacing

Let centers lie in a translate of $\mu D_4$, where $\mu>0$.

| Range of $\mu$ | Sharp upper density | Attaining center set, up to translation |
| --- | ---: | --- |
| $1/\sqrt2\le \mu<\sqrt{2/3}$ | $\pi^2/(64\mu^4)$ | $2\mu D_4$ |
| $\sqrt{2/3}\le \mu<1$ | $\pi^2/(36\mu^4)$ | $\mu T D_4$ for an integer similarity $T$ with $T^\top T=3I$ |
| $1\le \mu<\sqrt2$ | $\pi^2/(16\mu^4)$ | $\mu H$ |

The [intermediate-grid proof](D4-INTERMEDIATE-GRID.md) gives the explicit matrix $T$, derives the middle bound by a weighted spectral estimate, and extends the estimate to nonperiodic selections of sites.

For the highest listed interval, let $H=2\mathbb Z^4\cup((1,1,1,1)+2\mathbb Z^4)$, a sublattice with covolume 8 and minimum squared norm 4. The four points $0,e_1+e_2,e_1+e_3,e_1+e_4$ represent distinct $H$-cosets in $D_4$. Two parity patterns in the same $H$-coset are equal or complementary. The four representatives are pairwise at distance at most $\sqrt2$. Their $H$-translates partition $D_4$, and each scaled tile contains at most one packing center. The set $\mu H$ meets the distance requirement and attains the resulting bound. The similarity $(a,b,c,d)\mapsto(a+b,a-b,c+d,c-d)$ sends $D_4$ onto $H$, so $H$ is isometric to $\sqrt2 D_4$.

For the first interval, use the index-16 sublattice $2D_4$, of covolume 32. The representatives are zero, $2e_1$, $u=(1,1,1,1)$, $v=(1,1,1,-1)$, and one root from each antipodal pair. Choose its sign so that its first coordinate, dot product with $u$, and dot product with $v$ are all nonnegative. Such a choice exists. Make coordinate 1 positive if it is in the support. If coordinate 1 is absent but 4 is in the support, make the other coordinate positive. In the remaining case, choose the sign so the two coordinates sum to a nonnegative number.

Representatives from different parity patterns are distinct modulo $2D_4$. Within a fixed root support, the two representatives have sign patterns differing at one position, so their difference is $\pm2e_i\notin2D_4$. The same test separates zero from $2e_1$ and $u$ from $v$. Distinct nonantipodal roots have squared distance at most 6. The sign conditions give that same bound between each root and $2e_1,u,v$. The last three vectors have pairwise squared distance 4. Each scaled tile has diameter less than 2. The lattice $2\mu D_4$ has minimum distance $2\sqrt2\mu\ge2$ and attains the bound.

In either partition, each tile has an anchor in the corresponding sublattice. Tiles meeting a ball of radius $R$ have anchors in the ball enlarged by the maximum distance from the anchor to a tile point. Per unit volume, the number of anchors tends to the reciprocal covolume, uniformly over translated windows. To bound occupied volume, enlarge the window by one further unit to account for the balls crossing its boundary. The four-dimensional unit-ball volume is $\pi^2/2$, giving the displayed densities.

## Perturbations and reproducibility

Suppose each packing center is within $\varepsilon$ of an assigned site in the translated, scaled grid. Assign the center to the tile of that site. Any two centers assigned to one tile have separation at most $\mu d+2\varepsilon$, where $d=\sqrt2$ for the $H$ tiling and $d=\sqrt6$ for the $2D_4$ tiling. The same density bound therefore holds under arbitrary bounded displacements whenever $\mu d+2\varepsilon<2$. The local Voronoi proof concerns centers exactly on the unscaled grid.

Run `python scripts/verify_d4_grid.py` to check both short-neighbor shells and the pair distances and coset distinctions in both tiles. The arguments above supply the continuous and asymptotic steps. [Exact check record](../data/d4-grid.json)

## How close an extra center can come to a D4 contact shell

For a separate local result, place unit-ball centers at the origin and at all 24 points $\sqrt2(\pm e_i\pm e_j)$. Any additional center $x$, whether on a lattice or not, has norm at least $2\sqrt2$. To see this, let $a\ge b\ge c\ge d$ be its absolute coordinates and write $r=\lVert x\rVert$. Among the contact centers, the largest dot product with $x$ is $\sqrt2(a+b)$. The separation condition from that contact gives $r^2\ge2\sqrt2(a+b)$. Since $r^2\le a^2+3b^2\le(a+b)^2$, division by $r>0$ gives the claimed gap. Equality in the two estimates requires either $b=0$ or $a=b=c=d$. At radius $2\sqrt2$ these directions give the eight axis points and sixteen equal-magnitude points of the next D4 shell.

The gap persists under perturbations. Suppose the origin remains a center and 24 other centers each lie within distance $\varepsilon$ of their corresponding exact D4 contacts after a common rotation or reflection. Each extra center must be at distance at least $2-\varepsilon$ from every exact contact. Hence $r^2-2\sqrt2 r+4\varepsilon-\varepsilon^2\ge0$. For $0\le\varepsilon<2-\sqrt2$, this quadratic has two real roots and $r\ge2$ excludes the smaller branch, so

$$
r\ge \sqrt2+\sqrt{2-4\varepsilon+\varepsilon^2}.
$$

In particular, if $\varepsilon<2-\sqrt{10-4\sqrt3}$, the right side exceeds $\sqrt6$. This certifies the absence of a 25th center within the $\sqrt6$ shell under the stated correspondence and error tolerance. It supplies no volume estimate for the Voronoi cell formed by the perturbed neighbors.
