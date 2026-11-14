# Sharp extra-center radius for 24 fixed D4 rays

Place a unit-ball center at the origin of $\mathbb R^4$ and one center on each of the 24 unit rays $u=(\pm e_i\pm e_j)/\sqrt2$, with $i<j$. Allow the radii of those 24 centers to vary independently in $[2,R]$. Among all such packings, the smallest possible distance from the origin to an additional center is

$$
m(R)=\begin{cases}
\bigl(R+\sqrt{8-R^2}\bigr)/\sqrt2,&2\le R\le2\sqrt2,\\
2,&R\ge2\sqrt2.
\end{cases}
$$

In particular, an additional center at distance at most $\sqrt6$ is possible exactly when $R\ge1+\sqrt3$. At equality the extra center has radius exactly $\sqrt6$. The fixed-direction hypothesis differs from the [arbitrary small displacement estimate](D4-GRID-PACKINGS.md#how-close-an-extra-center-can-come-to-a-d4-contact-shell).

## Lower bound

Write an extra center as $x$, its norm as $r\ge2$, and its two largest absolute coordinates as $a\ge b$. The root direction maximizing $x\cdot u$ gives $(a+b)/\sqrt2\ge r/\sqrt2$. Indeed, $r^2\le a^2+3b^2\le(a+b)^2$. If $r\ge2\sqrt2$ the claimed bound is immediate. Otherwise the separation condition from the center at radius $s\in[2,R]$ on this maximizing ray is

$$
f(s)=r^2+s^2-2s(x\cdot u)-4\ge0.
$$

But $f(2)\le r(r-2\sqrt2)<0$. Convexity on $[2,R]$ therefore forces $f(R)\ge0$, which implies

$$
r^2-\sqrt2 Rr+R^2-4\ge0.
$$

For $2\le R<2\sqrt2$, this quadratic is strictly negative at $r=2$ because its value there is $R(R-2\sqrt2)$. Since $r\ge2$, its upper root is the required lower bound. At $R=2\sqrt2$ the upper and lower roots are both 2. Larger $R$ needs only $r\ge2$.

## Attainment and the cutoff

For $2\le R\le2\sqrt2$, take $x=m(R)e_1$. Assign radius $R$ to the six unit rays with first coordinate $1/\sqrt2$ and radius 2 to the others. Distinct root directions have inner product at most $1/2$, so any two centers on those rays with radii $s,t\ge2$ have squared separation at least $s^2+t^2-st=(s-t)^2+st\ge4$. The six radii $R$ give squared separation exactly 4 from $x$ by the quadratic equality. All other root directions have nonpositive first coordinate and give squared separation at least 8 from $x$. The origin satisfies its separation condition as well. For larger $R$ the same construction at $R=2\sqrt2$ is still allowed and gives $r=2$.

To see the $\sqrt6$ threshold directly, for $R<2\sqrt2$ the lower root is below 2. Thus the upper root is at most $\sqrt6$ precisely when the quadratic at $\sqrt6$ is nonnegative. That value is $R^2-2\sqrt3R+2=(R-\sqrt3)^2-1$, so for $R\ge2$ the condition is $R\ge1+\sqrt3$.

The radius formula permits an extra center off the lattice. For one special direction of that center, the Voronoi volume can also be bounded sharply.

## A Voronoi volume bound with one additional near center

Suppose one center lies on each of the 24 fixed root rays at radius at least 2. Among any further centers, allow at most one at distance less than $2\sqrt2$ from the origin. If present, suppose it lies on a ray through a vertex of the reference Voronoi cell. Then the cell at the origin has volume at least 8, with strict inequality whenever that extra center is present in the strict shell. Centers at distance at least $2\sqrt2$ may be arbitrary subject to packing.

Use scaled coordinates $t=z/\sqrt2$ for physical positions $z$ in the cell. The reference polytope $P$ in these coordinates is given by $|t_i|+|t_j|\le1$ for all $i<j$, and is contained in the unit ball. Its vertices are the points $\pm e_i$ and $(\pm1,\pm1,\pm1,\pm1)/2$. Signed permutations preserve the root directions. The orthogonal matrix

$$
\tfrac12\begin{pmatrix}1&1&1&1\\1&1&-1&-1\\1&-1&1&-1\\1&-1&-1&1\end{pmatrix}
$$

also preserves them, because any signed sum of two columns has two zero coordinates before normalization. It sends $e_1$ to $(1,1,1,1)/2$. We can therefore take the extra center to be $r e_1$ for $2\le r<2\sqrt2$. Its bisector in scaled coordinates is $t_1\le a$, where $a=r/(2\sqrt2)\in[1/\sqrt2,1)$. Write $b=\sqrt{1-a^2}$.

For each of the six root rays with positive first coordinate, the packing condition for its radius $s$ is $s^2-\sqrt2 rs+r^2-4\ge0$. The quadratic is negative at $s=2$ because $r<2\sqrt2$, so $s\ge2(a+b)$ by the upper-root formula. Thus the corresponding half-spaces contain all points satisfying $t_1+|t_j|\le a+b$ for $j>1$. Every other root bisector contains $P$. In particular, all of $P$ with $t_1\le1/2$ survives. For $1/2\le t=t_1\le a$, the cell also contains the cube in the remaining three coordinates with half-width

$$
h(t)=\min\left(\tfrac12, a+b-t,\sqrt{(1-t^2)/3}\right).
$$

Indeed, $|t_j|\le1/2$ handles all the roots with zero first coordinate, $-t+|t_j|\le1$ handles the backward roots, and the forward-root constraints were proved above. The last term confines the cube to the scaled unit ball, so no center at distance $2\sqrt2$ or farther can cut it. The same observation protects the surviving portion of $P$.

The old positive cap $1/2\le t\le1$ has cubes of half-width $1-t$. Comparing volumes, the common factor 8 from the cube volume cancels, and the old integral is $\int_{1/2}^{1}(1-t)^3\,dt=1/64$. We show the new integral is strictly larger.

- If $b\ge1/2$, the intervals $[1/2,3/5]$ and $[3/5,7/10]$ are both contained in $[1/2,a]$. On them $h(t)$ is at least $23/50$ and $41/100$, respectively. The ball constraint follows from $(3/5)^2+3(23/50)^2<1$ and $(7/10)^2+3(41/100)^2<1$. The forward constraint follows from $a+b-t\ge b$. Thus the integral is at least $((23/50)^3+(41/100)^3)/10>1/64$.
- If $0<b\le1/2$, then $h(t)\ge1-t$ throughout $[1/2,a]$. The inequality for the ball term is $(1-t^2)/3\ge(1-t)^2$ for $1/2\le t\le1$. On $[3/5,7/10]$, the cap $1/2$ exceeds $1-t$ by at least $1/10$, and the ball term exceeds it by at least $1/100$ because $\sqrt{(1-(7/10)^2)/3}>41/100$. The forward term exceeds it by $a+b-1\ge b-b^2\ge b/2$, hence $h(t)-(1-t)\ge b/50$ throughout this interval. The gain in the integral is at least $(1/10)\cdot3(3/10)^2\cdot b/50=27b/50000$. The lost cap contributes $(1-a)^4/4$. Since $a\ge\sqrt3/2>3/4$, we have $1-a=b^2/(1+a)\le4b^2/7$, so the loss is at most $64b^8/2401\le b/4802<27b/50000$.

The physical scaling multiplies both compared volumes by 4. Since the reference volume is 8, strict gain gives the claimed strict inequality. If there is no additional center in the strict shell, the radius-2 reference polytope remains inside the cell by half-space containment. The unrestricted conjecture still requires handling nonroot directions and extras away from these vertex rays. [Reference cell and volume](D4-GRID-PACKINGS.md) · [Problem formulation and related exact-contact results](https://hexagonmath.org/pdf/2611.00390v1)

## Several extras on vertex rays with nonpositive pairwise inner products

Retain the centers on the 24 root rays. Suppose every further center in the strict shell lies on a distinct reference vertex ray, and their unit directions form a nonempty set $v_1,\ldots,v_n$ with $v_i\cdot v_j\le0$ for $i\ne j$. Then the Voronoi volume is strictly greater than 8. Centers at distance at least $2\sqrt2$ remain arbitrary subject to packing.

For a chosen direction $v$, use the root-preserving transformation above to send $v$ to $e_1$. A different reference vertex $w$ with $v\cdot w\le0$ then has one of three forms: an orthogonal coordinate-axis vertex, the opposite vertex $-e_1$, or

$$w=(-1,\pm1,\pm1,\pm1)/2,$$

with $v\cdot w=-1/2$. These exhaust the nonpositive inner products between distinct reference vertices.

The old slabs $S_v=P\cap\{t\cdot v>1/2\}$ are pairwise disjoint. For orthogonal directions, the adapted-frame constraint $|t\cdot v|+|t\cdot w|\le1$ rules out membership in both slabs. Opposite directions cannot both have positive projection. When $v\cdot w=-1/2$, the vector $v+w$ has norm 1. Since $P$ lies in the unit ball, $(v+w)\cdot t\le1$ on $P$, again ruling out two projections greater than $1/2$.

For each extra, construct its new cube slab $G_v$ as in the one-center proof, using $t\cdot v>1/2$ and its own radius parameter $a_v$. In the frame $v=e_1$, this slab has $t_1>1/2$ and $|t_j|\le1/2$ for $j>1$. Its projection onto an orthogonal extra direction is therefore at most $1/2$, and its projection onto the opposite direction is negative. For a direction with inner product $-1/2$, it satisfies

$$t\cdot w\le\frac{-t_1+|t_2|+|t_3|+|t_4|}{2}<\frac12.$$

Thus every $G_v$ survives every other extra's bisector, whose threshold is at least $1/\sqrt2$. The same projection bounds show the new slabs are pairwise disjoint, because $G_w$ requires $t\cdot w>1/2$. Every new slab satisfies all root bisectors by the one-center proof: its own extra forces the six forward roots outward, and the other root constraints follow from the coordinate bounds. The scaled unit-ball truncation protects the slabs against all farther centers. The core $P\setminus\bigcup_v S_v$ survives every extra cut and is disjoint from every $G_v$. Each new slab has strictly greater volume than its old slab, so summing the comparisons proves the strict volume bound.

There are at most eight such directions. To see this directly, let $G=(v_i\cdot v_j)$ be their Gram matrix. For every off-diagonal entry $q\in[-1,0]$, $q^2\le-q$, while

$$\sum_{i\ne j}G_{ij}=\left\|\sum_i v_i\right\|^2-n\ge-n.$$

Hence $\operatorname{tr}(G^2)\le2n$. Its rank is at most 4, so Cauchy--Schwarz for its nonnegative eigenvalues gives $n^2=(\operatorname{tr}G)^2\le4\operatorname{tr}(G^2)\le8n$, and $n\le8$. If any pair has inner product $-1/2$, the trace inequality is strict and $n<8$. Positive-inner-product pairs and extras away from the reference vertex rays remain untreated.

Run `python scripts/verify_d4_partial_contacts.py` to check the root-preserving symmetry, all nonpositive vertex-pair support bounds, and their cube-projection bounds with exact rational arithmetic. The slice integrals and their comparison for arbitrary radii are proved above.
