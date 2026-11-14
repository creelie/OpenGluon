# An exact six-center obstruction for the D₄ packing

Let $D_4=\{z\in\mathbb Z^4:\sum_i z_i\text{ is even}\}$. We use balls of radius $1/\sqrt 2$, so the minimum permitted separation of two centers is $\sqrt 2$. A lattice center **blocks** a proposed insertion at $x$ when its distance from $x$ is **strictly less** than $\sqrt 2$. Tangency is allowed.

**Theorem.** Every point outside $D_4$ has at least six blockers in $D_4$. The bound is attained at $x=(2/3,1/3,1/3,0)$.

Consequently, deleting up to five centers permits no insertion at a new position. We also show below that removing six centers and inserting any off-lattice point allows at most five replacements. Thus the packing is **7-saturated** in the terminology of [Fejes Tóth, Kuperberg and Kuperberg](https://arxiv.org/abs/math/9511225). At the sharpness witness one may delete six and insert one. That loses five balls, so this witness gives no upper bound on the saturation order.

## Proof

Translate a nearest lattice point to the origin. Sign changes and coordinate permutations preserve $D_4$, so write the translated point as $x=(a,b,c,d)$ with $a\ge b\ge c\ge d\ge 0$. Since the origin is at least as close as the root $(1,1,0,0)$, we have $a+b\le 1$. The resulting chamber is the simplex with vertices

$$0,\quad(1,0,0,0),\quad(1/2,1/2,0,0),\quad(1/2,1/2,1/2,0),\quad(1/2,1/2,1/2,1/2).$$

In that order, its barycentric coordinates are $1-a-b$, $a-b$, $2(b-c)$, $2(c-d)$, and $2d$. They are nonnegative, sum to one, and reconstruct $x$. Put $T=\lVert x\rVert^2/2$. At the five vertices, the values of the functions used below are

| Function | Origin | $(1,0,0,0)$ | $(1/2,1/2,0,0)$ | $(1/2,1/2,1/2,0)$ | $(1/2,1/2,1/2,1/2)$ |
| --- | ---: | ---: | ---: | ---: | ---: |
| $\lVert x\rVert^2$ | 0 | 1 | 1/2 | 3/4 | 1 |
| $a+d-T$ | 0 | 1/2 | 1/4 | 1/8 | 1/2 |
| $a+c-2T$ | 0 | 0 | 0 | 1/4 | 0 |

By convexity of squared norm, $\lVert x\rVert^2\le 1$, so the origin blocks $x$. The second row and concavity give $a+d>T$ whenever $x\ne 0$. The third function is strictly concave, so $a+c>2T$ at every nonvertex. For instance, if $x=\sum_i\lambda_i v_i$ then

$$\sum_i\lambda_i\lVert v_i\rVert^2-\lVert x\rVert^2=\sum_{i<j}\lambda_i\lambda_j\lVert v_i-v_j\rVert^2,$$

which is positive whenever the combination uses two distinct vertices with positive weights.

Write $e_i$ for the coordinate vectors. A root $r=\pm e_i\pm e_j$ has squared norm two, so it blocks exactly when $\langle x,r\rangle>T$. The roots $e_1+e_2$, $e_1+e_3$, and $e_1+e_4$ all qualify because each inner product is at least $a+d$. Now use the two disjoint pairs

$$\{e_1-e_2,\ e_2+e_3\},\qquad \{e_1-e_4,\ e_3+e_4\}.$$

The inner products in each pair sum to $a+c$. At any nonvertex that sum exceeds $2T$, so each pair contributes a blocker. At the four nonzero vertices, the following choices have inner product strictly above $T$:

| Vertex | From first pair | From second pair |
| --- | --- | --- |
| $(1,0,0,0)$ | $e_1-e_2$ | $e_1-e_4$ |
| $(1/2,1/2,0,0)$ | $e_2+e_3$ | $e_1-e_4$ |
| $(1/2,1/2,1/2,0)$ | $e_2+e_3$ | $e_1-e_4$ |
| $(1/2,1/2,1/2,1/2)$ | $e_2+e_3$ | $e_3+e_4$ |

The two pairs contain four distinct roots that are different from the three already counted. An off-lattice $x$ stays nonzero after reduction. This gives five distinct blocking roots and the origin in every case.

## Consequence for six deletions

Suppose a set of six deleted lattice centers admits an off-lattice insertion. Every proposed off-lattice center must have been blocked by all six deleted centers, since it has at least six blockers and is compatible with every surviving center. No deleted lattice center can therefore be reinserted alongside any off-lattice insertion.

Some pair $z,w$ among the six deleted centers satisfies $\lVert z-w\rVert^2\ge 4$. Indeed, squared distances between distinct lattice points are positive even integers. If every pair had squared distance two, choosing any one of the six points as origin would yield five difference vectors with Gram matrix having diagonal entries two and off-diagonal entries one. That matrix is positive definite of rank five, impossible in $\mathbb R^4$.

Put $m=(z+w)/2$. Any replacement center $x$ must satisfy

$$\lVert x-m\rVert^2=\frac{\lVert x-z\rVert^2+\lVert x-w\rVert^2}{2}-\frac{\lVert z-w\rVert^2}{4}<1.$$

If two such centers $x,y$ are compatible, their squared separation is at least two. Since each lies strictly within distance one of $m$, the vectors $x-m,y-m$ have strictly negative inner product. At most five vectors in $\mathbb R^4$ can have all pairwise inner products strictly negative. To see this, any six vectors admit a nonzero affine dependence. Its coefficients sum to zero, so the positive and negative parts give equal positive linear combinations of disjoint groups of vectors. Taking their inner product gives a squared norm on one hand and a strictly negative number on the other.

It follows that a rearrangement deleting six centers and introducing an off-lattice center contains at most five replacements. A rearrangement restricted to lattice positions can only fill the vacated sites. This proves 7-saturation and rules out nontrivial equal-size replacements of six centers.

## Sharpness and verification

At $x=(2/3,1/3,1/3,0)$ the blockers are the origin, $e_1+e_2$, $e_1+e_3$, $e_1+e_4$, $e_1-e_4$, and $e_2+e_3$. A blocker must have each integer coordinate in $[-2,2]$ because $|z_i|<|x_i|+\sqrt 2<3$. Enumerating the even-sum vectors in that box with exact squared distances verifies that this list is complete. After deleting those six blockers, the point can be inserted.

```sh
python scripts/verify_d4_vacancy.py
```

The checker reconstructs the vertices from their chamber coordinates, checks the vertex table and root choices, and verifies the complete sharpness list over the finite box. It uses rational arithmetic and the written proof supplies the argument for every real point. The saved output is [available as JSON](../data/d4-vacancy.json).

This result controls local changes to the fixed $D_4$ packing after a small number of deletions. The unrestricted density and Voronoi-volume conjectures need an argument for other center configurations. For that distinction, see [Musin's problem formulation](https://arxiv.org/abs/1712.04099) and the [current scope of the linked D₄ research repository](https://github.com/creelie/d4-voronoi-cells). This note supplies a direct derivation and makes no claim of publication priority.
