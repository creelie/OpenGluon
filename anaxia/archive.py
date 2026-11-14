"""Opt-in, resumable arXiv OAI-PMH metadata archive; no PDFs or source bundles.

The SQLite cursor is authoritative. Each page's records, deletion tombstones and
next token commit together. The JSON state is an atomic, recoverable mirror.
"""

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import urllib.parse
import uuid
import xml.etree.ElementTree as ET

from .radar import DeferredRequest, PublicClient, after_utc, compact, elapsed_seconds, utc_now, xml_root

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = 'https://oaipmh.arxiv.org/oai'
OAI = '{http://www.openarchives.org/OAI/2.0/}'
ARXIV = '{http://arxiv.org/OAI/arXiv/}'
IDENTITY = re.compile(r'(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})')


def parse_page(body):
    root = xml_root(body)
    if root.tag != OAI + 'OAI-PMH':
        raise ValueError('Expected an OAI-PMH response')
    errors = root.findall(OAI + 'error')
    if errors:
        if len(errors) == 1 and errors[0].get('code') == 'noRecordsMatch':
            return [], '', root.findtext(OAI + 'responseDate') or '', None
        codes = ', '.join(compact(item.get('code'), 80) for item in errors)
        raise ValueError('OAI service error: ' + codes + '. Expired tokens are not restarted automatically; retain this database and begin a deliberate fresh harvest if needed.')
    listing = root.find(OAI + 'ListRecords')
    if listing is None:
        raise ValueError('OAI response has no ListRecords')
    records = listing.findall(OAI + 'record')
    if len(records) > 5000:
        raise ValueError('OAI page exceeds the 5000-record limit')
    output = []
    for record in records:
        header = record.find(OAI + 'header')
        if header is None:
            raise ValueError('OAI record has no header')
        identifier = header.findtext(OAI + 'identifier') or ''
        if not identifier.startswith('oai:arXiv.org:'):
            raise ValueError('Unexpected OAI identifier authority')
        identity = identifier.removeprefix('oai:arXiv.org:')
        if not IDENTITY.fullmatch(identity):
            raise ValueError('Invalid arXiv OAI record identity')
        stamp = header.findtext(OAI + 'datestamp') or ''
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?', stamp):
            raise ValueError('Invalid OAI modification datestamp')
        deleted = header.get('status') == 'deleted'
        result = {'arxiv_id': identity, 'url': 'https://arxiv.org/abs/' + identity,
                  'oai_datestamp': stamp, 'deleted': deleted,
                  'title': '', 'abstract': '', 'authors': [], 'categories': [], 'license': None}
        if not deleted:
            metadata = record.find(OAI + 'metadata/' + ARXIV + 'arXiv')
            if metadata is None or metadata.findtext(ARXIV + 'id') != identity:
                raise ValueError('OAI header and arXiv metadata identity disagree')
            result.update(title=compact(metadata.findtext(ARXIV + 'title'), 3000),
                          abstract=compact(metadata.findtext(ARXIV + 'abstract'), 30000),
                          categories=(metadata.findtext(ARXIV + 'categories') or '').split()[:100],
                          license=compact(metadata.findtext(ARXIV + 'license'), 1000) or None,
                          created=compact(metadata.findtext(ARXIV + 'created'), 40),
                          updated=compact(metadata.findtext(ARXIV + 'updated'), 40),
                          doi=compact(metadata.findtext(ARXIV + 'doi'), 1000) or None,
                          journal_reference=compact(metadata.findtext(ARXIV + 'journal-ref'), 2000) or None,
                          version_scope='Latest metadata exposed by OAI-PMH; this format does not enumerate every paper version.')
            if not result['title']:
                raise ValueError('OAI metadata has no title')
            for author in metadata.findall(ARXIV + 'authors/' + ARXIV + 'author')[:300]:
                result['authors'].append(compact(' '.join(filter(None, [author.findtext(ARXIV + 'forenames'), author.findtext(ARXIV + 'keyname'), author.findtext(ARXIV + 'suffix')])), 300))
        output.append(result)
    token_element = listing.find(OAI + 'resumptionToken')
    token = (token_element.text or '').strip() if token_element is not None else ''
    if len(token) > 4096 or any(ord(char) < 32 for char in token):
        raise ValueError('Invalid or excessive OAI resumption token')
    if not records and token:
        raise ValueError('An empty OAI page cannot advance a nonempty cursor')
    expiration = token_element.get('expirationDate') if token_element is not None else None
    return output, token, root.findtext(OAI + 'responseDate') or '', expiration


def _open(database, set_spec=None, create=False):
    database = Path(database)
    if not create and not database.exists():
        raise ValueError('Archive database does not exist; run archive harvest first')
    if create:
        database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(database), timeout=40, isolation_level=None)
    connection.row_factory = sqlite3.Row
    if create:
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('CREATE TABLE IF NOT EXISTS archive_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)')
        connection.execute('CREATE TABLE IF NOT EXISTS records (arxiv_id TEXT PRIMARY KEY, title TEXT NOT NULL, abstract TEXT NOT NULL, datestamp TEXT NOT NULL, deleted INTEGER NOT NULL, metadata TEXT NOT NULL)')
        state = connection.execute('SELECT payload FROM archive_state WHERE id=1').fetchone()
        if state is None:
            payload = {'schema_version': 1, 'archive_id': str(uuid.uuid4()), 'endpoint': ENDPOINT,
                       'set': set_spec, 'resumption_token': '', 'complete': False,
                       'pages_committed': 0, 'last_response_utc': None, 'last_request_utc': None,
                       'next_request_after_utc': None, 'token_expiration_utc': None}
            connection.execute('INSERT OR IGNORE INTO archive_state VALUES (1, ?)', (json.dumps(payload),))
    state = _state(connection)
    if state.get('schema_version') != 1 or state.get('endpoint') != ENDPOINT:
        connection.close()
        raise ValueError('Unsupported or mismatched archive schema/endpoint')
    if create and state.get('set') != set_spec:
        connection.close()
        raise ValueError('Archive set is fixed at creation; choose a separate database for another set')
    return connection


def _state(connection):
    row = connection.execute('SELECT payload FROM archive_state WHERE id=1').fetchone()
    if row is None:
        raise ValueError('Archive cursor is missing')
    return json.loads(row['payload'])


def _save_state(connection, state):
    connection.execute('UPDATE archive_state SET payload=? WHERE id=1', (json.dumps(state, sort_keys=True),))


def mirror_state(connection, database, state_path):
    state_path = Path(state_path)
    payload = dict(_state(connection), database=str(Path(database).resolve()), authoritative_cursor='SQLite archive_state row; this JSON file is a recoverable mirror.')
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_name(state_path.name + '.tmp-' + uuid.uuid4().hex)
    try:
        temporary.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, state_path)
    finally:
        temporary.unlink(missing_ok=True)


def status(database):
    database = Path(database)
    if not database.exists():
        return {'status': 'not_started', 'records': 0, 'deleted_records': 0, 'complete': False,
                'scope': 'No metadata archive exists at this path.'}
    with closing(_open(database)) as connection:
        state = _state(connection)
        counts = connection.execute('SELECT COUNT(*) AS total, COALESCE(SUM(deleted),0) AS deleted FROM records').fetchone()
        return {key: value for key, value in dict(state, status='completed_traversal' if state['complete'] else 'partial',
                records=counts['total'] - counts['deleted'], deleted_records=counts['deleted'],
                scope='Only records actually harvested into this local metadata database are searchable; no PDF/full-text archive.').items() if key != 'resumption_token'}


def harvest(database, state_path, max_pages=1, set_spec=None, fetch=None, now=None):
    if type(max_pages) is not int or not 1 <= max_pages <= 10:
        raise ValueError('max-pages must be between 1 and 10')
    if set_spec is not None and (not isinstance(set_spec, str) or not re.fullmatch(r'[A-Za-z0-9:_-]{1,80}', set_spec)):
        raise ValueError('Invalid OAI set specification')
    database, state_path = Path(database), Path(state_path)
    if database.resolve() == state_path.resolve():
        raise ValueError('Database and JSON mirror paths must differ')
    live_fetch = fetch is None
    fetch = fetch or PublicClient().get
    connection = _open(database, set_spec=set_spec, create=True)
    pages_this_run = 0
    deferred = None
    try:
        # Repair a missing/interrupted JSON mirror before resuming. Its contents
        # never override the authoritative transactional database cursor.
        mirror_state(connection, database, state_path)
        for _ in range(max_pages):
            connection.execute('BEGIN IMMEDIATE')
            state = _state(connection)
            moment = now or utc_now()
            if state['complete']:
                connection.execute('ROLLBACK')
                break
            wait = elapsed_seconds(state.get('next_request_after_utc'), moment)
            if wait is not None and wait > 0:
                connection.execute('ROLLBACK')
                deferred = 'Source requests are deferred until ' + state['next_request_after_utc']
                break
            since = elapsed_seconds(moment, state.get('last_request_utc'))
            if live_fetch and since is not None and 0 <= since < 3.1:
                # The persisted request clock also covers separate invocations.
                time.sleep(3.1 - since)
            token = state['resumption_token']
            params = {'verb': 'ListRecords', 'resumptionToken': token} if token else {'verb': 'ListRecords', 'metadataPrefix': 'arXiv'}
            if not token and set_spec is not None:
                params['set'] = set_spec
            try:
                records, next_token, response_date, expiration = parse_page(fetch(ENDPOINT + '?' + urllib.parse.urlencode(params)))
                if next_token and next_token == token:
                    raise ValueError('OAI service repeated the same resumption token; cursor was preserved')
                for record in records:
                    connection.execute('INSERT INTO records VALUES (?,?,?,?,?,?) ON CONFLICT(arxiv_id) DO UPDATE SET title=excluded.title, abstract=excluded.abstract, datestamp=excluded.datestamp, deleted=excluded.deleted, metadata=excluded.metadata WHERE excluded.datestamp >= records.datestamp',
                                       (record['arxiv_id'], record['title'], record['abstract'], record['oai_datestamp'], int(record['deleted']), json.dumps(record, ensure_ascii=False)))
                state.update(resumption_token=next_token, complete=not bool(next_token),
                             pages_committed=state['pages_committed'] + 1, last_response_utc=response_date or moment,
                             last_request_utc=moment, next_request_after_utc=None, token_expiration_utc=expiration)
                _save_state(connection, state)
                connection.execute('COMMIT')
                pages_this_run += 1
                mirror_state(connection, database, state_path)
            except DeferredRequest as error:
                state.update(last_request_utc=moment, next_request_after_utc=after_utc(moment, error.retry_after))
                _save_state(connection, state)
                connection.execute('COMMIT')
                mirror_state(connection, database, state_path)
                deferred = str(error)
                break
            except BaseException:
                if connection.in_transaction:
                    connection.execute('ROLLBACK')
                raise
        return dict(status(database), pages_this_run=pages_this_run, deferred=deferred)
    finally:
        connection.close()


def search(database, query, limit=20):
    if not isinstance(query, str) or not query.strip() or len(query) > 200:
        raise ValueError('Search requires 1..200 characters')
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('Search limit must be between 1 and 100')
    pattern = '%' + query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
    with closing(_open(database)) as connection:
        rows = connection.execute("SELECT metadata FROM records WHERE deleted=0 AND (title LIKE ? ESCAPE '\\' OR abstract LIKE ? ESCAPE '\\') ORDER BY datestamp DESC, arxiv_id LIMIT ?", (pattern, pattern, limit)).fetchall()
        result = []
        for row in rows:
            record = json.loads(row['metadata'])
            result.append({key: record.get(key) for key in ('arxiv_id', 'title', 'url', 'authors', 'categories', 'license', 'oai_datestamp')})
        return {'query': query, 'matches': result, 'scope': 'Local collected metadata only; no claim of exhaustive arXiv coverage.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('harvest', help='Opt in to a bounded resumable OAI metadata backfill')
    run.add_argument('--database', type=Path, default=ROOT / 'data/local/arxiv.sqlite3')
    run.add_argument('--state', type=Path, default=ROOT / 'data/local/arxiv-state.json')
    run.add_argument('--max-pages', type=int, default=1)
    run.add_argument('--set', dest='set_spec', help='Optional OAI set such as math; omit for all subjects')
    run = sub.add_parser('status', help='Show actual local harvest progress')
    run.add_argument('--database', type=Path, default=ROOT / 'data/local/arxiv.sqlite3')
    run = sub.add_parser('search', help='Search only the local metadata already harvested')
    run.add_argument('query')
    run.add_argument('--database', type=Path, default=ROOT / 'data/local/arxiv.sqlite3')
    run.add_argument('--limit', type=int, default=20)
    args = parser.parse_args(argv)
    try:
        if args.command == 'harvest':
            result = harvest(args.database, args.state, args.max_pages, args.set_spec)
        elif args.command == 'search':
            result = search(args.database, args.query, args.limit)
        else:
            result = status(args.database)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError, sqlite3.Error, ET.ParseError) as error:
        print('arXiv archive: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
