"""Bounded mathematical experiments and independently checked rational certificates.

This module accepts data, never executable expressions. A finite search is not a
proof on an infinite domain. A rational sum-of-squares identity is such a proof.
"""

import argparse
import copy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys


MAX_VARIABLES = 4
MAX_TERMS = 256
MAX_DEGREE = 12
MAX_POINTS = 100_000
MAX_OPERATIONS = 2_000_000
MAX_FILE_BYTES = 2_000_000
MAX_COEFFICIENT_BITS = 128
SCOPES = {
    'exact_sos_verified': 'Polynomial is nonnegative for every real assignment.',
    'counterexample_verified': 'The supplied nonnegativity statement is false on its stated domain.',
    'bounded_verified': 'Nonnegativity holds only on the finite integer box in this task.',
    'inconclusive': 'No global proof or counterexample was found; the real-domain conjecture remains unproved by this run.',
}


def _integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'{name} must be an integer in [{minimum}, {maximum}]')
    return value


def _rational(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError('coefficients must be rational strings or integers')
    if len(str(value)) > 90:
        raise ValueError('coefficient exceeds the rational input budget')
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('invalid rational coefficient') from exc
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_COEFFICIENT_BITS:
        raise ValueError('coefficient exceeds the rational bit budget')
    return result


def _polynomial(terms, dimensions, *, max_degree=MAX_DEGREE, max_terms=MAX_TERMS):
    if not isinstance(terms, list) or not 0 <= len(terms) <= max_terms:
        raise ValueError(f'polynomial must have at most {max_terms} terms')
    result = {}
    bit_budget = 0
    for term in terms:
        if not isinstance(term, dict) or set(term) != {'coefficient', 'powers'}:
            raise ValueError('each term needs exactly coefficient and powers')
        powers = term['powers']
        if not isinstance(powers, list) or len(powers) != dimensions:
            raise ValueError('powers must match the number of variables')
        powers = tuple(_integer(x, 'power', 0, max_degree) for x in powers)
        if sum(powers) > max_degree:
            raise ValueError('total polynomial degree exceeds the budget')
        coefficient = _rational(term['coefficient'])
        bit_budget += abs(coefficient.numerator).bit_length() + coefficient.denominator.bit_length()
        if bit_budget > 8192:
            raise ValueError('aggregate rational coefficient budget exceeded')
        result[powers] = result.get(powers, Fraction(0)) + coefficient
    if any(max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_COEFFICIENT_BITS
           for value in result.values()):
        raise ValueError('combined coefficient exceeds the rational bit budget')
    return {powers: coefficient for powers, coefficient in result.items() if coefficient}


def _terms(polynomial):
    return [{'coefficient': str(coefficient), 'powers': list(powers)}
            for powers, coefficient in sorted(polynomial.items())]


def _bounds(raw, dimensions):
    if not isinstance(raw, list) or len(raw) != dimensions:
        raise ValueError('integer_box bounds must match the variables')
    bounds = []
    size = 1
    for pair in raw:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError('each bound must be [lower, upper]')
        low, high = (_integer(x, 'bound', -10_000, 10_000) for x in pair)
        if low > high:
            raise ValueError('lower bound exceeds upper bound')
        size *= high - low + 1
        if size > MAX_POINTS:
            raise ValueError(f'integer box exceeds {MAX_POINTS} points')
        bounds.append([low, high])
    return bounds, size


def validate_task(task):
    """Return normalized JSON data after applying fixed arithmetic/search budgets."""
    if (not isinstance(task, dict) or type(task.get('schema_version')) is not int
            or task['schema_version'] != 1):
        raise ValueError('task schema_version must be 1')
    if task.get('kind') != 'polynomial_nonnegative':
        raise ValueError('supported task kind: polynomial_nonnegative')
    variables = task.get('variables')
    if (not isinstance(variables, list) or not 1 <= len(variables) <= MAX_VARIABLES
            or any(not isinstance(v, str) or not v.isascii() or not v.isidentifier()
                   or len(v) > 32 for v in variables) or len(set(variables)) != len(variables)):
        raise ValueError('use one to four distinct ASCII variable names')
    polynomial = _polynomial(task.get('polynomial'), len(variables))
    domain = task.get('domain')
    if (not isinstance(domain, dict) or not isinstance(domain.get('kind'), str)
            or domain['kind'] not in {'real', 'integer_box'}):
        raise ValueError('domain kind must be real or integer_box')
    if domain['kind'] == 'integer_box':
        bounds, size = _bounds(domain.get('bounds'), len(variables))
        domain = {'kind': 'integer_box', 'bounds': bounds}
    else:
        size = 9 ** len(variables)
        domain = {'kind': 'real'}
    if size * max(1, len(polynomial)) * len(variables) > MAX_OPERATIONS:
        raise ValueError('estimated finite search arithmetic exceeds the operation budget')
    title = task.get('title', 'Polynomial nonnegativity')
    if not isinstance(title, str) or len(title) > 240:
        raise ValueError('title must be a string of at most 240 characters')
    normalized = {'schema_version': 1, 'kind': 'polynomial_nonnegative', 'title': title,
                  'variables': list(variables), 'polynomial': _terms(polynomial), 'domain': domain}
    if 'certificate' in task:
        # Validate the candidate here; an invalid identity is a failed proof attempt.
        _expand_sos(task['certificate'], len(variables))
        normalized['certificate'] = copy.deepcopy(task['certificate'])
    return normalized


def _evaluate(polynomial, point):
    result = Fraction(0)
    for powers, coefficient in polynomial.items():
        value = coefficient
        for coordinate, power in zip(point, powers):
            value *= coordinate ** power
        result += value
    return result


def _expand_sos(certificate, dimensions):
    """Independent algebraic verifier: expand each weighted square exactly."""
    if not isinstance(certificate, dict) or set(certificate) != {'kind', 'squares'}:
        raise ValueError('SOS certificate needs exactly kind and squares')
    if certificate['kind'] != 'rational_sos':
        raise ValueError('supported certificate kind: rational_sos')
    squares = certificate['squares']
    if not isinstance(squares, list) or len(squares) > 32:
        raise ValueError('certificate has more than 32 squares')
    expanded = {}
    multiplication_budget = 0
    rational_budget = 0
    for square in squares:
        if not isinstance(square, dict) or set(square) != {'weight', 'polynomial'}:
            raise ValueError('each square needs exactly weight and polynomial')
        weight = _rational(square['weight'])
        if weight < 0:
            raise ValueError('SOS weights must be nonnegative')
        factor = _polynomial(square['polynomial'], dimensions, max_degree=6, max_terms=64)
        multiplication_budget += len(factor) ** 2
        rational_budget += sum(abs(v.numerator).bit_length() + v.denominator.bit_length()
                               for v in [weight, *factor.values()])
        if multiplication_budget > 16384 or rational_budget > 8192:
            raise ValueError('aggregate certificate arithmetic budget exceeded')
        for left, a in factor.items():
            for right, b in factor.items():
                powers = tuple(x + y for x, y in zip(left, right))
                expanded[powers] = expanded.get(powers, Fraction(0)) + weight * a * b
    return {powers: coefficient for powers, coefficient in expanded.items() if coefficient}


def verify_sos(polynomial, certificate, dimensions):
    """Check a supplied rational SOS identity without trusting its discovery."""
    target = _polynomial(polynomial, dimensions)
    return target == _expand_sos(certificate, dimensions)


def _quadratic_sos(polynomial, dimensions):
    """Discover an affine rational SOS by exact unpivoted LDL decomposition."""
    if any(sum(powers) > 2 for powers in polynomial):
        return None
    size = dimensions + 1
    matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for powers, coefficient in polynomial.items():
        indices = [i + 1 for i, power in enumerate(powers) for _ in range(power)]
        if not indices:
            matrix[0][0] += coefficient
        elif len(indices) == 1:
            matrix[0][indices[0]] += coefficient / 2
            matrix[indices[0]][0] += coefficient / 2
        elif indices[0] == indices[1]:
            matrix[indices[0]][indices[0]] += coefficient
        else:
            a, b = indices
            matrix[a][b] += coefficient / 2
            matrix[b][a] += coefficient / 2
    lower = [[Fraction(i == j) for j in range(size)] for i in range(size)]
    diagonal = []
    for j in range(size):
        pivot = matrix[j][j] - sum(lower[j][k] ** 2 * diagonal[k] for k in range(j))
        if pivot < 0:
            return None
        diagonal.append(pivot)
        for i in range(j + 1, size):
            residual = matrix[i][j] - sum(lower[i][k] * lower[j][k] * diagonal[k] for k in range(j))
            if not pivot:
                if residual:
                    return None
            else:
                lower[i][j] = residual / pivot
    squares = []
    for j, weight in enumerate(diagonal):
        if not weight:
            continue
        factor = {}
        for i in range(size):
            if lower[i][j]:
                powers = [0] * dimensions
                if i:
                    powers[i - 1] = 1
                factor[tuple(powers)] = lower[i][j]
        squares.append({'weight': str(weight), 'polynomial': _terms(factor)})
    candidate = {'kind': 'rational_sos', 'squares': squares}
    # Candidate arithmetic may exceed input certificate budgets: then decline it.
    try:
        return candidate if _expand_sos(candidate, dimensions) == polynomial else None
    except ValueError:
        return None


def _task_digest(task):
    encoded = json.dumps(task, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _points(bounds):
    return itertools.product(*(range(low, high + 1) for low, high in bounds))


def solve_task(task):
    """Try a supplied/discovered exact SOS, then a bounded counterexample search."""
    task = validate_task(task)
    dimensions = len(task['variables'])
    polynomial = _polynomial(task['polynomial'], dimensions)
    report = {'schema_version': 1, 'engine': 'anaxia-exact-lab/1', 'task': task,
              'task_sha256': _task_digest(task), 'status': 'inconclusive',
              'scope': '', 'evidence': {}, 'stages': []}
    report['stages'].append({'role': 'planner', 'finding':
        'Try exact rational sum-of-squares certification; otherwise enumerate a bounded integer box.'})
    certificate = task.get('certificate')
    if certificate is not None and _expand_sos(certificate, dimensions) != polynomial:
        report['stages'].append({'role': 'critic', 'finding': 'Supplied SOS identity does not equal the target polynomial.'})
        certificate = None
    if certificate is None:
        certificate = _quadratic_sos(polynomial, dimensions)
    if certificate is not None:
        report.update(status='exact_sos_verified', scope='Polynomial is nonnegative for every real assignment.',
                      evidence=copy.deepcopy(certificate))
        report['stages'].append({'role': 'explorer', 'finding': 'A rational weighted sum-of-squares identity was found.'})
    else:
        bounds = task['domain'].get('bounds', [[-4, 4] for _ in range(dimensions)])
        count = 0
        counterexample = None
        for point in _points(bounds):
            count += 1
            value = _evaluate(polynomial, point)
            if value < 0:
                counterexample = {'kind': 'exact_counterexample', 'point': list(point),
                                  'value': str(value), 'searched_bounds': bounds, 'points_checked': count}
                break
        if counterexample:
            report.update(status='counterexample_verified', scope='The supplied nonnegativity statement is false on its stated domain.',
                          evidence=counterexample)
        elif task['domain']['kind'] == 'integer_box':
            report.update(status='bounded_verified', scope='Nonnegativity holds only on the finite integer box in this task.',
                          evidence={'kind': 'finite_enumeration', 'bounds': bounds, 'points_checked': count})
        else:
            report.update(status='inconclusive', scope='No global proof or counterexample was found; the real-domain conjecture remains unproved by this run.',
                          evidence={'kind': 'search_only', 'bounds': bounds, 'points_checked': count})
        report['stages'].append({'role': 'explorer', 'finding': f'Evaluated {count} integer assignments using exact rational arithmetic.'})
    report['scope'] = SCOPES[report['status']]
    report['stages'].append({'role': 'critic', 'finding':
        ('Every SOS weight must be nonnegative and every expanded coefficient must match exactly.'
         if report['status'] == 'exact_sos_verified' else
         'A finite positive search supports only the stated finite domain; negative witnesses must lie inside the claimed domain.')})
    checked = verify_report(report)
    if not checked['valid']:
        raise ValueError('internal certificate verification failed: ' + checked['reason'])
    report['stages'].append({'role': 'verifier', 'finding': checked['reason']})
    return report


def verify_report(report):
    """Recheck the claim from task and evidence; never trust the claimed status."""
    try:
        if (not isinstance(report, dict) or type(report.get('schema_version')) is not int
                or report['schema_version'] != 1):
            raise ValueError('report schema_version must be 1')
        task = validate_task(report.get('task'))
        if report.get('task_sha256') != _task_digest(task):
            raise ValueError('task digest does not match')
        polynomial = _polynomial(task['polynomial'], len(task['variables']))
        evidence = report.get('evidence')
        if not isinstance(evidence, dict):
            raise ValueError('missing mathematical evidence')
        kind = evidence.get('kind')
        status = report.get('status')
        if not isinstance(status, str) or status not in SCOPES or report.get('scope') != SCOPES[status]:
            raise ValueError('report scope does not match its mathematical status')
        if status == 'exact_sos_verified' and kind == 'rational_sos':
            if not verify_sos(task['polynomial'], evidence, len(task['variables'])):
                raise ValueError('expanded SOS is not identical to the target polynomial')
            reason = 'Exact coefficient comparison verified the rational SOS identity over all real assignments.'
        elif status == 'counterexample_verified' and kind == 'exact_counterexample':
            point = evidence.get('point')
            if not isinstance(point, list) or len(point) != len(task['variables']):
                raise ValueError('counterexample dimension mismatch')
            point = [_integer(x, 'counterexample coordinate', -10_000, 10_000) for x in point]
            if task['domain']['kind'] == 'integer_box' and any(
                    not lo <= value <= hi for value, (lo, hi) in zip(point, task['domain']['bounds'])):
                raise ValueError('counterexample lies outside the claimed domain')
            value = _evaluate(polynomial, point)
            if value >= 0 or _rational(evidence.get('value')) != value:
                raise ValueError('counterexample does not have its claimed negative value')
            reason = 'Exact evaluation verified a negative value inside the stated domain.'
        elif ((status == 'bounded_verified' and kind == 'finite_enumeration')
              or (status == 'inconclusive' and kind == 'search_only')):
            bounds, size = _bounds(evidence.get('bounds'), len(task['variables']))
            if status == 'bounded_verified':
                if task['domain']['kind'] != 'integer_box' or bounds != task['domain']['bounds']:
                    raise ValueError('finite evidence does not cover the stated domain')
            elif task['domain']['kind'] != 'real' or bounds != [[-4, 4] for _ in task['variables']]:
                raise ValueError('search-only evidence does not match the configured real-domain search')
            if type(evidence.get('points_checked')) is not int or evidence['points_checked'] != size:
                raise ValueError('finite enumeration point count is incorrect')
            if any(_evaluate(polynomial, point) < 0 for point in _points(bounds)):
                raise ValueError('a negative value exists in the claimed checked box')
            reason = ('Exhaustive exact re-evaluation verified the finite integer box; no infinite-domain claim follows.'
                      if status == 'bounded_verified' else
                      'The bounded search record is consistent. This is not a proof on the real domain.')
        else:
            raise ValueError('status and evidence kind do not form a supported mathematical claim')
        return {'valid': True, 'status': status, 'reason': reason}
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return {'valid': False, 'reason': str(exc)}


def _read_json(path):
    path = Path(path)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('JSON input exceeds the 2 MB file budget')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except RecursionError:
        raise ValueError('JSON nesting exceeds the input limit') from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    solve = commands.add_parser('solve', help='run bounded exact mathematical tools on a JSON task')
    solve.add_argument('task')
    solve.add_argument('--output', type=Path)
    verify = commands.add_parser('verify', help='independently recheck a saved mathematical report')
    verify.add_argument('report')
    args = parser.parse_args(argv)
    try:
        if args.command == 'solve':
            result = solve_task(_read_json(args.task))
            encoded = json.dumps(result, indent=2, ensure_ascii=True) + '\n'
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(encoded, encoding='utf-8', newline='\n')
            print(encoded, end='')
            return 0 if result['status'] != 'inconclusive' else 3
        result = verify_report(_read_json(args.report))
        print(json.dumps(result, indent=2))
        return 0 if result['valid'] else 1
    except (ValueError, OSError) as exc:
        print(f'Anaxia lab: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
