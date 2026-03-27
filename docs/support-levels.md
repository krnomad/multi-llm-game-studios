# Support Levels

## Canonical posture values

The repository tracks support levels in `common/compatibility/feature-matrix.yaml`.
The current v0 scope itself is locked in `common/docs/migration/v0-whitelist.md`, including the single v0 workflow `collaboration-approval-gate`.

## OpenCode

- Posture: `highest_fidelity_v0_target`
- Meaning: OpenCode is the primary v0 projection target and prefers native mapping when canonical semantics line up.
- Maintainer expectation: `adapters/opencode/project/` is the closest generated form to the canonical manifests and workflow semantics.

## Codex

- Posture: `supported_with_workarounds`
- Meaning: Codex is supported, but some semantics depend on wrappers or fallback packaging.
- Known limitation: project-local custom agents are not treated as a reliable native loading surface.
- Concrete fallback: generated global-agent registration under `adapters/codex/install/global-agents/`
- Do not claim: OpenCode-equivalent fidelity or native selectable UI parity for structured choice flows.

## OpenClaw

- Posture: `repo_cli_compatibility_only`
- Meaning: v0 support is for repository layout and CLI-oriented use.
- Concrete surfaces: `adapters/openclaw/openclaw.json5`, `adapters/openclaw/workspace/SOUL.md`, `adapters/openclaw/workspace/AGENTS.md`, markdown-packaged agents and skills.
- Do not claim: gateway-native behavior, channel-native UI, or runtime hook parity.

## Feature-level interpretation

- OpenCode uses native support for agent manifests, skill manifests, policy guards, workflow approval gates, and delegation subcalls.
- Codex uses partial support for those same feature areas and depends on `generated_wrapper`, `protocol_downgrade`, and some native mapping.
- OpenClaw uses `cli_projection` for agent, skill, and delegation surfaces, and `externalized` handling for policy guards and workflow approval gates.

## Maintainer guidance

Use the posture labels as release language. If a feature needs fallback handling, describe the fallback plainly instead of implying parity that the current adapter does not provide.
