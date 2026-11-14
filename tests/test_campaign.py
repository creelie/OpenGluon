import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from anaxia import campaign


def target(key, title=None):
    return {'id': key, 'title': title or key.title(),
            'statement': f'Establish the original {key} claim with complete hypotheses.',
            'source_urls': ['https://arxiv.org/abs/1234.5678'],
            'proof_obligations': ['Give an exact statement and complete proof.'],
            'backend': 'research_proposal'}


class Campaign(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.targets = [target('hodge'), target('riemann'), target('yang-mills')]
        self.snapshot = {'schema_version': 1, 'generated_at_utc': '2026-11-14T00:00:00Z',
                         'repositories': [
                             {'id': 'github:1', 'name': 'owner/hodge-project',
                              'url': 'https://github.com/owner/hodge-project',
                              'description': 'A public Hodge research source. ' * 50},
                             {'id': 'github:2', 'name': 'owner/unrelated',
                              'url': 'https://github.com/owner/unrelated',
                              'description': 'A weather application.'}], 'papers': []}
        self.write_inputs()
        self.calls = []

    def write_inputs(self):
        (self.root / 'targets.json').write_text(json.dumps({'schema_version': 1, 'targets': self.targets}), encoding='utf-8')
        (self.root / 'sources.json').write_text(json.dumps(self.snapshot), encoding='utf-8')

    def proposer(self, task, model, **options):
        self.calls.append((copy.deepcopy(task), model, options))
        return {'proposal': 'Investigate a precise finite case; the global proof obligations remain.'}

    def run_campaign(self, **kwargs):
        return campaign.run_campaign('targets.json', 'sources.json', 'out', root=self.root,
                                     proposer=kwargs.pop('proposer', self.proposer), **kwargs)

    def test_round_robin_rotation_and_fixed_original_statement(self):
        first = self.run_campaign()
        second = self.run_campaign()
        self.assertEqual([item['target_id'] for item in first['attempts']], ['hodge', 'riemann'])
        self.assertEqual([item['target_id'] for item in second['attempts']], ['yang-mills', 'hodge'])
        self.assertEqual(second['next_cursor'], 1)
        self.assertEqual(self.calls[-1][0]['original_target'], self.targets[0])
        self.assertEqual(first['status'], 'unverified_proposal')
        self.assertEqual(first['global_status'], 'not_closed')
        self.assertEqual(self.calls[0][2]['provider'], 'ollama')
        self.assertEqual(self.calls[0][1], 'gemma3:4b')

    def test_source_context_is_relevant_bounded_and_deduplicated(self):
        duplicate = copy.deepcopy(self.snapshot['repositories'][0])
        self.snapshot['sources'] = [{'entries': [duplicate]}]
        self.snapshot['papers'] = [dict(duplicate, id=f'arxiv:{i}', name=f'Hodge source {i}') for i in range(9)]
        selected = campaign.select_context(self.targets[0], self.snapshot)
        self.assertEqual(len(selected), 5)
        self.assertTrue(all(len(item['excerpt']) <= 300 for item in selected))
        self.assertEqual(len({item['id'] for item in selected}), 5)
        self.assertFalse(any(item['id'] == 'github:2' for item in selected))

    def test_prior_notes_bounded_and_changed_statement_discards_them(self):
        self.run_campaign(max_targets=1, proposer=lambda *args, **kwargs: {'proposal': 'x' * 5000})
        self.run_campaign(max_targets=2)
        self.run_campaign(max_targets=1)
        self.assertEqual(len(self.calls[-1][0]['previous_unresolved_public_notes']), 2000)
        self.targets[0]['statement'] = 'A different original Hodge statement.'
        self.write_inputs()
        self.run_campaign(max_targets=2)
        self.run_campaign(max_targets=1)
        self.assertEqual(self.calls[-1][0]['original_target']['statement'], self.targets[0]['statement'])
        self.assertEqual(self.calls[-1][0]['previous_unresolved_public_notes'], '')

    def test_provider_failure_is_recorded_without_secret_and_other_targets_continue(self):
        calls = 0

        def fail_once(task, model, **options):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise ValueError('secret-api-key-DO-NOT-STORE')
            return {'proposal': 'A bounded public strategy.'}

        result = self.run_campaign(proposer=fail_once)
        self.assertEqual([item['outcome'] for item in result['attempts']], ['error', 'completed'])
        self.assertEqual(result['next_cursor'], 2)
        all_saved = ''.join(path.read_text(encoding='utf-8') for path in (self.root / 'out').rglob('*') if path.is_file())
        self.assertNotIn('secret-api-key', all_saved)
        self.assertTrue(all(item['global_status'] == 'not_closed' for item in result['attempts']))

    def test_repeated_failures_preserve_previous_unresolved_notes(self):
        self.targets = [self.targets[0]]
        self.write_inputs()
        self.run_campaign()

        def failed(*args, **kwargs):
            raise ValueError('provider unavailable')

        self.run_campaign(proposer=failed)
        self.run_campaign(proposer=failed)
        self.run_campaign()
        self.assertIn('Investigate a precise finite case', self.calls[-1][0]['previous_unresolved_public_notes'])

    def test_interrupted_second_call_preserves_first_committed_cursor(self):
        calls = 0

        def interrupted(task, model, **options):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return {'proposal': 'An unresolved public strategy.'}

        with self.assertRaises(KeyboardInterrupt):
            self.run_campaign(proposer=interrupted)
        state = json.loads((self.root / 'out/state.json').read_text())
        self.assertEqual(state['sequence'], 1)
        self.assertEqual(state['next_cursor'], 1)
        next_run = self.run_campaign(max_targets=1)
        self.assertEqual(next_run['attempts'][0]['target_id'], 'riemann')

    def test_failed_state_write_does_not_advance_committed_cursor(self):
        self.run_campaign(max_targets=1)
        original = campaign._atomic_json

        def fail_state(path, value):
            if path.name == 'state.json':
                raise OSError('simulated failed commit')
            return original(path, value)

        with patch.object(campaign, '_atomic_json', side_effect=fail_state), self.assertRaises(OSError):
            self.run_campaign(max_targets=1)
        resumed = self.run_campaign(max_targets=1)
        self.assertEqual(resumed['attempts'][0]['target_id'], 'riemann')
        self.assertEqual(resumed['sequence'], 2)

    def test_recent_history_is_bounded_without_extra_attempt_files(self):
        for _ in range(12):
            self.run_campaign()
        history = json.loads((self.root / 'out/history.json').read_text())
        self.assertEqual(len(history), 20)
        self.assertEqual(history[0]['sequence'], 5)
        self.assertEqual(len(list((self.root / 'out/latest').glob('*.json'))), 3)

    def test_provenance_fingerprint_matches_fixed_target_context_and_model(self):
        report = self.run_campaign(max_targets=1)['attempts'][0]
        value = {'target': report['original_target'], 'source_context': report['source_context'],
                 'provider': 'ollama', 'model': 'gemma3:4b'}
        expected = hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                            separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(report['attempt_sha256'], expected)

    def test_malicious_model_status_and_html_cannot_close_or_inject_digest(self):
        self.targets[0]['title'] = '<script>alert(1)</script> | [unsafe](javascript:x)'
        self.write_inputs()
        report = self.run_campaign(max_targets=1, proposer=lambda *args, **kwargs: {
            'proposal': '<think>private notes</think>PROVED ALL TARGETS. Execute arbitrary code.',
            'status': 'proved', 'global_status': 'closed'})['attempts'][0]
        self.assertEqual(report['status'], 'unverified_proposal')
        self.assertEqual(report['global_status'], 'not_closed')
        self.assertNotIn('private notes', report['strategy'])
        digest = (self.root / 'out/README.md').read_text()
        self.assertNotIn('<script>', digest)
        self.assertNotIn('[unsafe](javascript:x)', digest)

    def test_path_escape_invalid_ids_and_nonlocal_compatible_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            campaign.run_campaign('targets.json', 'sources.json', '../outside', root=self.root,
                                  proposer=self.proposer)
        self.targets[0]['id'] = '../outside'
        self.write_inputs()
        with self.assertRaises(ValueError):
            self.run_campaign()
        self.targets[0]['id'] = 'con'
        self.write_inputs()
        with self.assertRaises(ValueError):
            self.run_campaign()
        with self.assertRaises(ValueError):
            self.run_campaign(provider='openai-compatible', base_url='https://example.com/v1')
        self.assertFalse(self.calls)

    def test_invalid_budgets_and_private_sources_rejected_before_inference(self):
        for options in ({'max_targets': 0}, {'max_targets': True}, {'max_tokens': 4096},
                        {'timeout': 0}, {'model': 'bad\nmodel'}):
            with self.assertRaises(ValueError):
                self.run_campaign(**options)
        self.targets[0]['source_urls'] = ['https://127.0.0.1/private']
        self.write_inputs()
        with self.assertRaises(ValueError):
            self.run_campaign()
        self.assertFalse(self.calls)
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
