"""Bounded public proof proposals and critique, gated by exact verification."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

from . import lab, providers

MAX_ROUNDS = 4


def _statement(task):
    # Certificate data may change; the mathematical question may not.
    return {key: copy.deepcopy(task[key]) for key in
            ('schema_version', 'kind', 'variables', 'polynomial', 'domain')}


def statement_digest(task):
    return hashlib.sha256(json.dumps(_statement(lab.validate_task(task)), sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def extract_candidate(text):
    """Parse only public strategy and bounded evidence data; never executable text."""
    if not isinstance(text, str) or len(text.encode()) > providers.MAX_INPUT_BYTES:
        raise ValueError('Candidate exceeds its JSON input budget')
    text = providers._public_text(text)
    fenced = re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if fenced:
        text = fenced.group(1)
    try:
        value = json.loads(text)
    except (ValueError, RecursionError):
        raise ValueError('Model did not return a valid candidate JSON object') from None
    if not isinstance(value, dict) or set(value) - {'strategy', 'certificate', 'counterexample'}:
        raise ValueError('Candidate contains unsupported fields; replacement tasks and claimed proof status are rejected')
    strategy = value.get('strategy', '')
    if not isinstance(strategy, str) or len(strategy) > 1200:
        raise ValueError('Public strategy must be text of at most 1200 characters')
    return {'strategy': providers._public_text(strategy), 'certificate': value.get('certificate'),
            'counterexample': value.get('counterexample')}


def verify_candidate(original_task, candidate):
    """Bind proposed evidence to the original polynomial and domain exactly."""
    original = lab.validate_task(original_task)
    if not isinstance(candidate, dict) or set(candidate) - {'strategy', 'certificate', 'counterexample'}:
        raise ValueError('Candidate must contain only public strategy and supported evidence')
    if candidate.get('certificate') is not None:
        certificate = candidate['certificate']
        if not lab.verify_sos(original['polynomial'], certificate, len(original['variables'])):
            raise ValueError('Proposed SOS is not identical to the original polynomial')
        task = copy.deepcopy(original)
        task['certificate'] = copy.deepcopy(certificate)
        report = lab.solve_task(task)
    elif candidate.get('counterexample') is not None:
        witness = candidate['counterexample']
        if not isinstance(witness, dict) or set(witness) != {'point', 'value'}:
            raise ValueError('Counterexample needs exactly point and value')
        report = {'schema_version': 1, 'engine': 'anaxia-exact-lab/1', 'task': original,
                  'task_sha256': lab._task_digest(original), 'status': 'counterexample_verified',
                  'scope': lab.SCOPES['counterexample_verified'],
                  'evidence': dict(witness, kind='exact_counterexample'),
                  'stages': [{'role': 'verifier', 'finding': 'Recheck the proposed witness by exact evaluation.'}]}
    else:
        return None
    if _statement(report['task']) != _statement(original):
        raise ValueError('Candidate attempted to change the original mathematical statement')
    checked = lab.verify_report(report)
    if not checked['valid']:
        raise ValueError(checked['reason'])
    return report


def reason_task(task, model, *, provider='ollama', base_url=None, rounds=2,
                max_tokens=2048, timeout=120, api_key=None, opener=None, proposer=None):
    """Run at most two inference calls per round, with immutable proof criteria."""
    if type(rounds) is not int or not 1 <= rounds <= MAX_ROUNDS:
        raise ValueError('rounds must be between 1 and 4')
    if type(max_tokens) is not int or not 1 <= max_tokens <= 8192:
        raise ValueError('max_tokens must be between 1 and 8192')
    if type(timeout) not in (int, float) or not 1 <= timeout <= 300:
        raise ValueError('timeout must be between 1 and 300 seconds')
    providers.endpoint(provider, base_url)
    # Validate arithmetic before any inference request. External free-text papers
    # need a human-authored task formalization first.
    original = lab.validate_task(task)
    baseline = lab.solve_task(original)
    if not lab.verify_report(baseline)['valid']:
        raise ValueError('Deterministic baseline failed verification')
    generate = proposer or providers.propose
    call_options = {'provider': provider, 'base_url': base_url, 'max_tokens': max_tokens,
                    'timeout': timeout, 'api_key': api_key, 'opener': opener}
    result = {'schema_version': 1, 'engine': 'anaxia-proof-dialogue/1',
              'provider': provider, 'model': model, 'original_task': original,
              'statement_sha256': statement_digest(original),
              'round_limit': rounds, 'max_model_calls': 2 * rounds, 'model_calls': 0,
              'max_tokens_per_call': max_tokens, 'timeout_seconds_per_call': timeout,
              'rounds': [], 'baseline_result': baseline, 'verified_result': baseline,
              'model_evidence_verified': False,
              'scope': 'Public model strategies are unverified advice; only the attached exact checker result determines mathematical status.'}
    feedback = None
    for index in range(rounds):
        payload = {'original_task': copy.deepcopy(original), 'previous_public_feedback': feedback}
        proposed = generate(payload, model, purpose='certificate', **call_options)
        result['model_calls'] += 1
        record = {'round': index + 1, 'strategy': '', 'evidence_check': {'valid': False, 'reason': 'No candidate evidence supplied'}}
        candidate = None
        try:
            candidate = extract_candidate(proposed['proposal'])
            record['strategy'] = candidate['strategy']
            verified = verify_candidate(original, candidate)
            if verified is not None:
                result['verified_result'] = verified
                result['model_evidence_verified'] = True
                record['evidence_check'] = {'valid': True, 'status': verified['status'],
                                            'reason': lab.verify_report(verified)['reason']}
        except (ValueError, TypeError, KeyError) as error:
            record['evidence_check'] = {'valid': False, 'reason': str(error)}
        critique_payload = {'original_task': copy.deepcopy(original), 'candidate': candidate,
                            'exact_check': record['evidence_check']}
        criticism = generate(critique_payload, model, purpose='critique', **call_options)
        result['model_calls'] += 1
        record['critique'] = providers._public_text(criticism['proposal'])[:1200]
        result['rounds'].append(record)
        feedback = copy.deepcopy(record)
        if result['verified_result']['status'] in {'exact_sos_verified', 'counterexample_verified'}:
            break
    verified = result['verified_result']
    if (statement_digest(verified['task']) != result['statement_sha256']
            or not lab.verify_report(verified)['valid']):
        raise ValueError('Final evidence does not verify the original mathematical statement')
    result['status'] = verified['status']
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', type=Path)
    providers.add_provider_arguments(parser, default='ollama')
    parser.add_argument('--rounds', type=int, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        task = lab._read_json(args.task)
        result = reason_task(task, args.model, provider=args.provider, base_url=args.base_url,
                             rounds=args.rounds, max_tokens=args.max_tokens, timeout=args.timeout)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'status': result['status'], 'model_calls': result['model_calls'],
                          'model_evidence_verified': result['model_evidence_verified'],
                          'output': str(args.output)}, indent=2))
        return 3 if result['status'] == 'inconclusive' else 0
    except (ValueError, OSError, RecursionError) as error:
        print(f'Reasoning error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
