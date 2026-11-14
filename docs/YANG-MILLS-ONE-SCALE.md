# A wider pressure allowance in the conditional Yang–Mills criterion

The one-scale ascent in Theorem 7.56 of *The Yang–Mills Mass Gap from One Bound at One Scale* extends to a smaller initial window with a larger allowed pressure per spatial volume. The Wightman-limit hypothesis and the need for a uniform weak-coupling seed remain. The proof uses the source's spatial-cut estimate and trace inequalities. [Source manuscript, Sections 7.10–7.11](https://github.com/creelie/4Y-M/blob/paper/papers/4Y-MPaper.pdf) · [Preprint record](https://www.preprints.org/manuscript/202611.1282)

## One-scale conditions and consequences

Use the source notation $Z_s(T)=1+D_s(T)$ for the vacuum-normalized trace on a spatial torus with side tuple $s$ and volume $V(s)$. In both rows below, take an integer $T_0\ge3$ and require $\log Z_s(T_0)\le\gamma V(s)$ for every spatial torus $s$ whose three integer sides lie in $[2T_0,40T_0)$. The source's Theorem 7.56 uses a window up to $48T_0$ and the seed $\gamma T_0^3\le1/35{,}389{,}440$.

| Allowed $\gamma T_0^3$ | Increase in allowed coefficient | Guaranteed physical gap under (W) |
| ---: | ---: | ---: |
| $1/32{,}000{,}000$ | $10.592\%$ | $\log(2880/2401)/t_0$ |
| $3/81{,}920{,}000$ | $29.6\%$ | $\log(5120/5043)/t_0$ |

The continuum statements use the quantifiers of Theorem F. In its notation, for every sufficiently large $p$ and every $N\ge N_0(p)$, use a suitable integer $T_0=T_0(N,p)$ with $3\le T_0\le Nt_0$ at coupling $\beta_{N,p}$. The same selected row must apply throughout the family. At a fixed coupling the proof also bounds the leading nonvacuum eigenvalue on spatial tori with smallest side at least $2T_0$ and aspect ratio less than $20$.

## Proof

Put $T_i=2^iT_0$ and choose the integer cutting mesh $P_i=20T_i$. The conditions of Proposition 7.52, $T_i\ge3$ and $P_i>12T_i$, hold exactly. The factor from that proposition is

$$K=\frac{1}{1-12T_i/P_i}=\frac52.$$

The $i=0$ hypothesis therefore gives $\log Z_t(T_0)\le F_0 V(t)$ for every spatial torus with all sides at least $2T_0$, with $F_0=K\gamma$. Suppose the analogous bound holds at $T_i$ with $F_i\ge0$. To propagate it, use every torus $s$ with sides in

$$[2T_{i+1},2P_{i+1})=[4T_i,80T_i).$$

The inductive estimate applies on this window, and Lemma 7.27 gives

$$\log Z_s(T_{i+1})\le D_s(2T_i)\le D_s(T_i)^2\le (e^{F_iV(s)}-1)^2.$$

The function $(e^{F_i v}-1)^2/v$ is nondecreasing for $v>0$, as is seen by its nonnegative power-series coefficients. Since $V(s)<(80T_i)^3$, applying Proposition 7.52 at $T_{i+1}$ gives the next estimate with

$$F_{i+1}=K\frac{(e^{y_i}-1)^2}{(80T_i)^3},\qquad y_i=(80T_i)^3 F_i.$$

Thus $y_{i+1}=20(e^{y_i}-1)^2$. All cut meshes, time extents and side ranges here are integers. The original proposition supplies extensivity beyond the window at each step.

For $0\le y<3$, the bounds $n!\ge2\cdot3^{n-2}$ for $n\ge2$ give

$$e^y-1\le y+\frac{y^2}{2(1-y/3)}.$$

For the first row $y_0\le1/25$, so $e^y-1\le B y$ on this interval with $B=49/48$. For the second row $y_0\le3/64$, so $B=41/40$ works on its interval. Set $C=20B^2$ and $u_0=Cy_0$. The row-wise maxima for $u_0$ are $2401/2880$ and $5043/5120$, both strictly below one. Consequently $y_i$ stays in the selected interval and $Cy_i\le u_0^{2^i}$.

Given a spatial torus $t$ with smallest side $a\ge2T_0$ and largest side $b<20a$, take the largest index with $2T_i\le a$. Then $a<4T_i$ and $b<80T_i$. With $r_1(t)$ the leading nonvacuum eigenvalue ratio, positivity and the trace expansion give

$$r_1(t)^{T_i}\le D_t(T_i)\le e^{y_i}-1\le B y_i\le u_0^{2^i}.$$

Here $B/C<1$. Hence $r_1(t)\le u_0^{1/T_0}$. For a cube of side $n$ with $2T_i\le n<4T_i$, we have $F_i n^3\le y_i/8000$. Monotonicity in Euclidean time and the same trace inequality give

$$D_n(n)\le D_n(T_i)^2\le\left(\frac{B}{8000 C}\right)^2 u_0^{n/(2T_0)}.$$

If the seed is zero, these bounds hold with $u_0=0$, and for the following continuum conclusion one can simply use the strictly positive row-wise maximum of $u_0$ as its bound. With $n=NL_p$, $L_p\ge2t_0$ and $T_0\le Nt_0$, the cubic estimate implies condition (Z) of the source, while $r_1(t)\le e^{-\Delta/N}$ on the same cubes, with $\Delta$ as given in the table. These are the two inputs used after Theorem 7.56 in the proof of Theorem F. The original argument with (W) then gives equality of the phases, a unique vacuum, and this continuum gap.

The progress is quantitative: the conditional argument requires a smaller range of boxes and allows a larger initial pressure coefficient. It does not construct the Wightman limit or verify the pressure estimate along a continuum weak-coupling sequence.
