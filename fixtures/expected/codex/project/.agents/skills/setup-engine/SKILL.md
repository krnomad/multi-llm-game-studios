# setup-engine

This skill is projected for Codex from canonical manifests under `common/`.
Codex support remains workaround-backed rather than OpenCode-equivalent parity.

## Support posture
- supported_with_workarounds
- Workaround class: protocol_downgrade
- Invocation surface: explicit task intent for `setup-engine`

## Intent
Select or confirm engine and version, draft technical defaults, classify knowledge-gap risk, and produce version-aware references with approval before persistence.

## Required inputs
- engine_choice_or_guided_mode
- target_version
- project_constraints

## Required capabilities
- read
- glob
- grep
- write
- edit
- web_lookup
- fetch_url
- staged_delegation
- user_prompt_capture
- structured_output

## Workflow steps
### parse_mode
Determine explicit-input, engine-only, guided, or refresh mode.
Requires confirmation: no

### choose_engine
Gather constraints, recommend options, and capture user engine choice.
Requires confirmation: yes

### resolve_version
Confirm selected version from user input or current stable references.
Requires confirmation: yes

### draft_configuration_changes
Prepare project configuration updates and show planned edits before writes.
Requires confirmation: yes

### draft_technical_preferences
Generate engine defaults and request approval before persistence.
Requires confirmation: yes

### classify_knowledge_risk
Classify low, medium, or high version-risk against trusted baseline.
Requires confirmation: no

### produce_reference_docs
Create minimal or full version-pinned references based on risk level.
Requires confirmation: yes

### summarize_handoff
Output setup summary and ordered downstream next-step guidance.
Requires confirmation: no

## Structured choice workaround
Use explicit text-first options instead of assuming native selectable UI.
Label options deterministically as `OPTION_A`, `OPTION_B`, and so on.
Require the user response to include:
- `CHOSEN_OPTION: OPTION_X`
- `RATIONALE: <brief reason>`

## Outputs
- pinned_engine_configuration
- approved_technical_preferences
- knowledge_risk_classification
- engine_reference_artifacts

## Codex projection notes
- Downgrade deep delegation assumptions to explicit staged checkpoints.
- Slash-style entry is represented as explicit command/task intent.

## Workaround rules
- `W_TASK_DELEGATION_BRIDGED` / `protocol_downgrade` / `task_subcall_delegation`
  - Downgrade to explicit single-step delegation with surfaced checkpoints.
- `W_SLASH_COMMAND_ROUTED` / `protocol_downgrade` / `slash_commands`
  - Expose command intent through explicit task/command entrypoints.
- `W_SKILL_METADATA_RESHAPED` / `generated_wrapper` / `skill_metadata`
  - Generate adapter metadata while preserving invocation intent.
- `W_APPROVAL_PROTOCOL_ENFORCED` / `native_mapping` / `approval_before_write_protocol`
  - Enforce approval gate before_write in canonical workflow stages.

## Source refs
- Claude-Code-Game-Studios/.claude/skills/setup-engine/SKILL.md
- common/docs/workflows/engine-setup.md
- common/docs/workflows/validation-intent.md
