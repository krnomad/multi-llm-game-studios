# design-review

This skill is projected for Codex from canonical manifests under `common/`.
Codex support remains workaround-backed rather than OpenCode-equivalent parity.

## Support posture
- supported_with_workarounds
- Workaround class: protocol_downgrade
- Invocation surface: explicit task intent for `design-review`

## Intent
Perform read-only design quality review against completeness, consistency, implementability, and verdict criteria, then return structured findings and context-sensitive next-step recommendations without changing project files.

## Required inputs
- target_design_doc_path

## Required capabilities
- read
- glob
- grep
- structured_output

## Workflow steps
### load_review_inputs
Read target document, standards context, and related dependency documents.
Requires confirmation: no

### evaluate_quality_dimensions
Apply checklist, consistency, implementability, and cross-system checks.
Requires confirmation: no

### issue_verdict
Produce structured findings and verdict while remaining read-only.
Requires confirmation: no

### recommend_next_action
Provide context-sensitive guidance based on document type and verdict.
Requires confirmation: no

## Outputs
- design_review_report
- completeness_score
- verdict_classification
- prioritized_recommendations

## Codex projection notes
- Route invocation through explicit command intent while keeping report sections stable.
- Slash-style entry is represented as explicit command/task intent.

## Workaround rules
- `W_SLASH_COMMAND_ROUTED` / `protocol_downgrade` / `slash_commands`
  - Expose command intent through explicit task/command entrypoints.
- `W_SKILL_METADATA_RESHAPED` / `generated_wrapper` / `skill_metadata`
  - Generate adapter metadata while preserving invocation intent.

## Source refs
- Claude-Code-Game-Studios/.claude/skills/design-review/SKILL.md
- common/docs/workflows/design-review.md
