# brainstorm

OpenCode package for canonical skill `brainstorm`.

## Intent

Run collaborative game concept ideation from discovery through concept selection, loop definition, pillar alignment, feasibility framing, and approved concept persistence.

## Inputs

- `optional_theme_hint`
- `player_preferences`
- `practical_constraints`

## Interaction Contract

- Entrypoint: `brainstorm`
- Interactive capture mode: `structured_choice`
- OpenCode projection: `native_mapping` — Keep interactive concept choices native while preserving stepwise approvals.

## Workflow Steps

1. `parse_context` — Parse optional ideation hint and load existing concept artifacts when present. (requires confirmation: no)
1. `creative_discovery` — Gather emotional goals, player taste, and practical constraints through guided questions. (requires confirmation: yes)
1. `concept_generation` — Generate distinct concept options and capture a selected or merged direction. (requires confirmation: yes)
1. `loop_and_pillars` — Define core loops, pillars, anti-pillars, and target player motivations. (requires confirmation: yes)
1. `feasibility_alignment` — Recommend engine and scope tiers with explicit risks and MVP boundaries. (requires confirmation: yes)
1. `persist_concept` — Draft and save concept documentation only after explicit user confirmation. (requires confirmation: yes)
1. `propose_next_steps` — Output ordered downstream recommendations for setup, review, decomposition, and planning. (requires confirmation: no)

## Required Capabilities

- `read`
- `glob`
- `grep`
- `write`
- `user_prompt_capture`
- `structured_output`

## Outputs

- `chosen_concept_direction`
- `concept_pillars`
- `engine_recommendation`
- `concept_document_path`

## Preserved Compatibility Metadata

- `interactive_capture` -> `generated_wrapper` / `W_INTERACTIVE_CAPTURE_WRAPPED`: Generate wrapper prompts and response parser with deterministic option labels. [warning]
- `slash_commands` -> `protocol_downgrade` / `W_SLASH_COMMAND_ROUTED`: Expose command intent through explicit task/command entrypoints. [warning]
- `skill_metadata` -> `generated_wrapper` / `W_SKILL_METADATA_RESHAPED`: Generate adapter metadata while preserving invocation intent. [warning]

## Projection Notes

- `opencode` -> `native_mapping`: Keep interactive concept choices native while preserving stepwise approvals.
- `codex` -> `generated_wrapper`: Encode option selection as deterministic wrapper prompts with explicit labels.
- `openclaw` -> `protocol_downgrade`: Project guided ideation choices through protocol-downgraded task entrypoints.
