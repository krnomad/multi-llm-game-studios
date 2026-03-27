# design-review

OpenCode package for canonical skill `design-review`.

## Intent

Perform read-only design quality review against completeness, consistency, implementability, and verdict criteria, then return structured findings and context-sensitive next-step recommendations without changing project files.

## Inputs

- `target_design_doc_path`

## Interaction Contract

- Entrypoint: `design-review`
- Interactive capture mode: `none`
- OpenCode projection: `native_mapping` — Preserve read-only review output contract as a native analysis step.

## Workflow Steps

1. `load_review_inputs` — Read target document, standards context, and related dependency documents. (requires confirmation: no)
1. `evaluate_quality_dimensions` — Apply checklist, consistency, implementability, and cross-system checks. (requires confirmation: no)
1. `issue_verdict` — Produce structured findings and verdict while remaining read-only. (requires confirmation: no)
1. `recommend_next_action` — Provide context-sensitive guidance based on document type and verdict. (requires confirmation: no)

## Required Capabilities

- `read`
- `glob`
- `grep`
- `structured_output`

## Outputs

- `design_review_report`
- `completeness_score`
- `verdict_classification`
- `prioritized_recommendations`

## Preserved Compatibility Metadata

- `slash_commands` -> `protocol_downgrade` / `W_SLASH_COMMAND_ROUTED`: Expose command intent through explicit task/command entrypoints. [warning]
- `skill_metadata` -> `generated_wrapper` / `W_SKILL_METADATA_RESHAPED`: Generate adapter metadata while preserving invocation intent. [warning]

## Projection Notes

- `opencode` -> `native_mapping`: Preserve read-only review output contract as a native analysis step.
- `codex` -> `protocol_downgrade`: Route invocation through explicit command intent while keeping report sections stable.
- `openclaw` -> `generated_wrapper`: Keep review read-only and emit structured report sections through wrapper formatting.
