# start

OpenCode package for canonical skill `start`.

## Intent

Guide early-session onboarding by detecting project state, collecting the user's current starting point, routing to an appropriate next workflow, and requiring explicit user choice before handoff.

## Inputs

- `user_starting_point`

## Interaction Contract

- Entrypoint: `start`
- Interactive capture mode: `structured_choice`
- OpenCode projection: `native_mapping` — Preserve structured onboarding choices through native prompt interactions.

## Workflow Steps

1. `detect_state` — Silently inspect project context to tailor onboarding recommendations. (requires confirmation: no)
1. `capture_starting_point` — Present starting-point options and capture the user's self-assessment. (requires confirmation: yes)
1. `route_path` — Produce a recommended workflow path based on user input and detected state. (requires confirmation: no)
1. `confirm_next_step` — Confirm user-selected next action before handoff and avoid auto-execution. (requires confirmation: yes)

## Required Capabilities

- `read`
- `glob`
- `grep`
- `user_prompt_capture`
- `structured_output`

## Outputs

- `selected_next_action`
- `routed_workflow_path`
- `onboarding_rationale`

## Preserved Compatibility Metadata

- `interactive_capture` -> `generated_wrapper` / `W_INTERACTIVE_CAPTURE_WRAPPED`: Generate wrapper prompts and response parser with deterministic option labels. [warning]
- `slash_commands` -> `protocol_downgrade` / `W_SLASH_COMMAND_ROUTED`: Expose command intent through explicit task/command entrypoints. [warning]
- `approval_before_write_protocol` -> `native_mapping` / `W_APPROVAL_PROTOCOL_ENFORCED`: Enforce approval gate before_write in canonical workflow stages. [info]

## Projection Notes

- `opencode` -> `native_mapping`: Preserve structured onboarding choices through native prompt interactions.
- `codex` -> `protocol_downgrade`: Route command intent through explicit task entrypoints and wrapped choice prompts.
- `openclaw` -> `generated_wrapper`: Use wrapper-based structured choices in repo or CLI interaction surfaces.
