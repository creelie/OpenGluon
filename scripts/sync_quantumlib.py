"""Refresh pinned upstream commits without checking out or executing upstream code.

Requires Python 3.9+, Git, and network access to the public GitHub REST API.
GH_TOKEN is optional locally; Actions supplies its scoped GITHUB_TOKEN.
"""

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = 'https://api.github.com'
ORGANIZATION = 'quantumlib'


def api(path):
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'OpenGluon-upstream-sync',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(API_ROOT + path, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def public_repositories():
    repositories = []
    page = 1
    while True:
        batch = api(f'/orgs/{ORGANIZATION}/repos?type=public&sort=full_name&per_page=100&page={page}')
        if not isinstance(batch, list):
            raise RuntimeError('GitHub returned an invalid repository inventory')
        repositories.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    if not repositories:
        raise RuntimeError('Refusing to replace the inventory with an empty result')
    return sorted(repositories, key=lambda item: item['name'].casefold())


def record(repository):
    name = repository['name']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or name in ('.', '..'):
        raise RuntimeError('Unsafe upstream repository name')
    if repository.get('owner', {}).get('login', '').casefold() != ORGANIZATION:
        raise RuntimeError('Unexpected upstream owner')
    branch = repository['default_branch']
    route = f'/repos/{ORGANIZATION}/{urllib.parse.quote(name, safe="")}/git/ref/heads/{urllib.parse.quote(branch, safe="")}'
    head = api(route)
    commit = head['object']['sha']
    if head['object']['type'] != 'commit' or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise RuntimeError('Unexpected default-branch commit for ' + name)
    return {
        'name': name,
        'upstream': ORGANIZATION + '/' + name,
        'url': f'https://github.com/{ORGANIZATION}/{name}',
        'clone_url': f'https://github.com/{ORGANIZATION}/{name}.git',
        'path': ORGANIZATION + '/' + name,
        'default_branch': branch,
        'commit': commit,
        'archived': repository['archived'],
        'description': repository.get('description') or '',
        'license_spdx': (repository.get('license') or {}).get('spdx_id'),
    }


def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def inventory_table(records, retained):
    lines = [
        '| Project | Local path | Pinned commit | Archived | Description |',
        '| --- | --- | --- | --- | --- |',
    ]
    for item in records:
        description = item['description'].replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
        if item['name'] in retained:
            description += ' (Retained: upstream absent from the current public inventory.)'
        lines.append(f'| [{item["name"]}]({item["url"]}) | `{item["path"]}` | `{item["commit"][:12]}` | {"Yes" if item["archived"] else "No"} | {description} |')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Read upstream state and report differences without modifying files or the Git index')
    args = parser.parse_args()
    previous = json.loads((ROOT / 'quantumlib-lock.json').read_text(encoding='utf-8'))
    old_records = {item['name']: item for item in previous['repositories']}
    current = public_repositories()
    new_records = {}
    for repository in current:
        try:
            item = record(repository)
        except urllib.error.HTTPError as error:
            if error.code != 409 or repository['size'] != 0:
                raise
            print('Skipping empty repository with no commit:', repository['name'])
            continue
        new_records[item['name']] = item
    retained = sorted(set(old_records) - set(new_records), key=str.casefold)
    for name in retained:
        new_records[name] = old_records[name]
    records = sorted(new_records.values(), key=lambda item: item['name'].casefold())
    changed = [item['name'] for item in records if old_records.get(item['name']) != item]
    if not changed and previous.get('retained_missing_upstreams', []) == retained:
        print(f'All {len(records)} repositories are current.')
        return
    print('Changed repositories:', ', '.join(changed) or '(inventory availability only)')
    if retained:
        print('Retained absent upstreams:', ', '.join(retained))
    if args.dry_run:
        print('Dry run: no files or index entries changed.')
        return
    for item in records:
        key = 'submodule.' + item['path']
        git('config', '-f', '.gitmodules', key + '.path', item['path'])
        git('config', '-f', '.gitmodules', key + '.url', item['clone_url'])
        git('config', '-f', '.gitmodules', key + '.branch', item['default_branch'])
        git('update-index', '--add', '--cacheinfo', '160000,' + item['commit'] + ',' + item['path'])
    updated = {
        'organization': ORGANIZATION,
        'inventory_source': f'{API_ROOT}/orgs/{ORGANIZATION}/repos?type=public&per_page=100',
        'captured_at_utc': datetime.now(timezone.utc).isoformat(),
        'repository_count': len(records),
        'repositories': records,
    }
    if retained:
        updated['retained_missing_upstreams'] = retained
    (ROOT / 'quantumlib-lock.json').write_text(json.dumps(updated, indent=2) + '\n', encoding='utf-8', newline='\n')
    readme_path = ROOT / 'docs/QUANTUMLIB.md'
    readme = readme_path.read_text(encoding='utf-8')
    start = readme.index('| Project | Local path | Pinned commit | Archived | Description |')
    end = readme.index('\n\nThe complete commit IDs', start)
    readme = readme[:start] + inventory_table(records, retained) + readme[end:]
    readme = re.sub(r'\*\*\d+ public repositories\*\*', f'**{len(records)} public repositories**', readme, count=1)
    readme_path.write_text(readme, encoding='utf-8', newline='\n')
    git('add', '.gitmodules', 'quantumlib-lock.json', 'docs/QUANTUMLIB.md')
    print(f'Updated and staged {len(records)} repository pins. Upstream code was not executed.')


if __name__ == '__main__':
    main()
