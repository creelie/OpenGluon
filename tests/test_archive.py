import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import urllib.parse
import xml.etree.ElementTree as ET

from anaxia import archive
from anaxia.radar import DeferredRequest

NOW = '2026-11-14T01:00:00+00:00'


def record(identity='1234.56789', title='A sum of squares', stamp='2026-11-14', deleted=False):
    attributes = ' status="deleted"' if deleted else ''
    header = f'<header{attributes}><identifier>oai:arXiv.org:{identity}</identifier><datestamp>{stamp}</datestamp></header>'
    metadata = '' if deleted else f'''<metadata><arXiv xmlns="http://arxiv.org/OAI/arXiv/">
      <id>{identity}</id><created>2026-11-01</created><updated>2026-11-14</updated>
      <authors><author><keyname>Example</keyname><forenames>A.</forenames></author></authors>
      <title>{title}</title><categories>math.AG math.NT</categories>
      <abstract>A short metadata abstract about polynomials.</abstract>
      <license>http://arxiv.org/licenses/nonexclusive-distrib/1.0/</license></arXiv></metadata>'''
    return '<record>' + header + metadata + '</record>'


def page(records='', token='', error=None):
    listing = f'<error code="{error}">Recorded service response</error>' if error else '<ListRecords>' + records + '<resumptionToken expirationDate="2026-11-15T00:00:00Z">' + token + '</resumptionToken></ListRecords>'
    return ('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><responseDate>2026-11-14T01:00:00Z</responseDate>' + listing + '</OAI-PMH>').encode()


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / 'archive.sqlite3'
        self.state = self.root / 'cursor.json'

    def tearDown(self):
        self.temporary.cleanup()

    def harvest(self, fetch, **kwargs):
        return archive.harvest(self.database, self.state, fetch=fetch, now=NOW, **kwargs)

    def test_resumed_pages_commit_records_and_deleted_tombstones(self):
        first = self.harvest(lambda _: page(record(), 'next-page'))
        self.assertEqual(first['status'], 'partial')
        self.assertEqual(first['records'], 1)
        urls = []
        def fetch(url):
            urls.append(url)
            return page(record(deleted=True) + record('2345.67890', 'Another polynomial'))
        second = self.harvest(fetch)
        self.assertTrue(second['complete'])
        self.assertEqual(second['pages_committed'], 2)
        self.assertEqual(second['records'], 1)
        self.assertEqual(second['deleted_records'], 1)
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(urls[0]).query)
        self.assertEqual(query, {'verb': ['ListRecords'], 'resumptionToken': ['next-page']})
        self.assertEqual(archive.search(self.database, 'sum of squares')['matches'], [])
        self.assertEqual(archive.search(self.database, 'Another')['matches'][0]['arxiv_id'], '2345.67890')

    def test_database_cursor_repairs_untrusted_or_missing_json_mirror(self):
        self.harvest(lambda _: page(record(), 'real-cursor'))
        self.state.write_text('{"resumption_token":"external-cursor","database":"../../outside"}', encoding='utf-8')
        def fetch(url):
            self.assertIn('resumptionToken=real-cursor', url)
            self.assertNotIn('external-cursor', url)
            return page()
        self.harvest(fetch)
        mirror = json.loads(self.state.read_text())
        self.assertTrue(mirror['complete'])
        self.assertEqual(mirror['database'], str(self.database.resolve()))

    def test_invalid_second_page_preserves_cursor_and_prior_records(self):
        self.harvest(lambda _: page(record(), 'next-page'))
        before = json.loads(self.state.read_text())
        bad = page(record('2345.67890') + record('../outside'))
        with self.assertRaises(ValueError):
            self.harvest(lambda _: bad)
        after = json.loads(self.state.read_text())
        self.assertEqual(after, before)
        self.assertEqual(archive.status(self.database)['records'], 1)
        self.assertEqual(archive.status(self.database)['pages_committed'], 1)

    def test_interrupted_mirror_cannot_lose_a_committed_page(self):
        original = archive.mirror_state
        count = [0]
        def mirror(*args):
            count[0] += 1
            if count[0] == 2:
                raise OSError('simulated interrupted JSON replacement')
            return original(*args)
        with patch.object(archive, 'mirror_state', side_effect=mirror), self.assertRaises(OSError):
            self.harvest(lambda _: page(record(), 'committed-next'))
        self.assertEqual(archive.status(self.database)['pages_committed'], 1)
        def fetch(url):
            self.assertIn('committed-next', url)
            return page()
        result = self.harvest(fetch)
        self.assertEqual(result['records'], 1)
        self.assertEqual(result['pages_committed'], 2)
        self.assertTrue(json.loads(self.state.read_text())['complete'])

    def test_oai_errors_do_not_mark_archive_complete(self):
        self.harvest(lambda _: page(record(), 'expired'))
        with self.assertRaisesRegex(ValueError, 'badResumptionToken'):
            self.harvest(lambda _: page(error='badResumptionToken'))
        result = archive.status(self.database)
        self.assertFalse(result['complete'])
        self.assertEqual(result['pages_committed'], 1)
        self.assertEqual(json.loads(self.state.read_text())['resumption_token'], 'expired')

    def test_no_records_match_is_a_valid_empty_completed_traversal(self):
        result = self.harvest(lambda _: page(error='noRecordsMatch'))
        self.assertTrue(result['complete'])
        self.assertEqual(result['records'], 0)
        self.assertEqual(result['pages_this_run'], 1)

    def test_retry_after_defers_without_advancing_cursor_or_busy_loop(self):
        self.harvest(lambda _: page(record(), 'next'))
        def deferred(_):
            raise DeferredRequest('service Retry-After', 120)
        result = self.harvest(deferred)
        self.assertEqual(result['pages_this_run'], 0)
        self.assertEqual(result['pages_committed'], 1)
        self.assertIn('Retry-After', result['deferred'])
        with patch.object(archive.PublicClient, 'get') as fetch:
            later = archive.harvest(self.database, self.state, now='2026-11-14T01:00:30+00:00')
        fetch.assert_not_called()
        self.assertIn('deferred until', later['deferred'])

    def test_set_scope_is_fixed_and_all_subjects_omits_set_parameter(self):
        urls = []
        self.harvest(lambda url: urls.append(url) or page(record(), 'next'))
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(urls[0]).query)
        self.assertNotIn('set', query)
        self.assertEqual(query['metadataPrefix'], ['arXiv'])
        with self.assertRaisesRegex(ValueError, 'set is fixed'):
            self.harvest(lambda _: page(), set_spec='math')
        separate = self.root / 'math.sqlite3'
        urls.clear()
        archive.harvest(separate, self.root / 'math-state.json', set_spec='math', fetch=lambda url: urls.append(url) or page(), now=NOW)
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(urls[0]).query)['set'], ['math'])

    def test_duplicate_record_updates_without_duplicate_rows(self):
        self.harvest(lambda _: page(record(stamp='2026-11-13'), 'next'))
        result = self.harvest(lambda _: page(record(title='Updated polynomial', stamp='2026-11-14')))
        self.assertEqual(result['records'], 1)
        self.assertEqual(archive.search(self.database, 'Updated')['matches'][0]['title'], 'Updated polynomial')

    def test_repeated_token_and_entity_inputs_are_rejected(self):
        self.harvest(lambda _: page(record(), 'same'))
        with self.assertRaisesRegex(ValueError, 'repeated'):
            self.harvest(lambda _: page(record(), 'same'))
        for bad in (b'<!DOCTYPE a [<!ENTITY x "unsafe">]><a/>', b'<html/>', b'<bad', b'\xff\xfe<\x00a\x00/\x00>\x00'):
            with self.subTest(bad=bad), self.assertRaises((ValueError, ET.ParseError)):
                archive.parse_page(bad)

    def test_search_is_parameterized_and_status_does_not_create_empty_database(self):
        self.assertEqual(archive.status(self.database)['status'], 'not_started')
        self.assertFalse(self.database.exists())
        self.harvest(lambda _: page(record()))
        self.assertEqual(archive.search(self.database, "%' OR 1=1; DROP TABLE records;--")['matches'], [])
        self.assertEqual(archive.status(self.database)['records'], 1)
        with self.assertRaises(ValueError):
            archive.search(self.database, 'query', limit=1000)

    def test_invalid_budgets_and_alias_output_paths_fail_before_creation(self):
        for kwargs in ({'max_pages': 0}, {'max_pages': 11}, {'set_spec': '../outside'}):
            with self.assertRaises(ValueError):
                self.harvest(lambda _: page(), **kwargs)
        with self.assertRaises(ValueError):
            archive.harvest(self.database, self.database, fetch=lambda _: page())
        self.assertFalse(self.database.exists())


if __name__ == '__main__':
    unittest.main()
