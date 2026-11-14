"""Exact, bounded searches for universal modular Diophantine obstructions."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

from .lab import _polynomial, _terms, _integer

SCOPE = 'The submitted integer polynomial has no zero at any integer assignment.'
INCONCLUSIVE_SCOPE = 'No modular obstruction was found within this run; integer solvability is undecided.'


def validate(task):
    if not isinstance(task, dict) or type(task.get('schema_version')) is not int or task.get('schema_version') != 1 or task.get('kind') != 'integer_polynomial_zero':
        raise ValueError('Expected schema_version 1 and kind integer_polynomial_zero')
    variables = task.get('variables')
    if (not isinstance(variables, list) or not 1 <= len(variables) <= 4
            or any(not isinstance(v, str) or not v.isascii() or not v.isidentifier() or len(v) > 32 for v in variables)
            or len(set(variables)) != len(variables)):
        raise ValueError('Use one to four distinct ASCII variable names')
    polynomial = _polynomial(task.get('polynomial'), len(variables))
    if any(c.denominator != 1 for c in polynomial.values()):
        raise ValueError('Diophantine polynomials require integer coefficients')
    title = task.get('title', 'Integer polynomial zero')
    if not isinstance(title, str) or len(title) > 240:
        raise ValueError('Invalid title')
    return {'schema_version': 1, 'kind': 'integer_polynomial_zero', 'title': title,
            'variables': variables, 'polynomial': _terms(polynomial)}


def digest(task):
    return hashlib.sha256(json.dumps(task, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _value(terms, point, modulus=None):
    total = 0
    for powers, coefficient in terms.items():
        term = int(coefficient)
        for x, power in zip(point, powers):
            term *= pow(x, power, modulus) if modulus else x ** power
        total += term
    return total % modulus if modulus else total


def residues(task, modulus):
    _integer(modulus, 'modulus', 2, 64)
    size = modulus ** len(task['variables'])
    if size * max(1, len(task['polynomial'])) > 2_000_000:
        raise ValueError('Modular enumeration exceeds the arithmetic budget')
    polynomial = _polynomial(task['polynomial'], len(task['variables']))
    possible = {_value(polynomial, point, modulus)
                for point in itertools.product(range(modulus), repeat=len(task['variables']))}
    return sorted(possible), size


def solve(task, max_modulus=16):
    task = validate(task)
    _integer(max_modulus, 'max_modulus', 2, 32)
    report = {'schema_version': 1, 'engine': 'anaxia-modular/1', 'task': task,
              'task_sha256': digest(task), 'status': 'inconclusive',
              'scope': INCONCLUSIVE_SCOPE,
              'evidence': {'kind': 'search_only', 'moduli_checked': []}}
    total_work = 0
    for modulus in range(2, max_modulus + 1):
        work = modulus ** len(task['variables']) * max(1, len(task['polynomial']))
        if total_work + work > 2_000_000:
            break
        total_work += work
        possible, size = residues(task, modulus)
        report['evidence']['moduli_checked'].append(modulus)
        if 0 not in possible:
            report.update(status='modular_obstruction_verified', scope=SCOPE,
                          evidence={'kind': 'modular_obstruction', 'modulus': modulus,
                                    'assignments': size, 'possible_residues': possible})
            break
    if not verify(report)['valid']:
        raise ValueError('Internal independent modular verification failed')
    return report


def verify(report):
    try:
        if not isinstance(report, dict) or type(report.get('schema_version')) is not int or report.get('schema_version') != 1:
            raise ValueError('Invalid modular report')
        task = validate(report.get('task'))
        if digest(task) != report.get('task_sha256'):
            raise ValueError('Task digest differs')
        evidence = report.get('evidence')
        if not isinstance(evidence, dict):
            raise ValueError('Missing modular evidence')
        if report.get('status') == 'modular_obstruction_verified':
            if report.get('scope') != SCOPE or evidence.get('kind') != 'modular_obstruction':
                raise ValueError('Claim scope is inconsistent')
            possible, size = residues(task, evidence.get('modulus'))
            if (0 in possible or evidence.get('possible_residues') != possible
                    or type(evidence.get('assignments')) is not int or evidence['assignments'] != size):
                raise ValueError('Residue enumeration does not establish the obstruction')
            return {'valid': True, 'status': report['status'], 'scope': SCOPE,
                    'reason': 'All residue assignments were re-enumerated exactly. Every integer vector reduces modulo this modulus, so no integer zero exists.'}
        if report.get('status') != 'inconclusive' or evidence.get('kind') != 'search_only':
            raise ValueError('Unsupported modular claim')
        if report.get('scope') != INCONCLUSIVE_SCOPE:
            raise ValueError('Inconclusive report scope is inconsistent')
        return {'valid': True, 'status': 'inconclusive', 'reason': 'No proof claim is made.'}
    except (ValueError, TypeError, KeyError) as error:
        return {'valid': False, 'reason': str(error)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', type=Path)
    parser.add_argument('--max-modulus', type=int, default=16)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', action='store_true', help='recheck a saved modular report instead')
    args = parser.parse_args(argv)
    try:
        if args.task.stat().st_size > 2_000_000:
            raise ValueError('JSON exceeds 2 MB')
        data = json.loads(args.task.read_text(encoding='utf-8'))
        result = verify(data) if args.verify else solve(data, args.max_modulus)
        encoded = json.dumps(result, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(encoded.encode())
        print(encoded, end='')
        return (0 if result['valid'] else 1) if args.verify else (3 if result['status'] == 'inconclusive' else 0)
    except (ValueError, OSError, RecursionError) as error:
        print(f'Modular checker: {error}', file=sys.stderr)
        return 2
