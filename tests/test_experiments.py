import contextlib
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from anaxia import experiments
from anaxia.lab import verify_report


def polynomial(domain=None):
    return {'schema_version': 1, 'kind': 'polynomial_nonnegative', 'variables': ['x'],
            'polynomial': [{'coefficient': '1', 'powers': [2]}, {'coefficient': '-1', 'powers': [1]}],
            'domain': domain or {'kind': 'real'}}


class RegisteredExperimentsTests(unittest.TestCase):
    def prepare(self, root, tasks=None):
        (root / 'task.json').write_text(json.dumps(polynomial()), encoding='utf-8')
        (root / 'manifest.json').write_text(json.dumps({'schema_version': 1, 'tasks': tasks or [
            {'id': 'sample', 'path': 'task.json', 'tutorial': True}]}), encoding='utf-8')

    def test_inconclusive_is_recorded_and_every_output_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            index = experiments.run_manifest('manifest.json', 'reports', root=root)
            self.assertEqual(index['counts']['inconclusive'], 1)
            self.assertTrue(index['experiments'][0]['tutorial'])
            self.assertEqual(index['experiments'][0]['report_sha256'],
                             hashlib.sha256((root / 'reports/sample.json').read_bytes()).hexdigest())
            before = {path.name: path.read_bytes() for path in (root / 'reports').iterdir()}
            experiments.run_manifest('manifest.json', 'reports', root=root)
            self.assertEqual(before, {path.name: path.read_bytes() for path in (root / 'reports').iterdir()})
            self.assertTrue(verify_report(json.loads((root / 'reports/sample.json').read_text()))['valid'])

    def test_bad_task_does_not_stop_other_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, [{'id': 'missing', 'path': 'missing.json'},
                                {'id': 'good', 'path': 'task.json'}])
            index = experiments.run_manifest('manifest.json', 'reports', root=root)
            self.assertEqual(index['counts']['error'], 1)
            self.assertEqual(index['counts']['inconclusive'], 1)
            self.assertTrue((root / 'reports/good.json').exists())
            self.assertEqual(json.loads((root / 'reports/missing.json').read_text())['status'], 'error')

    def test_workspace_escape_is_a_visible_task_error_and_output_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, [{'id': 'escape', 'path': '../outside.json'}, {'id': 'safe', 'path': 'task.json'}])
            index = experiments.run_manifest('manifest.json', 'reports', root=root)
            self.assertEqual(index['counts']['error'], 1)
            self.assertEqual(index['counts']['inconclusive'], 1)
            with self.assertRaisesRegex(ValueError, 'workspace'):
                experiments.run_manifest('manifest.json', '../outside-output', root=root)

    def test_duplicate_reserved_and_over_budget_task_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for tasks in ([{'id': '../escape', 'path': 'task.json'}],
                          [{'id': 'index', 'path': 'task.json'}],
                          [{'id': 'same', 'path': 'task.json'}] * 2,
                          [{'id': f'task{i}', 'path': 'task.json'} for i in range(33)]):
                with self.subTest(tasks=tasks):
                    self.prepare(root, tasks)
                    with self.assertRaises(ValueError):
                        experiments.run_manifest('manifest.json', 'reports', root=root)
                    self.assertFalse((root / 'reports').exists())

    def test_input_cannot_be_overwritten_by_its_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, [{'id': 'task', 'path': 'reports/task.json'}])
            (root / 'reports').mkdir()
            original = json.dumps(polynomial())
            (root / 'reports/task.json').write_text(original)
            with self.assertRaisesRegex(ValueError, 'input'):
                experiments.run_manifest('manifest.json', 'reports', root=root)
            self.assertEqual((root / 'reports/task.json').read_text(), original)

    def test_references_are_rendered_as_data_without_markdown_injection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, [{'id': 'sample', 'path': 'task.json', 'reference': '<script> | [bad](x)',
                                'source_url': 'https://arxiv.org/abs/1234.5678'}])
            experiments.run_manifest('manifest.json', 'reports', root=root)
            digest = (root / 'reports/README.md').read_text()
            self.assertNotIn('<script>', digest)
            self.assertIn('\\|', digest)
            self.assertIn('https://arxiv.org/abs/1234.5678', digest)

    def test_built_in_manifest_is_explicitly_tutorial_and_verifies(self):
        manifest = json.loads((experiments.ROOT / 'config/research-tasks.json').read_text())
        self.assertEqual(len(manifest['tasks']), 4)
        self.assertTrue(all(item['tutorial'] is True for item in manifest['tasks']))

    def test_cli_returns_nonzero_for_task_errors_but_not_for_inconclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            real_run = experiments.run_manifest
            def run(*args):
                return real_run(*args, root=root)
            with patch.object(experiments, 'run_manifest', side_effect=run), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(experiments.main(['--tasks', 'manifest.json', '--output', 'reports']), 0)
                self.prepare(root, [{'id': 'missing', 'path': 'missing.json'}])
                self.assertEqual(experiments.main(['--tasks', 'manifest.json', '--output', 'reports']), 2)


if __name__ == '__main__':
    unittest.main()
