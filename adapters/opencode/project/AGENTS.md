# AGENTS.md

This OpenCode / Oh My OpenCode v0 slice is generated from canonical manifests under `common/`. Treat this file as the instruction surface for the projected repo.

## Collaboration Contract

- Stage order: `Question -> Options -> Decision -> Draft -> Approval`
- Approval before write: `true`
- Human decision owner: `true`
- Do not commit changes unless the user explicitly asks for a commit.

## OpenCode v0 Mapping

- Target posture: `highest_fidelity_v0_target`
- Native mapping is preferred for this target whenever canonical semantics are available directly.
- Canonical skill entrypoints are packaged under `.opencode/skills/<id>/SKILL.md`.
- Command aliases and helper templates are packaged under `.opencode/commands/` when entrypoint routing or text capture needs an explicit surface.
- Lower-fidelity workaround metadata is preserved in `.opencode/oh-my-opencode.jsonc` rather than silently dropped.

## Skill Entrypoints

- `start` -> `.opencode/skills/start/SKILL.md` (structured_choice)
- `brainstorm` -> `.opencode/skills/brainstorm/SKILL.md` (structured_choice)
- `setup-engine` -> `.opencode/skills/setup-engine/SKILL.md` (hybrid)
- `design-review` -> `.opencode/skills/design-review/SKILL.md` (none)

## Agents

### Creative Director (`creative-director`)

- Purpose: Final creative authority for game vision, tone, and cross-discipline direction.
- Model profile: `strategic_high`
- Delegation intent: `single_delegate`
- Capabilities:
  - `strategic_decision_framing`
  - `cross_discipline_alignment`
  - `structured_choice_capture`
- Tool capability needs:
  - `file_read`
  - `file_write`
  - `file_edit`
  - `pattern_search`
  - `text_search`
  - `web_fetch`
- Warning rules:
  - `W_MODEL_PROFILE_NORMALIZED`: Persist canonical model_profile strategic_high.
  - `W_INTERACTIVE_CAPTURE_WRAPPED`: Use generated wrapper prompts with deterministic option labels.

### Technical Director (`technical-director`)

- Purpose: Owns architecture, technology decisions, and performance-risk strategy across systems.
- Model profile: `strategic_high`
- Delegation intent: `single_delegate`
- Capabilities:
  - `architecture_governance`
  - `strategic_decision_framing`
  - `technical_risk_management`
  - `structured_choice_capture`
- Tool capability needs:
  - `file_read`
  - `file_write`
  - `file_edit`
  - `pattern_search`
  - `text_search`
  - `web_fetch`
  - `execute_shell`
- Warning rules:
  - `W_MODEL_PROFILE_NORMALIZED`: Persist canonical model_profile strategic_high.
  - `W_INTERACTIVE_CAPTURE_WRAPPED`: Use generated wrapper prompts with deterministic option labels.

### Producer (`producer`)

- Purpose: Coordinates sprint planning, milestone delivery, and cross-team production risk management.
- Model profile: `strategic_high`
- Delegation intent: `multi_delegate`
- Capabilities:
  - `production_coordination`
  - `sprint_planning`
  - `risk_management`
  - `structured_choice_capture`
- Tool capability needs:
  - `file_read`
  - `file_write`
  - `file_edit`
  - `pattern_search`
  - `text_search`
  - `web_fetch`
  - `execute_shell`
- Warning rules:
  - `W_MODEL_PROFILE_NORMALIZED`: Persist canonical model_profile strategic_high.
  - `W_INTERACTIVE_CAPTURE_WRAPPED`: Use generated wrapper prompts with deterministic option labels.

### QA Lead (`qa-lead`)

- Purpose: Owns test strategy, bug triage, regression planning, and release quality gates.
- Model profile: `quality_mid`
- Delegation intent: `single_delegate`
- Capabilities:
  - `quality_gate_enforcement`
  - `test_strategy_planning`
  - `bug_triage_governance`
- Tool capability needs:
  - `file_read`
  - `file_write`
  - `file_edit`
  - `pattern_search`
  - `text_search`
  - `execute_shell`
- Warning rules:
  - `W_MODEL_PROFILE_NORMALIZED`: Persist canonical model_profile quality_mid.
  - `W_APPROVAL_PROTOCOL_ENFORCED`: Enforce approval gate before_write in canonical workflow stages.

## Policy Guards

### Commit Validation Intent (`commit-validation-intent`)

- Enforcement level: `blocking`
- Applies to: workflow, runtime
- Rules:
  - `POL_VALIDATE_DESIGN_DOC_COMPLETENESS` (warning/warn): Before a commit-equivalent approval boundary, changed design documents must be checked for required sections such as Overview, Player Fantasy, Detailed Rules, Formulas, Edge Cases, Dependencies, Tuning Knobs, and Acceptance Criteria; when native lifecycle hooks are unavailable, preserve this intent through protocol_downgrade into canonical pre-commit validation stages rather than dropping the check.
  - `POL_VALIDATE_STRUCTURED_DATA_INTEGRITY` (error/block): Machine-readable project data must be syntactically valid before the commit-equivalent action proceeds; invalid structured data blocks progression, and runtimes without native commit interception must run the validation through an external_runner so the blocking guarantee remains explicit.
  - `POL_WARN_ON_ACTIONABLE_CODE_QUALITY_SIGNALS` (warning/warn): Implementation changes should surface actionable warnings for obvious anti-patterns such as unowned TODO or FIXME markers and hardcoded gameplay balance values that belong in data, with warnings preserved even when enforcement is routed through protocol_downgrade or external_runner fallback paths.
  - `POL_REQUIRE_VISIBLE_FALLBACK_HANDLING` (error/fallback): If a target runtime cannot express native pre-commit validation hooks, the harness must route commit-validation intent to external_runner or protocol_downgrade handling and must not silently omit the validation boundary.

### Test Standards (`test-standards`)

- Enforcement level: `required`
- Applies to: agent, workflow, runtime
- Rules:
  - `POL_TEST_NAMES_ARE_DESCRIPTIVE` (warning/warn): Tests should use descriptive names that encode the system, scenario, and expected result so failures remain readable and reviewable.
  - `POL_TESTS_USE_CLEAR_STRUCTURE` (warning/warn): Tests should make setup, execution, and assertion steps explicit so intent is inspectable and regressions are easy to diagnose.
  - `POL_UNIT_TESTS_ARE_DETERMINISTIC` (error/block): Unit tests must not depend on uncontrolled external state such as filesystem, network, database, or shared mutable data; external dependencies should be mocked so checks stay fast and deterministic.
  - `POL_INTEGRATION_TESTS_CLEAN_UP` (error/block): Integration tests must clean up resources they create so repeated runs produce the same outcome and do not poison later validation cycles.
  - `POL_PERFORMANCE_TESTS_DECLARE_THRESHOLDS` (error/block): Performance tests must state an acceptable threshold and fail when the measured result exceeds it so performance regressions are objective.
  - `POL_BUG_FIXES_INCLUDE_REGRESSION_TESTS` (warning/fallback): A bug fix should include a regression test that would have caught the original failure, preserving the validation signal across future changes even if the target runner executes tests via external_runner fallback.
