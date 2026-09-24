#!/usr/bin/env python3
"""Read-only recovery check after a chat interruption. Never dispatches a build.

Example: python3 tools/remote_status.py --commit <sha> --wait-seconds 180
Authentication is optional for this public repository; use GH_TOKEN or a private
--token-file if the unauthenticated API quota is exhausted. No token is printed.
"""
import argparse
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = 'https://api.github.com/repos/tobirama2904-cell/poco-survival-ue5'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--workflow', choices=['core', 'engine'], default='core')
    parser.add_argument('--wait-seconds', type=int, default=0)
    parser.add_argument('--token-file', type=Path)
    args = parser.parse_args()
    token = args.token_file.read_text().strip() if args.token_file else os.environ.get('GH_TOKEN', '')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'poco-build-recovery'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    def get(path):
        with urlopen(Request(BASE + path, headers=headers), timeout=20) as response:
            return json.load(response)
    release = get('/releases?per_page=1')
    print('PUBLISHED_RELEASE', release[0]['html_url'] if release else 'none', flush=True)
    deadline = time.monotonic() + min(max(args.wait_seconds, 0), 300)
    last = None
    while True:
        runs = get('/actions/runs?' + urlencode({'head_sha': args.commit, 'per_page': 20}))['workflow_runs']
        workflow_path = '.github/workflows/' + ('core-tests.yml' if args.workflow == 'core' else 'engine-probe.yml')
        core = next((r for r in runs if r['path'] == workflow_path), None)
        result = ({'commit': args.commit, 'id': core['id'], 'url': core['html_url'],
                   'status': core['status'], 'conclusion': core['conclusion'],
                   'test_scope': ('portable domain C++; NOT Unreal or Android' if args.workflow == 'core' else 'UHT/UBT and headless Unreal integration; NOT Android or visual gameplay')} if core else
                  {'commit': args.commit, 'status': 'not_found', 'conclusion': None})
        if result != last:
            print(json.dumps(result), flush=True)
            last = result
        if core and core['status'] == 'completed':
            Path('.cache').mkdir(exist_ok=True)
            Path('.cache/latest-' + args.workflow + '-status.json').write_text(json.dumps(result, indent=2) + '\n')
            return 0 if core['conclusion'] == 'success' else 1
        if time.monotonic() >= deadline:
            return 2
        time.sleep(5)

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except HTTPError as error:
        print('GitHub API HTTP', error.code, '(no automatic retry or duplicate dispatch)')
        raise SystemExit(3)
