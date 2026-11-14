"""Bounded public GitHub/arXiv metadata discovery; never executes discovered code.

Only explicitly signalled open-problem language in abstracts enters the review
queue. A candidate is a report about a paper, not a verified mathematical fact.
"""

import argparse
import copy
from email.utils import parsedate_to_datetime
import gzip
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- ANAXIA:RADAR:START -->'
END = '<!-- ANAXIA:RADAR:END -->'
ATOM = '{http://www.w3.org/2005/Atom}'
OPEN_SEARCH = '{http://a9.com/-/spec/opensearch/1.1/}'
MAX_RESPONSE_BYTES = 8_000_000
BLOG_FEEDS = {
    'https://terrytao.wordpress.com/feed/': ('Terence Tao', 'terrytao.wordpress.com'),
    'https://gowers.wordpress.com/feed/': ('Timothy Gowers', 'gowers.wordpress.com'),
}
SOURCE_HOSTS = {'api.github.com', 'export.arxiv.org', 'oaipmh.arxiv.org', 'api.stackexchange.com'} | {item[1] for item in BLOG_FEEDS.values()}
STACK_FILTER = '!)6t3dr6pphdzy-FFcJmy5WA8HtuvDC1'
STACK_SITES = {'mathoverflow': 'mathoverflow.net', 'math': 'math.stackexchange.com'}
OPEN_LANGUAGE = re.compile(
    r'\b(?:remains? open|remain unresolved|open (?:problem|conjecture|question)s?'
    r'|we conjecture|we formulate (?:a |the )?conjecture|conjecture that)\b', re.I)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def compact(value, limit=12000):
    return re.sub(r'\s+', ' ', str(value or '')).strip()[:limit]


class DeferredRequest(OSError):
    def __init__(self, message, seconds):
        super().__init__(message)
        self.retry_after = max(1, min(int(seconds), 86400))


def retry_after_seconds(value):
    try:
        if str(value).isdigit():
            return max(1, min(int(value), 86400))
        moment = parsedate_to_datetime(value)
        return max(1, min(int((moment - datetime.now(timezone.utc)).total_seconds()) + 1, 86400))
    except (TypeError, ValueError, OverflowError):
        return 60


def decompress_body(body, encoding=''):
    """Bound both wire and expanded bytes; never inflate an unbounded gzip body."""
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError('API response exceeds 8 MB limit')
    if encoding == 'gzip' or body.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as stream:
            body = stream.read(MAX_RESPONSE_BYTES + 1)
    elif encoding == 'deflate':
        decoder = zlib.decompressobj()
        body = decoder.decompress(body, MAX_RESPONSE_BYTES + 1)
        if decoder.unconsumed_tail or not decoder.eof:
            raise ValueError('Invalid or excessive deflate response')
    elif encoding not in ('', 'identity'):
        raise ValueError('Unsupported response content encoding')
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError('Expanded API response exceeds 8 MB limit')
    return body


def xml_root(body):
    if not isinstance(body, bytes) or len(body) > MAX_RESPONSE_BYTES:
        raise ValueError('XML input must be bounded bytes')
    if b'\x00' in body or b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():
        raise ValueError('DTD/entity declarations are not accepted in feeds')
    parser = ET.XMLPullParser(events=('start', 'end'))
    root, count, depth = None, 0, 0
    for offset in range(0, len(body), 65536):
        parser.feed(body[offset:offset + 65536])
        for event, element in parser.read_events():
            if event == 'start':
                root = element if root is None else root
                count += 1
                depth += 1
                if count > 40000 or depth > 128:
                    raise ValueError('XML feed exceeds element/depth limits')
            else:
                depth -= 1
    parser.close()
    if root is None:
        raise ValueError('XML feed is empty')
    return root


class PublicClient:
    """One sequential request stream with strict hosts, sizes and time budgets."""

    last_arxiv = None
    stack_cache = {}

    def __init__(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise urllib.error.HTTPError(req.full_url, code, 'API redirects are disabled', headers, fp)
        self.opener = urllib.request.build_opener(NoRedirect())

    def get(self, url):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in SOURCE_HOSTS or parsed.username or parsed.password:
            raise ValueError('Only configured public research-source HTTPS hosts are accepted')
        arxiv = parsed.hostname in {'export.arxiv.org', 'oaipmh.arxiv.org'}
        stack = parsed.hostname == 'api.stackexchange.com'
        if stack and url in self.stack_cache:
            captured, body = self.stack_cache[url]
            if time.monotonic() - captured < 60:
                return body
        if arxiv and PublicClient.last_arxiv is not None:
            time.sleep(max(0, 3.1 - (time.monotonic() - PublicClient.last_arxiv)))
        headers = {'User-Agent': 'Anaxia-Research-Radar/1.1 (public metadata; https://github.com/creelie/Anaxia)', 'Accept-Encoding': 'gzip'}
        if parsed.hostname == 'api.github.com':
            headers.update({'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
            if token:
                headers['Authorization'] = 'Bearer ' + token
        try:
            with self.opener.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
                # Refuse unexpected redirect destinations before reading a body.
                if urllib.parse.urlsplit(response.geturl()).hostname != parsed.hostname:
                    raise ValueError('Unexpected API redirect')
                body = decompress_body(response.read(MAX_RESPONSE_BYTES + 1), response.headers.get('Content-Encoding', '').lower())
                if stack:
                    self.stack_cache[url] = (time.monotonic(), body)
                return body
        except urllib.error.HTTPError as error:
            if error.code in (429, 503):
                raise DeferredRequest('Source deferred requests after HTTP ' + str(error.code), retry_after_seconds(error.headers.get('Retry-After'))) from error
            raise
        finally:
            if arxiv:
                PublicClient.last_arxiv = time.monotonic()


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
    stack = config.get('stackexchange', {})
    blogs = config.get('blogs', {})
    if not isinstance(stack, dict) or not isinstance(blogs, dict):
        raise ValueError('Stack Exchange and blog settings must be objects')
    for provider, section, field in (('stackexchange', stack, 'sites'), ('blogs', blogs, 'feeds')):
        entries = section.get(field, [])
        size, pages = section.get('per_page', 20), section.get('max_pages', 1)
        if not isinstance(entries, list) or len(entries) > 6:
            raise ValueError('Use a bounded source list')
        if type(size) is not int or not 1 <= size <= 100 or type(pages) is not int or not 1 <= pages <= 3:
            raise ValueError('Source pagination requires 1..100 per page and 1..3 pages')
        if provider == 'blogs' and pages != 1:
            raise ValueError('Blog feeds use one metadata page')
        for entry in entries:
            if not isinstance(entry, str) or (provider == 'stackexchange' and entry not in {'mathoverflow', 'math'}) or (provider == 'blogs' and entry not in BLOG_FEEDS):
                raise ValueError('Only curated mathematics community sites and verified primary blog feeds are enabled')
            digest = hashlib.sha256(entry.encode()).hexdigest()[:16]
            kind = 'questions' if provider == 'stackexchange' else 'feed'
            specs.append({'key': provider + ':' + kind + ':' + digest, 'provider': provider, 'kind': kind,
                          'query': entry, 'per_page': size, 'max_pages': pages})
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
    root = xml_root(body)
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


def unix_time(value):
    if type(value) is not int or not 0 <= value <= 10000000000:
        raise ValueError('Invalid source timestamp')
    return datetime.fromtimestamp(value, timezone.utc).isoformat(timespec='seconds')


def read_stackexchange(spec, fetch):
    entries, has_more, quota, backoff = [], False, None, 0
    for page in range(1, spec['max_pages'] + 1):
        params = {'site': spec['query'], 'page': page, 'pagesize': spec['per_page'],
                  'order': 'desc', 'sort': 'activity', 'filter': STACK_FILTER}
        raw = json.loads(fetch('https://api.stackexchange.com/2.3/questions?' + urllib.parse.urlencode(params)))
        if not isinstance(raw, dict) or raw.get('error_id') or not isinstance(raw.get('items'), list):
            raise ValueError('Stack Exchange returned an error or invalid question list')
        if len(raw['items']) > spec['per_page'] or type(raw.get('has_more')) is not bool:
            raise ValueError('Invalid Stack Exchange pagination')
        quota, backoff = raw.get('quota_remaining'), raw.get('backoff', 0)
        if type(quota) is not int or quota < 0 or type(backoff) is not int or not 0 <= backoff <= 86400:
            raise ValueError('Invalid Stack Exchange quota/backoff response')
        for item in raw['items']:
            if not isinstance(item, dict) or type(item.get('question_id')) is not int or item['question_id'] <= 0:
                raise ValueError('Invalid Stack Exchange question identity')
            identity, site = item['question_id'], spec['query']
            if type(item.get('is_answered')) is not bool or type(item.get('score')) is not int:
                raise ValueError('Invalid Stack Exchange question status')
            accepted = item.get('accepted_answer_id')
            if accepted is not None and (type(accepted) is not int or accepted <= 0):
                raise ValueError('Invalid accepted answer identity')
            owner = item.get('owner') or {}
            if not isinstance(owner, dict):
                raise ValueError('Invalid Stack Exchange author metadata')
            author = compact(html.unescape(str(owner.get('display_name') or 'deleted or undisclosed user')), 200)
            canonical = 'https://' + STACK_SITES[site] + '/questions/' + str(identity)
            entries.append({'id': 'stackexchange:' + site + ':' + str(identity), 'provider': 'stackexchange',
                            'kind': 'question', 'site': site, 'question_id': identity,
                            'name': compact(html.unescape(str(item.get('title') or 'Untitled question')), 1000),
                            'url': canonical, 'score': item['score'], 'is_answered': item['is_answered'],
                            'accepted_answer_id': accepted, 'answer_count': item.get('answer_count'),
                            'author': author, 'author_url': 'https://' + STACK_SITES[site] + '/users/' + str(owner['user_id']) if type(owner.get('user_id')) is int and owner['user_id'] > 0 else None,
                            'license': compact(item.get('content_license') or 'unspecified; consult original post', 100),
                            'tags': [compact(x, 100) for x in item.get('tags', [])[:20]],
                            'updated_at': unix_time(item['last_activity_date']),
                            'published_at': unix_time(item['creation_date']),
                            'research_status': 'community_question',
                            'scope': 'Answer and acceptance flags describe the site discussion, not whether a mathematical conjecture is open or proven.'})
        has_more = raw['has_more']
        if not has_more or backoff or quota == 0:
            break
    return entries, {'pages_read': page, 'reported_total': None, 'truncated': has_more,
                     'quota_remaining': quota, 'backoff_seconds': backoff,
                     'defer_seconds': max(backoff, 3600 if quota == 0 else 0)}


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def blog_excerpt(value):
    parser = PlainText()
    parser.feed(value or '')
    return compact(' '.join(' '.join(parser.parts).split()[:24]), 180)


def feed_date(value):
    if not value:
        return ''
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat(timespec='seconds')
    except (TypeError, ValueError, OverflowError):
        return compact(value, 40)


def read_blog(spec, fetch):
    root = xml_root(fetch(spec['query']))
    attribution, host = BLOG_FEEDS[spec['query']]
    if root.tag == 'rss':
        items = root.findall('./channel/item')
        atom = False
    elif root.tag == ATOM + 'feed':
        items = root.findall(ATOM + 'entry')
        atom = True
    else:
        raise ValueError('Expected a primary-blog RSS or Atom feed')
    entries = []
    for item in items[:spec['per_page']]:
        if atom:
            link = next((child.get('href') for child in item.findall(ATOM + 'link') if child.get('rel', 'alternate') == 'alternate'), '')
            name = item.findtext(ATOM + 'title')
            excerpt = item.findtext(ATOM + 'summary') or ''
            published = item.findtext(ATOM + 'published') or item.findtext(ATOM + 'updated')
            updated = item.findtext(ATOM + 'updated') or published
        else:
            link, name = item.findtext('link'), item.findtext('title')
            excerpt, published = item.findtext('description') or '', item.findtext('pubDate')
            updated = published
        parsed = urllib.parse.urlsplit(link or '')
        if parsed.scheme not in {'https', 'http'} or parsed.hostname != host or parsed.username or parsed.password:
            raise ValueError('Blog item permalink must stay on its curated primary-source host')
        link = urllib.parse.urlunsplit(('https', parsed.netloc, parsed.path, parsed.query, ''))
        identity = hashlib.sha256(link.encode()).hexdigest()[:24]
        entries.append({'id': 'blog:' + identity, 'provider': 'blogs', 'kind': 'blog_post',
                        'name': compact(html.unescape(name or 'Untitled blog post'), 1000),
                        'url': link, 'feed_url': spec['query'], 'author': attribution,
                        'excerpt': blog_excerpt(excerpt), 'published_at': feed_date(published),
                        'updated_at': feed_date(updated), 'license': 'Rights retained by the author; consult the original post.',
                        'scope': 'Primary-source blog metadata and a short attributed feed excerpt; no article body is archived.'})
    return entries, {'pages_read': 1, 'reported_total': len(items), 'truncated': len(items) > spec['per_page']}


def after_utc(now, seconds):
    return (datetime.fromisoformat(now.replace('Z', '+00:00')) + timedelta(seconds=seconds)).isoformat(timespec='seconds')


def elapsed_seconds(now, before):
    try:
        return (datetime.fromisoformat(now.replace('Z', '+00:00')) - datetime.fromisoformat(before.replace('Z', '+00:00'))).total_seconds()
    except (ValueError, TypeError, AttributeError):
        return None


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
    if previous and previous.get('schema_version', 1) != 1:
        raise ValueError('Unsupported previous research snapshot schema')
    old_sources = {x['key']: x for x in (previous or {}).get('sources', [])}
    readers = {'github': read_github, 'arxiv': read_arxiv, 'stackexchange': read_stackexchange, 'blogs': read_blog}
    stack_block_until = max((x.get('next_poll_after_utc') or '' for x in old_sources.values() if x.get('provider') == 'stackexchange'), default='')
    sources, successes = [], 0
    for spec in specs:
        source = {key: spec[key] for key in ('key', 'provider', 'kind', 'query', 'per_page', 'max_pages')}
        source['attempted_at_utc'] = now
        try:
            old = old_sources.get(spec['key'], {})
            if spec['provider'] == 'stackexchange':
                remaining = elapsed_seconds(stack_block_until, now)
                if remaining is not None and remaining > 0:
                    raise DeferredRequest('Stack Exchange method backoff/quota window is active', int(remaining) + 1)
                age = elapsed_seconds(now, old.get('attempted_at_utc'))
                if age is not None and 0 <= age < 60:
                    if not old.get('last_success_at_utc'):
                        raise DeferredRequest('Identical Stack Exchange request was attempted less than one minute ago', 60 - int(age))
                    source.update(copy.deepcopy(old), attempted_at_utc=now, status='cached', error=None,
                                  cache_note='Reused prior capture to avoid semantically identical polling within one minute.')
                    # Do not reset the actual request time when serving a cache hit.
                    source['attempted_at_utc'] = old['attempted_at_utc']
                    sources.append(source)
                    successes += 1
                    continue
            entries, metadata = readers[spec['provider']](spec, fetch)
            # Deduplicate within a query and retain the newest observed version.
            records = {}
            for entry in sorted(entries, key=lambda item: (item.get('updated_at', ''), item.get('version', ''))):
                records[entry['id']] = entry
            source.update(metadata, entries=[records[key] for key in sorted(records)],
                          status='ok', last_success_at_utc=now, error=None)
            if metadata.get('defer_seconds'):
                source['next_poll_after_utc'] = after_utc(now, metadata['defer_seconds'])
                stack_block_until = source['next_poll_after_utc']
            successes += 1
        except (OSError, ValueError, TypeError, KeyError, AttributeError, ET.ParseError, zlib.error) as error:
            old = old_sources.get(spec['key'], {})
            source.update(entries=copy.deepcopy(old.get('entries', [])), status='stale' if old.get('last_success_at_utc') else 'error',
                          last_success_at_utc=old.get('last_success_at_utc'),
                          reported_total=old.get('reported_total'), truncated=old.get('truncated', False),
                          error=type(error).__name__ + ': ' + compact(str(error), 280))
            if isinstance(error, DeferredRequest):
                source['next_poll_after_utc'] = after_utc(now, error.retry_after)
                if spec['provider'] == 'stackexchange':
                    stack_block_until = source['next_poll_after_utc']
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
    questions = sorted((x for x in records.values() if x['kind'] == 'question'), key=lambda x: x['id'])
    blog_posts = sorted((x for x in records.values() if x['kind'] == 'blog_post'), key=lambda x: x['id'])
    candidates = candidates_for(papers)
    old_ids = {item['id'] for kind in ('repositories', 'papers', 'questions', 'blog_posts') for item in (previous or {}).get(kind, [])}
    new_ids = sorted(set(records) - old_ids)
    return {'schema_version': 1, 'generated_at_utc': now, 'mode': mode,
            'scope': 'Bounded configured public metadata searches, not exhaustive global coverage. Candidate language requires human review.',
            'sources': sources, 'repositories': repositories, 'papers': papers, 'questions': questions, 'blog_posts': blog_posts, 'candidates': candidates,
            'summary': {'repositories': len(repositories), 'papers': len(papers), 'candidates': len(candidates),
                        'questions': len(questions), 'blog_posts': len(blog_posts),
                        'sources_ok': sum(x['status'] == 'ok' for x in sources),
                        'sources_cached': sum(x['status'] == 'cached' for x in sources),
                        'sources_stale_or_error': len(sources) - successes,
                        'sources_truncated': sum(bool(x.get('truncated')) for x in sources),
                        'new_records': len(new_ids)}, 'new_record_ids': new_ids}


def markdown_text(value, limit=240):
    text = html.escape(compact(value, limit), quote=False)
    return re.sub(r'([\\`*_{\}\[\]()|#!+\-])', r'\\\1', text)


def safe_link(label, url):
    parsed = urllib.parse.urlsplit(url)
    hosts = {'github.com', 'arxiv.org'} | set(STACK_SITES.values()) | {x[1] for x in BLOG_FEEDS.values()}
    if parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.username or parsed.password:
        return markdown_text(label)
    escaped_url = urllib.parse.quote(url, safe=':/?=&.%')
    return '[' + markdown_text(label) + '](' + escaped_url + ')'


def render_brief(snapshot):
    summary = snapshot['summary']
    label = 'Offline demonstration' if snapshot['mode'] == 'offline_fixture' else 'Public metadata capture'
    lines = [f"**{label} · {markdown_text(snapshot['generated_at_utc'])}**", '',
             '| Repositories | Papers | Community questions | Blog posts | Review candidates | Sources refreshed |',
             '| ---: | ---: | ---: | ---: | ---: | ---: |',
             f"| {summary['repositories']} | {summary['papers']} | {summary.get('questions', 0)} | {summary.get('blog_posts', 0)} | {summary['candidates']} | {summary['sources_ok']} |", '',
             'Configured, bounded sources; candidate language and community answer flags do not establish that a conjecture is open or solved.']
    if summary.get('sources_cached'):
        lines.extend(['', f"{summary['sources_cached']} source(s) reused their recent capture to respect API polling limits."])
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
    lines.extend(['', '## Mathematics community questions', '',
                  'Answer flags describe discussion on MathOverflow or Mathematics Stack Exchange. An unanswered post is not automatically an open conjecture; an accepted answer is not a machine-verified proof.', '',
                  '| Question | Author | Score | Answered / accepted | Content license |', '| --- | --- | ---: | --- | --- |'])
    for item in sorted(snapshot.get('questions', []), key=lambda x: x.get('updated_at', ''), reverse=True)[:40]:
        author = safe_link(item['author'], item['author_url']) if item.get('author_url') else markdown_text(item['author'])
        flags = str(item['is_answered']) + ' / ' + (str(item['accepted_answer_id']) if item.get('accepted_answer_id') else 'none')
        lines.append('| ' + safe_link(item['name'], item['url']) + ' | ' + author + ' | ' + str(item['score']) + ' | ' + flags + ' | ' + markdown_text(item['license']) + ' |')
    lines.extend(['', '## Primary research blog feeds', '', 'Titles, author attribution, dates and short feed excerpts only. Follow the original article for context and reuse terms.', ''])
    for item in sorted(snapshot.get('blog_posts', []), key=lambda x: x.get('updated_at', ''), reverse=True)[:16]:
        lines.extend(['- ' + safe_link(item['name'], item['url']) + ' — ' + markdown_text(item['author']) + ' · ' + markdown_text(item['published_at']),
                      '  ' + markdown_text(item['excerpt'], 180)])
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
        elif parsed.hostname == 'api.stackexchange.com':
            provider, kind, term = 'stackexchange', 'questions', query['site'][0]
        elif parsed.hostname in {x[1] for x in BLOG_FEEDS.values()}:
            provider, kind, term = 'blogs', 'feed', url
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
