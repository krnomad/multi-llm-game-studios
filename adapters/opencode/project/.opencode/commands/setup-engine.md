# /setup-engine

Alias command for `.opencode/skills/setup-engine/SKILL.md`.

## Route

- Skill package: `.opencode/skills/setup-engine/SKILL.md`
- Entrypoint id: `setup-engine`
- Capture mode: `hybrid`

## Alias Behavior

- Use the Explain -> Capture helper flow: explain the available options in plain text, then ask the user to choose or refine one explicitly.
- Preserve approval-before-write and user decision ownership from `AGENTS.md`.
- Keep output deterministic and aligned to the canonical workflow step order.
