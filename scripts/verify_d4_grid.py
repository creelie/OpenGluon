"""Check the finite integer data for the D4 grid packing proofs."""

import argparse
from itertools import combinations, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZERO = (0, 0, 0, 0)
ONES = (1, 1, 1, 1)
DIRECTION_MINUS = (1, 1, 1, -1)
TWO_E1 = (2, 0, 0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm_squared(vector):
    return dot(vector, vector)


def difference(a, b):
    return tuple(x - y for x, y in zip(a, b))


def in_d4(vector):
    return sum(vector) % 2 == 0


def in_h(vector):
    return len({value % 2 for value in vector}) == 1


def in_double_d4(vector):
    return all(value % 2 == 0 for value in vector) and sum(vector) % 4 == 0


def points_in_ball(radius_squared):
    # All coordinates of any vector of squared norm at most 8 lie in [-2, 2].
    require(0 <= radius_squared <= 8, "Enumeration accepts squared radii up to 8")
    return [
        vector for vector in product(range(-2, 3), repeat=4)
        if norm_squared(vector) <= radius_squared
    ]


def check_tile(points, expected_index, sublattice, diameter_squared):
    require(len(points) == expected_index, "Wrong number of representatives")
    require(all(in_d4(point) for point in points), "Representative outside D4")
    distinct_pairs = list(combinations(points, 2))
    distances = [norm_squared(difference(a, b)) for a, b in distinct_pairs]
    require(all(not sublattice(difference(a, b)) for a, b in distinct_pairs),
            "Repeated sublattice coset")
    require(max(distances) == diameter_squared, "Wrong tile diameter")
    return {"cosets": expected_index, "pairs_checked": len(distances),
            "diameter_squared": max(distances), "representatives": points}


def verify():
    small = points_in_ball(8)
    roots = [point for point in small if in_d4(point) and norm_squared(point) == 2]
    require(len(roots) == 24, "Unexpected D4 root count")
    tile_h = check_tile([ZERO, (1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1)], 4, in_h, 2)
    require(min(norm_squared(y) for y in small if y != ZERO and in_h(y)) == 4,
            "Wrong minimum distance in H")
    tile_h.update({"covolume": 8, "minimum_sublattice_distance_squared": 4})

    # Use a deterministic representative from each antipodal root pair.
    oriented = []
    for root in roots:
        opposite = tuple(-value for value in root)
        if root > opposite:
            continue
        allowed = [
            choice for choice in (root, opposite)
            if choice[0] >= 0 and dot(choice, ONES) >= 0 and dot(choice, DIRECTION_MINUS) >= 0
        ]
        require(allowed, "Could not orient an antipodal pair")
        oriented.append(allowed[0])
    tile_double = check_tile([ZERO, *oriented, TWO_E1, ONES, DIRECTION_MINUS], 16,
                             in_double_d4, 6)
    require(min(norm_squared(y) for y in small if y != ZERO and in_double_d4(y)) == 8,
            "Wrong minimum distance in 2D4")
    tile_double.update({"covolume": 32, "minimum_sublattice_distance_squared": 8})

    relevant = [y for y in small if in_d4(y) and 4 <= norm_squared(y) < 8]
    for y in relevant:
        require(2 * max(dot(y, root) for root in roots) <= norm_squared(y),
                "An admissible neighbor cuts the reference 24-cell")
    facet_centers = {y for y in relevant if norm_squared(y) == 4}
    coordinate_normals = {
        tuple(2 * sign if j == i else 0 for j in range(4))
        for i in range(4) for sign in (-1, 1)
    }
    signed_normals = set(product((-1, 1), repeat=4))
    require(facet_centers == coordinate_normals | signed_normals, "Wrong facet centers")
    require(all(in_h(y) for y in facet_centers), "A facet center is outside H")
    return {
        "schema_version": 1,
        "scope": "Finite exact checks for the fixed-grid proofs. The unrestricted 24-cell and density questions are outside this result.",
        "local_reference_cell": {
            "root_vertices": len(roots),
            "short_neighbor_counts": {
                str(squared_norm): sum(norm_squared(y) == squared_norm for y in relevant)
                for squared_norm in (4, 6)
            },
            "facet_centers": len(facet_centers),
            "reference_volume_from_orthant_decomposition": 8,
        },
        "tiles": {"H": tile_h, "2D4": tile_double},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/d4-grid.json")
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print("Verified 24 facet centers, two short-neighbor shells, and both coset tilings.")


if __name__ == "__main__":
    main()
