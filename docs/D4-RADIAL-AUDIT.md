# Four-dimensional sphere packing: a radial reduction counterexample

The all-contact reduction in Lemma 2.9 of arXiv:2609.25120v2 does not preserve packing feasibility. Here is an exact example with eight active Voronoi facets. The half-space monotonicity used in the lemma holds. The conclusion that the minimum over packing-valid radii occurs with every radius equal to two requires that this assignment be feasible. [Preprint, Section 2.6](https://arxiv.org/html/2609.25120v2#S2.SS6)

## Exact witness

Use the nine centers

$$
0,\quad \pm(5/2,0,0,0),\quad \pm(3/2,2,0,0),\quad \pm(0,0,2,0),\quad \pm(0,0,0,2).
$$

Every distinct pair has squared distance at least $4$, so unit balls at these centers form a packing. Between the first two antipodal pairs, the possible squared distances are $5$ and $20$. Between either of those pairs and the last two, they are $41/4$. Between the last two pairs, the squared distance is $8$. The squared radii are $25/4$ and $4$, so all eight neighbors lie inside the shell cutoff $2\sqrt{2}$.

For each neighbor $y$, its midpoint $y/2$ with the origin satisfies the bisector equality for $y$ and every other bisector inequality strictly. For distinct neighbors of equal norm this follows from strict Cauchy–Schwarz or direct substitution. Between unequal norms in this example the neighbors are orthogonal. Thus each neighbor defines a facet. The four pairs of opposite normals span $\mathbb{R}^4$, so the cell is bounded.

Moving the first two positive centers inward along their respective rays to radius $2$ gives

$$
p'=(2,0,0,0),\qquad q'=(6/5,8/5,0,0).
$$

Their squared distance is $(-4/5)^2+(8/5)^2=16/5<4$. Their unit balls overlap. The all-contact assignment on these same fixed directions is therefore infeasible.

For a direct volume check, use coordinates $(x_1,(3x_1+4x_2)/5,x_3,x_4)$, with Jacobian determinant $4/5$. The packing's Voronoi cell at $0$ becomes a rectangular box with side lengths $(5/2,5/2,2,2)$, hence has volume $125/4$. The formal half-space intersection after the radial move has volume $20$. Both volumes exceed $8$.

## The actual minimum for these eight rays

Keep all eight rays and allow their radii to vary independently. Let $r,s\ge 2$ be the two positive radii in the first plane and let $p=rs$. The packing condition gives $r^2+s^2-6p/5\ge4$. Also $(r^2-4)(s^2-4)\ge0$, so $r^2+s^2\le4+p^2/4$. Combining the inequalities gives $p\ge24/5$. The same argument applies to the product of the two opposite radii.

If the two opposite radii on each of the first two lines are $r_+,r_-$ and $s_+,s_-$, then

$$
(r_++r_-)(s_++s_-)\ge\left(\sqrt{r_+s_+}+\sqrt{r_-s_-}\right)^2\ge96/5.
$$

Each width in the first plane is half the sum of its opposite radii. The remaining two widths are at least $2$ each, and the determinant is $4/5$. Consequently the volume is at least $24$. This is attained with radius $2$ on the first line, $12/5$ on the second line, and $2$ on the two orthogonal axes. The feasible minimum for these fixed rays is $24$. The formal all-contact value is $20$.

## Exact minimum for the two-line family

Take two distinct lines with unit directions $u,v$ in a plane. Orient the directions so that $c=\langle u,v\rangle\in[0,1)$. Take two mutually orthogonal axes in the perpendicular plane. Place one neighbor on each of the eight rays, subject to unit-ball packing and with no upper bound on radii. The minimum Voronoi volume at the origin is

$$
\frac{4\max(4,8c)}{\sqrt{1-c^2}}.
$$

For either same-sign pair of plane rays, packing implies $r^2+s^2-2cp\ge4$ for $p=rs$. Since $r,s\ge2$, the inequality $r^2+s^2\le4+p^2/4$ gives $p\ge8c$. Thus each same-sign product is at least $\max(4,8c)$. The width-product argument above applies with that bound and determinant $\sqrt{1-c^2}$. For equality use radii $2$ on the first line, $\max(2,4c)$ on the second line, and $2$ on the other axes. When $c\le1/2$, all radii equal $2$ and the same-sign squared separation is $8(1-c)\ge4$. When $c>1/2$, the same-sign squared separation at the stated radii is exactly $4$. All other pairs have either nonpositive inner product or opposite directions, so they satisfy the packing constraint. Every choice of positive widths defines a bounded box in the four normal coordinates.

For $c>1/2$ the feasible volume is $2c$ times the volume of the infeasible all-contact intersection. The displayed minimizers are inside the strict shell of radius $2\sqrt2$ when $c<1/\sqrt2$. The formula treats eight specified neighbors and does not bound the volume after adding other cutting neighbors.

## When the reduction works

For unit directions $u_i$ and radii $r_i$, the selected centers form a packing with the origin if $r_i\ge 2$ and each pair satisfies

$$
r_i^2+r_j^2-2r_i r_j \langle u_i,u_j\rangle \ge 4.
$$

At $r_i=r_j=2$ this becomes $\langle u_i,u_j\rangle\le 1/2$. If every pair of directions meets this angular condition, the all-contact assignment is feasible in the model retaining those neighbors, and half-space containment proves the proposed minimization in that model. Otherwise the all-contact assignment lies outside the admissible set. A bound for contact configurations alone cannot cover that case through this reduction.

The unrestricted volume bound remains unresolved by this calculation. The current supplementary repository distinguishes its proved cases from the residual shell configurations. [Supplementary repository](https://github.com/creelie/d4-voronoi-cells) · [Independent work on the all-contact and near-lattice cases](https://hexagonmath.org/pdf/2611.00390v1)

## Reproduce

Run `python scripts/audit_d4_radial_reduction.py` from the Anaxia checkout. The verifier uses exact rational arithmetic for all 36 center pairs, all eight active facets, and the overlap after projection. [Machine-readable evidence](../data/d4-radial-audit.json)
