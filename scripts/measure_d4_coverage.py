"""Measure where the census pair bound leaves a proposed D4 threshold uncertified."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/d4-coverage.json')
    args = parser.parse_args()
    source = ROOT / 'engines/anaxia/src'
    if not (source / 'ebllm/construct/seed_intervals.py').is_file():
        parser.error('Initialize the pinned engines/anaxia submodule before running this check')
    sys.path.insert(0, str(source))
    from ebllm.construct import seed_intervals

    census_path = seed_intervals.DATA / 'seed_point_pairs.csv'
    census = seed_intervals.load_census(census_path)
    bounds = seed_intervals.pair_bounds(census)
    thresholds = []
    for target in (24, 50, 346):
        insufficient = [pair for pair, bound in bounds.items() if bound > target]
        thresholds.append({'target_upper_bound': target,
                           'point_count_pairs_above_target': len(insufficient),
                           'polytope_count_without_pair_bound_at_target': sum(census[pair] for pair in insufficient)})
    result = {'schema_version': 1,
              'engine_commit': subprocess.check_output(
                  ['git', '-C', str(source.parent), 'rev-parse', 'HEAD'], text=True).strip(),
              'census_sha256': hashlib.sha256(census_path.read_bytes()).hexdigest(),
              'total_polytopes_in_supplied_census': sum(census.values()),
              'largest_pair_bound': max(bounds.values()), 'thresholds': thresholds,
              'scope': 'These counts measure where the raw pair bound fails to certify a threshold. They do not count actual descent depths or exceptions after applying other certificates.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
