"""Checks for CALM_DATA.md (geometry, link classification, lattice sum, constants).

Pure Python, no dependencies beyond the standard library and mpmath (optional).
Conventions follow forest/main.tex, Definition blockgauge and Sec. ssec:smallfibres:
  blocks B(y) = 2y + {0,1}^4; offset o = x mod 2;
  link (x,mu) is a tree link iff o_mu = 0 and o_nu = 0 for all nu > mu; else active;
  the cut-off average V#_{y,mu} is a function of the 16 paths
  P_x = U_(x,mu) U_(x+e_mu,mu), x in B(y) (tree links are I and are not variables).
Cube: W = blocks y in [0, n/2)^4, A_W = active links with base in the union of W.
Lattice: periodic of side Lside (large enough that the cube does not wrap).
"""
import itertools, math
from fractions import Fraction

DIM = 4

def is_tree(x, mu):
    o = [c % 2 for c in x]
    return o[mu] == 0 and all(o[nu] == 0 for nu in range(mu + 1, DIM))

def add(x, mu, s=1, L=None):
    y = list(x); y[mu] += s
    if L: y[mu] %= L
    return tuple(y)

def plaquettes_of(link, L):
    x, mu = link
    out = []
    for nu in range(DIM):
        if nu == mu: continue
        for s in (+1, -1):
            # plaquette in plane (mu,nu) with link (x,mu) as one side
            base = x if s == 1 else add(x, nu, -1, L)
            p = [(base, mu), (add(base, mu, 1, L), nu), (add(base, nu, 1, L), mu), (base, nu)]
            out.append(frozenset(p))
    return out

def midpoint_dist(a, b, L):
    (x, mu), (z, nu) = a, b
    m = 0.0
    for i in range(DIM):
        pa = x[i] + (0.5 if i == mu else 0); pb = z[i] + (0.5 if i == nu else 0)
        d = abs(pa - pb) % L; d = min(d, L - d)
        m = max(m, d)
    return m

def run(n=4, Lside=10):
    L = Lside
    nb = n // 2
    W = [y for y in itertools.product(range(nb), repeat=DIM)]
    Wset = set(W)
    def block_of(x): return tuple(c // 2 for c in x)
    AW = set()
    for y in W:
        for o in itertools.product((0, 1), repeat=DIM):
            x = tuple(2 * y[i] + o[i] for i in range(DIM))
            for mu in range(DIM):
                if not is_tree(x, mu): AW.add((x, mu))
    assert len(AW) == 49 * len(W), len(AW)
    # links entering each average (variables only)
    enters = {}
    for y in W:
        for mu in range(DIM):
            S = set()
            for o in itertools.product((0, 1), repeat=DIM):
                x = tuple(2 * y[i] + o[i] for i in range(DIM))
                for l in [(x, mu), (add(x, mu, 1, L), mu)]:
                    if not is_tree(*l): S.add(l)
            enters[(y, mu)] = S
    # exterior active links sharing a plaquette with A_W, or entering an average
    ext = set()
    for a in AW:
        for p in plaquettes_of(a, L):
            for l in p:
                if l not in AW and not is_tree(*l): ext.add(l)
    typeb = {}
    for k, S in enters.items():
        for l in S:
            if l not in AW:
                assert not is_tree(*l)
                typeb.setdefault(l, []).append(k)
    plaq_b = sum(1 for l in typeb if l in ext)
    ext |= set(typeb)
    # (1) each exterior j: neighbours in A_W through plaquettes
    maxnb = 0; maxmult = 0; maxd = 0
    for j in ext:
        cnt = {}
        for p in plaquettes_of(j, L):
            for a in p:
                if a in AW: cnt[a] = cnt.get(a, 0) + 1
        maxnb = max(maxnb, len(cnt)); maxmult = max(maxmult, max(cnt.values(), default=0))
        maxd = max([maxd] + [midpoint_dist(a, j, L) for a in cnt])
        if j in typeb:  # distance from j to the links entering its average
            maxdb = max(midpoint_dist(a, j, L) for a in enters[typeb[j][0]])
            assert maxdb <= 2.5, maxdb
    # (2) type (b) links: exactly one average, the path from an o_mu=1 site, j = (x+e_mu, mu)
    for j, ks in typeb.items():
        assert len(ks) == 1, (j, ks)
        (y, mu) = ks[0]
        z, nu = j
        assert nu == mu
        x = add(z, mu, -1, L)
        assert block_of(x) == y and x[mu] % 2 == 1, (j, ks)
        assert tuple((y[i] + (1 if i == mu else 0)) for i in range(DIM)) not in Wset
    # (3) private links of V_{y,mu}: (x,mu), x in B(y), o_mu = 1 -> enter only V_{y,mu}
    for (y, mu), S in enters.items():
        for o in itertools.product((0, 1), repeat=DIM):
            if o[mu] != 1: continue
            x = tuple(2 * y[i] + o[i] for i in range(DIM))
            others = [k for k, T in enters.items() if (x, mu) in T and k != (y, mu)]
            assert not others, ((x, mu), others)
    # (4) counts per class (residue mod 2, direction)
    cls = {}
    for j in ext:
        c = (tuple(v % 2 for v in j[0]), j[1]); cls[c] = cls.get(c, 0) + 1
    bound = 4 * (nb + 1) ** 3
    print(f"n={n}: |W|={len(W)} |A_W|={len(AW)} exterior coupled links={len(ext)} "
          f"type(b)={len(typeb)} (of which {plaq_b} share a plaquette with A_W)")
    print(f"  max #A_W-neighbours of an exterior link via plaquettes = {maxnb} (claim <= 18)")
    print(f"  max #plaquettes shared by j and one a                  = {maxmult} (claim 1)")
    print(f"  max midpoint l_inf distance j--a                        = {maxd} (claim <= 1)")
    print(f"  max exterior links per class = {max(cls.values())}  (claim <= 4(n/2+1)^3 = {bound})")
    assert maxnb <= 18 and maxmult == 1 and maxd <= 1 and max(cls.values()) <= bound
    return len(typeb)

def S_bound(alpha):
    a = Fraction(alpha)
    return 4 * (24 / a**4 + 24 / a**3 + 12 / a**2 + 4 / a + 1)

def S_numeric(alpha, Rmax_factor=40):
    """sum over all links a of exp(-2 alpha d(a,j)), d = l_inf distance of midpoints,
    computed exactly by counting l_inf shells (worst case over the position of j)."""
    best = 0.0
    # positions of j's midpoint relative to the four midpoint lattices: offsets 0 or 1/2 per coordinate
    jmu = 0
    for mu in range(DIM):  # lattice of midpoints of links in direction mu: Z^4 + e_mu/2
        pass
    def count_1d(off, R):  # #{k in Z : |k + off| <= R}
        return math.floor(R - off) + math.floor(R + off) + 1 if R >= abs(off) else 0
    total = 0.0
    # j in direction 0: offset of lattice mu relative to j's midpoint
    for mu in range(DIM):
        offs = [0.0] * DIM
        offs[0] -= 0.5  # j midpoint has +1/2 in coordinate 0
        offs[mu] += 0.5
        # distances take values in (1/2)Z; sum shells
        prev = 0; s = 0.0; R = 0.0
        Rmax = Rmax_factor / alpha
        while R <= Rmax:
            c = 1
            for o in offs: c *= count_1d(o, R)
            s += (c - prev) * math.exp(-2 * alpha * R); prev = c; R += 0.5
        total += s
    return total

if __name__ == "__main__":
    nb = [run(4, 10), run(6, 12)]
    alpha = Fraction(1, 4000)
    Sb = S_bound(alpha); Sn = S_numeric(2.5e-4)
    print(f"S(alpha) at alpha=1/4000: shell sum {Sn:.6e}, closed-form bound {float(Sb):.6e}")
    assert Sn <= float(Sb)
    # the constant of Theorem 1
    pbar = 4.8; r_su2 = 2
    # |e^{-a phi} grad'F| <= pbar * 2 * S^(1/2)   (|g^F_a| <= 2, convention of prop:explicitdecay)
    # |e^{+a phi} grad'G| <= pbar * e^a * 2 sqrt(18)
    Cstar = 120 * pbar**2 * 2 * 2 * math.sqrt(18) * math.exp(2.5e-4) * math.sqrt(float(Sb))
    print(f"C_* = 480 sqrt(18) e^alpha pbar^2 S^(1/2) = {Cstar:.4e}")
    print(f"(pi/2) C_* = {math.pi/2*Cstar:.4e}")
    # type (b): private-link transport
    al_ = 2 * math.asin(1 / (2 * math.sqrt(2))); Lam = al_ / math.sin(al_)
    sigma0 = (1 - 7 * Lam / 8) / math.sqrt(2)
    Ybound = Lam / (16 * sigma0)
    print(f"Lambda={Lam:.6f} sigma0={sigma0:.6f}  |Y|_2 <= Lambda/(16 sigma0) = {Ybound:.4f}; |Y|_1 <= sqrt8*that = {math.sqrt(8)*Ybound:.3f}")
    assert sigma0 > 0.031
    Cb = 120 * pbar**2 * 2 * 48 * Ybound * math.exp(3 * 2.5e-4) * math.sqrt(float(Sb))
    print(f"C_b (leading, lambda-independent part) = 240 pbar^2 48 |Y|_2 e^(3 alpha) S^(1/2) = {Cb:.4e}")
    # threshold of the constrained cube condition CC(n, alpha): K_c <= 4(n/2+1)^3 C <= alpha N_n = alpha (n/2)^4
    C = math.pi / 2 * max(Cstar, Cb)
    print(f"C = (pi/2) max(C_*, C_b) = {C:.4e}")
    for al in (0.5, 0.1):
        m = 1
        while 4 * (m + 1) ** 3 * C > al * m ** 4: m *= 2
        lo, hi = m // 2, m
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if 4 * (mid + 1) ** 3 * C > al * mid ** 4: lo = mid
            else: hi = mid
        print(f"alpha={al}: the bound K_c <= alpha N_n holds for n/2 >= {hi} (n >= {2*hi:.3e})")
    print("all checks passed")
