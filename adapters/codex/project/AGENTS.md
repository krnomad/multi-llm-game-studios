# AGENTS.md

This Codex projection is generated from canonical manifests under `common/`.

## Support posture
- Codex: `supported_with_workarounds`
- Not OpenCode-equivalent fidelity.
- Limitation: Project-local custom agents are not a reliable native loading surface.
- Required fallback: Emit generated install wrapper for globally discoverable agent registration.

## Repository layout
- `.codex/config.toml` configures support posture and generated agent files.
- `.codex/agents/*.toml` contains project-local Codex agent definitions.
- `.agents/skills/*/SKILL.md` contains projected skill instructions.
- `adapters/codex/install/global-agents/` contains the first-class global install workaround package.

## Structured choice contract
- Use text-first deterministic options labeled `OPTION_A`, `OPTION_B`, and so on.
- Require explicit capture fields `CHOSEN_OPTION` and `RATIONALE`.
- Do not claim native selectable UI parity when Codex does not guarantee it.

## Agents
- creative-director — Final creative authority for game vision, tone, and cross-discipline direction.
- producer — Coordinates sprint planning, milestone delivery, and cross-team production risk management.
- qa-lead — Owns test strategy, bug triage, regression planning, and release quality gates.
- technical-director — Owns architecture, technology decisions, and performance-risk strategy across systems.

## Skills
- brainstorm — `brainstorm`
- design-review — `design-review`
- setup-engine — `setup-engine`
- start — `start`

## Policies
- commit-validation-intent
- test-standards

## Workflows
- collaboration-approval-gate — User-directed collaboration stages that preserve draft review and explicit approval before any write operation.
