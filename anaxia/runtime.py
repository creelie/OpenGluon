"""Start or inspect an explicitly configured loopback-only local CPU runtime."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

from .providers import _NoRedirect

ROOT = Path(__file__).resolve().parents[1]


def load_config(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 64_000:
        raise ValueError('Runtime config must be a JSON file below 64 KB')
    try:
        raw = json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError, UnicodeError, RecursionError):
        raise ValueError('Runtime config is invalid JSON') from None
    if (not isinstance(raw, dict) or type(raw.get('schema_version')) is not int
            or raw['schema_version'] != 1):
        raise ValueError('Runtime config requires schema_version 1')
    if raw.get('host', '127.0.0.1') != '127.0.0.1':
        raise ValueError('Runtime host must be 127.0.0.1')
    for key, default, low, high in (('port', 18081, 1024, 65535), ('context', 2048, 128, 8192),
                                   ('threads', 4, 1, 32), ('startup_timeout', 30, 1, 30)):
        value = raw.get(key, default)
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f'Runtime {key} must be an integer between {low} and {high}')
        raw[key] = value
    alias = raw.get('alias')
    if not isinstance(alias, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}', alias):
        raise ValueError('Runtime alias must be a short model identifier')
    for key in ('binary', 'model'):
        value = raw.get(key)
        if not isinstance(value, str) or not value or '\x00' in value:
            raise ValueError(f'Runtime config needs an explicit {key} file path')
        location = Path(value).expanduser()
        if not location.is_absolute():
            location = path.resolve().parent / location
        location = location.resolve()
        if not location.is_file():
            raise ValueError(f'Configured runtime {key} is not a regular file')
        if key == 'binary' and os.name == 'nt' and location.suffix.lower() != '.exe':
            raise ValueError('Windows runtime binary must be an .exe file')
        raw[key] = str(location)
    expected = raw.get('binary_sha256')
    if expected is not None:
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('binary_sha256 must be a lowercase SHA-256 checksum')
        with Path(raw['binary']).open('rb') as stream:
            checksum = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                checksum.update(chunk)
            actual = checksum.hexdigest()
        if actual != expected:
            raise ValueError('Configured runtime binary checksum mismatch')
    raw['host'] = '127.0.0.1'
    return raw


def _read_url(url):
    opener = urllib.request.build_opener(_NoRedirect(), urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=2) as response:
        data = response.read(64_001)
    if len(data) > 64_000:
        raise ValueError('Local runtime status response exceeded its limit')
    return json.loads(data)


def probe(config):
    """The expected alias and health must both match before a server is reused."""
    base = f"http://127.0.0.1:{config['port']}"
    try:
        health = _read_url(base + '/health')
        models = _read_url(base + '/v1/models')
        entries = models.get('data') if isinstance(models, dict) else None
        matched = (isinstance(entries, list) and any(isinstance(item, dict)
                   and item.get('id') == config['alias'] for item in entries))
        if not isinstance(health, dict) or health.get('status') != 'ok' or not matched:
            return {'status': 'mismatch', 'ready': False, 'reason': 'Port responds but health or model alias does not match'}
        return {'status': 'ready', 'ready': True, 'provider': 'openai-compatible',
                'base_url': base + '/v1', 'model': config['alias']}
    except urllib.error.HTTPError as error:
        code = error.code
        error.close()
        return {'status': 'loading' if code == 503 else 'mismatch', 'ready': False,
                'reason': f'Local runtime returned HTTP {code}'}
    except (urllib.error.URLError, OSError):
        return {'status': 'unreachable', 'ready': False, 'reason': 'Expected local server is not reachable'}
    except (ValueError, TypeError, RecursionError):
        return {'status': 'mismatch', 'ready': False, 'reason': 'Local runtime returned invalid status data'}


def ensure(config, *, root=ROOT):
    current = probe(config)
    if current['ready']:
        return dict(current, started=False)
    if current['status'] != 'unreachable':
        raise ValueError('Expected runtime is not ready; another server may occupy its port')
    root = Path(root).resolve()
    local = (root / 'data/local').resolve()
    if not local.is_relative_to(root):
        raise ValueError('Runtime logs must stay inside workspace data/local')
    local.mkdir(parents=True, exist_ok=True)
    arguments = [config['binary'], '-m', config['model'], '--alias', config['alias'],
                 '--host', '127.0.0.1', '--port', str(config['port']), '--ctx-size', str(config['context']),
                 '--threads', str(config['threads']), '--threads-batch', str(config['threads']),
                 '--gpu-layers', '0', '--parallel', '1', '--batch-size', '128', '--ubatch-size', '128',
                 '--no-webui', '--offline']
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith('LLAMA_') and key not in
                   {'ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'MOONSHOT_API_KEY', 'OPENAI_COMPATIBLE_API_KEY', 'HF_TOKEN'}}
    stdout_path, stderr_path = local / 'runtime.stdout.log', local / 'runtime.stderr.log'
    for output in (stdout_path, stderr_path, local / 'runtime-state.json'):
        if output.is_symlink() or not output.resolve().is_relative_to(local):
            raise ValueError('Runtime log destinations cannot leave data/local')
    with stdout_path.open('ab') as stdout, stderr_path.open('ab') as stderr:
        process = subprocess.Popen(arguments, cwd=str(Path(config['binary']).parent),
                                   stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL,
                                   shell=False, env=environment,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    (local / 'runtime-state.json').write_text(json.dumps({
        'pid': process.pid, 'binary': config['binary'], 'alias': config['alias'],
        'port': config['port'], 'scope': 'Only a PID started by this command; no stop command is provided.'}, indent=2) + '\n',
        encoding='utf-8', newline='\n')
    deadline = time.monotonic() + config['startup_timeout']
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise ValueError('Configured local runtime exited during startup; see data/local/runtime.stderr.log')
        current = probe(config)
        if current['ready']:
            return dict(current, started=True, pid=process.pid)
        if current['status'] == 'mismatch':
            raise ValueError('Started runtime failed the expected model-alias check')
        time.sleep(0.25)
    raise ValueError('Local runtime startup timed out; inspect local logs before retrying')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('ensure', 'status'))
    parser.add_argument('--config', type=Path, default=Path('data/local/runtime.json'))
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = ensure(config) if args.command == 'ensure' else probe(config)
        print(json.dumps(result, indent=2))
        return 0 if result['ready'] else 3
    except (ValueError, OSError) as error:
        print(f'Runtime error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
