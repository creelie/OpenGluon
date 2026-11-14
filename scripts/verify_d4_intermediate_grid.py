"""Replay the exact finite checks for the intermediate D4 grid bound."""

import argparse
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
T = ((1, -1, -1, 0), (1, 1, 0, 1), (1, 0, 1, -1), (0, -1, 1, 1))
FREQUENCY = (1, 1, 1, 3)
SIXTH_ROOT_POWERS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def require(condition, description):
    if not condition:
        raise ValueError(description)


def verify():
    columns = tuple(zip(*T))
    require(all(sum(col) % 2 == 1 for col in columns), 'Map does not preserve parity')
    require(all(dot(a, b) == 3 * (i == j)
                for i, a in enumerate(columns) for j, b in enumerate(columns)),
            'Similarity Gram matrix is not 3I')

    neighbors = {v: 2 if dot(v, v) == 2 else 1
                 for v in product(range(-2, 3), repeat=4)
                 if sum(v) % 2 == 0 and dot(v, v) in (2, 4)}
    require(list(neighbors.values()).count(2) == 24 and list(neighbors.values()).count(1) == 24,
            'Incorrect displacement shell counts')
    degree = sum(neighbors.values())
    require(degree == 72, 'Incorrect weighted degree')

    # Exact evaluation in the basis 1, zeta, where zeta is exp(pi i/3).
    mode_values = [(weight, SIXTH_ROOT_POWERS[dot(v, FREQUENCY) % 6])
                   for v, weight in neighbors.items()]
    eigenvalue = tuple(sum(weight * value[i] for weight, value in mode_values) for i in range(2))
    require(eigenvalue == (-9, 0), 'The period-six Fourier mode misses the sharp eigenvalue')

    # Coefficients, in increasing order, of 27*(1+4*(q-1)^2)-16*q^3.
    expanded = tuple(sum(a * b for i, a in enumerate((9, -12, 4))
                         for j, b in enumerate((15, -4)) if i + j == k) for k in range(4))
    require(expanded == (135, -216, 108, -16), 'Incorrect cubic factorization')

    torus = [v for v in product(range(6), repeat=4) if sum(v) % 2 == 0]
    image = {tuple(dot(row, v) % 6 for row in T) for v in torus}
    require(len(torus) == 648 and len(image) == 72, 'Incorrect torus lattice density')
    forbidden = {tuple(value % 6 for value in v) for v in neighbors}
    require(all(tuple((x - y) % 6 for x, y in zip(a, b)) not in forbidden
                for a, b in combinations(image, 2)), 'Found forbidden pair in attaining lattice')
    require(Fraction(len(image), len(torus)) == Fraction(9, degree + 9),
            'Attaining lattice does not meet the spectral bound')

    return {
        'schema_version': 1,
        'scope': 'Fixed D4 grid, sqrt(2/3) <= mu < 1. Does not settle unrestricted packing.',
        'similarity_matrix': T,
        'sublattice_index': 9,
        'weighted_degree': degree,
        'period_six_frequency': FREQUENCY,
        'minimum_eigenvalue': eigenvalue[0],
        'twenty_seven_times_polynomial_coefficients': expanded,
        'torus_vertices': len(torus),
        'attaining_lattice_vertices': len(image),
        'optimal_grid_fraction': '1/9',
        'sharp_density': 'pi^2/(36*mu^4)',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/d4-intermediate-grid.json')
    args = parser.parse_args()
    record = verify()
    args.output.write_bytes((json.dumps(record, indent=2) + '\n').encode('utf-8'))
    print('Verified the index-9 lattice, period-six spectral equality, and 2,556 center pairs.')


if __name__ == '__main__':
    main()
