"""Auditable finite challenge experiments; no extrapolation to universal closure."""

import argparse
import hashlib
import itertools
import json
from math import isqrt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {'quick': (100, 100, 30, 30), 'standard': (10000, 10000, 500, 200)}
FINITE_SCOPE = 'Only the stated finite domain is checked; no universal conjecture is closed.'
D4_SCOPE = 'Exact 24-point construction only; universal upper bound and uniqueness are not re-proved.'


def _integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'Expected integer in [{low}, {high}]')
    return value


def _prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def _sieve(limit):
    values = bytearray(b'\x01') * (limit + 1)
    values[:2] = b'\x00\x00'
    for p in range(2, isqrt(limit) + 1):
        if values[p]:
            values[p*p:limit+1:p] = b'\x00' * ((limit-p*p)//p+1)
    return values


def collatz(limit, max_steps=10000):
    _integer(limit, 1, 100000)
    _integer(max_steps, 1, 10000)
    witnesses, unfinished, work = [], [], 0
    for start in range(1, limit + 1):
        n, steps = start, 0
        while n != 1 and steps < max_steps and n.bit_length() <= 1024 and work < 20_000_000:
            n = 3*n+1 if n % 2 else n//2
            steps += 1
            work += 1
        if n == 1:
            witnesses.append([start, steps])
        else:
            unfinished.append(start)
    return {'id': 'collatz', 'title': 'Collatz', 'limit': limit, 'max_steps': max_steps,
            'witnesses': witnesses, 'unfinished': unfinished, 'operations': work}


def goldbach(limit):
    _integer(limit, 4, 100000)
    primes = _sieve(limit)
    witnesses, unfinished = [], []
    for n in range(4, limit + 1, 2):
        p = next((p for p in range(2, n//2+1) if primes[p] and primes[n-p]), None)
        if p is None:
            unfinished.append(n)
        else:
            witnesses.append([n, p, n-p])
    return {'id': 'goldbach', 'title': 'Even Goldbach', 'limit': limit,
            'witnesses': witnesses, 'unfinished': unfinished}


def legendre(limit):
    _integer(limit, 1, 1000)
    primes = _sieve((limit+1)**2)
    witnesses, unfinished = [], []
    for n in range(1, limit+1):
        p = next((p for p in range(n*n+1, (n+1)**2) if primes[p]), None)
        if p is None:
            unfinished.append(n)
        else:
            witnesses.append([n, p])
    return {'id': 'legendre', 'title': 'Legendre prime between consecutive squares', 'limit': limit,
            'witnesses': witnesses, 'unfinished': unfinished}


def erdos_straus(limit):
    _integer(limit, 2, 1000)
    witnesses, unfinished, work = [], [], 0
    for n in range(2, limit+1):
        found = None
        for x in range(n//4+1, 3*n//4+1):
            a, b = 4*x-n, n*x
            for y in range(max(x, b//a+1), min(2*b//a, 100000)+1):
                work += 1
                if work > 2_000_000:
                    break
                denominator = a*y-b
                numerator = b*y
                if numerator % denominator == 0 and numerator//denominator >= y:
                    found = [n, x, y, numerator//denominator]
                    break
            if found is not None or work > 2_000_000:
                break
        if found:
            witnesses.append(found)
        else:
            unfinished.append(n)
    return {'id': 'erdos-straus', 'title': 'Erdos-Straus', 'limit': limit,
            'witnesses': witnesses, 'unfinished': unfinished, 'operations': work}


def d4_configuration():
    points = []
    for i, j in itertools.combinations(range(4), 2):
        for a, b in itertools.product((-1, 1), repeat=2):
            vector = [0]*4
            vector[i], vector[j] = a, b
            points.append(vector)
    return {'id': 'd4-kissing', 'title': 'D4 24-point kissing construction',
            'points': sorted(points), 'norm_squared': 2, 'minimum_squared_distance': 2,
            'scope': D4_SCOPE}


def _checked_result(report, result):
    if 'verification' in report and report['verification'] != result:
        raise ValueError('Stored verification summary differs from the independent check')
    if 'status' in report and report['status'] != result['status']:
        raise ValueError('Stored status differs from the independently established evidence scope')
    return result


def verify_experiment(report):
    """Re-evaluate witness conditions separately from candidate search algorithms."""
    try:
        if not isinstance(report, dict):
            raise ValueError('Challenge evidence must be an object')
        name = report['id']
        if name not in {'d4-kissing', 'collatz', 'goldbach', 'legendre', 'erdos-straus'}:
            raise ValueError('Unsupported challenge')
        if report.get('global_status', 'not_closed') != 'not_closed':
            raise ValueError('This evidence cannot assert a global closure')
        if 'schema_version' in report and (type(report['schema_version']) is not int or report['schema_version'] != 1):
            raise ValueError('Unsupported challenge schema version')
        for field in ('global_closure', 'new_result', 'paper_eligible'):
            if field in report and report[field] is not False:
                raise ValueError('Challenge evidence cannot assert ' + field)
        if 'global_closures' in report and (type(report['global_closures']) is not int or report['global_closures'] != 0):
            raise ValueError('Challenge evidence establishes zero global closures')
        if 'scope' in report and report['scope'] != (D4_SCOPE if name == 'd4-kissing' else FINITE_SCOPE):
            raise ValueError('Stored scope overstates or differs from the supported challenge claim')
        if name == 'd4-kissing':
            points = report['points']
            if (len(points) != 24 or len({tuple(p) for p in points}) != 24
                    or any(len(p) != 4 or any(type(x) is not int or abs(x) > 1 for x in p)
                           or sum(x*x for x in p) != 2 for p in points)):
                raise ValueError('Invalid D4 root construction')
            distances = [sum((a-b)**2 for a, b in zip(p, q)) for p, q in itertools.combinations(points, 2)]
            if min(distances) != 2 or report.get('norm_squared') != 2 or report.get('minimum_squared_distance') != 2:
                raise ValueError('D4 separation fails')
            return _checked_result(report, {'valid': True, 'status': 'exact_configuration_verified', 'pairs_checked': len(distances),
                    'global_closure': False, 'new_result': False})
        lower = 4 if name == 'goldbach' else 2 if name == 'erdos-straus' else 1
        upper = 1000 if name in {'legendre', 'erdos-straus'} else 100000
        limit = _integer(report['limit'], lower, upper)
        rows = report['witnesses']
        if not isinstance(rows, list) or len(rows) > 100000:
            raise ValueError('Invalid witness table')
        expected = set(range(4, limit+1, 2)) if name == 'goldbach' else set(range(2 if name == 'erdos-straus' else 1, limit+1))
        seen = set()
        for row in rows:
            if not isinstance(row, list) or any(type(x) is not int or abs(x) > 10**12 for x in row):
                raise ValueError('Invalid integer witness')
            n = row[0]
            if n not in expected or n in seen:
                raise ValueError('Duplicated or out-of-domain witness')
            seen.add(n)
            if name == 'goldbach':
                if (len(row) != 3 or not 2 <= row[1] <= n or not 2 <= row[2] <= n
                        or row[1]+row[2] != n or not _prime(row[1]) or not _prime(row[2])):
                    raise ValueError('Invalid Goldbach prime witness')
            elif name == 'legendre':
                if len(row) != 2 or not n*n < row[1] < (n+1)**2 or not _prime(row[1]):
                    raise ValueError('Invalid interval prime')
            elif name == 'erdos-straus':
                if len(row) != 4 or any(v <= 0 for v in row[1:]):
                    raise ValueError('Invalid unit-fraction witness')
                _, x, y, z = row
                if 4*x*y*z != n*(x*y+x*z+y*z):
                    raise ValueError('Unit-fraction identity is false')
            elif name == 'collatz':
                if len(row) != 2:
                    raise ValueError('Invalid Collatz witness')
                steps = _integer(row[1], 0, 10000)
                if steps > _integer(report['max_steps'], 1, 10000):
                    raise ValueError('Collatz witness exceeds the declared search budget')
                value = n
                for _ in range(steps):
                    if value == 1 or value.bit_length() > 1024:
                        raise ValueError('Invalid Collatz path length')
                    value = value//2 if value % 2 == 0 else value*3+1
                if value != 1:
                    raise ValueError('Collatz witness does not end at 1')
            else:
                raise ValueError('Unsupported challenge')
        remaining = expected-seen
        unfinished = report.get('unfinished')
        if (not isinstance(unfinished, list) or any(type(n) is not int for n in unfinished)
                or len(unfinished) != len(set(unfinished)) or set(unfinished) != remaining):
            raise ValueError('Coverage does not match declared domain')
        return _checked_result(report, {'valid': True, 'status': 'finite_evidence_verified' if not remaining else 'inconclusive',
                'checked_cases': len(seen), 'unfinished_cases': len(remaining),
                'global_closure': False, 'new_result': False})
    except (ValueError, KeyError, TypeError, IndexError) as error:
        return {'valid': False, 'reason': str(error), 'global_closure': False}


def run(profile='standard', output=Path('data/challenges')):
    if profile not in PROFILES:
        raise ValueError('Unknown challenge profile')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    limits = PROFILES[profile]
    candidates = [collatz(limits[0]), goldbach(limits[1]), legendre(limits[2]), erdos_straus(limits[3]), d4_configuration()]
    index = {'schema_version': 1, 'profile': profile, 'global_closures': 0,
             'paper_eligible': False, 'experiments': [], 'research_targets': []}
    for report in candidates:
        result = verify_experiment(report)
        if not result['valid']:
            raise ValueError(f"Verification failed for {report['id']}: {result}")
        report.update(schema_version=1, verification=result, global_status='not_closed',
                      scope=report.get('scope', FINITE_SCOPE))
        encoded = (json.dumps(report, indent=2) + '\n').encode()
        filename = report['id']+'.json'
        (output/filename).write_bytes(encoded)
        index['experiments'].append({'id': report['id'], 'title': report['title'], 'status': result['status'],
                                     'cases': result.get('checked_cases', len(report.get('points', []))),
                                     'limit': report.get('limit'), 'report': filename,
                                     'sha256': hashlib.sha256(encoded).hexdigest()})
    targets = json.loads((ROOT/'config/challenge-targets.json').read_text(encoding='utf-8'))['targets']
    for target in targets:
        index['research_targets'].append({'id': target['id'], 'title': target['title'],
             'global_status': 'not_closed', 'status': 'configuration_only' if target['id']=='d4-kissing' else 'inconclusive',
             'backend': target['backend'], 'proof_obligations': target['proof_obligations'],
             'source_urls': target['source_urls']})
    (output/'index.json').write_bytes((json.dumps(index, indent=2)+'\n').encode())
    lines = ['# Anaxia challenge results', '', '**Global closures: 0. New-paper eligibility: false.**', '',
             'Every executable result below was independently rechecked using integer arithmetic. These are replication and capability tests.', '',
             '| Experiment | Checked cases | Evidence | Scope |', '| --- | ---: | --- | --- |']
    for row in index['experiments']:
        lines.append(f"| {row['title']} | {row['cases']} | [{row['status']}]({row['report']}) | {'24-point construction' if row['id']=='d4-kissing' else 'Finite domain'} |")
    lines += ['', '## Full-closure assessment', '', '| Target | Result |', '| --- | --- |']
    lines += [f"| {r['title']} | {r['status']}; no new full proof verified |" for r in index['research_targets']]
    lines += ['', 'See [proof obligations](../../docs/CHALLENGES.md) and the [local research campaign](../campaign/README.md).', '',
              'Hodge, Yang-Mills and Riemann require mathematical structures beyond the exact polynomial and modular checkers. '
              'Their cards record unsupported proof obligations, not numerical simulations purporting to prove them. '
              'The D4 construction supplies a lower-bound configuration; it does not re-prove the known upper bound. '
              'No manuscript, release or DOI is generated by this command.', '']
    (output/'README.md').write_bytes('\n'.join(lines).encode())
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    run_parser = commands.add_parser('run')
    run_parser.add_argument('--profile', choices=PROFILES, default='standard')
    run_parser.add_argument('--output', type=Path, default=Path('data/challenges'))
    verify_parser = commands.add_parser('verify')
    verify_parser.add_argument('report', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            if args.report.stat().st_size > 10_000_000:
                raise ValueError('Challenge evidence exceeds 10 MB')
            result = verify_experiment(json.loads(args.report.read_text(encoding='utf-8')))
            print(json.dumps(result, indent=2))
            return 0 if result['valid'] else 1
        result = run(args.profile, args.output)
        print(json.dumps({'experiments': len(result['experiments']), 'global_closures': 0,
                          'paper_eligible': False, 'output': str(args.output)}, indent=2))
        return 0
    except (ValueError, OSError, RecursionError) as error:
        print(f'Challenge error: {error}', file=sys.stderr)
        return 2
