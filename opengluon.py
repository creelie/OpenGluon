"""Local entry point for the OpenGluon workspace; standard-library only."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def doctor():
    missing, drifted = [], []
    count = 0
    for filename in ('quantumlib-lock.json', 'toolkit-lock.json'):
        data = json.loads((ROOT / filename).read_text(encoding='utf-8'))
        for item in data['repositories']:
            count += 1
            path = ROOT / item['path']
            if not (path / '.git').exists():
                missing.append(item['path'])
                continue
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=path, capture_output=True, text=True)
            if result.returncode or result.stdout.strip() != item['commit']:
                drifted.append(item['path'])
    report = {'pinned_repositories':count,'missing_checkouts':missing,'different_commits':drifted,'ready':not missing and not drifted,'scope':'Source checkouts only; project dependencies and theorem proofs are not tested by doctor.'}
    print(json.dumps(report, indent=2))
    return 0 if report['ready'] else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['doctor','portfolio','upstreams','routes','certify'])
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command == 'doctor':
        return doctor()
    source = ROOT / 'engines/anaxia/src'
    if not (source / 'ebllm/cli.py').exists():
        print('Initialize Anaxia with: git submodule update --init engines/anaxia', file=sys.stderr)
        return 2
    sys.path.insert(0, str(source))
    from ebllm.cli import main as anaxia
    return anaxia([args.command, *args.arguments])


if __name__ == '__main__':
    raise SystemExit(main())
