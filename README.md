# multi-llm-game-studios

Harness-neutral Game Studios adaptation of the original Claude-focused template, projected to:

- OpenCode / Oh My OpenCode
- OpenAI Codex
- OpenClaw (repo/CLI compatibility)

## Repository layout

- `common/` — canonical manifests, docs, schemas, compatibility contracts
- `adapters/` — generated target-specific projections
- `tools/` — generators and validators
- `tests/` — schema, manifest, projector, drift, and docs validation
- `fixtures/expected/` — expected generated outputs for drift checks

## Maintainer commands

- Generate all targets: `python3 tools/projectors/generate_all.py`
- Validate everything: `python3 tools/validate/run_all.py`

## Authoring rule

Edit canonical sources in `common/` only. Generated adapter outputs under `adapters/` are not the primary hand-edit surface.

## Scope lock

The v0 scope is locked in `common/docs/migration/v0-whitelist.md`.

## Upstream attribution

This project adapts ideas and source material from `Donchitos/Claude-Code-Game-Studios` into a multi-harness structure.
