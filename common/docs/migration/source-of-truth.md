# v0 Source of Truth (Frozen Claude Input)

This migration wave treats the existing Claude repository as **read-only source input**.

## Frozen inputs for v0

- Root `CLAUDE.md`
- Root `.claude/` tree (including agents, skills, hooks, rules, and docs)

## Contract

1. The files above are the canonical **migration input** for v0 extraction work.
2. They are **not** rewritten, moved, or normalized in place.
3. All migration outputs are authored outside the source repository under the new target paths (for example `common/` and `tests/`).
4. Any behavior or artifact included in v0 must be explicitly listed in `common/docs/migration/v0-whitelist.md`.

## Non-goals for this step

- No edits to `Claude-Code-Game-Studios/.claude/**`
- No edits to `Claude-Code-Game-Studios/CLAUDE.md`
- No implied support for Claude-only runtime affordances unless explicitly whitelisted and documented for projection
