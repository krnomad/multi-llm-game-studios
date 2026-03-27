# Multi-Harness Overview

## Purpose

This repository keeps one canonical source under `common/`, then projects that source into adapter-specific outputs for OpenCode, Codex, and OpenClaw.

## Source of truth

- Author canonical manifests in `common/manifests/`.
- Author canonical shared docs in `common/docs/`.
- Author compatibility and workaround policy in `common/compatibility/`.
- Respect the locked v0 scope in `common/docs/migration/v0-whitelist.md` before adding new canonical artifacts.
- The whitelist includes the approved v0 workflow surface, including `collaboration-approval-gate`.
- Treat `adapters/` as generated output, not the normal authoring surface.

## Generated targets

### OpenCode

- Support posture: `highest_fidelity_v0_target`
- Generated project root: `adapters/opencode/project/`
- Main surfaces: `opencode.json`, `AGENTS.md`, `.opencode/skills/`, `.opencode/commands/`, `.opencode/oh-my-opencode.jsonc`

### Codex

- Support posture: `supported_with_workarounds`
- Generated project root: `adapters/codex/project/`
- Main surfaces: `AGENTS.md`, `.codex/config.toml`, `.codex/agents/*.toml`, `.agents/skills/*/SKILL.md`
- First-class workaround package: `adapters/codex/install/global-agents/`

### OpenClaw

- Support posture: `repo_cli_compatibility_only`
- Generated output root: `adapters/openclaw/`
- Main surfaces: `openclaw.json5`, `workspace/SOUL.md`, `workspace/AGENTS.md`, `workspace/agents/`, `workspace/skills/`
- v0 goal is repository and CLI compatibility, not channel-native parity

## Maintainer workflow

1. Edit canonical files in `common/` only.
2. Regenerate all adapter outputs with `python3 tools/projectors/generate_all.py`.
3. Validate all generated outputs with `python3 tools/validate/run_all.py`.
4. Review generated adapter diffs, but do not hand-edit them as the normal workflow.

## What belongs where

- `common/` holds the durable, harness-neutral contract.
- `adapters/opencode/` holds the highest-fidelity projected repo.
- `adapters/codex/` holds a workaround-backed Codex repo plus the global-agent install package.
- `adapters/openclaw/` holds the repo and CLI oriented projection.

## Operator rule of thumb

If a maintainer wants to change behavior, start in `common/`. If a generated adapter file looks wrong, fix the canonical source or projector logic, then rerun generation.
