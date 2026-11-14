# Source coverage, attribution and archives

Anaxia combines a bounded current-awareness radar with a separate, opt-in local arXiv metadata archive. These are discovery tools. Source text, forum votes, accepted answers and heuristic conjecture candidates are not mathematical proof certificates.

## Current research radar

Configure `config/research-watch.json`, then run `python anaxia.py radar refresh --readme README.md`. The snapshot records source identities, request/capture times, page caps, incomplete responses and per-source failures. A failed source retains its last successful capture and is marked stale. If every configured source fails, existing published snapshot files are preserved. Snapshot schema 1 gains optional `questions` and `blog_posts` collections; existing schema-1 snapshots remain readable.

| Source | Metadata captured | Default coverage | Interpretation |
| --- | --- | --- | --- |
| GitHub | Repository identity, permalink, reported update dates, branch, topics and license | creelie owner inventory, at most 500 repositories; three global mathematics/AI/formalization searches, at most 100 results each | Public repository metadata; no discovered code is executed or automatically installed |
| arXiv query API | Paper identity/version, title, authors, category, dates and abstract | Recent `math.*` and an open-problem-focused mathematics query, at most 60 records each | Abstract language creates review candidates; it cannot establish current openness or a proof |
| MathOverflow | Question identity, title, author/permalink, score, answer/acceptance flags, tags and reported content license | At most 40 recently active questions | Discussion state, not a list of formally open conjectures |
| Mathematics Stack Exchange | The same attributed question metadata | At most 40 recently active questions | Unanswered does not imply an open research problem; acceptance does not imply independently verified proof |
| Terence Tao's primary blog | Title, original permalink, author, publication date and a short feed excerpt | At most 8 RSS entries | Original article retains context and reuse terms |
| Timothy Gowers's primary blog | The same limited feed metadata | At most 8 RSS entries | No full article body is stored |

The MathOverflow and Mathematics Stack Exchange API filter explicitly requests attribution and `content_license`, while excluding question bodies and answers. Preserve each record's author, source link and license when reusing its text. Metadata may report deleted or undisclosed authors; those cases are labeled accordingly. Community questions and blog posts never become conjecture candidates solely because of answer flags or feed language.

The verified primary feeds are [Terence Tao's RSS feed](https://terrytao.wordpress.com/feed/) and [Timothy Gowers's RSS feed](https://gowers.wordpress.com/feed/). The n-Category Café feed could not be reached during verification and is not enabled. Additions require a verified primary feed and corresponding hostname allowlist update; arbitrary feed URLs are rejected.

Requests accept bounded gzip/deflate responses, refuse feed DTD/entity declarations and unexpected redirects, and never send GitHub credentials to another provider. arXiv calls use a sequential 3.1-second spacing. Stack Exchange quota/backoff fields stop further calls and publish a next-eligible time; identical successful requests are reused within one minute. HTTP 429/503 `Retry-After` is recorded as a bounded deferral rather than retried in a busy loop. Scheduled jobs may be delayed, and source APIs may be incomplete or unavailable.

The source contracts are documented by [GitHub's search API](https://docs.github.com/en/rest/search/search), [arXiv's query API](https://info.arxiv.org/help/api/user-manual.html), [Stack Exchange question metadata](https://api.stackexchange.com/docs/types/question), [Stack Exchange throttling](https://api.stackexchange.com/docs/throttle) and [compression rules](https://api.stackexchange.com/docs/compression).

## Resumable all-subject arXiv metadata archive

The optional archive uses arXiv's official [OAI-PMH service](https://info.arxiv.org/help/oa/index.html) at `https://oaipmh.arxiv.org/oai`, with `ListRecords` and `metadataPrefix=arXiv`. Omitting a set requests all subjects. `--set math` limits a separate archive to mathematics. This interface exposes the latest metadata for each article; a metadata modification datestamp is not necessarily the submission date.

```sh
python anaxia.py archive harvest --max-pages 1
python anaxia.py archive status
python anaxia.py archive search "sum of squares" --limit 20

# Optional separate mathematics-only archive
python anaxia.py archive harvest --set math --database data/local/math.sqlite3 --state data/local/math-state.json --max-pages 1
```

Each invocation processes only its page budget. Rerun it to continue from the stored resumption token. Records, deletion tombstones and the next cursor are committed together in a SQLite transaction. The small JSON state file is an atomic, recoverable copy of that database cursor. Local archive files belong under ignored `data/local/`; full metadata databases and cursor files are not committed to GitHub. An archive cannot silently switch between all subjects and a selected set.

The archive downloads bibliographic metadata and abstracts, not PDFs, source bundles or article bodies. Search runs locally against records actually collected. Status distinguishes an empty, partial or completed OAI traversal and reports its real record count. Providing a resumable harvester does not mean that all of arXiv has already been collected. Harvesting can take many bounded invocations, and expired resumption tokens require a deliberate restart into a fresh archive rather than an automatic claim of completion.

arXiv states that its metadata may be reused in commercial and non-commercial systems; per-record license information and original arXiv links are retained. Consult the linked original paper for the permissions applying to full text. No release, Zenodo deposit, DOI registration, manuscript submission or other publication is performed by source discovery or local archive commands.
