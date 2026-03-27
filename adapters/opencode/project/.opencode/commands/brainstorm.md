# /brainstorm

Alias command for `.opencode/skills/brainstorm/SKILL.md`.

## Route

- Skill package: `.opencode/skills/brainstorm/SKILL.md`
- Entrypoint id: `brainstorm`
- Capture mode: `structured_choice`

## Alias Behavior

- Use the Explain -> Capture helper flow: explain the available options in plain text, then ask the user to choose or refine one explicitly.
- Preserve approval-before-write and user decision ownership from `AGENTS.md`.
- Keep output deterministic and aligned to the canonical workflow step order.
