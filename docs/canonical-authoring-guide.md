# Canonical Authoring Guide

## Rule one

Author in `common/` only.

That means:

- manifests go in `common/manifests/`
- shared docs go in `common/docs/`
- compatibility policy goes in `common/compatibility/`

Generated adapter files under `adapters/` are outputs. They are not the normal hand-edit surface.

## Authoring flow

1. Change the canonical file in `common/`.
2. Run `python3 tools/projectors/generate_all.py`.
3. Run `python3 tools/validate/run_all.py`.
4. Inspect the generated adapter changes.

## Canonical areas

### Manifests

- `common/manifests/agents/*.yaml`
- `common/manifests/skills/*.yaml`
- `common/manifests/policies/*.yaml`
- `common/manifests/workflows/*.yaml`

### Shared docs

- `common/docs/protocols/`
- `common/docs/workflows/`
- `common/docs/migration/`

## Scope lock

Before adding a new canonical artifact, check `common/docs/migration/v0-whitelist.md`.
If the artifact is not explicitly listed there for v0, update the whitelist first instead of letting a projector widen scope implicitly.

### Compatibility contracts

- `common/compatibility/feature-matrix.yaml`
- `common/compatibility/workaround-matrix.yaml`
- `common/compatibility/warning-taxonomy.yaml`

## What not to do

- Do not hand-edit `adapters/opencode/project/` as the normal workflow.
- Do not hand-edit `adapters/codex/project/` as the normal workflow.
- Do not hand-edit `adapters/openclaw/workspace/` as the normal workflow.
- Do not patch generated files first and backfill `common/` later.

## When adapter inspection is still useful

Read the generated adapter files to confirm that projection looks right for each target. If something is off, fix the canonical input or the projector, regenerate, and validate again.

## Operator commands

- Regenerate all targets: `python3 tools/projectors/generate_all.py`
- Validate all targets: `python3 tools/validate/run_all.py`

## Practical example

If a skill workflow changes, update the skill manifest in `common/manifests/skills/`, regenerate all adapters, then validate all adapters. Do not treat `.opencode/skills/`, `.agents/skills/`, or `workspace/skills/` as the primary edit point.
