# brainstorm

This skill is projected for Codex from canonical manifests under `common/`.
Codex support remains workaround-backed rather than OpenCode-equivalent parity.

## Support posture
- supported_with_workarounds
- Workaround class: generated_wrapper
- Invocation surface: explicit task intent for `brainstorm`

## Intent
Run collaborative game concept ideation from discovery through concept selection, loop definition, pillar alignment, feasibility framing, and approved concept persistence.

## Required inputs
- optional_theme_hint
- player_preferences
- practical_constraints

## Required capabilities
- read
- glob
- grep
- write
- user_prompt_capture
- structured_output

## Workflow steps
### parse_context
Parse optional ideation hint and load existing concept artifacts when present.
Requires confirmation: no

### creative_discovery
Gather emotional goals, player taste, and practical constraints through guided questions.
Requires confirmation: yes

### concept_generation
Generate distinct concept options and capture a selected or merged direction.
Requires confirmation: yes

### loop_and_pillars
Define core loops, pillars, anti-pillars, and target player motivations.
Requires confirmation: yes

### feasibility_alignment
Recommend engine and scope tiers with explicit risks and MVP boundaries.
Requires confirmation: yes

### persist_concept
Draft and save concept documentation only after explicit user confirmation.
Requires confirmation: yes

### propose_next_steps
Output ordered downstream recommendations for setup, review, decomposition, and planning.
Requires confirmation: no

## Structured choice workaround
Use explicit text-first options instead of assuming native selectable UI.
Label options deterministically as `OPTION_A`, `OPTION_B`, and so on.
Require the user response to include:
- `CHOSEN_OPTION: OPTION_X`
- `RATIONALE: <brief reason>`

## Outputs
- chosen_concept_direction
- concept_pillars
- engine_recommendation
- concept_document_path

## Codex projection notes
- Encode option selection as deterministic wrapper prompts with explicit labels.
- Slash-style entry is represented as explicit command/task intent.

## Workaround rules
- `W_INTERACTIVE_CAPTURE_WRAPPED` / `generated_wrapper` / `interactive_capture`
  - Generate wrapper prompts and response parser with deterministic option labels.
- `W_SLASH_COMMAND_ROUTED` / `protocol_downgrade` / `slash_commands`
  - Expose command intent through explicit task/command entrypoints.
- `W_SKILL_METADATA_RESHAPED` / `generated_wrapper` / `skill_metadata`
  - Generate adapter metadata while preserving invocation intent.

## Source refs
- Claude-Code-Game-Studios/.claude/skills/brainstorm/SKILL.md
- common/docs/workflows/onboarding.md
- common/docs/workflows/engine-setup.md
