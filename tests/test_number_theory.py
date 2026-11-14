import copy
import json
from pathlib import Path
import unittest
from anaxia.number_theory import solve, verify

ROOT = Path(__file__).resolve().parents[1]


class ModularProofTests(unittest.TestCase):
    def setUp(self):
        self.task = json.loads((ROOT / 'examples/modular-obstruction.json').read_text())

    def test_obstruction_is_a_universal_claim_with_rechecked_residues(self):
        report = solve(self.task)
        self.assertEqual(report['status'], 'modular_obstruction_verified')
        self.assertEqual(report['evidence']['modulus'], 4)
        self.assertTrue(verify(report)['valid'])

    def test_falsified_residues_or_scope_cannot_close_a_problem(self):
        for field, value in [('assignments', 4), ('possible_residues', [1])]:
            report = solve(self.task)
            report['evidence'][field] = value
            self.assertFalse(verify(report)['valid'])
        report = solve(self.task)
        report['scope'] = 'Riemann hypothesis solved'
        self.assertFalse(verify(report)['valid'])

    def test_solvable_equation_is_inconclusive_not_universal(self):
        self.task['polynomial'][-1]['coefficient'] = '-2'
        self.assertEqual(solve(self.task)['status'], 'inconclusive')

    def test_rational_coefficients_and_large_moduli_rejected(self):
        self.task['polynomial'][0]['coefficient'] = '1/2'
        with self.assertRaises(ValueError):
            solve(self.task)
        with self.assertRaises(ValueError):
            solve({}, 1_000_000)

    def test_tampered_equation_is_rejected(self):
        report = solve(self.task)
        report['task']['polynomial'][0]['coefficient'] = '-2'
        self.assertFalse(verify(report)['valid'])

    def test_boolean_schema_versions_are_rejected(self):
        self.task['schema_version'] = True
        with self.assertRaises(ValueError):
            solve(self.task)
        self.task['schema_version'] = 1
        report = solve(self.task)
        report['schema_version'] = True
        self.assertFalse(verify(report)['valid'])

    def test_inconclusive_scope_cannot_be_forged_into_a_proof_claim(self):
        self.task['polynomial'][-1]['coefficient'] = '-2'
        report = solve(self.task)
        self.assertEqual(report['status'], 'inconclusive')
        self.assertTrue(verify(report)['valid'])
        report['scope'] = 'All integer equations have now been solved.'
        self.assertFalse(verify(report)['valid'])


if __name__ == '__main__':
    unittest.main()
