"""Update explicitly selected tool/engine gitlinks using public metadata only."""

import argparse
import base64
import html
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENGINE_FILES = {
    'src/ebllm/research/data/portfolio.json':'data/research-portfolio.json',
    'src/ebllm/research/data/public-upstream-watch.json':'data/public-upstream-watch.json',
    'src/ebllm/research/data/construction-atlas.json':'data/construction-atlas.json',
    'docs/RESEARCH-PORTFOLIO.md':'docs/RESEARCH-PORTFOLIO.md',
    'docs/PUBLIC-UPSTREAM-WATCH.md':'docs/PUBLIC-UPSTREAM-WATCH.md',
    'docs/CONSTRUCTION-ROUTES.md':'docs/CONSTRUCTION-ROUTES.md',
}


def engine_files(records):
    engine = next((item for item in records if item['upstream'].casefold() == 'creelie/ebllm'), None)
    if not engine:
        return {}
    content = {}
    for source, target in ENGINE_FILES.items():
        url = 'https://raw.githubusercontent.com/' + engine['upstream'] + '/' + engine['commit'] + '/' + source
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'OpenGluon-source-transfer'}), timeout=60) as response:
            text = response.read(12_000_001)
        if len(text) > 12_000_000:
            raise ValueError('Source data exceeds the per-file transfer limit')
        text = text.decode('utf-8')
        if source.endswith('.json'):
            json.loads(text)
        content[target] = text
    return content


def render_stats():
    quantum = json.loads((ROOT/'quantumlib-lock.json').read_text(encoding='utf-8'))
    portfolio = json.loads((ROOT/'data/research-portfolio.json').read_text(encoding='utf-8'))
    watch = json.loads((ROOT/'data/public-upstream-watch.json').read_text(encoding='utf-8'))
    atlas = json.loads((ROOT/'data/construction-atlas.json').read_text(encoding='utf-8'))
    entries=[(len(quantum['repositories']),'quantum source projects'),(portfolio['repository_count'],'research source records'),(watch['repository_count'],'public repositories watched'),(len(atlas['routes']),'construction routes')]
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="122" viewBox="0 0 1200 122" role="img" aria-label="Current source inventory counts"><rect width="1200" height="122" rx="16" fill="#0b1428"/>']
    for i,(value,label) in enumerate(entries):
        x=i*300+30
        parts.append(f'<text x="{x}" y="54" fill="#76ead4" font-family="Segoe UI,Arial,sans-serif" font-size="36" font-weight="600">{value:,}</text><text x="{x}" y="88" fill="#b4c8de" font-family="Segoe UI,Arial,sans-serif" font-size="15">{html.escape(label)}</text>')
    parts.append('</svg>')
    path=ROOT/'docs/assets/workspace-stats.svg'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(parts)+'\n',encoding='utf-8')
    readme=ROOT/'README.md'
    text=readme.read_text(encoding='utf-8')
    text=re.sub(r'\*\*\d+\*\* quantumlib projects',f'**{len(quantum["repositories"])}** quantumlib projects',text)
    text=re.sub(r'\*\*\d+\*\* public sources',f'**{portfolio["repository_count"]}** public sources',text)
    text=re.sub(r'\*\*\d+\*\* targeted routes',f'**{len(atlas["routes"])}** targeted routes',text)
    readme.write_text(text,encoding='utf-8')


def api(path):
    headers = {'Accept':'application/vnd.github+json','User-Agent':'OpenGluon-toolkit-sync','X-GitHub-Api-Version':'2022-11-28'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request('https://api.github.com' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()


def refresh(item):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', item['upstream']):
        raise ValueError('Invalid upstream owner/repository')
    if not re.fullmatch(r'(?:mathematics|engines)/[A-Za-z0-9_-]+', item['path']):
        raise ValueError('Tool paths must stay inside mathematics/ or engines/')
    metadata = api('/repos/' + item['upstream'])
    if metadata['private']:
        raise ValueError('Only public upstreams may be included')
    branch = metadata['default_branch']
    head = api('/repos/' + item['upstream'] + '/git/ref/heads/' + urllib.parse.quote(branch, safe=''))
    commit = head['object']['sha']
    if head['object']['type'] != 'commit' or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Invalid upstream commit')
    return dict(item, default_branch=branch, commit=commit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'toolkit-lock.json'
    old = json.loads(path.read_text(encoding='utf-8'))
    updated = [refresh(item) for item in old['repositories']]
    if updated == old['repositories']:
        print('All selected mathematical libraries and Anaxia are current.')
        return
    for before, after in zip(old['repositories'], updated):
        if before != after:
            print(after['upstream'] + ': ' + before['commit'][:12] + ' -> ' + after['commit'][:12])
    if args.dry_run:
        print('Dry run: no files or index entries changed.')
        return
    transferred = engine_files(updated)
    # All remote reads finish before any local mutation.
    for item in updated:
        key = 'submodule.' + item['path']
        git('config', '-f', '.gitmodules', key + '.path', item['path'])
        git('config', '-f', '.gitmodules', key + '.url', 'https://github.com/' + item['upstream'] + '.git')
        git('config', '-f', '.gitmodules', key + '.branch', item['default_branch'])
        git('update-index', '--add', '--cacheinfo', '160000,' + item['commit'] + ',' + item['path'])
    old['repositories'] = updated
    old['captured_at_utc'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(old, indent=2) + '\n', encoding='utf-8')
    git('add', '.gitmodules', 'toolkit-lock.json')
    for target, text in transferred.items():
        destination=ROOT/target
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(text,encoding='utf-8')
        git('add',target)
    if transferred:
        render_stats()
        git('add','README.md','docs/assets/workspace-stats.svg')
    print('Updated toolkit pins without executing upstream code.')


if __name__ == '__main__':
    main()
