import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from anaxia import runtime


class LocalRuntimeTests(unittest.TestCase):
    def config(self, root):
        binary = root / 'llama-server.exe'
        model = root / 'existing.gguf'
        binary.write_bytes(b'fixture executable; never run')
        model.write_bytes(b'GGUF fixture; never load')
        data = {'schema_version': 1, 'binary': str(binary), 'model': str(model),
                'host': '127.0.0.1', 'port': 18081, 'alias': 'test-model',
                'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
        path = root / 'runtime.json'
        path.write_text(json.dumps(data))
        return path, data

    def test_configuration_checks_files_checksum_and_loopback(self):
        with tempfile.TemporaryDirectory() as directory:
            path, data = self.config(Path(directory))
            self.assertEqual(runtime.load_config(path)['threads'], 4)
            for update in ({'host': '0.0.0.0'}, {'binary_sha256': '0' * 64},
                           {'port': True}, {'context': 9000}, {'startup_timeout': 60},
                           {'model': 'missing.gguf'}, {'alias': 'bad;command'}):
                with self.subTest(update=update):
                    path.write_text(json.dumps(dict(data, **update)))
                    with self.assertRaises(ValueError):
                        runtime.load_config(path)

    def test_ready_expected_server_is_reused_without_launch(self):
        config = {'port': 18081, 'alias': 'test-model'}
        with patch.object(runtime, 'probe', return_value={'status': 'ready', 'ready': True}), \
                patch.object(runtime.subprocess, 'Popen') as launch:
            result = runtime.ensure(config)
        self.assertFalse(result['started'])
        launch.assert_not_called()

    def test_probe_requires_health_and_expected_alias(self):
        config = {'port': 18081, 'alias': 'test-model'}
        with patch.object(runtime, '_read_url', side_effect=[{'status': 'ok'}, {'data': [{'id': 'other-model'}]}]):
            self.assertEqual(runtime.probe(config)['status'], 'mismatch')
        with patch.object(runtime, '_read_url', side_effect=[{'status': 'ok'}, {'data': [{'id': 'test-model'}]}]):
            result = runtime.probe(config)
            self.assertTrue(result['ready'])
            self.assertEqual(result['base_url'], 'http://127.0.0.1:18081/v1')

    def test_wrong_server_is_not_replaced_or_terminated(self):
        with patch.object(runtime, 'probe', return_value={'status': 'mismatch', 'ready': False}), \
                patch.object(runtime.subprocess, 'Popen') as launch:
            with self.assertRaises(ValueError):
                runtime.ensure({'port': 18081, 'alias': 'test-model'})
            launch.assert_not_called()

    def test_launch_uses_fixed_argument_list_hidden_cpu_and_only_local_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, _ = self.config(root)
            config = runtime.load_config(path)
            process = Mock(pid=12345)
            process.poll.return_value = None
            with patch.object(runtime, 'probe', side_effect=[{'status': 'unreachable', 'ready': False},
                                                            {'status': 'ready', 'ready': True}]), \
                    patch.object(runtime.subprocess, 'Popen', return_value=process) as launch:
                result = runtime.ensure(config, root=root)
            self.assertTrue(result['started'])
            args, kwargs = launch.call_args
            argv = args[0]
            self.assertIsInstance(argv, list)
            self.assertEqual(argv[argv.index('--host') + 1], '127.0.0.1')
            self.assertEqual(argv[argv.index('--gpu-layers') + 1], '0')
            self.assertIn('--offline', argv)
            self.assertIn('--no-webui', argv)
            self.assertFalse(kwargs['shell'])
            self.assertNotIn('OPENAI_API_KEY', kwargs['env'])
            self.assertTrue((root / 'data/local/runtime-state.json').is_file())

    def test_failed_child_is_reported_without_claiming_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, _ = self.config(root)
            process = Mock(pid=12345)
            process.poll.return_value = 1
            with patch.object(runtime, 'probe', return_value={'status': 'unreachable', 'ready': False}), \
                    patch.object(runtime.subprocess, 'Popen', return_value=process):
                with self.assertRaisesRegex(ValueError, 'exited'):
                    runtime.ensure(runtime.load_config(path), root=root)


if __name__ == '__main__':
    unittest.main()
