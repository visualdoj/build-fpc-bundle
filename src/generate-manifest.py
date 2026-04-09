#!/usr/bin/env python3
"""
Generate a release manifest JSON file listing all available artifacts.

This manifest allows external GitHub Actions to discover and download
the appropriate FPC bundles for their target platform.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_artifact_name(filename: str) -> dict:
    """
    Parse artifact filename to extract components.

    Expected formats:
    - fpc-{version}-{host_os}.tar.gz                    (host compiler)
    - fpc-{version}-{host_os}-cross-{cpu}-{os}.tar.gz   (cross compiler)
    """
    # Remove .tar.gz extension
    name = filename.replace('.tar.gz', '')

    # Try cross-compiler pattern first
    cross_match = re.match(
        r'^fpc-([0-9.]+)-(\w+)-cross-(\w+)-(\w+)$',
        name
    )
    if cross_match:
        return {
            'type': 'cross',
            'version': cross_match.group(1),
            'host_os': cross_match.group(2),
            'target_cpu': cross_match.group(3),
            'target_os': cross_match.group(4),
            'filename': filename
        }

    # Try host compiler pattern
    host_match = re.match(
        r'^fpc-([0-9.]+)-(\w+)$',
        name
    )
    if host_match:
        return {
            'type': 'host',
            'version': host_match.group(1),
            'host_os': host_match.group(2),
            'filename': filename
        }

    return None


def main():
    parser = argparse.ArgumentParser(description='Generate release manifest')
    parser.add_argument('--version', required=True, help='FPC version')
    parser.add_argument('--branch', required=True, help='Git branch')
    parser.add_argument('--commit', default='', help='Git commit SHA')
    parser.add_argument('--artifacts-dir', required=True, help='Directory containing artifacts')
    parser.add_argument('--output', required=True, help='Output manifest file')
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)

    manifest = {
        'version': args.version,
        'branch': args.branch,
        'commit': args.commit,
        'build_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'schema_version': '1.0',
        'artifacts': {
            'windows': {'host': None, 'cross': {}},
            'linux': {'host': None, 'cross': {}},
            'macos': {'host': None, 'cross': {}}
        }
    }

    # Find all .tar.gz files
    tar_files = []
    if artifacts_dir.exists():
        for root, dirs, files in os.walk(artifacts_dir):
            for f in files:
                if f.endswith('.tar.gz'):
                    tar_files.append(f)

    print(f"Found {len(tar_files)} artifacts", file=sys.stderr)

    for filename in tar_files:
        parsed = parse_artifact_name(filename)
        if not parsed:
            print(f"  Skipping unrecognized: {filename}", file=sys.stderr)
            continue

        host_os = parsed['host_os']
        if host_os not in manifest['artifacts']:
            print(f"  Skipping unknown host OS: {host_os}", file=sys.stderr)
            continue

        if parsed['type'] == 'host':
            manifest['artifacts'][host_os]['host'] = filename
            print(f"  Host ({host_os}): {filename}", file=sys.stderr)
        elif parsed['type'] == 'cross':
            target_key = f"{parsed['target_cpu']}-{parsed['target_os']}"
            manifest['artifacts'][host_os]['cross'][target_key] = filename
            print(f"  Cross ({host_os} -> {target_key}): {filename}", file=sys.stderr)

    # Generate summary
    summary = {
        'total_artifacts': len(tar_files),
        'hosts': {},
        'cross_targets': set()
    }

    for host_os, data in manifest['artifacts'].items():
        host_count = 1 if data['host'] else 0
        cross_count = len(data['cross'])
        summary['hosts'][host_os] = {
            'host': host_count,
            'cross': cross_count
        }
        summary['cross_targets'].update(data['cross'].keys())

    manifest['summary'] = {
        'total_artifacts': summary['total_artifacts'],
        'hosts': summary['hosts'],
        'available_targets': sorted(summary['cross_targets'])
    }

    # Write manifest
    with open(args.output, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to {args.output}", file=sys.stderr)
    print(f"Summary: {json.dumps(manifest['summary'], indent=2)}", file=sys.stderr)


if __name__ == '__main__':
    main()
