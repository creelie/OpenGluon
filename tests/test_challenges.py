import copy
import json
import tempfile
import unittest
from pathlib import Path

from anaxia.challenges import collatz, goldbach, legendre, erdos_straus, d4_configuration, verify_experiment, run


class ChallengeEvidenceTests(unittest.TestCase):
    def test_four_finite_experiments_do_not_claim_global_closure(self):
        for report in (collatz(100), goldbach(100), legendre(20), erdos_straus(30)):
            checked = verify_experiment(report)
            self.assertTrue(checked['valid'], checked)
            self.assertEqual(checked['status'], 'finite_evidence_verified')
            self.assertFalse(checked['global_closure'])

    def test_truncated_collatz_search_is_inconclusive(self):
        report = collatz(30, 1)
        checked = verify_experiment(report)
        self.assertTrue(checked['valid'])
        self.assertEqual(checked['status'], 'inconclusive')

    def test_tampered_prime_and_collatz_witnesses_rejected(self):
        report = goldbach(10)
        report['witnesses'][-1] = [10, 1, 9]
        self.assertFalse(verify_experiment(report)['valid'])
        report = collatz(10)
        report['witnesses'][-1][1] += 1
        self.assertFalse(verify_experiment(report)['valid'])

    def test_missing_coverage_and_unit_fraction_mutation_rejected(self):
        report = legendre(10)
        report['witnesses'].pop()
        self.assertFalse(verify_experiment(report)['valid'])
        report = erdos_straus(20)
        report['witnesses'][0][-1] += 1
        self.assertFalse(verify_experiment(report)['valid'])

    def test_d4_exact_construction_has_276_checked_pairs(self):
        report = d4_configuration()
        checked = verify_experiment(report)
        self.assertTrue(checked['valid'])
        self.assertEqual(checked['pairs_checked'], 276)
        self.assertFalse(checked['new_result'])
        report['points'][0] = [0, 0, 0, 0]
        self.assertFalse(verify_experiment(report)['valid'])

    def test_tampered_global_claim_and_unknown_target_rejected(self):
        report = goldbach(10)
        report['global_status'] = 'closed'
        self.assertFalse(verify_experiment(report)['valid'])
        self.assertFalse(verify_experiment({'id': 'riemann', 'limit': 1, 'witnesses': [], 'unfinished': [1]})['valid'])

    def test_hidden_scope_novelty_and_schema_promotions_are_rejected(self):
        for key, value in (('scope', 'Goldbach is proved for every even integer.'),
                           ('global_closure', True), ('global_closures', 1),
                           ('new_result', True), ('paper_eligible', True), ('schema_version', True)):
            report = goldbach(30)
            report[key] = value
            with self.subTest(key=key):
                self.assertFalse(verify_experiment(report)['valid'])

    def test_stored_verification_and_status_cannot_be_forged(self):
        report = collatz(30, 1)
        report['verification'] = dict(verify_experiment(report), status='finite_evidence_verified')
        self.assertFalse(verify_experiment(report)['valid'])
        report = d4_configuration()
        report['verification'] = dict(verify_experiment(report), global_closure=True)
        self.assertFalse(verify_experiment(report)['valid'])
        report = legendre(20)
        report['status'] = 'universal_conjecture_closed'
        self.assertFalse(verify_experiment(report)['valid'])

    def test_degenerate_or_excessive_declared_domains_are_rejected(self):
        for report in ({'id': 'goldbach', 'limit': 1, 'witnesses': [], 'unfinished': []},
                       {'id': 'erdos-straus', 'limit': 1, 'witnesses': [], 'unfinished': []},
                       {'id': 'erdos-straus', 'limit': 1001, 'witnesses': [], 'unfinished': list(range(2,1002))}):
            self.assertFalse(verify_experiment(report)['valid'])

    def test_full_assessment_has_no_new_closure_or_paper_eligibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run('quick', Path(temporary))
            self.assertEqual(result['global_closures'], 0)
            self.assertFalse(result['paper_eligible'])
            self.assertEqual({r['id'] for r in result['research_targets']},
                             {'hodge', 'yang-mills', 'riemann', 'd4-descent', 'd4-kissing', 'd4-packing'})
            self.assertTrue((Path(temporary)/'README.md').exists())
            for path in Path(temporary).glob('*.json'):
                if path.name != 'index.json':
                    self.assertTrue(verify_experiment(json.loads(path.read_text()))['valid'])


if __name__ == '__main__':
    unittest.main()
