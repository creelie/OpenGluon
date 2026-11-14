"""Check a bounded four-dimensional counterexample to radial reduction."""

from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def squared_distance(left, right):
    return sum((a - b) ** 2 for a, b in zip(left, right))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def audit():
    origin = (0, 0, 0, 0)
    neighbors = [
        (F(5, 2), 0, 0, 0), (F(-5, 2), 0, 0, 0),
        (F(3, 2), 2, 0, 0), (F(-3, 2), -2, 0, 0),
        (0, 0, 2, 0), (0, 0, -2, 0),
        (0, 0, 0, 2), (0, 0, 0, -2),
    ]
    centers = [origin, *neighbors]
    distances = [squared_distance(a, b) for a, b in combinations(centers, 2)]
    require(min(distances) >= 4, 'original centers must form a unit-ball packing')
    require(all(4 <= squared_distance(origin, y) < 8 for y in neighbors),
            'all eight neighbors must be in the inner shell')

    # A strict midpoint witness proves that each bisector defines a facet.
    for neighbor in neighbors:
        midpoint = tuple(F(coordinate, 2) for coordinate in neighbor)
        radius_squared = squared_distance(midpoint, origin)
        require(radius_squared == squared_distance(midpoint, neighbor), 'wrong bisector')
        require(all(squared_distance(midpoint, other) > radius_squared
                    for other in neighbors if other != neighbor), 'inactive neighbor')

    projected = [tuple(F(4, 5) * coordinate for coordinate in y) if index < 4 else y
                 for index, y in enumerate(neighbors)]
    require(all(squared_distance(origin, y) == 4 for y in projected), 'wrong contact radii')
    collision_squared = squared_distance(projected[0], projected[2])
    require(collision_squared == F(16, 5) < 4, 'the projected pair must overlap')

    # The cell in the four unit-normal coordinates is a rectangular box.
    normal_determinant = F(4, 5)
    cell_volume = F(5, 2)**2 * 2**2 / normal_determinant
    formal_contact_cell_volume = F(2)**4 / normal_determinant
    require(cell_volume == F(125, 4) and formal_contact_cell_volume == 20,
            'Voronoi half-space volume calculation changed')
    # The note proves the lower bound. Check that a packing attains it.
    extremal = [tuple(F(4, 5) * x for x in y) if i < 2 else
                tuple(F(24, 25) * x for x in y) if i < 4 else y
                for i, y in enumerate(neighbors)]
    require(min(squared_distance(a, b) for a, b in combinations([origin, *extremal], 2)) == 4,
            'claimed minimum must be attained by a packing')
    feasible_minimum = F(2) * F(12, 5) * F(2)**2 / normal_determinant
    require(feasible_minimum == 24, 'incorrect volume at the feasible extremal packing')
    return {
        'source': 'https://arxiv.org/html/2609.25120v2#S2.SS6',
        'target': 'packing feasibility of the all-contact radial reduction',
        'centers': [[str(x) for x in y] for y in centers],
        'pairs_checked': len(distances),
        'minimum_original_distance_squared': str(min(distances)),
        'active_neighbors': len(neighbors),
        'original_voronoi_volume': str(cell_volume),
        'projected_centers': [[str(x) for x in y] for y in projected],
        'overlapping_projected_pair': [0, 2],
        'projected_pair_distance_squared': str(collision_squared),
        'formal_contact_halfspace_volume': str(formal_contact_cell_volume),
        'minimum_volume_for_these_fixed_rays': str(feasible_minimum),
        'centers_attaining_minimum': [[str(x) for x in y] for y in [origin, *extremal]],
        'result': 'all_contact_reduction_not_packing_preserving',
        'scope': 'Counterexample to the feasible-corner conclusion for fixed directions. The 24-cell volume inequality is not refuted.',
    }


if __name__ == '__main__':
    result = json.dumps(audit(), indent=2) + '\n'
    path = ROOT / 'data' / 'd4-radial-audit.json'
    path.write_bytes(result.encode('utf-8'))
    print(f'Checked 36 center pairs and eight active facets. Saved {path.relative_to(ROOT)}.')
