#!/usr/bin/env python3
"""
Generate build matrices for cross-compilation based on tier configuration.
"""

import argparse
import json
import os
import sys


# Which targets can be built from which host OS
HOST_TARGET_COMPATIBILITY = {
    'Windows': {
        'can_build': [
            # Windows can build most targets with binutils
            'win32', 'win64', 'linux', 'freebsd', 'netbsd', 'openbsd',
            'go32v2', 'wince', 'embedded', 'nativent', 'android',
            'darwin', 'aix', 'solaris', 'haiku', 'aros', 'morphos',
            'amiga', 'atari', 'msdos', 'win16', 'java', 'wasi',
            'palmos', 'macosclassic', 'wii', 'gba', 'nds', 'symbian',
            'freertos', 'zxspectrum', 'msxdos', 'amstradcpc', 'sinclairql',
            'dragonfly', 'netware', 'netwlibc', 'os2', 'emx', 'watcom',
            'beos', 'wdosx', 'iphonesim'
        ],
        'exclude': ['ios']  # iOS requires macOS
    },
    'Linux': {
        'can_build': [
            'linux', 'win32', 'win64', 'freebsd', 'netbsd', 'openbsd',
            'embedded', 'wince', 'android', 'wasi', 'java',
            'freertos', 'solaris', 'haiku', 'aros', 'dragonfly'
        ],
        'exclude': ['darwin', 'ios', 'iphonesim']  # Apple targets need macOS
    },
    'macOS': {
        'can_build': [
            'darwin', 'ios', 'iphonesim', 'linux', 'win32', 'win64',
            'freebsd', 'embedded', 'wince', 'android', 'wasi', 'java',
            'freertos'
        ],
        'exclude': []
    }
}


def can_build_target(host_os: str, target_os: str) -> bool:
    """Check if a target OS can be built from a host OS."""
    compat = HOST_TARGET_COMPATIBILITY.get(host_os, {})
    if target_os in compat.get('exclude', []):
        return False
    # For simplicity, allow if in can_build list or not explicitly excluded
    return target_os in compat.get('can_build', [])


def main():
    parser = argparse.ArgumentParser(description='Generate build matrices')
    parser.add_argument('--targets-config', required=True, help='Path to targets.json')
    parser.add_argument('--tier', required=True, help='Comma-separated tiers to include')
    parser.add_argument('--version', required=True, help='FPC version')
    args = parser.parse_args()

    with open(args.targets_config, 'r') as f:
        config = json.load(f)

    tiers_to_include = [t.strip() for t in args.tier.split(',') if t.strip()]

    # Collect all targets from requested tiers
    all_targets = []
    for tier_name in tiers_to_include:
        tier_data = config.get('tiers', {}).get(tier_name, {})
        all_targets.extend(tier_data.get('targets', []))

    # Group targets by host OS
    matrices = {
        'windows': [],
        'linux': [],
        'macos': []
    }

    for target in all_targets:
        target_os = target.get('os', '')
        target_entry = {
            'cpu': target.get('cpu', ''),
            'os': target_os,
            'opt': target.get('opt', ''),
            'crossopt': target.get('crossopt', ''),
            'make_opt': target.get('make_opt', '')
        }

        # Add to compatible hosts
        if can_build_target('Windows', target_os):
            matrices['windows'].append(target_entry)
        if can_build_target('Linux', target_os):
            matrices['linux'].append(target_entry)
        if can_build_target('macOS', target_os):
            matrices['macos'].append(target_entry)

    # Remove duplicates (by cpu-os combination)
    for host in matrices:
        seen = set()
        unique = []
        for t in matrices[host]:
            key = f"{t['cpu']}-{t['os']}"
            if key not in seen:
                seen.add(key)
                unique.append(t)
        matrices[host] = unique

    # Output for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT', '')

    build_date = __import__('datetime').datetime.utcnow().strftime('%Y%m%d')
    release_tag = f"v{args.version}-{build_date}"

    outputs = {
        'host_matrix': json.dumps([
            {'os': 'windows-latest', 'name': 'windows'},
            {'os': 'ubuntu-latest', 'name': 'linux'},
            {'os': 'macos-26-intel', 'name': 'macos'},
            {'os': 'macos-latest', 'name': 'arm64-macos'}
        ]),
        'cross_matrix_windows': json.dumps(matrices['windows']),
        'cross_matrix_linux': json.dumps(matrices['linux']),
        'cross_matrix_macos': json.dumps(matrices['macos']),
        'cross_matrix_macos_arm64': json.dumps(matrices['macos']),
        'release_tag': release_tag,
        'build_date': build_date
    }

    if github_output:
        with open(github_output, 'a') as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")
    else:
        for key, value in outputs.items():
            print(f"{key}={value}")

    # Print summary to stderr
    print(f"Tiers: {tiers_to_include}", file=sys.stderr)
    print(f"Windows targets: {len(matrices['windows'])}", file=sys.stderr)
    print(f"Linux targets: {len(matrices['linux'])}", file=sys.stderr)
    print(f"macOS (x86_64) targets: {len(matrices['macos'])}", file=sys.stderr)
    print(f"macOS (arm64) targets: {len(matrices['macos'])}", file=sys.stderr)


if __name__ == '__main__':
    main()
