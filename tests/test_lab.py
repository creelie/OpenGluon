import copy
import contextlib
import io
import json
from pathlib import Path
import random
import tempfile
import unittest

from anaxia import lab


ROOT = Path(__file__).resolve().parents[1]


def task(polynomial, *, domain=None, variables=None):
    return {'schema_version': 1, 'kind': 'polynomial_nonnegative',
            'variables': variables or ['x'], 'polynomial': polynomial,
            'domain': domain or {'kind': 'real'}}


def term(coefficient, *powers):
    return {'coefficient': coefficient, 'powers': list(powers)}


class ExactLabTests(unittest.TestCase):
    def test_discovered_quadratic_sos_is_exact_and_globally_scoped(self):
        # (x - y)^2 + (x + 1)^2 / 3 is not just a numerical sample.
        source = task([term('4/3', 2, 0), term('-2', 1, 1), term('1', 0, 2),
                       term('2/3', 1, 0), term('1/3', 0, 0)], variables=['x', 'y'])
        result = lab.solve_task(source)
        self.assertEqual(result['status'], 'exact_sos_verified')
        self.assertTrue(lab.verify_report(result)['valid'])
        self.assertTrue(lab.verify_sos(source['polynomial'], result['evidence'], 2))
        self.assertEqual([stage['role'] for stage in result['stages']],
                         ['planner', 'explorer', 'critic', 'verifier'])

    def test_zero_polynomial_and_zero_pivot_are_certified(self):
        for source in (task([]), task([term('1', 2)])):
            result = lab.solve_task(source)
            self.assertEqual(result['status'], 'exact_sos_verified')
            self.assertTrue(lab.verify_report(result)['valid'])

    def test_quadratic_discovery_reconstructs_generated_psd_examples(self):
        randomizer = random.Random(71)
        for dimensions in range(1, 5):
            for _ in range(5):
                squares = []
                for _ in range(dimensions + 2):
                    factor = [term(str(randomizer.randint(-3, 3)), *([0] * dimensions))]
                    for index in range(dimensions):
                        powers = [0] * dimensions
                        powers[index] = 1
                        factor.append(term(str(randomizer.randint(-3, 3)), *powers))
                    squares.append({'weight': str(randomizer.randint(0, 3)), 'polynomial': factor})
                expected = {'kind': 'rational_sos', 'squares': squares}
                polynomial = lab._expand_sos(expected, dimensions)
                result = lab.solve_task(task(lab._terms(polynomial),
                                            variables=['x', 'y', 'z', 'w'][:dimensions]))
                self.assertEqual(result['status'], 'exact_sos_verified')
                self.assertTrue(lab.verify_report(result)['valid'])

    def test_supplied_quartic_sos_is_independently_checked(self):
        source = task([term('1', 4), term('-2', 2), term('1', 0)])
        source['certificate'] = {'kind': 'rational_sos', 'squares': [
            {'weight': '1', 'polynomial': [term('1', 2), term('-1', 0)]}]}
        result = lab.solve_task(source)
        self.assertEqual(result['status'], 'exact_sos_verified')
        tampered = copy.deepcopy(result)
        tampered['evidence']['squares'][0]['weight'] = '2'
        check = lab.verify_report(tampered)
        self.assertFalse(check['valid'])
        self.assertIn('not identical', check['reason'])

    def test_wrong_supplied_identity_is_not_accepted(self):
        source = task([term('1', 4), term('-1', 0)])
        source['certificate'] = {'kind': 'rational_sos', 'squares': [
            {'weight': '1', 'polynomial': [term('1', 2)]}]}
        result = lab.solve_task(source)
        self.assertEqual(result['status'], 'counterexample_verified')
        self.assertEqual(result['evidence']['point'], [0])

    def test_integer_valued_nonnegative_polynomial_has_only_finite_claim(self):
        # x(x-1) >= 0 for integers, but not for real x in (0,1).
        source = task([term('1', 2), term('-1', 1)],
                      domain={'kind': 'integer_box', 'bounds': [[-5, 5]]})
        result = lab.solve_task(source)
        self.assertEqual(result['status'], 'bounded_verified')
        self.assertEqual(result['evidence']['points_checked'], 11)
        self.assertTrue(lab.verify_report(result)['valid'])
        forged = copy.deepcopy(result)
        forged['status'] = 'exact_sos_verified'
        self.assertFalse(lab.verify_report(forged)['valid'])

    def test_same_polynomial_on_reals_is_inconclusive(self):
        result = lab.solve_task(task([term('1', 2), term('-1', 1)]))
        self.assertEqual(result['status'], 'inconclusive')
        self.assertTrue(lab.verify_report(result)['valid'])
        self.assertIn('not a proof', lab.verify_report(result)['reason'])

    def test_negative_value_is_verified_as_exact_rational(self):
        source = task([term('1/3', 2), term('-1/2', 0)],
                      domain={'kind': 'integer_box', 'bounds': [[0, 4]]})
        result = lab.solve_task(source)
        self.assertEqual(result['status'], 'counterexample_verified')
        self.assertEqual(result['evidence']['point'], [0])
        self.assertEqual(result['evidence']['value'], '-1/2')
        forged = copy.deepcopy(result)
        forged['evidence']['value'] = '-2/3'
        self.assertFalse(lab.verify_report(forged)['valid'])

    def test_counterexample_outside_domain_is_rejected(self):
        source = task([term('1', 2), term('-2', 0)],
                      domain={'kind': 'integer_box', 'bounds': [[2, 5]]})
        report = lab.solve_task(source)
        report.update(status='counterexample_verified', scope=lab.SCOPES['counterexample_verified'], evidence={
            'kind': 'exact_counterexample', 'point': [0], 'value': '-2'})
        self.assertFalse(lab.verify_report(report)['valid'])

    def test_bounded_scope_cannot_be_rewritten_as_a_global_claim(self):
        source = task([term('1', 4), term('1', 0)],
                      domain={'kind': 'integer_box', 'bounds': [[-2, 2]]})
        report = lab.solve_task(source)
        report['scope'] = lab.SCOPES['exact_sos_verified']
        self.assertFalse(lab.verify_report(report)['valid'])

    def test_zero_pivot_with_nonzero_off_diagonal_cannot_make_a_certificate(self):
        result = lab.solve_task(task([term('1', 1)]))
        self.assertEqual(result['status'], 'counterexample_verified')
        self.assertTrue(lab.verify_report(result)['valid'])

    def test_tampered_task_and_incomplete_finite_counts_are_rejected(self):
        source = task([term('1', 4), term('1', 0)],
                      domain={'kind': 'integer_box', 'bounds': [[-2, 2]]})
        report = lab.solve_task(source)
        self.assertEqual(report['status'], 'bounded_verified')
        forged = copy.deepcopy(report)
        forged['task']['polynomial'][0]['coefficient'] = '2'
        self.assertFalse(lab.verify_report(forged)['valid'])
        report['evidence']['points_checked'] -= 1
        self.assertFalse(lab.verify_report(report)['valid'])

    def test_search_budgets_reject_large_inputs_before_enumeration(self):
        sources = [
            task([term('1', 13)]),
            task([term('1', 2)], domain={'kind': 'integer_box', 'bounds': [[-10000, 10000], [0, 100]]}, variables=['x', 'y']),
            task([term('1', 2)], domain={'kind': 'integer_box', 'bounds': [[2, 1]]}),
            task([term('1' * 100, 0)]),
            task([term('1', True)]),
            task([term('1', 2)], variables=['x', 'x']),
            dict(task([term('1', 2)]), schema_version=True),
            task([term('1', 2)], domain={'kind': []}),
        ]
        for source in sources:
            with self.subTest(source=source), self.assertRaises(ValueError):
                lab.solve_task(source)

    def test_executable_and_negative_weight_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            lab.solve_task(task([term("__import__('os').system('echo unsafe')", 2)]))
        source = task([term('1', 2)])
        source['certificate'] = {'kind': 'rational_sos', 'squares': [
            {'weight': '-1', 'polynomial': [term('1', 1)]}]}
        with self.assertRaises(ValueError):
            lab.solve_task(source)

    def test_cli_round_trip_and_examples(self):
        for name in ('quadratic-sos.json', 'quartic-sos.json', 'bounded-polynomial.json', 'false-polynomial.json'):
            result = lab.solve_task(json.loads((ROOT / 'examples' / name).read_text()))
            self.assertTrue(lab.verify_report(result)['valid'])
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'proof.json'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lab.main(['solve', str(ROOT / 'examples/quadratic-sos.json'), '--output', str(output)]), 0)
                self.assertEqual(lab.main(['verify', str(output)]), 0)


if __name__ == '__main__':
    unittest.main()
