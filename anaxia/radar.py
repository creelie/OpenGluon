"""Bounded public GitHub/arXiv metadata discovery; never executes discovered code.

Only explicitly signalled open-problem language in abstracts enters the review
queue. A candidate is a report about a paper, not a verified mathematical fact.
"""

import argparse
import copy
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- ANAXIA:RADAR:START -->'
END = '<!-- ANAXIA:RADAR:END -->'
ATOM = '{http://www.w3.org/2005/Atom}'
OPEN_SEARCH = '{http://a9.com/-/spec/opensearch/1.1/}'
OPEN_LANGUAGE = re.compile(
    r'\b(?:remains? open|remain unresolved|open (?:problem|conjecture|question)s?'
    r'|we conjecture|we formulate (?:a |the )?conjecture|conjecture that)\b', re.I)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def compact(value, limit=12000):
    return re.sub(r'\s+', ' ', str(value or '')).strip()[:limit]


class PublicClient:
    """One sequential request stream with strict hosts, sizes and time budgets."""

    def __init__(self):
        self.last_arxiv = None
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise urllib.error.HTTPError(req.full_url, code, 'API redirects are disabled', headers, fp)
        self.opener = urllib.request.build_opener(NoRedirect())

    def get(self, url):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in {'api.github.com', 'export.arxiv.org'}:
            raise ValueError('Only public GitHub and arXiv API URLs are accepted')
        arxiv = parsed.hostname == 'export.arxiv.org'
        if arxiv and self.last_arxiv is not None:
            time.sleep(max(0, 3.1 - (time.monotonic() - self.last_arxiv)))
        headers = {'User-Agent': 'Anaxia-Research-Radar/1.0 (public metadata; https://github.com/creelie/Anaxia)'}
        if not arxiv:
            headers.update({'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
            if token:
                headers['Authorization'] = 'Bearer ' + token
        try:
            with self.opener.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
                # Refuse unexpected redirect destinations before reading a body.
                if urllib.parse.urlsplit(response.geturl()).hostname != parsed.hostname:
                    raise ValueError('Unexpected API redirect')
                body = response.read(8_000_001)
                if len(body) > 8_000_000:
                    raise ValueError('API response exceeds 8 MB limit')
                return body
        finally:
            if arxiv:
                self.last_arxiv = time.monotonic()


def validate_config(config):
    if not isinstance(config, dict) or config.get('schema_version') != 1:
        raise ValueError('Research watch config requires schema_version 1')
    specs = []
    for provider in ('github', 'arxiv'):
        section = config.get(provider, {})
        if not isinstance(section, dict):
            raise ValueError('Each provider config must be an object')
        per_page = section.get('per_page', 30)
        pages = section.get('max_pages', 2)
        if type(per_page) is not int or not 1 <= per_page <= 100:
            raise ValueError('per_page must be between 1 and 100')
        if type(pages) is not int or not 1 <= pages <= 5:
            raise ValueError('max_pages must be between 1 and 5')
        owners = section.get('owners', []) if provider == 'github' else []
        queries = section.get('queries', [])
        if not isinstance(owners, list) or not isinstance(queries, list) or len(owners) + len(queries) > 12:
            raise ValueError('Use lists with at most 12 sources per provider')
        for owner in owners:
            if not isinstance(owner, str) or not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})', owner):
                raise ValueError('Invalid GitHub owner')
            owner_size = section.get('owner_per_page', per_page)
            owner_pages = section.get('owner_max_pages', pages)
            if type(owner_size) is not int or not 1 <= owner_size <= 100 or type(owner_pages) is not int or not 1 <= owner_pages <= 5:
                raise ValueError('Owner pagination requires 1..100 per page and 1..5 pages')
            specs.append({'key': 'github:owner:' + owner.lower(), 'provider': provider, 'kind': 'owner',
                          'query': owner, 'per_page': owner_size, 'max_pages': owner_pages})
        for query in queries:
            if not isinstance(query, str) or not query.strip() or len(query) > 256:
                raise ValueError('Queries must contain 1 to 256 characters')
            digest = hashlib.sha256(query.encode()).hexdigest()[:16]
            specs.append({'key': provider + ':query:' + digest, 'provider': provider, 'kind': 'query',
                          'query': query, 'per_page': per_page, 'max_pages': pages})
    if not specs:
        raise ValueError('At least one public research source is required')
    if len({spec['key'] for spec in specs}) != len(specs):
        raise ValueError('Duplicate research source')
    return specs


def github_repository(raw):
    if not isinstance(raw, dict) or raw.get('private') is True:
        return None
    name = raw.get('full_name', '')
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name):
        raise ValueError('Invalid repository name in GitHub response')
    number = raw.get('id')
    if type(number) is not int or number <= 0:
        raise ValueError('Missing numeric GitHub repository identity')
    topics = raw.get('topics') or []
    return {'id': 'github:' + str(number), 'provider': 'github', 'kind': 'repository',
            'name': name, 'url': 'https://github.com/' + name,
            'description': compact(raw.get('description'), 1200),
            'updated_at': compact(raw.get('updated_at'), 40),
            'pushed_at': compact(raw.get('pushed_at'), 40),
            'default_branch': compact(raw.get('default_branch'), 256),
            'stars': raw.get('stargazers_count', 0), 'archived': bool(raw.get('archived', False)),
            'fork': bool(raw.get('fork', False)),
            'topics': sorted(compact(x, 100) for x in topics[:30]) if isinstance(topics, list) else [],
            'license': compact((raw.get('license') or {}).get('spdx_id'), 100)}


def read_github(spec, fetch):
    entries, total, truncated, incomplete = [], None, False, False
    for page in range(1, spec['max_pages'] + 1):
        params = {'per_page': spec['per_page'], 'page': page, 'sort': 'updated', 'direction': 'desc'}
        if spec['kind'] == 'owner':
            path = '/users/' + spec['query'] + '/repos'
            params['type'] = 'owner'
        else:
            path = '/search/repositories'
            params.update({'q': spec['query'], 'order': 'desc'})
        raw = json.loads(fetch('https://api.github.com' + path + '?' + urllib.parse.urlencode(params)))
        if spec['kind'] == 'query':
            if not isinstance(raw, dict) or not isinstance(raw.get('items'), list):
                raise ValueError('Invalid GitHub search response')
            rows = raw['items']
            total = raw.get('total_count')
            incomplete = incomplete or bool(raw.get('incomplete_results'))
        else:
            rows = raw
        if not isinstance(rows, list):
            raise ValueError('Invalid GitHub repository response')
        if len(rows) > spec['per_page']:
            raise ValueError('GitHub page exceeds configured limit')
        entries.extend(item for item in (github_repository(row) for row in rows) if item is not None)
        if len(rows) < spec['per_page']:
            break
        if page == spec['max_pages']:
            truncated = total is None or total > page * spec['per_page']
    return entries, {'reported_total': total, 'truncated': truncated or incomplete,
                     'incomplete_results': incomplete, 'pages_read': page}


def arxiv_page(body):
    if b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():
        raise ValueError('DTD/entity declarations are not accepted in Atom feeds')
    root = ET.fromstring(body)
    if root.tag != ATOM + 'feed':
        raise ValueError('Expected an arXiv Atom feed')
    total = root.findtext(OPEN_SEARCH + 'totalResults')
    if total is not None and not total.isdigit():
        raise ValueError('Invalid arXiv total result count')
    entries = []
    for entry in root.findall(ATOM + 'entry'):
        raw_id = (entry.findtext(ATOM + 'id') or '').strip()
        match = re.fullmatch(r'https?://arxiv.org/abs/((?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7}))(v\d+)?', raw_id)
        if not match:
            raise ValueError('Invalid arXiv paper identity or API error entry')
        paper_id, version = match.groups()
        abstract = compact(entry.findtext(ATOM + 'summary'))
        title = compact(entry.findtext(ATOM + 'title'), 1000)
        if not title:
            raise ValueError('arXiv entry has no title')
        entries.append({'id': 'arxiv:' + paper_id, 'provider': 'arxiv', 'kind': 'paper',
                        'name': title, 'url': 'https://arxiv.org/abs/' + paper_id + (version or ''),
                        'arxiv_id': paper_id, 'version': version or 'unspecified',
                        'updated_at': compact(entry.findtext(ATOM + 'updated'), 40),
                        'published_at': compact(entry.findtext(ATOM + 'published'), 40),
                        'abstract': abstract,
                        'authors': [compact(item.findtext(ATOM + 'name'), 200) for item in entry.findall(ATOM + 'author')][:80],
                        'categories': sorted(set(item.get('term', '') for item in entry.findall(ATOM + 'category')))})
    return entries, int(total) if total is not None else None


def read_arxiv(spec, fetch):
    entries, total, truncated = [], None, False
    for page in range(spec['max_pages']):
        params = {'search_query': spec['query'], 'start': page * spec['per_page'],
                  'max_results': spec['per_page'], 'sortBy': 'lastUpdatedDate', 'sortOrder': 'descending'}
        rows, total = arxiv_page(fetch('https://export.arxiv.org/api/query?' + urllib.parse.urlencode(params)))
        if len(rows) > spec['per_page']:
            raise ValueError('arXiv page exceeds configured limit')
        entries.extend(rows)
        if len(rows) < spec['per_page'] or (total is not None and len(entries) >= total):
            break
        if page + 1 == spec['max_pages']:
            truncated = total is None or total > len(entries)
    return entries, {'reported_total': total, 'truncated': truncated, 'pages_read': page + 1}


def candidates_for(papers):
    candidates = []
    for paper in papers:
        abstract = paper['abstract']
        matches = list(OPEN_LANGUAGE.finditer(abstract))
        if not matches:
            continue
        # Preserve exact abstract excerpt and the matching offset for inspection.
        hit = matches[0]
        left, right = max(0, hit.start() - 140), min(len(abstract), hit.end() + 240)
        candidates.append({'id': 'candidate:' + paper['id'], 'paper_id': paper['id'],
                           'title': paper['name'], 'source_url': paper['url'],
                           'paper_updated_at': paper['updated_at'],
                           'status': 'reported_open_candidate',
                           'evidence': abstract[left:right], 'matched_phrase': hit.group(),
                           'evidence_start': left, 'evidence_end': right,
                           'review_required': True,
                           'scope': 'Abstract-language heuristic; neither openness nor a formal statement is verified.'})
    return sorted(candidates, key=lambda x: (x['paper_updated_at'], x['id']), reverse=True)


def refresh(config, previous=None, fetch=None, now=None, mode='live'):
    """Return a complete snapshot in memory; raise before writes on total failure."""
    specs = validate_config(config)
    fetch = fetch or PublicClient().get
    now = now or utc_now()
    old_sources = {x['key']: x for x in (previous or {}).get('sources', [])}
    sources, successes = [], 0
    for spec in specs:
        source = {key: spec[key] for key in ('key', 'provider', 'kind', 'query', 'per_page', 'max_pages')}
        source['attempted_at_utc'] = now
        try:
            entries, metadata = (read_github if spec['provider'] == 'github' else read_arxiv)(spec, fetch)
            # Deduplicate within a query and retain the newest observed version.
            records = {}
            for entry in sorted(entries, key=lambda item: (item.get('updated_at', ''), item.get('version', ''))):
                records[entry['id']] = entry
            source.update(metadata, entries=[records[key] for key in sorted(records)],
                          status='ok', last_success_at_utc=now, error=None)
            successes += 1
        except (OSError, ValueError, TypeError, KeyError, ET.ParseError) as error:
            old = old_sources.get(spec['key'], {})
            source.update(entries=copy.deepcopy(old.get('entries', [])), status='stale' if old.get('last_success_at_utc') else 'error',
                          last_success_at_utc=old.get('last_success_at_utc'),
                          reported_total=old.get('reported_total'), truncated=old.get('truncated', False),
                          error=type(error).__name__ + ': ' + compact(str(error), 280))
        sources.append(source)
    if not successes:
        errors = '; '.join(x['key'] + ': ' + x['error'] for x in sources)
        raise RuntimeError('No research source refreshed; existing files were preserved. ' + errors)
    records = {}
    for source in sources:
        for entry in source['entries']:
            key = entry['id']
            observed = dict(entry, sources=[source['key']], observed_at_utc=source['last_success_at_utc'])
            if key not in records:
                records[key] = observed
            else:
                memberships = sorted(set(records[key]['sources'] + observed['sources']))
                if (observed.get('updated_at', ''), observed.get('observed_at_utc') or '') > (records[key].get('updated_at', ''), records[key].get('observed_at_utc') or ''):
                    records[key] = observed
                records[key]['sources'] = memberships
    repositories = sorted((x for x in records.values() if x['kind'] == 'repository'), key=lambda x: x['id'])
    papers = sorted((x for x in records.values() if x['kind'] == 'paper'), key=lambda x: x['id'])
    candidates = candidates_for(papers)
    old_ids = {item['id'] for kind in ('repositories', 'papers') for item in (previous or {}).get(kind, [])}
    new_ids = sorted(set(records) - old_ids)
    return {'schema_version': 1, 'generated_at_utc': now, 'mode': mode,
            'scope': 'Bounded configured public metadata searches, not exhaustive global coverage. Candidate language requires human review.',
            'sources': sources, 'repositories': repositories, 'papers': papers, 'candidates': candidates,
            'summary': {'repositories': len(repositories), 'papers': len(papers), 'candidates': len(candidates),
                        'sources_ok': successes, 'sources_stale_or_error': len(sources) - successes,
                        'sources_truncated': sum(bool(x.get('truncated')) for x in sources),
                        'new_records': len(new_ids)}, 'new_record_ids': new_ids}


def markdown_text(value, limit=240):
    text = html.escape(compact(value, limit), quote=False)
    return re.sub(r'([\\`*_{\}\[\]()|#!+\-])', r'\\\1', text)


def safe_link(label, url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in {'github.com', 'arxiv.org'} or parsed.username or parsed.password:
        return markdown_text(label)
    escaped_url = urllib.parse.quote(url, safe=':/?=&.%')
    return '[' + markdown_text(label) + '](' + escaped_url + ')'


def render_brief(snapshot):
    summary = snapshot['summary']
    label = 'Offline demonstration' if snapshot['mode'] == 'offline_fixture' else 'Public metadata capture'
    lines = [f"**{label} · {markdown_text(snapshot['generated_at_utc'])}**", '',
             '| Repositories | Papers | Review candidates | Sources refreshed |',
             '| ---: | ---: | ---: | ---: |',
             f"| {summary['repositories']} | {summary['papers']} | {summary['candidates']} | {summary['sources_ok']} |", '',
             'Configured, bounded searches; candidate language does not establish that a conjecture is open or solved.']
    if summary['sources_stale_or_error'] or summary['sources_truncated']:
        lines.extend(['', f"Coverage: {summary['sources_stale_or_error']} source(s) stale/unavailable; {summary['sources_truncated']} source(s) reached a limit or reported incomplete results."])
    candidates = snapshot['candidates'][:3]
    if candidates:
        lines.extend(['', '**Latest review candidates**', ''])
        for item in candidates:
            lines.append('- ' + safe_link(item['title'], item['source_url']) + ' — reported open candidate; review required.')
    lines.extend(['', '[Full research radar](docs/RESEARCH-RADAR.md) · [Machine-readable snapshot](data/research-radar.json)'])
    return '\n'.join(lines)


def render_digest(snapshot):
    lines = ['# Anaxia research radar', '', render_brief(snapshot).replace('(docs/RESEARCH-RADAR.md)', '(RESEARCH-RADAR.md)').replace('(data/research-radar.json)', '(../data/research-radar.json)'), '',
             '## Source coverage', '', '| Source | State | Last successful capture | Records | Limited |', '| --- | --- | --- | ---: | --- |']
    for source in snapshot['sources']:
        lines.append('| ' + ' | '.join([markdown_text(source['provider'] + ': ' + source['query']),
                     markdown_text(source['status']), markdown_text(source['last_success_at_utc'] or 'never'),
                     str(len(source['entries'])), str(bool(source.get('truncated')))]) + ' |')
    for source in snapshot['sources']:
        if source.get('error'):
            lines.extend(['', 'Source error (' + markdown_text(source['key']) + '): ' + markdown_text(source['error'])])
    lines.extend(['', '## Conjecture review queue', '',
                  'An abstract may discuss a problem already resolved elsewhere or use open-problem language historically. Each entry needs literature review, exact formalization and an independent proof check. The radar never submits papers or executes source code.', ''])
    for item in snapshot['candidates'][:100]:
        lines.extend(['### ' + safe_link(item['title'], item['source_url']), '',
                      '**Status:** `reported_open_candidate` · **Action:** human review', '',
                      '> ' + markdown_text(item['evidence'], 500), ''])
    if not snapshot['candidates']:
        lines.extend(['No candidate language detected in the captured abstracts.', ''])
    lines.extend(['## Recently updated repositories', '', '| Repository | Last update reported by GitHub | License reported by GitHub |', '| --- | --- | --- |'])
    for item in sorted(snapshot['repositories'], key=lambda x: x.get('updated_at', ''), reverse=True)[:40]:
        lines.append('| ' + safe_link(item['name'], item['url']) + ' | ' + markdown_text(item['updated_at']) + ' | ' + markdown_text(item['license'] or 'unspecified') + ' |')
    return '\n'.join(lines) + '\n'


def update_readme(text, snapshot):
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError('README must contain exactly one ordered ANAXIA:RADAR marker pair')
    start, end = text.index(START) + len(START), text.index(END)
    return text[:start] + '\n\n' + render_brief(snapshot) + '\n\n' + text[end:]


def fixture_fetch(fixture):
    """Recorded raw response bodies keyed by provider/kind/query; pages in arrays."""
    sources = fixture.get('responses', [])
    counters = {}
    def fetch(url):
        parsed = urllib.parse.urlsplit(url)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.hostname == 'api.github.com':
            kind = 'owner' if parsed.path.startswith('/users/') else 'query'
            term = parsed.path.split('/')[2] if kind == 'owner' else query['q'][0]
            provider = 'github'
        else:
            provider, kind, term = 'arxiv', 'query', query['search_query'][0]
        key = (provider, kind, term)
        page = counters.get(key, 0)
        counters[key] = page + 1
        response = next((x for x in sources if (x['provider'], x['kind'], x['query']) == key), None)
        if response is None or page >= len(response.get('pages', [])):
            raise ValueError('Fixture has no recorded page for source')
        body = response['pages'][page]
        if isinstance(body, dict) and 'fixture_error' in body:
            raise OSError(body['fixture_error'])
        return body.encode() if isinstance(body, str) else json.dumps(body).encode()
    return fetch


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    command = sub.add_parser('refresh', help='Refresh configured public metadata or recorded offline fixtures')
    command.add_argument('--config', type=Path, default=ROOT / 'config/research-watch.json')
    command.add_argument('--offline', type=Path, metavar='FIXTURE')
    command.add_argument('--output', type=Path, default=ROOT / 'data/research-radar.json')
    command.add_argument('--digest', type=Path, default=ROOT / 'docs/RESEARCH-RADAR.md')
    command.add_argument('--readme', type=Path, help='Update only the marked README section')
    command = sub.add_parser('show', help='Print the latest local radar summary')
    command.add_argument('--input', type=Path, default=ROOT / 'data/research-radar.json')
    args = parser.parse_args(argv)
    try:
        if args.command == 'show':
            snapshot = json.loads(args.input.read_text(encoding='utf-8'))
            print(json.dumps({key: snapshot[key] for key in ('mode', 'generated_at_utc', 'summary')}, indent=2))
            return 0
        config = json.loads(args.config.read_text(encoding='utf-8'))
        previous = json.loads(args.output.read_text(encoding='utf-8')) if args.output.exists() else None
        fetch, now, mode = None, None, 'live'
        if args.offline:
            fixture = json.loads(args.offline.read_text(encoding='utf-8'))
            config = fixture.get('config', config)
            fetch, now, mode = fixture_fetch(fixture), fixture['captured_at_utc'], 'offline_fixture'
        # Demo records are never retained as real captures after a failed live source.
        if previous and previous.get('mode') != mode:
            previous = None
        snapshot = refresh(config, previous=previous, fetch=fetch, now=now, mode=mode)
        payloads = {args.output: json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n', args.digest: render_digest(snapshot)}
        if args.readme:
            payloads[args.readme] = update_readme(args.readme.read_text(encoding='utf-8'), snapshot)
        # Validate/render all outputs before changing any file.
        for path, content in payloads.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        print(json.dumps({'mode': mode, 'generated_at_utc': now or snapshot['generated_at_utc'], 'summary': snapshot['summary']}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print('Research radar: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
