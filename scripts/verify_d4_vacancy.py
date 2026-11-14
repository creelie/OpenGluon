"""Exact finite checks for the D4 vacancy proof and its sharpness witness."""

import argparse
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def squared_distance(left, right):
    return sum((a - b) ** 2 for a, b in zip(left, right))


def chamber_coordinates(point):
    a, b, c, d = point
    return (1 - a - b, a - b, 2 * (b - c), 2 * (c - d), 2 * d)


def verify():
    half = Fraction(1, 2)
    zero = (0, 0, 0, 0)
    vertices = (zero, (1, 0, 0, 0), (half, half, 0, 0),
                (half, half, half, 0), (half, half, half, half))
    barycentric = [chamber_coordinates(vertex) for vertex in vertices]
    for index, coordinates in enumerate(barycentric):
        require(coordinates == tuple(int(index == column) for column in range(5)),
                'The listed chamber vertices do not invert the coordinates')
    require(all(squared_distance(u, v) > 0 for u, v in combinations(vertices, 2)),
            'Strict concavity requires distinct vertices')

    vertex_checks = []
    for point in vertices:
        a, _, c, d = point
        norm_squared = dot(point, point)
        threshold = Fraction(norm_squared, 2)
        vertex_checks.append((norm_squared, a + d - threshold, a + c - norm_squared))
    require(tuple(vertex_checks) == ((0, 0, 0), (1, half, 0),
            (half, Fraction(1, 4), 0), (Fraction(3, 4), Fraction(1, 8), Fraction(1, 4)),
            (1, half, 0)), 'Chamber vertex table disagrees with the proof')

    shared_roots = ((1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1))
    first_pair = ((1, -1, 0, 0), (0, 1, 1, 0))
    second_pair = ((1, 0, 0, -1), (0, 0, 1, 1))
    roots = (*shared_roots, *first_pair, *second_pair)
    require(len(set(roots)) == 7 and all(dot(root, root) == 2 and sum(root) % 2 == 0 for root in roots),
            'The proof needs seven distinct D4 roots')
    for pair in (first_pair, second_pair):
        require(tuple(map(sum, zip(*pair))) == (1, 0, 1, 0), 'Paired inner products must sum to a+c')
    for point in vertices[1:]:
        threshold = Fraction(dot(point, point), 2)
        for group, needed in ((shared_roots, 3), (first_pair, 1), (second_pair, 1)):
            require(sum(dot(point, root) > threshold for root in group) >= needed,
                    'A nonzero chamber vertex has too few blockers')

    witness = (Fraction(2, 3), Fraction(1, 3), Fraction(1, 3), Fraction(0))
    require(any(value.denominator != 1 for value in witness), 'Sharpness witness must be off-lattice')
    require(all((3 - abs(value)) ** 2 > 2 and abs(value) < 3 for value in witness),
            'Coordinate box does not cover all possible blockers')
    candidates = [point for point in product(range(-2, 3), repeat=4) if sum(point) % 2 == 0]
    blockers = sorted(point for point in candidates if squared_distance(witness, point) < 2)
    expected = sorted((zero, *shared_roots, second_pair[0], first_pair[1]))
    require(blockers == expected, 'Sharpness witness blocker list differs from the proof')

    return {
        'schema_version': 1,
        'minimum_permitted_squared_separation': 2,
        'chamber_vertices': [[str(value) for value in vertex] for vertex in vertices],
        'chamber_vertex_checks': [[str(value) for value in row] for row in vertex_checks],
        'sharpness_witness': [str(value) for value in witness],
        'witness_search_box': [-2, 2],
        'even_sum_points_checked': len(candidates),
        'blockers': [{'center': point, 'distance_squared': str(squared_distance(witness, point))}
                     for point in blockers],
        'minimum_off_lattice_blockers': len(blockers),
        'scope': 'Exact finite arithmetic checks supporting the written six-center obstruction for the fixed D4 packing.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='save the verified record as JSON')
    args = parser.parse_args()
    result = json.dumps(verify(), indent=2) + '\n'
    if args.output:
        args.output.write_bytes(result.encode('utf-8'))
    print(result, end='')


if __name__ == '__main__':
    main()
