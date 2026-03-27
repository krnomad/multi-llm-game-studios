# Workaround Matrix

## Default ladder

When a target cannot express a canonical behavior directly, use the approved workaround classes in this order:

1. `native_mapping`
2. `generated_wrapper`
3. `external_runner`
4. `protocol_downgrade`

Those classes are defined in `common/compatibility/workaround-matrix.yaml`.

## What each rung means

### `native_mapping`

Use the target's own feature surface while preserving the canonical meaning.

Examples:

- model profile normalization across all targets
- permission intent normalization across all targets
- approval-before-write invariants when the target can still preserve the rule plainly

### `generated_wrapper`

Use generated prompts, helpers, or metadata when the target needs extra structure to preserve the intent.

Examples:

- Codex and OpenClaw structured choice capture via deterministic option labels
- Codex skill metadata reshaping

### `external_runner`

Move enforcement to an explicit validator, wrapper script, or operator-controlled boundary when the runtime cannot enforce the rule itself.

Examples:

- OpenClaw policy guards
- OpenClaw workflow approval gates

### `protocol_downgrade`

Keep the semantic contract, but express it through a simpler interaction protocol because the native surface does not exist or is not stable.

Examples:

- Codex and OpenClaw slash-style skill invocation routed through explicit task or command entrypoints
- Codex and OpenClaw delegation reduced to explicit single-step checkpoints
- OpenClaw agent and skill manifests projected for repo and CLI use instead of native runtime parity

## Feature-specific examples from the current repo

- `interactive_capture` maps to `generated_wrapper` for Codex and OpenClaw, with `W_INTERACTIVE_CAPTURE_WRAPPED`
- `slash_commands` maps to `protocol_downgrade` for Codex and OpenClaw, with `W_SLASH_COMMAND_ROUTED`
- `hook_event_semantics` maps to `external_runner` for Codex and OpenClaw, with `W_HOOK_EVENT_DOWNGRADED`
- `approval_before_write_protocol` maps to `native_mapping` for OpenCode and Codex, with `W_APPROVAL_PROTOCOL_ENFORCED`
- OpenClaw workflow approval gates are externalized through `external_runner_metadata` rather than claimed as native parity
- OpenClaw `policy_guards` and `workflow_approval_gates` are `externalized` in `common/compatibility/feature-matrix.yaml`, which is why `adapters/openclaw/openclaw.json5` routes them through `external_runner_metadata`

## Operator guidance

Pick the first workaround class that preserves the canonical behavior honestly. If a target only supports repo and CLI projection, say that plainly. Do not upgrade the wording to native parity when the current adapter does not provide it.
