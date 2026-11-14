import contextlib
import gzip
import io
import json
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

from anaxia import radar

ROOT = Path(__file__).resolve().parents[1]
NOW = '2026-11-14T00:00:00+00:00'


def repo(identity=1, name='example/repo', **kwargs):
    return dict(id=identity, full_name=name, private=False, updated_at=NOW, **kwargs)


def config(github=True, arxiv=False, per_page=2, max_pages=2):
    return {'schema_version': 1,
            'github': {'owners': ['example'] if github else [], 'queries': [], 'per_page': per_page, 'max_pages': max_pages},
            'arxiv': {'queries': ['cat:math.NT'] if arxiv else [], 'per_page': per_page, 'max_pages': max_pages}}


def feed(paper_id='1234.56789v1', abstract='We conjecture an inequality.', title='Paper', updated=NOW):
    return f'''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:o="http://a9.com/-/spec/opensearch/1.1/">
    <o:totalResults>1</o:totalResults><entry><id>http://arxiv.org/abs/{paper_id}</id><title>{title}</title>
    <summary>{abstract}</summary><updated>{updated}</updated><author><name>A. Author</name></author>
    <category term="math.NT"/></entry></feed>'''.encode()


class ResearchRadarTests(unittest.TestCase):
    def test_stackexchange_flags_are_metadata_with_attribution_not_candidates(self):
        cfg = config(False)
        cfg['stackexchange'] = {'sites': ['mathoverflow'], 'per_page': 2, 'max_pages': 1}
        row = {'question_id': 12, 'title': 'An inequality &amp; its cases', 'score': 4,
               'is_answered': False, 'answer_count': 0, 'content_license': 'CC BY-SA 4.0',
               'owner': {'display_name': 'A &amp; B', 'user_id': 10}, 'tags': ['inequalities'],
               'creation_date': 1794614400, 'last_activity_date': 1794614500}
        snapshot = radar.refresh(cfg, fetch=lambda _: json.dumps({'items': [row], 'has_more': False, 'quota_remaining': 290}), now=NOW)
        question = snapshot['questions'][0]
        self.assertEqual(question['research_status'], 'community_question')
        self.assertEqual(question['license'], 'CC BY-SA 4.0')
        self.assertEqual(question['author'], 'A & B')
        self.assertEqual(question['name'], 'An inequality & its cases')
        self.assertEqual(question['url'], 'https://mathoverflow.net/questions/12')
        self.assertEqual(snapshot['candidates'], [])
        self.assertIn('not automatically an open conjecture', radar.render_digest(snapshot))

    def test_stackexchange_cache_avoids_repolling_within_one_minute(self):
        cfg = config(False)
        cfg['stackexchange'] = {'sites': ['math'], 'per_page': 2, 'max_pages': 1}
        old = radar.refresh(cfg, fetch=lambda _: json.dumps({'items': [], 'has_more': False, 'quota_remaining': 290}), now=NOW)
        with patch('anaxia.radar.PublicClient.get') as fetch:
            snapshot = radar.refresh(cfg, previous=old, now='2026-11-14T00:00:30+00:00')
        fetch.assert_not_called()
        self.assertEqual(snapshot['sources'][0]['status'], 'cached')
        self.assertEqual(snapshot['sources'][0]['last_success_at_utc'], NOW)

    def test_stackexchange_backoff_stops_other_question_requests(self):
        cfg = config(False)
        cfg['stackexchange'] = {'sites': ['mathoverflow', 'math'], 'per_page': 2, 'max_pages': 2}
        calls = []
        def fetch(url):
            calls.append(url)
            return json.dumps({'items': [], 'has_more': True, 'quota_remaining': 0, 'backoff': 90})
        snapshot = radar.refresh(cfg, fetch=fetch, now=NOW)
        self.assertEqual(len(calls), 1)
        self.assertTrue(snapshot['sources'][0]['truncated'])
        self.assertEqual(snapshot['sources'][1]['status'], 'error')
        self.assertIn('next_poll_after_utc', snapshot['sources'][1])

    def test_primary_blog_feed_keeps_short_attributed_excerpts_and_host(self):
        cfg = config(False)
        url = 'https://terrytao.wordpress.com/feed/'
        cfg['blogs'] = {'feeds': [url], 'per_page': 1, 'max_pages': 1}
        body = b'''<rss version="2.0"><channel><item><title>Research &amp; discussion</title>
        <link>https://terrytao.wordpress.com/2026/11/14/research/</link>
        <pubDate>Sat, 14 Nov 2026 00:00:00 +0000</pubDate><description><![CDATA[<p>Short feed summary.</p><script>unsafe()</script>]]></description>
        </item></channel></rss>'''
        snapshot = radar.refresh(cfg, fetch=lambda _: body, now=NOW)
        post = snapshot['blog_posts'][0]
        self.assertEqual(post['author'], 'Terence Tao')
        self.assertEqual(post['excerpt'], 'Short feed summary.')
        self.assertNotIn('content', post)
        self.assertEqual(snapshot['candidates'], [])
        spec = radar.validate_config(cfg)[0]
        with self.assertRaises(ValueError):
            radar.read_blog(spec, lambda _: body.replace(b'https://terrytao.wordpress.com/2026', b'https://evil.test/2026'))

    def test_bounded_gzip_and_deflate_decoding(self):
        raw = b'{"items": []}'
        self.assertEqual(radar.decompress_body(gzip.compress(raw)), raw)
        self.assertEqual(radar.decompress_body(zlib.compress(raw), 'deflate'), raw)
        with patch.object(radar, 'MAX_RESPONSE_BYTES', 100), self.assertRaises(ValueError):
            radar.decompress_body(gzip.compress(b'x' * 1000))
        with self.assertRaises(ValueError):
            radar.decompress_body(b'body', 'br')

    def test_old_schema_snapshot_migrates_with_additive_empty_sources(self):
        old = radar.refresh(config(), fetch=lambda _: '[]', now=NOW)
        old.pop('questions')
        old.pop('blog_posts')
        snapshot = radar.refresh(config(), previous=old, fetch=lambda _: '[]', now=NOW)
        self.assertEqual(snapshot['schema_version'], 1)
        self.assertEqual(snapshot['questions'], [])
        self.assertEqual(snapshot['blog_posts'], [])

    def test_github_pagination_and_deduplication(self):
        urls = []
        pages = [[repo(), repo(2, 'example/second')], [repo(2, 'example/second')]]
        def fetch(url):
            urls.append(url)
            return json.dumps(pages.pop(0)).encode()
        result = radar.refresh(config(), fetch=fetch, now=NOW)
        self.assertEqual(result['summary']['repositories'], 2)
        self.assertEqual(result['sources'][0]['pages_read'], 2)
        self.assertFalse(result['sources'][0]['truncated'])
        self.assertIn('page=2', urls[1])

    def test_page_cap_is_visible(self):
        result = radar.refresh(config(max_pages=1), fetch=lambda _: json.dumps([repo(), repo(2)]), now=NOW)
        self.assertTrue(result['sources'][0]['truncated'])

    def test_duplicate_across_sources_keeps_both_provenances(self):
        cfg = config()
        cfg['github']['queries'] = ['topic:mathematics']
        def fetch(url):
            if '/search/' in url:
                return json.dumps({'items': [repo()], 'total_count': 1})
            return json.dumps([repo()])
        result = radar.refresh(cfg, fetch=fetch, now=NOW)
        self.assertEqual(len(result['repositories']), 1)
        self.assertEqual(len(result['repositories'][0]['sources']), 2)

    def test_search_incomplete_flag_is_visible(self):
        cfg = config(False)
        cfg['github']['queries'] = ['topic:mathematics']
        result = radar.refresh(cfg, fetch=lambda _: json.dumps({'items': [repo()], 'total_count': 1, 'incomplete_results': True}), now=NOW)
        self.assertTrue(result['sources'][0]['truncated'])

    def test_private_repositories_are_not_captured(self):
        row = repo()
        row['private'] = True
        result = radar.refresh(config(), fetch=lambda _: json.dumps([row]), now=NOW)
        self.assertEqual(result['repositories'], [])

    def test_arxiv_version_identity_and_evidence_provenance(self):
        result = radar.refresh(config(False, True), fetch=lambda _: feed(), now=NOW)
        paper, candidate = result['papers'][0], result['candidates'][0]
        self.assertEqual(paper['id'], 'arxiv:1234.56789')
        self.assertEqual(paper['version'], 'v1')
        self.assertEqual(candidate['status'], 'reported_open_candidate')
        self.assertEqual(candidate['evidence'], paper['abstract'][candidate['evidence_start']:candidate['evidence_end']])
        self.assertTrue(candidate['review_required'])

    def test_proof_only_abstract_is_not_a_candidate(self):
        result = radar.refresh(config(False, True), fetch=lambda _: feed(abstract='We prove the conjecture for every integer.'), now=NOW)
        self.assertEqual(result['candidates'], [])

    def test_invalid_and_entity_feeds_are_rejected(self):
        for body in (b'<html>maintenance</html>', b'<feed', b'<!DOCTYPE feed [<!ENTITY x "text">]><feed/>', b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/api/errors</id></entry></feed>'):
            with self.subTest(body=body), self.assertRaises((ValueError, radar.ET.ParseError)):
                radar.arxiv_page(body)
        with self.assertRaises(ValueError):
            radar.xml_root(b'<a>' * 130 + b'</a>' * 130)

    def test_partial_failure_retains_last_success_and_marks_stale(self):
        cfg = config(True, True)
        old = radar.refresh(cfg, fetch=lambda url: feed() if 'arxiv' in url else json.dumps([repo()]), now=NOW)
        def fetch(url):
            if 'arxiv' in url:
                raise OSError('service unavailable')
            return json.dumps([repo(2, 'example/new')])
        result = radar.refresh(cfg, previous=old, fetch=fetch, now='2026-11-15T00:00:00+00:00')
        source = result['sources'][1]
        self.assertEqual(source['status'], 'stale')
        self.assertEqual(source['last_success_at_utc'], NOW)
        self.assertEqual(source['entries'], old['sources'][1]['entries'])
        self.assertEqual(result['papers'][0]['observed_at_utc'], NOW)
        self.assertEqual(result['summary']['new_records'], 1)
        digest = radar.render_digest(result)
        self.assertLess(digest.index('| arxiv:'), digest.index('Source error ('))

    def test_total_failure_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cfg, output, digest = root / 'config.json', root / 'snapshot.json', root / 'digest.md'
            cfg.write_text(json.dumps(config()), encoding='utf-8')
            output.write_text('{"sources": [], "mode": "live"}', encoding='utf-8')
            digest.write_text('retained digest', encoding='utf-8')
            old = output.read_bytes()
            with patch.object(radar.PublicClient, 'get', side_effect=OSError('offline')), contextlib.redirect_stderr(io.StringIO()):
                code = radar.main(['refresh', '--config', str(cfg), '--output', str(output), '--digest', str(digest)])
            self.assertEqual(code, 2)
            self.assertEqual(output.read_bytes(), old)
            self.assertEqual(digest.read_text(), 'retained digest')

    def test_untrusted_markdown_is_escaped_and_links_restricted(self):
        malicious = '<script>alert(1)</script> [x](javascript:bad) | ![img](https://evil.test/x)\n# injected'
        escaped = radar.markdown_text(malicious)
        self.assertNotIn('<script>', escaped)
        self.assertIn('\\[x\\]', escaped)
        self.assertIn('\\|', escaped)
        self.assertNotIn('\n', escaped)
        self.assertNotIn('](javascript:', radar.safe_link('evil', 'javascript:alert(1)'))
        self.assertNotIn('](', radar.safe_link('evil', 'https://github.com@evil.test/'))

    def test_apostrophes_and_html_entities_render_without_double_escaping(self):
        escaped = radar.markdown_text("Onsager's conjecture & <script>unsafe</script>")
        self.assertIn("Onsager's conjecture", escaped)
        self.assertIn('&amp;', escaped)
        self.assertIn('&lt;script&gt;', escaped)
        self.assertNotIn('x27', escaped)
        self.assertNotIn('\\#', escaped)
        self.assertNotIn('&amp;lt;', escaped)
        self.assertNotIn('<script>', escaped)

    def test_readme_replacement_is_confined_and_requires_markers(self):
        snapshot = radar.refresh(config(), fetch=lambda _: '[]', now=NOW)
        text = 'before\n' + radar.START + '\nold\n' + radar.END + '\nafter'
        result = radar.update_readme(text, snapshot)
        self.assertTrue(result.startswith('before\n' + radar.START))
        self.assertTrue(result.endswith(radar.END + '\nafter'))
        self.assertNotIn('\nold\n', result)
        for invalid in ('no markers', radar.END + radar.START, radar.START + radar.START + radar.END):
            with self.assertRaises(ValueError):
                radar.update_readme(invalid, snapshot)

    def test_fixture_is_deterministic_and_explicitly_labelled(self):
        fixture = json.loads((ROOT / 'examples/radar-fixture.json').read_text())
        first = radar.refresh(fixture['config'], fetch=radar.fixture_fetch(fixture), now=fixture['captured_at_utc'], mode='offline_fixture')
        second = radar.refresh(fixture['config'], fetch=radar.fixture_fetch(fixture), now=fixture['captured_at_utc'], mode='offline_fixture')
        self.assertEqual(first, second)
        self.assertIn('Offline demonstration', radar.render_brief(first))
        self.assertEqual(first['summary']['candidates'], 1)

    def test_api_hosts_and_config_limits_are_enforced(self):
        with self.assertRaises(ValueError):
            radar.PublicClient().get('https://evil.test/api')
        for invalid in ({'schema_version': 2}, config(per_page=0), config(max_pages=6)):
            with self.assertRaises(ValueError):
                radar.validate_config(invalid)
        cfg = config()
        cfg['github']['owners'] = ['../outside']
        with self.assertRaises(ValueError):
            radar.validate_config(cfg)

    def test_arxiv_politeness_and_token_not_sent_to_arxiv(self):
        client = radar.PublicClient()
        response = unittest.mock.MagicMock()
        response.geturl.return_value = 'https://export.arxiv.org/api/query'
        response.headers = {}
        response.read.return_value = b'body'
        client.opener.open = unittest.mock.MagicMock()
        client.opener.open.return_value.__enter__.return_value = response
        with patch.object(radar.time, 'monotonic', side_effect=[10.0, 10.1, 13.1]), patch.object(radar.time, 'sleep') as sleep, patch.dict(radar.os.environ, {'GITHUB_TOKEN': 'do-not-send'}):
            client.get('https://export.arxiv.org/api/query')
            client.get('https://export.arxiv.org/api/query')
            self.assertAlmostEqual(sleep.call_args.args[0], 3.0)
            for call in client.opener.open.call_args_list:
                self.assertNotIn('Authorization', call.args[0].headers)


if __name__ == '__main__':
    unittest.main()
