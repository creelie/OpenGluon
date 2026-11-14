"""Check partial D4 contacts and the geometry of the vertex-ray slab proof."""

from fractions import Fraction as F
from itertools import combinations, permutations, product


def dot(left, right):
    return sum(a*b for a, b in zip(left, right))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    coordinate_pairs = list(combinations(range(4), 2))
    roots = {tuple(a if k == i else b if k == j else 0 for k in range(4))
             for i, j in coordinate_pairs for a, b in product((-1, 1), repeat=2)}
    require(len(roots) == 24, 'wrong root count')
    require(all(dot(a, b) <= 1 for a, b in combinations(roots, 2)),
            'contact roots overlap')

    star = [(1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1)]
    triangle = [(1, 1, 0, 0), (1, 0, 1, 0), (0, 1, 1, 0)]
    witnesses = [
        (star, (F(9, 5), F(1, 5), F(1, 5), F(1, 5)), (1, 0, 0, 0)),
        (triangle, (F(9, 10), F(9, 10), F(9, 10), F(0)), (F(1, 2),)*4),
    ]
    orbits = []
    for missing, extra, cut_point in witnesses:
        norm = dot(extra, extra)
        require(norm >= 2, 'extra center overlaps central ball')
        require(all(2*dot(extra, root) <= norm for root in roots - set(missing)),
                'extra center overlaps a retained ball')
        require(all(dot(cut_point, root) <= 1 for root in roots),
                'claimed cut point is outside the reference cell')
        require(2*dot(extra, cut_point) > norm, 'witness does not cut the reference cell')
        orbit = set()
        for perm in permutations(range(4)):
            for signs in product((-1, 1), repeat=4):
                transformed = frozenset(tuple(signs[i]*root[perm[i]] for i in range(4))
                                        for root in missing)
                orbit.add(transformed)
        orbits.append(orbit)

    all_triples = list(combinations(roots, 3))
    close_triples = {frozenset(triple) for triple in all_triples
                     if all(dot(a, b) == 1 for a, b in combinations(triple, 2))}
    require([len(orbit) for orbit in orbits] == [64, 32], 'wrong signed shape counts')
    require(not (orbits[0] & orbits[1]), 'the shapes must be disjoint')
    require(orbits[0] | orbits[1] == close_triples, 'deletion shape classification fails')
    require(len(all_triples) - len(close_triples) == 1928, 'wrong containment count')
    print('Checked 2,024 deletion triples, 96 exceptional cuts by symmetry, and both rational witnesses.')

    vertices = {tuple(F(sign) if k == i else F(0) for k in range(4))
                for i in range(4) for sign in (-1, 1)}
    vertices.update(tuple(F(sign, 2) for sign in signs)
                    for signs in product((-1, 1), repeat=4))
    hadamard = [(1, 1, 1, 1), (1, 1, -1, -1),
                (1, -1, 1, -1), (1, -1, -1, 1)]
    transformed_roots = {tuple(F(dot(row, root), 2) for row in hadamard)
                         for root in roots}
    require(transformed_roots == roots, 'Hadamard map must preserve every root')
    transformed_vertices = {tuple(F(dot(row, vertex), 2) for row in hadamard)
                            for vertex in vertices}
    require(transformed_vertices == vertices, 'Hadamard map must preserve the vertices')
    require(tuple(F(row[0], 2) for row in hadamard) == (F(1, 2),) * 4,
            'the map must connect the axis and half-sign vertex families')
    relevant_pairs = 0
    for vertex in vertices:
        if vertex[0] > 0:
            continue
        direction_sum = (1 + vertex[0], *vertex[1:])
        support = max(max(map(abs, direction_sum)), sum(map(abs, direction_sum)) / 2)
        require(support <= 1, 'old slabs may overlap')
        cube_projection = vertex[0] / 2 + sum(map(abs, vertex[1:])) / 2
        require(cube_projection <= F(1, 2), 'another extra may cut a new slab')
        relevant_pairs += 1
    require(relevant_pairs == 15, 'wrong number of nonpositive vertex directions')
    print('Checked root-preserving triality and all nonpositive vertex-pair slab bounds.')


if __name__ == '__main__':
    main()
