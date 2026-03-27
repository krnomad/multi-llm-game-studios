# setup-engine

OpenCode package for canonical skill `setup-engine`.

## Intent

Select or confirm engine and version, draft technical defaults, classify knowledge-gap risk, and produce version-aware references with approval before persistence.

## Inputs

- `engine_choice_or_guided_mode`
- `target_version`
- `project_constraints`

## Interaction Contract

- Entrypoint: `setup-engine`
- Interactive capture mode: `hybrid`
- OpenCode projection: `native_mapping` — Map setup flow directly while preserving explicit user approval before writes.

## Workflow Steps

1. `parse_mode` — Determine explicit-input, engine-only, guided, or refresh mode. (requires confirmation: no)
1. `choose_engine` — Gather constraints, recommend options, and capture user engine choice. (requires confirmation: yes)
1. `resolve_version` — Confirm selected version from user input or current stable references. (requires confirmation: yes)
1. `draft_configuration_changes` — Prepare project configuration updates and show planned edits before writes. (requires confirmation: yes)
1. `draft_technical_preferences` — Generate engine defaults and request approval before persistence. (requires confirmation: yes)
1. `classify_knowledge_risk` — Classify low, medium, or high version-risk against trusted baseline. (requires confirmation: no)
1. `produce_reference_docs` — Create minimal or full version-pinned references based on risk level. (requires confirmation: yes)
1. `summarize_handoff` — Output setup summary and ordered downstream next-step guidance. (requires confirmation: no)

## Required Capabilities

- `read`
- `glob`
- `grep`
- `write`
- `edit`
- `web_lookup`
- `fetch_url`
- `staged_delegation`
- `user_prompt_capture`
- `structured_output`

## Outputs

- `pinned_engine_configuration`
- `approved_technical_preferences`
- `knowledge_risk_classification`
- `engine_reference_artifacts`

## Preserved Compatibility Metadata

- `task_subcall_delegation` -> `protocol_downgrade` / `W_TASK_DELEGATION_BRIDGED`: Downgrade to explicit single-step delegation with surfaced checkpoints. [warning]
- `slash_commands` -> `protocol_downgrade` / `W_SLASH_COMMAND_ROUTED`: Expose command intent through explicit task/command entrypoints. [warning]
- `skill_metadata` -> `generated_wrapper` / `W_SKILL_METADATA_RESHAPED`: Generate adapter metadata while preserving invocation intent. [warning]
- `approval_before_write_protocol` -> `native_mapping` / `W_APPROVAL_PROTOCOL_ENFORCED`: Enforce approval gate before_write in canonical workflow stages. [info]

## Projection Notes

- `opencode` -> `native_mapping`: Map setup flow directly while preserving explicit user approval before writes.
- `codex` -> `protocol_downgrade`: Downgrade deep delegation assumptions to explicit staged checkpoints.
- `openclaw` -> `generated_wrapper`: Use wrapper metadata for setup-stage prompts and version verification notes.
