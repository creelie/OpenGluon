"""Audit explicitly formalized source-linked claims; never infer a paper error.

Source excerpts and their correspondence with mathematical tasks remain unreviewed.
Exact evidence concerns only the submitted formal task and its stated domain.
"""

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys
import urllib.parse

from . import lab, number_theory
from .radar import markdown_text, safe_link, utc_now

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 2_000_000


def read_json(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError('Audit input exceeds the 2 MB file limit')
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def source_url(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 2000:
        raise ValueError('Each claim requires a source URL')
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != 'https' or parsed.hostname not in {'arxiv.org', 'github.com'}
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or any(ord(char) < 32 for char in value)):
        raise ValueError('Claim sources must be public arXiv or GitHub HTTPS URLs')
    if parsed.hostname == 'arxiv.org' and not parsed.path.startswith(('/abs/', '/pdf/')):
        raise ValueError('Use the original arXiv paper permalink')
    if parsed.hostname == 'github.com' and len(parsed.path.strip('/').split('/')) < 2:
        raise ValueError('Use a GitHub repository/file permalink')
    return value


def load_manifest(path):
    path = Path(path).resolve()
    manifest, manifest_hash = read_json(path)
    if (not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int
            or manifest['schema_version'] != 1):
        raise ValueError('Audit manifest requires schema_version 1')
    claims = manifest.get('claims')
    if not isinstance(claims, list) or not 1 <= len(claims) <= 20:
        raise ValueError('Audit manifest requires 1..20 explicitly formalized claims')
    if 'tutorial' in manifest and type(manifest['tutorial']) is not bool:
        raise ValueError('tutorial must be a boolean')
    loaded, identities = [], set()
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', claim['id']):
            raise ValueError('Use a safe claim ID containing letters, numbers, underscores or hyphens')
        identity = claim['id'].casefold()
        if identity == 'audit' or re.fullmatch(r'(?:con|prn|aux|nul|com[1-9]|lpt[1-9])', identity):
            raise ValueError('Claim ID conflicts with a reserved output filename')
        if identity in identities:
            raise ValueError('Duplicate audit claim ID')
        identities.add(identity)
        source_url(claim.get('source_url'))
        for field, limit in (('source_location', 500), ('source_excerpt', 4000), ('formalization_note', 4000)):
            if not isinstance(claim.get(field), str) or not claim[field].strip() or len(claim[field]) > limit:
                raise ValueError('Each claim requires bounded nonempty ' + field)
        if claim.get('backend') not in ('polynomial', 'modular'):
            raise ValueError('Supported audit backends are polynomial and modular')
        relative = claim.get('task')
        if not isinstance(relative, str) or not relative or len(relative) > 500:
            raise ValueError('Each claim requires a local task file')
        task_path = (path.parent / relative).resolve()
        if Path(relative).is_absolute() or not task_path.is_relative_to(path.parent) or task_path == path:
            raise ValueError('Task paths must stay beneath the manifest directory, including resolved symlinks')
        task, task_hash = read_json(task_path)
        (lab.validate_task if claim['backend'] == 'polynomial' else number_theory.validate)(task)
        loaded.append((copy.deepcopy(claim), task, task_hash))
    return manifest, manifest_hash, loaded


def proposed_correction(task, evidence):
    """Try one exact constant shift; retain a proposal only with scoped evidence."""
    proposal = {'kind': 'revise_inequality_or_domain', 'status': 'requires_human_review',
                'scope': 'A verified negative witness refutes only the supplied nonnegativity task. No correction to the original source has been established.'}
    if evidence.get('kind') != 'exact_counterexample':
        return proposal
    shift = -Fraction(evidence['value'])
    corrected = copy.deepcopy(task)
    corrected.pop('certificate', None)
    corrected['title'] = 'Proposed constant-shift correction to the formal task'
    corrected['polynomial'].append({'coefficient': str(shift), 'powers': [0] * len(task['variables'])})
    try:
        candidate = lab.solve_task(corrected)
        checked = lab.verify_report(candidate)
        if candidate['status'] in {'exact_sos_verified', 'exact_univariate_verified', 'bounded_verified'} and checked['valid']:
            return {'kind': 'add_constant_to_polynomial', 'status': 'formal_proposal_verified_source_correspondence_unreviewed',
                    'added_constant': str(shift), 'scope': candidate['scope'],
                    'relationship': 'This proves a different explicitly stated inequality. Whether it is a relevant correction to the source remains unreviewed.',
                    'evidence_report': candidate, 'independent_verification': checked}
    except (ValueError, TypeError, KeyError):
        pass
    return proposal


def audit_manifest(path, now=None):
    manifest, manifest_hash, loaded = load_manifest(path)
    findings = []
    for claim, task, task_hash in loaded:
        backend = claim['backend']
        report = lab.solve_task(task) if backend == 'polynomial' else number_theory.solve(task)
        checked = lab.verify_report(report) if backend == 'polynomial' else number_theory.verify(report)
        if not checked['valid']:
            raise ValueError('Independent checking failed for claim ' + claim['id'])
        solver_status = report['status']
        result = 'inconclusive'
        if solver_status in {'counterexample_verified', 'exact_univariate_refuted'}:
            result = 'formal_claim_refuted'
        elif solver_status in {'exact_sos_verified', 'exact_univariate_verified', 'bounded_verified', 'modular_obstruction_verified'}:
            result = 'formal_claim_verified'
        finding = dict(claim, status=result, task_file_sha256=task_hash,
                       source_excerpt_sha256=hashlib.sha256(claim['source_excerpt'].encode('utf-8')).hexdigest(),
                       source_claim_requires_review=True, source_correspondence='unreviewed',
                       source_correspondence_scope='The supplied excerpt has not been retrieved or checked for faithful correspondence to this formal task. This result does not establish an error in the paper.',
                       formal_statement_kind='polynomial_nonnegative_on_task_domain' if backend == 'polynomial' else 'integer_polynomial_has_no_integer_zero',
                       scope=report['scope'], evidence_report=report, independent_verification=checked,
                       proposed_correction=proposed_correction(task, report['evidence']) if result == 'formal_claim_refuted' else None)
        findings.append(finding)
    return {'schema_version': 1, 'generated_at_utc': now or utc_now(),
            'tutorial': manifest.get('tutorial', False), 'manifest_sha256': manifest_hash,
            'scope': 'Audit of supplied formalizations only. Source correspondence is unreviewed; no original paper is automatically accused, corrected or published.',
            'summary': {status: sum(item['status'] == status for item in findings) for status in ('formal_claim_verified', 'formal_claim_refuted', 'inconclusive')},
            'claims': findings}


def render_report(report):
    label = 'Synthetic tutorial claim audit' if report['tutorial'] else 'Formalized claim audit'
    lines = ['# ' + label, '',
             'Every result concerns a submitted JSON statement and its stated domain. Source correspondence remains **unreviewed**. A negative witness is not, by itself, evidence that the cited paper is wrong.', '',
             '| Claim | Formal result | Source correspondence |', '| --- | --- | --- |']
    for claim in report['claims']:
        lines.append('| ' + markdown_text(claim['id']) + ' | ' + claim['status'] + ' | unreviewed |')
    for claim in report['claims']:
        lines.extend(['', '## ' + markdown_text(claim['id']), '',
                      safe_link('Original source', claim['source_url']) + ' · ' + markdown_text(claim['source_location'], 500), '',
                      '**Supplied source excerpt** (JSON preserves the exact original string and its SHA-256):', ''])
        lines.extend('> ' + markdown_text(line, 4000) for line in claim['source_excerpt'].splitlines())
        lines.extend(['', '**Formalization note:** ' + markdown_text(claim['formalization_note'], 4000), '',
                      '**Formal statement kind:** `' + claim['formal_statement_kind'] + '`', '',
                      '**Result:** `' + claim['status'] + '`', '',
                      '**Evidence scope:** ' + markdown_text(claim['scope'], 1000), '',
                      '[Exact task, evidence and independent check](' + claim['id'] + '.json)', '',
                      '**Source correspondence:** unreviewed; human literature and formalization review is required.'])
        proposal = claim.get('proposed_correction')
        if proposal:
            lines.extend(['', '**Proposed correction:** `' + proposal['kind'] + '` · `' + proposal['status'] + '`', '',
                          markdown_text(proposal['scope'], 1000)])
            if proposal.get('relationship'):
                lines.extend(['', markdown_text(proposal['relationship'], 1000)])
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/audits')
    args = parser.parse_args(argv)
    try:
        report = audit_manifest(args.manifest)
        payloads = {'audit.json': json.dumps(report, indent=2, ensure_ascii=True) + '\n', 'AUDIT.md': render_report(report)}
        payloads.update({claim['id'] + '.json': json.dumps(claim, indent=2, ensure_ascii=True) + '\n' for claim in report['claims']})
        args.output.mkdir(parents=True, exist_ok=True)
        for filename, content in payloads.items():
            (args.output / filename).write_text(content, encoding='utf-8')
        print(json.dumps({'tutorial': report['tutorial'], 'summary': report['summary'], 'output': str(args.output)}, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        print('Claim audit: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
