# /design-review

Alias command for `.opencode/skills/design-review/SKILL.md`.

## Route

- Skill package: `.opencode/skills/design-review/SKILL.md`
- Entrypoint id: `design-review`
- Capture mode: `none`

## Alias Behavior

- This alias is a thin command surface for a read-only or direct skill flow.
- Preserve approval-before-write and user decision ownership from `AGENTS.md`.
- Keep output deterministic and aligned to the canonical workflow step order.
