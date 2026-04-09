#!/usr/bin/env python3
"""
Check for new commits in FPC GitLab repository and determine which versions need rebuilding.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime


def get_gitlab_ref_commit(api_base: str, ref: str, ref_type: str = 'branch') -> dict:
    """Fetch the latest commit info for a branch or tag from GitLab API."""
    # URL-encode ref name (e.g., "svn/fixes_2_2" -> "svn%2Ffixes_2_2")
    encoded_ref = urllib.parse.quote(ref, safe='')

    if ref_type == 'tag':
        url = f"{api_base}/repository/tags/{encoded_ref}"
    else:
        url = f"{api_base}/repository/branches/{encoded_ref}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return {
                'sha': data['commit']['id'],
                'date': data['commit']['committed_date'],
                'message': data['commit']['title']
            }
    except urllib.error.HTTPError as e:
        print(f"Warning: Could not fetch {ref_type} {ref}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching {ref_type} {ref}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='Check for FPC updates')
    parser.add_argument('--versions-config', required=True, help='Path to versions.json')
    parser.add_argument('--tracker', required=True, help='Path to current commit tracker')
    parser.add_argument('--output', required=True, help='Path to write updated tracker')
    parser.add_argument('--force', default='false', help='Force build regardless of changes')
    parser.add_argument('--version-filter', default='', help='Only check specific version')
    args = parser.parse_args()

    # Load configurations
    with open(args.versions_config, 'r') as f:
        versions_config = json.load(f)

    # Load current tracker
    try:
        with open(args.tracker, 'r') as f:
            tracker = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tracker = {}

    gitlab_api = versions_config.get('gitlab_api',
        'https://gitlab.com/api/v4/projects/freepascal.org%2Ffpc%2Fsource')

    versions_to_build = []
    updated_tracker = dict(tracker)
    force = args.force.lower() == 'true'

    for version in versions_config['versions']:
        if not version.get('enabled', True):
            continue

        version_name = version['name']
        ref = version['branch']  # Can be branch or tag name
        ref_type = version.get('ref_type', 'branch')  # 'branch' or 'tag'

        # Apply version filter if specified
        if args.version_filter and args.version_filter != version_name:
            continue

        print(f"Checking {version_name} ({ref_type}: {ref})...", file=sys.stderr)

        # Get latest commit from GitLab
        commit_info = get_gitlab_ref_commit(gitlab_api, ref, ref_type)
        if not commit_info:
            print(f"  Skipping {version_name}: could not fetch commit info", file=sys.stderr)
            continue

        current_sha = commit_info['sha']
        tracked_sha = tracker.get(version_name, {}).get('sha', '')

        # Check if we need to build
        needs_build = force or (current_sha != tracked_sha)

        if needs_build:
            print(f"  {version_name}: NEW commit {current_sha[:8]} (was: {tracked_sha[:8] if tracked_sha else 'none'})",
                  file=sys.stderr)
            versions_to_build.append({
                'name': version_name,
                'branch': branch,
                'bootstrap_fpc': version['bootstrap_fpc'],
                'run_tests': str(version.get('run_tests', False)).lower(),
                'commit': current_sha,
                'priority': version.get('priority', 99)
            })
            # Update tracker
            updated_tracker[version_name] = {
                'sha': current_sha,
                'date': commit_info['date'],
                'message': commit_info['message'],
                'last_checked': datetime.utcnow().isoformat() + 'Z'
            }
        else:
            print(f"  {version_name}: no changes (commit: {current_sha[:8]})", file=sys.stderr)
            # Update last_checked time
            if version_name in updated_tracker:
                updated_tracker[version_name]['last_checked'] = datetime.utcnow().isoformat() + 'Z'

    # Sort by priority (lower = higher priority)
    versions_to_build.sort(key=lambda x: x['priority'])

    # Write updated tracker
    with open(args.output, 'w') as f:
        json.dump(updated_tracker, f, indent=2)

    # Output for GitHub Actions
    has_updates = 'true' if versions_to_build else 'false'

    # Write to GITHUB_OUTPUT
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"has_updates={has_updates}\n")
            f.write(f"versions_to_build={json.dumps(versions_to_build)}\n")
    else:
        # For local testing
        print(f"has_updates={has_updates}")
        print(f"versions_to_build={json.dumps(versions_to_build)}")

    return 0 if versions_to_build or not force else 0


if __name__ == '__main__':
    sys.exit(main())
