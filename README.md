# FPC Bundle Builder

Automated portable builds of Free Pascal Compiler from GitLab sources.

## Workflow Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐
│  check-fpc-updates.yml  │     │   scheduled-builds.yml  │
│  (every 6 hours)        │     │  (daily/weekly)         │
│                         │     │                         │
│  Checks GitLab for      │     │  Runs on fixed schedule │
│  NEW commits only       │     │  regardless of commits  │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            │  (only if new commits)        │  (always)
            ▼                               ▼
        ┌───────────────────────────────────────┐
        │         build-orchestrator.yml        │
        │                                       │
        │  - Concurrency control                │
        │  - Decides which tiers to build       │
        │  - Creates release with manifest      │
        └───────────────────┬───────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │build-fpc- │   │build-fpc- │   │run-fpc-   │
    │host.yml   │   │cross.yml  │   │tests.yml  │
    │(3x: Win,  │   │(3x: Win,  │   │(3x: Win,  │
    │Linux,Mac) │   │Linux,Mac) │   │Linux,Mac) │
    └───────────┘   └───────────┘   └───────────┘
```

## Build Tiers

| Tier  | Targets                                       | Schedule      |
|-------|-----------------------------------------------|---------------|
| tier1 | Core targets (win32, win64, linux, darwin)    | Every build   |
| tier2 | Common targets (android, ios, freebsd, wasm)  | Daily         |
| tier3 | Extended targets (m68k, avr, z80, etc.)       | Weekly        |

## Configuration

- `fpc-config/versions.json` - FPC versions to build
- `fpc-config/targets.json` - Cross-compiler targets by tier

## Releases

Each FPC version gets one release (e.g., `v3.2.3-latest`) containing:
- Host compilers for Windows, Linux, macOS
- Cross-compilers for all built targets
- `manifest.json` for external discovery
