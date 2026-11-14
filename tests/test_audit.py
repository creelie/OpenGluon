import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from anaxia import audit, lab

ROOT = Path(__file__).resolve().parents[1]


class ClaimAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.manifest = self.root / 'claims.json'
        for filename in ('false-polynomial.json', 'true-polynomial.json', 'no-integer-root.json'):
            (self.root / filename).write_bytes((ROOT / 'examples/audit' / filename).read_bytes())
        self.template = json.loads((ROOT / 'examples/audit/synthetic-claims.json').read_text())

    def tearDown(self):
        self.temporary.cleanup()

    def write_manifest(self, manifest=None):
        self.manifest.write_text(json.dumps(self.template if manifest is None else manifest), encoding='utf-8')
        return self.manifest

    def test_synthetic_counterexample_and_correction_have_independent_evidence(self):
        report = audit.audit_manifest(self.write_manifest())
        self.assertTrue(report['tutorial'])
        self.assertEqual(report['summary'], {'formal_claim_verified': 2, 'formal_claim_refuted': 1, 'inconclusive': 0})
        refuted = report['claims'][0]
        self.assertEqual(refuted['status'], 'formal_claim_refuted')
        self.assertEqual(refuted['evidence_report']['evidence']['point'], [0])
        proposal = refuted['proposed_correction']
        self.assertEqual(proposal['added_constant'], '1')
        self.assertEqual(proposal['status'], 'formal_proposal_verified_source_correspondence_unreviewed')
        self.assertTrue(lab.verify_report(proposal['evidence_report'])['valid'])

    def test_source_correspondence_never_promoted_by_a_verified_formal_task(self):
        self.template['claims'][1]['source_correspondence'] = 'reviewed'
        self.template['claims'][1]['source_claim_requires_review'] = False
        report = audit.audit_manifest(self.write_manifest())
        for claim in report['claims']:
            self.assertEqual(claim['source_correspondence'], 'unreviewed')
            self.assertTrue(claim['source_claim_requires_review'])
            self.assertIn('does not establish an error in the paper', claim['source_correspondence_scope'])

    def test_exact_supplied_excerpt_and_hash_are_retained(self):
        excerpt = 'For every real x,\n    x squared plus one is nonnegative.  '
        self.template['claims'][1]['source_excerpt'] = excerpt
        report = audit.audit_manifest(self.write_manifest())
        claim = report['claims'][1]
        self.assertEqual(claim['source_excerpt'], excerpt)
        self.assertEqual(claim['source_excerpt_sha256'], hashlib.sha256(excerpt.encode()).hexdigest())

    def test_modular_interpretation_is_explicitly_no_integer_zero(self):
        report = audit.audit_manifest(self.write_manifest())
        claim = report['claims'][2]
        self.assertEqual(claim['formal_statement_kind'], 'integer_polynomial_has_no_integer_zero')
        self.assertEqual(claim['evidence_report']['status'], 'modular_obstruction_verified')
        self.assertTrue(claim['independent_verification']['valid'])

    def test_finite_verified_claim_does_not_gain_global_scope(self):
        task = json.loads((self.root / 'true-polynomial.json').read_text())
        task['polynomial'] = [{'coefficient': '1', 'powers': [4]}, {'coefficient': '1', 'powers': [0]}]
        task['domain'] = {'kind': 'integer_box', 'bounds': [[-2, 2]]}
        (self.root / 'true-polynomial.json').write_text(json.dumps(task))
        report = audit.audit_manifest(self.write_manifest())
        claim = report['claims'][1]
        self.assertEqual(claim['status'], 'formal_claim_verified')
        self.assertEqual(claim['evidence_report']['status'], 'bounded_verified')
        self.assertIn('finite integer box', claim['scope'])

    def test_inconclusive_task_remains_inconclusive(self):
        task = json.loads((self.root / 'true-polynomial.json').read_text())
        task['variables'] = ['x', 'y']
        task['polynomial'] = [{'coefficient': '1', 'powers': [2, 0]}, {'coefficient': '-1', 'powers': [1, 0]}]
        (self.root / 'true-polynomial.json').write_text(json.dumps(task))
        report = audit.audit_manifest(self.write_manifest())
        self.assertEqual(report['claims'][1]['status'], 'inconclusive')
        self.assertIsNone(report['claims'][1]['proposed_correction'])

    def test_paths_and_reserved_or_duplicate_output_ids_are_rejected(self):
        for field, value in (('task', '../outside.json'), ('task', str((self.root / 'true-polynomial.json').resolve())),
                             ('id', '../outside'), ('id', 'audit'), ('id', 'CON'), ('id', self.template['claims'][1]['id'].upper())):
            manifest = copy.deepcopy(self.template)
            manifest['claims'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                audit.audit_manifest(self.write_manifest(manifest))

    def test_unsupported_sources_and_missing_formalization_are_rejected(self):
        for field, value in (('source_url', 'file:///private/paper.pdf'), ('source_url', 'https://arxiv.org@evil.test/paper'),
                             ('source_url', 'https://arxiv.org/help'), ('source_excerpt', ''),
                             ('source_location', ''), ('formalization_note', ''), ('backend', 'exec')):
            manifest = copy.deepcopy(self.template)
            manifest['claims'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit.audit_manifest(self.write_manifest(manifest))

    def test_failed_verification_and_invalid_later_claim_write_no_outputs(self):
        output = self.root / 'output'
        with patch.object(lab, 'verify_report', return_value={'valid': False, 'reason': 'test rejection'}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(audit.main([str(self.write_manifest()), '--output', str(output)]), 2)
        self.assertFalse(output.exists())
        self.template['claims'][-1]['task'] = '../outside.json'
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(audit.main([str(self.write_manifest()), '--output', str(output)]), 2)
        self.assertFalse(output.exists())

    def test_unsafe_text_is_escaped_in_markdown_but_preserved_in_json(self):
        text = '<script>alert(1)</script> [link](javascript:bad) | # heading'
        self.template['claims'][0]['source_excerpt'] = text
        report = audit.audit_manifest(self.write_manifest())
        rendered = audit.render_report(report)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('\\[link\\]', rendered)
        self.assertEqual(report['claims'][0]['source_excerpt'], text)

    def test_cli_writes_readable_and_exact_evidence_artifacts(self):
        output = self.root / 'output'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(audit.main([str(self.write_manifest()), '--output', str(output)]), 0)
        self.assertTrue((output / 'AUDIT.md').exists())
        self.assertTrue((output / 'synthetic-refutation.json').exists())
        combined = json.loads((output / 'audit.json').read_text())
        self.assertTrue(combined['tutorial'])
        self.assertEqual(len(combined['claims']), 3)

    def test_budget_and_schema_validation(self):
        manifest = copy.deepcopy(self.template)
        manifest['schema_version'] = True
        with self.assertRaises(ValueError):
            audit.audit_manifest(self.write_manifest(manifest))
        manifest['schema_version'] = 1
        manifest['claims'] *= 8
        with self.assertRaises(ValueError):
            audit.audit_manifest(self.write_manifest(manifest))
        oversized = self.root / 'too-large.json'
        oversized.write_bytes(b' ' * (audit.MAX_FILE_BYTES + 1))
        with self.assertRaises(ValueError):
            audit.read_json(oversized)


if __name__ == '__main__':
    unittest.main()
