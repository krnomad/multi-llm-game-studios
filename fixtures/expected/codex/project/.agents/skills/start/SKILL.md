# start

This skill is projected for Codex from canonical manifests under `common/`.
Codex support remains workaround-backed rather than OpenCode-equivalent parity.

## Support posture
- supported_with_workarounds
- Workaround class: protocol_downgrade
- Invocation surface: explicit task intent for `start`

## Intent
Guide early-session onboarding by detecting project state, collecting the user's current starting point, routing to an appropriate next workflow, and requiring explicit user choice before handoff.

## Required inputs
- user_starting_point

## Required capabilities
- read
- glob
- grep
- user_prompt_capture
- structured_output

## Workflow steps
### detect_state
Silently inspect project context to tailor onboarding recommendations.
Requires confirmation: no

### capture_starting_point
Present starting-point options and capture the user's self-assessment.
Requires confirmation: yes

### route_path
Produce a recommended workflow path based on user input and detected state.
Requires confirmation: no

### confirm_next_step
Confirm user-selected next action before handoff and avoid auto-execution.
Requires confirmation: yes

## Structured choice workaround
Use explicit text-first options instead of assuming native selectable UI.
Label options deterministically as `OPTION_A`, `OPTION_B`, and so on.
Require the user response to include:
- `CHOSEN_OPTION: OPTION_X`
- `RATIONALE: <brief reason>`

## Outputs
- selected_next_action
- routed_workflow_path
- onboarding_rationale

## Codex projection notes
- Route command intent through explicit task entrypoints and wrapped choice prompts.
- Slash-style entry is represented as explicit command/task intent.

## Workaround rules
- `W_INTERACTIVE_CAPTURE_WRAPPED` / `generated_wrapper` / `interactive_capture`
  - Generate wrapper prompts and response parser with deterministic option labels.
- `W_SLASH_COMMAND_ROUTED` / `protocol_downgrade` / `slash_commands`
  - Expose command intent through explicit task/command entrypoints.
- `W_APPROVAL_PROTOCOL_ENFORCED` / `native_mapping` / `approval_before_write_protocol`
  - Enforce approval gate before_write in canonical workflow stages.

## Source refs
- Claude-Code-Game-Studios/.claude/skills/start/SKILL.md
- common/docs/workflows/onboarding.md
