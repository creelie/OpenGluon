"""Run registered, local mathematical tasks reproducibly without network access."""

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import urllib.parse

from .lab import MAX_FILE_BYTES, solve_task, verify_report

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ('exact_sos_verified', 'exact_univariate_verified', 'exact_univariate_refuted',
            'bounded_verified', 'counterexample_verified', 'inconclusive', 'error')


def _inside(path, root, name):
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError(f'{name} must stay inside the workspace') from None
    if resolved == root:
        raise ValueError(f'{name} must be a workspace child')
    return resolved


def _read_json(path, limit):
    if not path.is_file():
        raise ValueError('registered JSON file does not exist or is not a regular file')
    if path.stat().st_size > limit:
        raise ValueError('registered JSON file exceeds its size limit')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (UnicodeError, RecursionError):
        raise ValueError('registered JSON file has invalid encoding or excessive nesting') from None


def _manifest(value):
    if (not isinstance(value, dict) or type(value.get('schema_version')) is not int
            or value['schema_version'] != 1):
        raise ValueError('experiment manifest schema_version must be 1')
    tasks = value.get('tasks')
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 32:
        raise ValueError('register between 1 and 32 local mathematical tasks')
    entries, seen = [], set()
    for item in tasks:
        if not isinstance(item, dict):
            raise ValueError('each registered task must be an object')
        task_id = item.get('id')
        if not isinstance(task_id, str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,63}', task_id):
            raise ValueError('task ids must use 1..64 lowercase letters, digits, underscores or hyphens')
        if task_id in seen or task_id in {'index', 'readme'}:
            raise ValueError('task ids must be unique and cannot be index or readme')
        seen.add(task_id)
        path = item.get('path')
        if not isinstance(path, str) or not path or len(path) > 512:
            raise ValueError('each task requires a local JSON path of at most 512 characters')
        tutorial = item.get('tutorial', False)
        if type(tutorial) is not bool:
            raise ValueError('tutorial must be a boolean')
        normalized = {'id': task_id, 'path': path, 'tutorial': tutorial}
        if 'source_url' in item:
            url = item['source_url']
            if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 for c in url):
                raise ValueError('source_url must be a valid HTTPS reference')
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError('source_url must be an HTTPS reference without credentials')
            normalized['source_url'] = url
        if 'reference' in item:
            if not isinstance(item['reference'], str) or len(item['reference']) > 500:
                raise ValueError('reference must be text of at most 500 characters')
            normalized['reference'] = item['reference']
        entries.append(normalized)
    return entries


def _encoded(value):
    return json.dumps(value, indent=2, ensure_ascii=True) + '\n'


def _text(value):
    value = html.escape(' '.join(str(value).split()), quote=True)
    for character in '\\|[]*_`':
        value = value.replace(character, '\\' + character)
    return value


def render_digest(index):
    lines = ['# Anaxia registered experiments', '',
             'Deterministic results from explicitly registered, local, formalized tasks. '
             'Discovery does not automatically translate or solve an arXiv conjecture.', '',
             '| Task | Type | Result | Evidence |', '| --- | --- | --- | --- |']
    for item in index['experiments']:
        label = 'Tutorial example' if item['tutorial'] else 'Registered research task'
        lines.append(f"| {_text(item['id'])} | {label} | `{item['status']}` | [JSON]({item['report']}) |")
    lines.extend(['', 'Global nonnegativity can follow from an exact rational SOS identity or a univariate Sturm calculation. '
                  'Finite integer checks retain their finite scope. Counterexamples are evaluated exactly. '
                  'An inconclusive result makes no proof claim.', ''])
    for item in index['experiments']:
        if 'reference' in item or 'source_url' in item:
            reference = _text(item.get('reference', 'Source reference'))
            if 'source_url' in item:
                url = item['source_url'].replace('<', '%3C').replace('>', '%3E').replace('\\', '%5C')
                reference += f' — [source](<{url}>)'
            lines.append(f"- **{_text(item['id'])}**: {reference}")
    return '\n'.join(lines) + '\n'


def run_manifest(manifest_path, output_path, *, root=ROOT):
    """Finish every registered task and return a deterministic index of outcomes."""
    root = Path(root).resolve()
    manifest_path = _inside(root / manifest_path, root, 'manifest')
    output = _inside(root / output_path, root, 'output directory')
    entries = _manifest(_read_json(manifest_path, 256_000))
    # Check every destination before solving or writing any task. A symlink in
    # a pre-existing report directory must not redirect writes elsewhere.
    destinations = [output / (entry['id'] + '.json') for entry in entries]
    destinations += [output / 'index.json', output / 'README.md']
    for target in destinations:
        resolved = _inside(target, root, 'report destination')
        if resolved.parent != output:
            raise ValueError('report destinations must be direct output-directory children')
        if target.is_symlink():
            raise ValueError('report destinations cannot be symbolic links')
    if manifest_path in destinations:
        raise ValueError('experiment output cannot overwrite its manifest')
    for entry in entries:
        try:
            source = _inside(root / entry['path'], root, 'task path')
        except ValueError:
            # Record this task's path error below; other valid tasks still run.
            continue
        if source in destinations:
            raise ValueError('a task input cannot also be an experiment output')
    output.mkdir(parents=True, exist_ok=True)
    outcomes = []
    for entry in entries:
        task_id = entry['id']
        try:
            source = _inside(root / entry['path'], root, 'task path')
            if source.suffix.lower() != '.json':
                raise ValueError('registered tasks must be JSON files')
            report = solve_task(_read_json(source, MAX_FILE_BYTES))
            verification = verify_report(report)
            if not verification['valid']:
                raise ValueError('independent mathematical verification failed')
            report['experiment'] = dict(entry)
        except (ValueError, OSError) as error:
            # OSError text may contain machine-specific paths: keep runs portable.
            reason = str(error) if isinstance(error, ValueError) else 'registered JSON file could not be read'
            report = {'schema_version': 1, 'status': 'error', 'experiment': dict(entry), 'error': reason}
        encoded = _encoded(report)
        report_name = task_id + '.json'
        # Write canonical UTF-8/LF bytes so hashes match on Windows and Linux.
        (output / report_name).write_bytes(encoded.encode('utf-8'))
        outcome = dict(entry, status=report['status'], report=report_name,
                       report_sha256=hashlib.sha256(encoded.encode()).hexdigest())
        if 'task_sha256' in report:
            outcome['task_sha256'] = report['task_sha256']
        if report['status'] == 'error':
            outcome['error'] = report['error']
        outcomes.append(outcome)
    index = {'schema_version': 1, 'engine': 'anaxia-registered-experiments/1',
             'scope': 'Only explicitly registered, formalized local tasks are run. Tutorial examples are not new arXiv results.',
             'counts': {status: sum(item['status'] == status for item in outcomes) for status in STATUSES},
             'experiments': outcomes}
    (output / 'index.json').write_bytes(_encoded(index).encode('utf-8'))
    (output / 'README.md').write_bytes(render_digest(index).encode('utf-8'))
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', type=Path, default=Path('config/research-tasks.json'))
    parser.add_argument('--output', type=Path, default=Path('data/experiments'))
    args = parser.parse_args(argv)
    try:
        index = run_manifest(args.tasks, args.output)
    except (ValueError, OSError) as error:
        print(f'Experiment error: {error}', file=sys.stderr)
        return 2
    print(json.dumps({'counts': index['counts'], 'output': str(args.output)}, indent=2))
    return 2 if index['counts']['error'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
