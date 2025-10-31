#!/usr/bin/env python3
"""linkedin_publish.py

Minimal LinkedIn preview + posting helper for CircleCI.

Features (safe defaults):
- generate-previews: scan _posts for posts with category containing 'linkedin' and no linkedin_post_id; write previews to out dir
- post: post a single markdown file to LinkedIn (requires LINKEDIN_ACCESS_TOKEN); updates front-matter with linkedin_post_id and linkedin_post_url and can optionally commit back to git
- whoami: print person and org URNs for a token

This is intentionally minimal and safe: by default `post` only posts a single file passed with --file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

try:
    import requests
    import yaml
except Exception:
    print("This script requires the 'requests' and 'PyYAML' packages. Install with: pip install -r requirements.txt")
    sys.exit(2)

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


def parse_front_matter(text: str) -> Tuple[Dict, str]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    meta_raw, body = m.group(1), m.group(2)
    try:
        meta = yaml.safe_load(meta_raw) or {}
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        meta = {}
    return meta, body


def write_front_matter(path: Path, meta: Dict, body: str) -> None:
    yaml_block = yaml.safe_dump(meta, sort_keys=False).rstrip('\n')
    content = '---\n' + yaml_block + '\n---\n' + body.lstrip('\n')
    path.write_text(content, encoding='utf-8')


def find_linkedin_posts(posts_dir: Path) -> List[Path]:
    results: List[Path] = []
    patterns = (posts_dir.glob('*.md'), posts_dir.glob('*.markdown'))
    for p in (p for g in patterns for p in g):
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        meta, _ = parse_front_matter(text)
        categories = []
        if 'categories' in meta:
            categories = meta['categories'] if isinstance(meta['categories'], list) else [meta['categories']]
        if 'category' in meta:
            categories += meta['category'] if isinstance(meta['category'], list) else [meta['category']]
        categories = [c.lower() for c in categories if isinstance(c, str)]
        if 'linkedin' in categories and 'linkedin_post_id' not in meta:
            results.append(p)
    return results


def extract_preview_text(markdown: str, max_chars: int = 1200) -> str:
    md = re.sub(r'```[\s\S]*?```', '', markdown)
    md = re.sub(r'!\[.*?\]\(.*?\)', '', md)
    md = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', md)
    md = re.sub(r'[#>*`]', '', md)
    md = re.sub(r'\s+', ' ', md).strip()
    if len(md) <= max_chars:
        return md
    idx = md.rfind('.', 0, max_chars)
    if idx == -1:
        return md[:max_chars].rstrip() + '...'
    return md[: idx+1].strip()


def generate_previews_for_files(files: Iterable[Path], out_dir: Path) -> List[Tuple[Path, Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: List[Tuple[Path, Path]] = []
    for p in files:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        meta, body = parse_front_matter(text)
        preview = extract_preview_text(body, max_chars=1200)
        slug = p.stem
        out_file = out_dir / f"{slug}.txt"
        out_file.write_text(preview, encoding='utf-8')
        results.append((p, out_file))
    return results


def post_to_linkedin(access_token: str, author_urn: str, text: str) -> Dict:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    resp = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, data=json.dumps(payload))
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'LinkedIn API returned {resp.status_code}: {resp.text}')
    return resp.json()


def get_linkedin_author_urn(access_token: str) -> str:
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f'Failed to get /me from LinkedIn: {resp.status_code} {resp.text}')
    data = resp.json()
    if 'id' not in data:
        raise RuntimeError(f'LinkedIn /me response missing id: {data}')
    return f"urn:li:person:{data['id']}"


def git_commit_and_push(path: Path, message: str) -> None:
    name = os.environ.get('GIT_COMMITTER_NAME', os.environ.get('USER', 'circleci'))
    email = os.environ.get('GIT_COMMITTER_EMAIL', os.environ.get('USER_EMAIL', 'ci@example.com'))
    subprocess.run(['git', 'config', 'user.name', name], check=True)
    subprocess.run(['git', 'config', 'user.email', email], check=True)
    subprocess.run(['git', 'add', str(path)], check=True)
    try:
        subprocess.run(['git', 'commit', '-m', message], check=True)
    except subprocess.CalledProcessError:
        print('No changes to commit')
        return
    github_pat = os.environ.get('GITHUB_PAT')
    owner = os.environ.get('CIRCLE_PROJECT_USERNAME')
    repo = os.environ.get('CIRCLE_PROJECT_REPONAME')
    if github_pat and owner and repo:
        origin_url = f'https://x-access-token:{github_pat}@github.com/{owner}/{repo}.git'
        subprocess.run(['git', 'remote', 'set-url', 'origin', origin_url], check=True)
        subprocess.run(['git', 'push', 'origin', 'HEAD'], check=True)
        print('Pushed commit to origin')
    else:
        print('No GITHUB_PAT/CIRCLE_PROJECT_* available; attempting to push with existing credentials')
        subprocess.run(['git', 'push', 'origin', 'HEAD'], check=True)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')

    g = sub.add_parser('generate-previews')
    g.add_argument('--posts-dir', default='_posts')
    g.add_argument('--out-dir', default='linkedin_previews')

    p = sub.add_parser('post')
    p.add_argument('--file', help='Single markdown file to post (path)')
    p.add_argument('--posts-dir', default='_posts')
    p.add_argument('--commit-after-post', action='store_true')
    p.add_argument('--dry-run', action='store_true')

    w = sub.add_parser('whoami')

    args = parser.parse_args()

    if args.cmd == 'generate-previews':
        posts = find_linkedin_posts(Path(args.posts_dir))
        if not posts:
            print('No new linkedin posts found.')
            return
        generated = generate_previews_for_files(posts, Path(args.out_dir))
        print(f'Generated {len(generated)} previews:')
        for src, out in generated:
            print(f' - {src} -> {out}')

    elif args.cmd == 'post':
        access_token = os.environ.get('LINKEDIN_ACCESS_TOKEN')
        if not access_token:
            raise RuntimeError('Missing LINKEDIN_ACCESS_TOKEN environment variable')
        if args.file:
            targets = [Path(args.file)]
        else:
            targets = find_linkedin_posts(Path(args.posts_dir))
        if not targets:
            print('No targets to post')
            return
        author_urn = os.environ.get('LINKEDIN_AUTHOR_URN')
        if not author_urn:
            author_urn = get_linkedin_author_urn(access_token)
            print(f'Using author urn: {author_urn}')
        for t in targets:
            text = t.read_text(encoding='utf-8')
            meta, body = parse_front_matter(text)
            preview = extract_preview_text(body, max_chars=1300)
            print('Posting preview for', t)
            print(preview)
            if args.dry_run:
                print('Dry run enabled — not posting to LinkedIn')
                continue
            resp = post_to_linkedin(access_token, author_urn, preview)
            post_id = resp.get('id') or resp.get('serviceUrl') or json.dumps(resp)
            post_url = f'https://www.linkedin.com/feed/update/{post_id}' if isinstance(post_id, str) else str(post_id)
            meta['linkedin_post_id'] = post_id
            meta['linkedin_post_url'] = post_url
            write_front_matter(t, meta, body)
            print(f'Posted {t} => {post_url}')
            if args.commit_after_post:
                try:
                    git_commit_and_push(t, f'chore(linkedin): mark {t.name} as posted')
                except Exception as e:
                    print('Failed to commit/push changes:', e)

    elif args.cmd == 'whoami':
        access_token = os.environ.get('LINKEDIN_ACCESS_TOKEN')
        if not access_token:
            raise RuntimeError('Missing LINKEDIN_ACCESS_TOKEN environment variable')
        try:
            person_urn = get_linkedin_author_urn(access_token)
            print('Person URN:', person_urn)
        except Exception as e:
            print('Failed to fetch person URN:', e)
        try:
            # list organizations but ignore errors
            headers = {'Authorization': f'Bearer {access_token}'}
            url = 'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR&state=APPROVED'
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                urns = [el.get('organizationalTarget') for el in data.get('elements', []) if el.get('organizationalTarget')]
                if urns:
                    print('Organization URNs:')
                    for o in urns:
                        print(' -', o)
                else:
                    print('No organization URNs found (or insufficient permissions).')
            else:
                print('Failed to list organizations:', resp.status_code, resp.text)
        except Exception as e:
            print('Failed to list organizations:', e)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
