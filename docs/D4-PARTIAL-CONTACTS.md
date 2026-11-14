# When a partial D4 contact shell contains the reference 24-cell

**A packing with at least 22 exact D4 neighbors contains the reference 24-cell at its central Voronoi cell.** All 24 neighbors are necessary for equality in this class. With 21 exact D4 neighbors, the same containment follows for 1,928 of the 2,024 possible sets of three missing roots. The other 96 sets each admit a packing whose central cell cuts the reference cell. The additional centers can have arbitrary directions and need only satisfy the packing separation.

## Normalization

Use minimum center separation $\sqrt2$ and put the central point at $0$. Write $\mathcal R=\{\pm e_i\pm e_j:1\le i<j\le4\}$. The reference cell is

$$P=\{x: x\cdot r\le1\text{ for every }r\in\mathcal R\}
=\operatorname{conv}\bigl(\{\pm e_i\}\cup\{(\pm1/2,\pm1/2,\pm1/2,\pm1/2)\}\bigr).$$

Indeed, the half-space conditions are $|x_i|+|x_j|\le1$ for $i\ne j$. If no absolute coordinate exceeds $1/2$, the point lies in the unit cube. If its largest absolute coordinate is $a>1/2$, its other three coordinates have absolute value at most $1-a$. It lies in the pyramid from the corresponding signed axis point to that face of the cube. The cube has volume $1$, and the eight pyramids each have base volume $1$ and height $1/2$, so $P$ has volume $2$. Rescaling centers by $\sqrt2$ gives unit-radius balls and reference volume $8$.

For any candidate center $y$, arrange its absolute coordinates as $a\ge b\ge c\ge d\ge0$ by a signed permutation. The support of $P$ against $y$ is

$$h_P(y)=\max\{a,(a+b+c+d)/2\}.$$

## Proof and equality

Let $r_{ij}=e_i+e_j$ in these sorted coordinates. The two roots $r_{12},r_{13}$ have dot products at least $h_P(y)$. Indeed, $a+b\ge a+c\ge a$, and $a+c\ge b+d$. At least one of $r_{14},r_{23}$ also has dot product at least $h_P(y)$, since $a+d\ge a$ and $\max(a+d,b+c)\ge(a+b+c+d)/2$. Thus there are always three distinct roots $r$ with $r\cdot y\ge h_P(y)$.

If $y$ is a retained root, its bisector already contains $P$. For any other center $y$, packing from a retained root $r$ implies $\lVert y-r\rVert^2\ge2$, or $\lVert y\rVert^2\ge2y\cdot r$. If at least 22 roots are retained, one of the three roots above must be available, and the bisector $2x\cdot y\le\lVert y\rVert^2$ contains $P$. This holds for every center $y$.

If all 24 roots are present, their bisectors already define $P$. If some root $q$ is absent but containment holds, the point $q/2$ obeys every remaining bisector inequality strictly. Cauchy–Schwarz gives $q\cdot y\le\sqrt2\lVert y\rVert\le\lVert y\rVert^2$, with equality only for $y=q$. A packing is locally finite, and centers with $\lVert y\rVert>4$ impose no restriction in a neighborhood of $q/2$ of radius $1$. Hence a sufficiently small open ball about $q/2$ lies in the central cell and extends beyond $P$, giving strict volume increase.

## Sharp containment classification for 21 contacts

If an additional center $y$ cuts $P$, then $\lVert y\rVert^2<2h_P(y)$. All three roots given above must be missing. Since exactly three are missing, in the sorted coordinates their supports are either $12,13,14$ (a star) or $12,13,23$ (a triangle), with consistent signs on the common indices before sorting. There are $4\cdot2^4=64$ signed stars and $\binom43\cdot2^3=32$ consistently signed triangles. Their supports are different and determine their shapes. The other $\binom{24}{3}-96=1928$ deletion sets therefore guarantee containment for every admissible center. They have strict volume greater than $8$ if exactly 21 roots are present, by the same midpoint argument.

Both exceptional shapes genuinely allow a cut. These witnesses give rational coordinates in the $\sqrt2$ separation normalization. To verify packing, compare the squared norm $\lVert y\rVert^2$ with $2$ for the central center and compare it with $2\max_{r\text{ retained}}y\cdot r$ for the retained roots.

| Missing positive roots | Additional center $y$ | $\lVert y\rVert^2$ | Twice largest retained dot product | $2h_P(y)$ |
| --- | --- | ---: | ---: | ---: |
| $r_{12},r_{13},r_{14}$ | $(9/5,1/5,1/5,1/5)$ | $84/25$ | $16/5$ | $18/5$ |
| $r_{12},r_{13},r_{23}$ | $(9/10,9/10,9/10,0)$ | $243/100$ | $9/5$ | $27/10$ |

In both rows the first two comparisons certify a packing, and the squared norm is strictly less than twice the support, so the new center cuts the reference cell. Signed permutations give a witness for every exceptional deletion set. The 96 triples are exactly the triples of roots with pairwise dot product $1$. The shapes in the table refer to signed coordinate permutations. The full root-system symmetry relates the star and triangle shapes. These cuts establish failure of containment. They do not establish a central cell volume below $8$.

The deletion-triple count and all-contact restrictions are already discussed in Propositions 7.55–7.56 and Appendix G of the linked preprint. The argument here gives a support-function classification for additional centers at unrestricted radii. [Four-dimensional sphere-packing preprint, section 7.8](https://arxiv.org/html/2609.25120v2#S7.SS8)

Run `python scripts/verify_d4_partial_contacts.py` for an exact replay of the 2,024 deletion triples and both cuts. The support argument supplies the conclusion for every potential center and all remaining radii.
