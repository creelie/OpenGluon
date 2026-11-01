# From local decay to the cube coefficient, for calm boundary data

Status: November 2026. Working note, not refereed.

This note is part of the Yang–Mills notes in this directory; `../README.md` explains
the research programme they come from and defines the terms used (cube estimate, fibre, calm, chart). In brief: a
lattice approach to the Yang–Mills mass gap
([romanov360/4Y-M](https://github.com/romanov360/4Y-M), branch `claude/yang-mills-mass-gap-wf5h8x`) reduces the gap in
the continuum to one *cube estimate*, plus the existence of the continuum limit. Four steps of the cube estimate are open:
- **the cube coefficient**: from the proved local decay to the cube's response to a boundary change;
- **non-calm fibres**: control of field configurations with no nearby small-field configuration;
- **harmless large fields**: rare regions of large field do not spoil the bound;
- **composition across scales**: combining the cube conditions at all scales (renormalisation group).

We write **CC(n, α)** for the paper's *constrained cube condition*: for every class c of exterior links, the summed
cube coefficients K^c_c of a cube of side n with its block averages held fixed are at most α(n/2)⁴ (the number of
translates containing a link). This is the paper's Definition `def:cube` with the block averages fixed.

This note works on the cube-coefficient step for calm (small-field) boundary data. It proves one of the two cases and reduces the other to an
open local estimate (§0).

It builds on the paper `strong-coupling/forest/main.tex` of that repository. Labels such as `thm:chartdecay` are its
`\label` names. The results used most are:
- **`fibrechart`**: a convex coordinate chart on the fibre around a calm field;
- **`chartdecay` / `explicitdecay`**: on that chart, covariances decay exponentially, at the explicit rate 2.5·10⁻⁴ per
  lattice unit and with amplitude ∝ 1/β;
- **`calmfibres` / `calmexterior`**: the probability of leaving the chart is tiny on calm data;
- **`privatesubmersion`**: each block average can be moved by its own eight "private" links.

## 0. Summary

The cube-coefficient step asks for the passage from the fibre decay of Theorem `chartdecay` to the constrained cube
coefficient, with a supremum over boundary conditions. This note does the calm-exterior case.

**Proved:**
- **Lemma 1, the split of the exterior links.** The exterior links that couple to the cube V = A_W come in exactly two
  disjoint kinds:
  - **type (a)**: links that share a plaquette with A_W. They enter no average.
  - **type (b)**: links that enter one cut-off average V♯_k. They share no plaquette with A_W, and they enter exactly
    one average, through a single path.

  This is proved by hand below and checked by enumeration (`checks/geometry_checks.py`).
- **Theorem 1 (type-(a) links, calm data).** For every type-(a) link j and every calm boundary datum (E, c), the
  local cube coefficient obeys

  c_{V,j}(E, c) ≤ C_* + 120 r λ ε_W(K, λ) |A_W|,  C_* = 480√18 e^{α_G} p̄² S(α_G)^{1/2} ≤ 7.4·10¹².

  - C_* depends neither on λ (so not on β) nor on n, |W| or the background.
  - The second term is the mass off the chart times the oscillations.
- **Corollary 1.** The type-(a) part of K^c_c is at most 4(n/2+1)³ (π/2)(C_* + 120 r λ ε_W |A_W|).

**Reduced, not proved:**
- **Theorem 2 (type (b), a reduction).** For a type-(b) link, transporting the fibre along the eight private links of
  its average gives a λ-independent leading constant C_b ≈ 9.2·10¹³ (explicit). It also gives
  - an O(1/λ) term whose constant is only sketched, and
  - one remainder Ξ_j: the Lipschitz dependence, on E_j, of the constrained measure restricted to the large-path set of
    the single block of j's average.

  Ξ_j is not bounded here. It is a one-block large-field statement, part of the harmless-large-fields step.
- **Corollary 2 (CC(n, α) on calm data, conditional).** It needs two inputs:
  - Ξ_j ≤ C_Ξ for every type-(b) link;
  - λ ε_W |A_W| ≤ 1.

  If both hold, the constrained cube condition CC(n, α) holds on calm data for n ≥ 2.3·10¹⁵/α + O(1) (α ≤ 1/2), with
  C_Ξ entering the threshold linearly. This is the nonabelian counterpart, on calm data, of Theorem `constrainedcube`(iii)
  of the paper, which proves the same condition for the quadratic (Gaussian) approximation for n ≥ 2·10¹⁵/α. The two thresholds are of the same size.

**What this does not do:**
- **The off-chart term is not uniform along the tuning.** It is λ ε_W |A_W|, with ε_W ≈ (C/K³)^{45|W|} e^{−3λK²/4}.
  It is small only when λK² ≫ |W| log(…), that is, for β_W ≳ 10³⁹|W|. On cubes of fixed physical size,
  |W| ∼ a⁻⁴ while β ∼ log(1/a), so the bound fails there. This is exactly the non-calm-fibres and harmless-large-fields steps: by Proposition `calmrare` of the paper, non-calm windows are the typical case on such cubes. §5 states the local estimate that would remove the factor |A_W|.
- **Non-calm data are excluded.** Fibres with no calm field and exteriors with no calm completion belong to the non-calm-fibres step.

So the cube-coefficient step is closed for type-(a) links on calm data. For type-(b) links it is reduced to one local large-field remainder.
The remaining non-uniformity is moved entirely into a *localised* off-chart estimate, which is the interface with the harmless-large-fields step.

## 1. Setting and definitions

As in Sec. `ssec:smallfibres`:
- **Lattice and blocks.** G ⊂ U(r) compact, the periodic lattice of side 2L, the tree gauge of Definition `blockgauge`.
  W is the set of blocks of the cube [0, n)⁴ (n even), and A_W the active links with base in ⋃W. **The cube of the
  cube condition is V = A_W**, with |A_W| = 49|W|.
- **Exterior and averages.** An *exterior* E is an assignment of the active links off A_W. Tree links are I and are not
  variables. The averages c = (c_k), k = (y, μ), y ∈ W, are values of the cut-off averages V♯_k of (`eq:cutoff`).
- **The constrained law.** π_{E,c} is the conditional law of e^{−λQ} ∏_{e∈A_W} dU_e given V♯ = c, in the coarea
  version: density e^{−λQ} J⁻¹, J = det(Dc Dc*)^{1/2}, with respect to the Riemannian volume of the fibre
  F_E(c) = {U ∈ G^{A_W} : V♯_k(U, E) = c_k ∀k}. Here Q = Σ_p ‖U_p − I‖²_HS over the plaquettes meeting A_W.
- **Distances.** δ(g, h) = ‖g − h‖_HS (chordal), d_V(U, U′) = Σ_{e∈A_W} δ(U_e, U′_e), and W₁ is the Kantorovich
  distance for d_V. Link distance d(a, b) is the ℓ^∞ distance of midpoints. Geodesic distance on G satisfies
  δ ≤ d_geo ≤ (π/2)δ.

**Definition 1 (calm data).** (E, c) is *calm* with parameters (K, λ, s) if F_E(c) contains a field U^0 with
δ(U^0_p, I) ≤ K/(4√n_P) for every plaquette p with a vertex in a block of W⁺, and the hypotheses of Corollary
`calmfibres` hold at U^0. Two things then hold:
- Theorem `chartdecay` (with Proposition `explicitdecay`: α_G = 2.5·10⁻⁴, p̄_α = ‖P̄‖_{(α)} ≤ 4.8) applies to
  μ = π_{E,c}(· | Φ(Ω_r));
- π_{E,c}(F \ Φ(Ω_r)) ≤ ε_W(K, λ).

Corollary `calmexterior` gives the following. On every exterior with a calm completion, all fibres except a set of
mass ≤ ε″_W in the law of the averages are calm.

**Definition 2 (local cube coefficient).** For an exterior link j, Z ∈ 𝔤 with |Z| = 1, let E_t equal E except at j,
where (E_t)_j = E_j e^{tZ}. Put

c_{V,j}(E, c) = sup_{F, Z} limsup_{t→0} |E_{π_{E_t,c}} F − E_{π_{E,c}} F| / |t|,

the supremum over 1-Lipschitz F for d_V. If t ↦ E_{π_{E_t,c}}F is continuous on [0, T], and c_{V,j}(E_t, c) ≤ C for
every t, then this function is C-Lipschitz, because its Dini derivatives are bounded by C. Hence

W₁(π_{E,c}, π_{E′,c}) ≤ C d_geo(E_j, E′_j) ≤ (π/2) C δ(E_j, E′_j)

whenever the geodesic from E_j to E′_j stays in the calm set. The constrained cube coefficient of CC(n, α), restricted to
calm pairs, is therefore at most (π/2) sup c_{V,j}.

## 2. Lemma 1: the two types of exterior links

**Lemma 1.** Let j be an active link off A_W.
- (i) If j enters some V♯_k, k = (y, μ), y ∈ W, then:
  - j = (x + e_μ, μ) with x ∈ B(y), o_μ(x) = 1, and y + e_μ ∉ W;
  - j enters only the path P_x = U_{x,μ} U_{x+e_μ,μ} of V♯_k, and no other average;
  - no plaquette contains j and a link of A_W.
- (ii) Otherwise j enters no average, and V♯ does not depend on j.
- (iii) The private links of V♯_k, namely (x, μ) with x ∈ B(y) and o_μ(x) = 1, enter no average other than V♯_k.

*Proof.*
- **Which links enter V♯_k.** V♯_k is a function of the sixteen paths P_x = U_{x,μ} U_{x+e_μ,μ}, x ∈ B(y). This includes
  the cut-off χ_k, which uses the same paths, and P_{2y}. The tree links are I. Every link (x, μ), x ∈ B(y), lies in A_W.
  A second link (x + e_μ, μ) lies off ⋃W only if x + e_μ ∉ B(y). Then o_μ(x) = 1 and x + e_μ ∈ B(y + e_μ), so
  y + e_μ ∉ W.
- **It enters no other average.** The averages of direction ν ≠ μ use only links of direction ν. An average V♯_{y′,μ}
  uses links with base in B(y′) ∪ B(y′ + e_μ). For j the second option forces y′ = y, and the first is excluded since
  j's base is not in ⋃W.
- **No shared plaquette.** Since y ∈ W and y + e_μ ∉ W, y_μ = n/2 − 1. So x_μ = 2y_μ + 1 = n − 1, and j = (z, μ)
  with z_μ = n.
  - A plaquette through j lies in a plane (μ, ν) and spans the μ-interval [n, n + 1].
  - Its four links have base z, z + e_μ, z ± e_ν or z ± e_ν + e_μ, all with μ-coordinate n or n + 1.
  - So no link of the plaquette has base in [0, n)⁴, and none is in A_W.
- **Private links (iii).** (x, μ) with o_μ(x) = 1 is a link of direction μ with base in B(y). It enters only averages of
  direction μ, of blocks y′ with B(y′) ∋ x or B(y′ + e_μ) ∋ x. The second needs x ∈ B(y′ + e_μ) = B(y), so y′ = y − e_μ,
  and there it would be in S^μ_y, which consists of links with o_μ = 0. Hence only V♯_{y,μ}. ∎

Checked by enumeration for n = 4 and n = 6 (`checks/geometry_checks.py`): all type-(b) links found share no plaquette with
A_W. The same script checks the following:
- every type-(a) link shares exactly one plaquette with each of its A_W-neighbours;
- it has at most 5 such neighbours (we use the trivial bound 18 = 6 plaquettes × 3 links);
- all of them lie at link distance ≤ 1.

**Counting.** A link coupled to A_W has base in [−1, n]⁴. In a class (a residue mod 2 and a direction) there are at
most (n/2 + 1)⁴ − (n/2)⁴ ≤ 4(n/2 + 1)³ such exterior links (checked: 43 ≤ 108 at n = 4, 134 ≤ 256 at n = 6).

## 3. Theorem 1 (type (a))

**Theorem 1.** Let (E, c) be calm, and let j be a type-(a) link. Then

c_{V,j}(E, c) ≤ C_* + 120 r λ ε_W(K, λ) |A_W|,

where C_* = 480 √18 e^{α_G} p̄_{α_G}² S(α_G)^{1/2}, and

S(α) = sup_j Σ_a e^{−2α d(a,j)} ≤ 4(24α⁻⁴ + 24α⁻³ + 12α⁻² + 4α⁻¹ + 1).

At α_G = 2.5·10⁻⁴ and p̄ ≤ 4.8: S ≤ 2.4582·10¹⁶ and C_* ≤ 7.36·10¹². For SU(2), r = 2.

*Proof.*

**Step 1: exact derivative.**
- By Lemma 1(ii) the fibre F = F_{E_t}(c), as a subset of G^{A_W}, does not depend on t. So J does not depend on t
  either, and π_t := π_{E_t,c} has density ∝ e^{−λQ_t} with respect to the fixed finite measure J⁻¹ dvol_F.
- Q_t − Q_0 involves only the plaquettes p ∋ j, and t ↦ Q_t is smooth. F is compact, so for bounded measurable F,

  (d/dt) E_{π_t} F |_{t=0} = −λ Cov_{π_0}(F, Q̇),  Q̇ = Σ_{p∋j} DQ_p[Z_j].

- The derivative is continuous in t, so t ↦ E_{π_t}F is C¹. It suffices to treat smooth F with per-link Lipschitz
  constant ≤ 1: mollify on G^{A_W} (a 1-Lipschitz function is a uniform limit of smooth functions with per-link
  gradient ≤ 1 + η).

**Step 2: split at the chart.**
- Let A = Φ_{U^0}(Ω_r), p = π_0(A), μ = π_0(·|A) and ν = π_0(·|A^c). By the law of total covariance,

  Cov_{π_0}(F, G) = p Cov_μ(F, G) + (1−p) Cov_ν(F, G) + p(1−p)(E_μF − E_νF)(E_μG − E_νG).

- Since |Cov_ν(F, G)| ≤ ¼ osc F osc G and 1 − p ≤ ε_W,

  |Cov_{π_0}(F, G)| ≤ |Cov_μ(F, G)| + (5/4) ε_W osc F osc G.

**Step 3: the chart term.**
- Apply Theorem `chartdecay`(ii) with φ = d(·, j) (1-Lipschitz on all indices) and α = α_G:

  |Cov_μ(F, Q̇)| ≤ (120/λ) ‖e^{−αφ}∇′F‖_{L²(μ)} ‖e^{αφ}∇′Q̇‖_{L²(μ)}.

- As in the proof of Proposition `explicitdecay`(iii), ∇′F = P̄* g^F, where g^F is the gradient of F(U e^X) in X, and
  |g^F_a| ≤ 2 for every a. Hence

  |e^{−αφ}∇′F| ≤ ‖P̄‖_{(α)} |e^{−αφ} g^F|₂ ≤ 2 p̄ S(α)^{1/2}.

- For Q̇, use the bound |D²Q_p[Y, Z]| ≤ 2(Σ_{e∈p}|Y_e|)(Σ_{e∈p}|Z_e|) of that proof (Duhamel). It is valid for the
  mixed derivative in X_a and in the exterior coordinate t, because both enter as U_e e^{X_e}.
  - So g^{Q̇}_a := ∇_a Q̇ obeys |g^{Q̇}_a| ≤ 2 m(a, j), with m(a, j) ≤ 1 the number of plaquettes containing a and j.
  - It vanishes unless a shares a plaquette with j: at most 18 links, all at distance ≤ 1 from j (Lemma 1, checks).
  - Hence |e^{αφ}∇′Q̇| ≤ p̄ e^{α} 2√18.
- So λ|Cov_μ(F, Q̇)| ≤ 120 · 2p̄S^{1/2} · 2√18 e^α p̄ = C_*.

**Step 4: the off-chart term.**
- osc F ≤ diam_{d_V} ≤ 2√r |A_W|, since δ ≤ 2√r on U(r).
- |DQ_p[Z]| ≤ 2‖U_p − I‖ ≤ 4√r for the ≤ 6 plaquettes through j, so osc Q̇ ≤ 48√r.
- So λ(5/4)ε_W osc F osc Q̇ ≤ 120 r λ ε_W |A_W|. ∎

**The lattice sum.**
- N(R) := #{a : d(a, j) ≤ R} ≤ 4(2R + 1)⁴: four directions, and per coordinate at most ⌊2R⌋ + 1 points of a shifted
  copy of ℤ in an interval of length 2R.
- By the layer-cake formula, Σ_a e^{−2αd(a,j)} = ∫₀^∞ 2α e^{−2αR} N(R) dR ≤ 4 Σ_{k=0}^4 C(4,k) k! α^{−k}.
- The script sums the exact ℓ^∞ shells: 2.45760·10¹⁶ ≤ 2.45821·10¹⁶.

**Remarks.**
1. **Independence of λ.** The amplitude 120/λ of the chart covariance cancels the factor λ of the boundary coupling.
   This is why C_* does not depend on β. The same cancellation makes the Gaussian coefficient ‖u_j‖₁ of Theorem
   `constrainedcube` independent of b.
2. **The weight is essential.** With α = 0 the same argument gives 120 · 2|A_W|^{1/2} · 2√18, which grows with the cube.
   The exponential weight of `chartdecay`(ii), not (iii), is what makes the bound uniform in n. Using (iii) link by link
   instead loses Σ_a |X_1||X_2| and gives the same order, with c_9 in place of 120 p̄².
3. **Size of C_*.** The constant is dominated by α_G⁻² ≈ 1.6·10⁷ from S^{1/2}. The floating-point decay of the chart
   Hessian quoted in Remark `chartdecayopen` (factor ≈ 0.4 per unit distance) suggests that the true C_* is of order
   10²–10³.

## 4. Theorem 2 (type (b)): transport along the private links

Let j be type (b), k = (y, μ) its average, Pr the 8 private links of k, and x_j the site with j = (x_j + e_μ, μ).

**Construction.**
- **The analytic region.** On R = {U : m_y(U, E) < ρ_G/2}, where m_y = max_{x∈B(y)} δ(P_x, P_{2y}), the cut-off is
  χ_k ≡ 1, the logarithms are principal, and V♯_k is real-analytic in (U, E_j).
- **The transport field.** By Lemma `privatesubmersion` the derivative J_k of V♯_k along Pr satisfies J_k J_k* ≥ σ_0²,
  σ_0 = (1 − 7Λ/8)/√2 = 0.03105. Define on R

  Y_t(U) = −J_k*(J_k J_k*)⁻¹ ∂_t c_k(U, E_t) on Pr, and 0 elsewhere.

  - By Lemma 1(i),(iii), the flow Θ_t of Y_t maps F_{E_0}(c) ∩ R into F_{E_t}(c) and preserves every other constraint.
  - Only P_{x_j} depends on j, with weight 1/16, so |∂_t c_k| ≤ Λ/16 (the bound on the logarithm's derivative used in
    the proof of `privatesubmersion`, with dexp of norm ≤ 1). Hence |Y|₂ ≤ Λ/(16σ_0) = 2.1994 and |Y|₁ ≤ √8 |Y|₂ ≤ 6.23.
- **The localisation.** Let ψ = Σ_x δ(P_x, P_{2y})², which is smooth. Let θ be a smooth cut-off with θ = 1 on
  [0, ρ_G²/64] and θ = 0 on [ρ_G²/16, ∞), and put θ_t = θ(ψ(·, E_t)). Then supp θ_t ⊂ {m_y < ρ_G/4} ⊂ R.
  - On the chart, every path of block y is within O(κ + s) ≪ ρ_G/8 of P_{2y}. So θ ≡ 1 there, and θ̇ = 0 there.

**The derivative.**
- Write ν_t for the unnormalised measure on F_{E_t}(c) and Z_t for its mass. Pull back the θ_t part by Θ_t. Then
  Θ_t⁻¹_#(θ_t ν_t) has a smooth density relative to ν_0 on F_{E_0}(c) ∩ R. Its logarithmic derivative at t = 0 is

  ℓ̇ = −λ DQ[Y] + ω.

  - The first term: the action moves only through Pr, since j itself is in no plaquette meeting A_W.
  - ω collects the t-derivatives of log J and of the fibre Jacobian of Θ_t. It does not depend on λ.
- Differentiating E_{π_t}F = (∫Fθ_t dν_t + ∫F(1 − θ_t) dν_t)/Z_t gives

  (d/dt) E_{π_t}F |₀ = E_{π_0}[θ ⟨∇F, Y⟩] + Cov_{π_0}(F, θℓ̇ + θ̇) + Ξ_j(F),

  where Ξ_j(F) = (d/dt)[∫F(1−θ_t)dν_t − E_{π_0}F ∫(1−θ_t)dν_t]/Z_0, taken as an upper Dini derivative.

**Theorem 2.** For calm (E, c) and type-(b) j,

c_{V,j}(E, c) ≤ √8|Y|₂ + C_b + (5/4) ε_W osc F osc(θℓ̇) + sup_F |Ξ_j(F)|,

with

C_b = 240 p̄² S^{1/2} e^{3α_G} (48|Y|₂ + 12κ′C′_G) + 240 p̄² S^{1/2} C″_G/λ.

- The leading part, 240 · 48 p̄² S^{1/2} e^{3α}|Y|₂ = 9.16·10¹³, is explicit and independent of λ.
- osc(θℓ̇) ≤ 48√r λ|Y|₁ + C_G.

*Proof of the explicit part.*
- **First term.** |⟨∇F, Y⟩| ≤ |Y|₁.
- **Chart term.**
  - On the chart, θ = 1 and θ̇ = 0, so the chart covariance is Cov_μ(F, ℓ̇).
  - ∇_X(DQ[Y]) = D²Q[Y, ·] + DQ[DY ·].
  - The first piece, as a functional, has norm ≤ 48|Y|₂ (the bound ‖D²Q‖ ≤ 48 of `explicitdecay`). It is supported on
    links that share a plaquette with Pr, all within distance 3 of j, so its weight is ≤ e^{3α}.
  - The second piece is at most 12κ′|DY|, and |DY| ≤ C′_G by analyticity on R.
  - Insert these into `chartdecay`(ii) as in Theorem 1.
- **Off-chart term.** Exactly as Step 4 of Theorem 1, with |DQ[Y]| ≤ 24√r|Y|₁. ∎

*What is only sketched.*
- The constants C′_G and C″_G are not computed. C″_G bounds |e^{αφ}∇′ω|.
- ω is a trace of (Dc Dc*)⁻¹ against a perturbation localised near k. Globally Dc Dc* ≥ σ_0², because it is
  block-diagonal on the private links.
- On the chart the weighted-norm calculus of `explicitdecay` (Lemma `weightednorms`) bounds the gradient. This is
  routine, but it is not written out.
- Both C′_G and C″_G enter only multiplied by κ′ or 1/λ, so they do not affect the leading constant for large β.

*What is open.*
- Ξ_j. It concerns only the part of the fibre where some path of the single block y is at least ρ_G/8 from straight.
  Its total mass is ≤ ε_W, but its derivative in E_j is not controlled.
  - On {m_y > ρ_G} the constraint V♯_k = P_{2y} does not depend on j. So only the cut-off shell ρ_G/8 ≤ m_y ≤ ρ_G and
    the motion of its boundary contribute.
- **Conjecture B.** |Ξ_j(F)| ≤ C (1 + λ) π_0(m_y ≥ ρ_G/8) for 1-Lipschitz F.
  This is a one-block large-field statement, part of the harmless-large-fields step. It is plausible because everything moves at speed O(1) and
  the action enters with λ. But the cut-off shell has kinks (χ is piecewise linear, and m_y is a maximum), and a proof
  would need either a smooth cut-off with the `privatesubmersion` bound or a coarea argument across the kinks.

## 5. Corollary and what is left

**Corollary 2 (conditional).** Assume:
- every (E_s, c) on the geodesics involved is calm;
- Ξ_j ≤ C_Ξ for every type-(b) link;
- λ ε_W |A_W| ≤ 1.

Then K^c_c ≤ 4(n/2 + 1)³ (π/2)(max(C_*, C_b) + C_Ξ + O(1)), where the O(1) includes 120r and the small terms. So
CC(n, α) holds on calm data for

(n/2)⁴ α ≥ 4(n/2 + 1)³ · 1.44·10¹⁴(1 + C_Ξ/C_b), that is, n ≥ 2.3·10¹⁵(1 + C_Ξ/C_b)/α up to O(1),

for α ≤ 1/2 (`checks/geometry_checks.py`: n ≥ 2.302·10¹⁵ at α = 1/2 and 1.151·10¹⁶ at α = 1/10 when C_Ξ = 0).

**The non-uniform term, precisely.** In Theorems 1 and 2, the only quantity that grows with the cube is the off-chart
term (5/4) ε_W osc F osc G. It is crude in two ways:
- osc F ∼ |A_W| charges the whole cube;
- ε_W is the probability that *some* plaquette in the cube is large.

What would make the cube-coefficient bound uniform along the tuning is a localised version:

**Conjecture L (local off-chart covariance).** For calm (E, c), a 1-Lipschitz F and G a smooth function of links within
distance 1 of j with per-link gradient ≤ 1,

|Cov_{π}(F, G) − Cov_μ(F, G)| ≤ C Σ_x e^{−α d(x,j)} π(some plaquette at x is not calm).

Suppose large plaquettes are rare site by site under every exterior. Theorem `defects` of the paper proves this rarity
on the torus; extending it to arbitrary exteriors is open. Then the right-hand side is O(q(β_W) S(α)), uniform in |W|.
Conjecture L is the statement "large fields are harmless" in covariance form. Two further open ingredients would
enter here, an annealed Dobrushin comparison and the transport of the island bound to chart coordinates:
- **Islands.** Inside an island of bad plaquettes the single-link W₁ coefficients are bounded uniformly in the field:
  each entry is at most β_W/4 and each row at most 4.5β_W, so an island of n sites amplifies influence by at most
  (4.5β_W)^{4n}.
- **Leaving an island.** The chart decay of this note controls the influence once it leaves the island.
- **The missing step.** The two have to be glued in one metric, and the section S of the chart (row sums ≤ 14, range 1)
  is the natural change of metric.

**Averaging over v.** Lemma `mixture` holds with ε replaced by ∫W₁(κ(·|v), κ′(·|v)) ρ(dv). Its proof integrates the
first term against ρ. So Corollary `compose` only needs the constrained coefficient *on average* over the averages v,
under the law of the averages given the exterior. That law gives the non-calm fibres mass ≤ ε″_W (Corollary
`calmexterior`). This does not remove the need for the non-calm-fibres step: the non-calm fibres still contribute W₁ ≤ diam, which is not
proportional to δ. But it shows that only their mass, not a supremum over them, is needed if that step is proved in a form
proportional to δ.

## 6. Status table

| item | status |
|---|---|
| Lemma 1 (two types of exterior links, private links, counts) | proved; enumerated for n = 4, 6 |
| Theorem 1 (type (a), calm data, explicit C_* ≤ 7.4·10¹²) | proved (relies on `chartdecay`(ii), `explicitdecay`, `calmfibres` of the forest paper, themselves not refereed) |
| Theorem 2, explicit λ-independent part C_b ≤ 9.2·10¹³ | proved |
| Theorem 2, constants C′_G, C″_G | sketched |
| Ξ_j (cut-off shell of one block) | open; Conjecture B |
| Corollary 2, CC(n, α) on calm data for n ≳ 2.3·10¹⁵/α | conditional on Conjecture B and λ ε_W |A_W| ≤ 1; therefore not uniform along the tuning |
| Conjecture L (localised off-chart covariance) | open; it is "large fields are harmless" in covariance form |
| Numerical | only the geometry, the lattice sum and the constants are checked; no Monte Carlo was run |
