#!/usr/bin/env python3
"""
Generate a Markdown table of all available FPC releases with cross compilers.

Usage:
    python src/generate-releases-table.py [--repo OWNER/REPO] [--output FILE]

Requires:
    - requests (pip install requests)
"""

import argparse
import os
import sys
from collections import defaultdict

import requests


def get_releases(repo: str, token: str = None) -> list[dict]:
    """Get all releases from the repository."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    releases = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{repo}/releases"
        response = requests.get(
            url,
            headers=headers,
            params={"page": page, "per_page": per_page}
        )
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        releases.extend(data)
        if len(data) < per_page:
            break
        page += 1

    return releases


def parse_asset_name(name: str) -> dict:
    """
    Parse asset name to extract version, platform, and cross target info.

    Examples:
        fpc-3.2.3-windows.tar.gz -> {version: 3.2.3, platform: windows, cross: None}
        fpc-3.2.3-linux-cross-aarch64-linux.tar.gz -> {version: 3.2.3, platform: linux, cross: aarch64-linux}
        fpc-main-arm64-macos.tar.gz -> {version: main, platform: arm64-macos, cross: None}
    """
    if not name.endswith(".tar.gz"):
        return None

    name = name[:-7]  # Remove .tar.gz

    if not name.startswith("fpc-"):
        return None

    name = name[4:]  # Remove fpc-

    # Check for cross compiler pattern
    if "-cross-" in name:
        parts = name.split("-cross-")
        if len(parts) != 2:
            return None

        # Parse version and platform from first part
        first_part = parts[0]
        cross_target = parts[1]

        # Find the platform (last segment before -cross-)
        # Platforms: windows, linux, macos, arm64-macos
        if first_part.endswith("-arm64-macos"):
            platform = "arm64-macos"
            version = first_part[:-12]
        elif first_part.endswith("-macos"):
            platform = "macos"
            version = first_part[:-6]
        elif first_part.endswith("-linux"):
            platform = "linux"
            version = first_part[:-6]
        elif first_part.endswith("-windows"):
            platform = "windows"
            version = first_part[:-8]
        else:
            return None

        return {
            "version": version,
            "platform": platform,
            "cross": cross_target
        }
    else:
        # Host compiler
        if name.endswith("-arm64-macos"):
            platform = "arm64-macos"
            version = name[:-12]
        elif name.endswith("-macos"):
            platform = "macos"
            version = name[:-6]
        elif name.endswith("-linux"):
            platform = "linux"
            version = name[:-6]
        elif name.endswith("-windows"):
            platform = "windows"
            version = name[:-8]
        else:
            return None

        return {
            "version": version,
            "platform": platform,
            "cross": None
        }


def version_sort_key(version: str) -> tuple:
    """Sort key for versions (main comes first, then semantic versions descending)."""
    if version == "main":
        return (0, 0, 0, 0)

    parts = version.split(".")
    try:
        nums = [int(p) for p in parts]
        # Pad to 3 elements
        while len(nums) < 3:
            nums.append(0)
        # Return negative for descending order
        return (1, -nums[0], -nums[1], -nums[2])
    except ValueError:
        return (2, 0, 0, 0)


def generate_markdown_table(releases_data: dict, repo: str) -> str:
    """Generate Markdown table from releases data."""
    lines = []

    # Header
    lines.append("# Available FPC Builds")
    lines.append("")
    lines.append(f"Use with [visualdoj/setup-fpc](https://github.com/visualdoj/setup-fpc)")
    lines.append("")

    # Platform display names (GitHub runner names)
    platform_names = {
        "windows": "windows-latest",
        "linux": "ubuntu-latest",
        "macos": "macos-13",
        "arm64-macos": "macos-latest"
    }

    platforms = ["windows", "linux", "macos", "arm64-macos"]

    # Sort versions
    versions = sorted(releases_data.keys(), key=version_sort_key)

    # Single table with version, host, and available cross compilers
    lines.append("| Version | Host | Cross Compilers |")
    lines.append("|---------|------|-----------------|")

    for version in versions:
        release_url = f"https://github.com/{repo}/releases/tag/v{version}-latest"

        for platform in platforms:
            # Skip if no host compiler for this platform
            if platform not in releases_data[version]["hosts"]:
                continue

            host_asset = releases_data[version]["hosts"][platform]
            host_url = host_asset["url"]

            # Get cross compilers for this version+platform
            cross_links = []
            if platform in releases_data[version]["cross"]:
                for target in sorted(releases_data[version]["cross"][platform].keys()):
                    cross_asset = releases_data[version]["cross"][platform][target]
                    cross_links.append(f"[{target}]({cross_asset['url']})")

            cross_str = ", ".join(cross_links) if cross_links else "-"

            version_link = f"[{version}]({release_url})"
            host_link = f"[{platform_names[platform]}]({host_url})"

            lines.append(f"| {version_link} | {host_link} | {cross_str} |")

    lines.append("")
    lines.append(f"*Generated from [{repo}](https://github.com/{repo}/releases)*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown table of FPC releases"
    )
    parser.add_argument(
        "--repo",
        default="visualdoj/build-fpc-bundle",
        help="GitHub repository (default: visualdoj/build-fpc-bundle)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token (default: from GITHUB_TOKEN env var)"
    )
    args = parser.parse_args()

    print(f"Fetching releases from {args.repo}...", file=sys.stderr)

    # Get all releases (assets are included in the response)
    releases = get_releases(args.repo, args.token)

    # Filter to only version releases (v*-latest pattern)
    version_releases = [
        r for r in releases
        if r["tag_name"].startswith("v") and r["tag_name"].endswith("-latest")
    ]

    print(f"Found {len(version_releases)} version releases", file=sys.stderr)

    # Structure: {version: {hosts: {platform: asset}, cross: {platform: {target: asset}}}}
    releases_data = defaultdict(lambda: {"hosts": {}, "cross": defaultdict(dict)})

    for release in version_releases:
        tag = release["tag_name"]
        # Extract version from tag (v3.2.3-latest -> 3.2.3)
        version = tag[1:-7]  # Remove 'v' prefix and '-latest' suffix

        print(f"  Processing {tag}...", file=sys.stderr)

        assets = release.get("assets", [])

        for asset in assets:
            name = asset["name"]
            # Use browser_download_url for direct downloads
            url = asset["browser_download_url"]

            parsed = parse_asset_name(name)
            if not parsed:
                continue

            # Use version from tag, not from asset name (they should match)
            platform = parsed["platform"]
            cross = parsed["cross"]

            if cross:
                releases_data[version]["cross"][platform][cross] = {
                    "name": name,
                    "url": url
                }
            else:
                releases_data[version]["hosts"][platform] = {
                    "name": name,
                    "url": url
                }

    # Generate Markdown
    markdown = generate_markdown_table(dict(releases_data), args.repo)

    if args.output:
        with open(args.output, "w") as f:
            f.write(markdown)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
