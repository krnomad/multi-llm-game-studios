import json
from pathlib import Path
from typing import Any, cast

import jsonschema
import pytest
import yaml
from jsonschema.exceptions import ValidationError


SCHEMA_DIR = Path("common/schema")


def _load_schema(name: str) -> dict[str, Any]:
    return cast(
        dict[str, Any], json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
    )


def _validate(schema_name: str, fixture_yaml: str) -> None:
    schema = _load_schema(schema_name)
    data = cast(dict[str, Any], yaml.safe_load(fixture_yaml))
    jsonschema.Draft202012Validator(schema).validate(data)


def test_agent_schema_accepts_task4_contract_fixture() -> None:
    fixture = """
schema_version: "1.0"
kind: agent
id: creative-director
title: Creative Director
purpose: Maintains coherent vision and decision quality.
collaboration_contract_ref: collaboration-protocol
capabilities: [strategic_decisioning, collaborative_consulting, interactive_capture]
model_profile: strategic_high
tool_capability_needs: [read, glob, grep, write, edit]
delegation_intent: single_delegate
source_refs:
  - Claude-Code-Game-Studios/.claude/agents/creative-director.md:1-175
projection_notes:
  - target: codex
    note: Use generated wrapper for missing structured capture primitives.
    workaround_class: generated_wrapper
warning_rules:
  - code: W_INTERACTIVE_CAPTURE_WRAPPED
    trigger_condition: Structured choice capture unavailable natively.
    recommended_fallback: Use generated wrapper and deterministic prompt labels.
"""
    _validate("agent.schema.json", fixture)


def test_agent_schema_rejects_missing_plan_required_field() -> None:
    fixture = """
id: producer
title: Producer
purpose: Coordinates planning and delivery.
collaboration_contract_ref: collaboration-protocol
capabilities: [planning, coordination]
model_profile: strategic_high
tool_capability_needs: [read, write]
delegation_intent: none
source_refs: [Claude-Code-Game-Studios/.claude/agents/producer.md:1-148]
projection_notes:
  - target: opencode
    note: Native mapping.
    workaround_class: native_mapping
"""
    schema = _load_schema("agent.schema.json")
    data = cast(dict[str, Any], yaml.safe_load(fixture))
    with pytest.raises(ValidationError):
        jsonschema.Draft202012Validator(schema).validate(data)


def test_agent_schema_rejects_provider_specific_model_tier() -> None:
    fixture = """
id: qa-lead
title: QA Lead
purpose: Drives validation and release gates.
collaboration_contract_ref: collaboration-protocol
capabilities: [quality_assurance]
model_profile: opus
tool_capability_needs: [read, grep]
delegation_intent: none
source_refs: [Claude-Code-Game-Studios/.claude/agents/qa-lead.md:1-107]
projection_notes:
  - target: openclaw
    note: Repo/CLI compatibility only.
    workaround_class: protocol_downgrade
warning_rules:
  - code: W_MODEL_PROFILE_NORMALIZED
    trigger_condition: Provider tier name detected.
    recommended_fallback: Normalize to canonical model profile.
"""
    schema = _load_schema("agent.schema.json")
    data = cast(dict[str, Any], yaml.safe_load(fixture))
    with pytest.raises(ValidationError):
        jsonschema.Draft202012Validator(schema).validate(data)


def test_skill_schema_accepts_task5_contract_fixture() -> None:
    fixture = """
schema_version: "1.0"
kind: skill
id: brainstorm
user_entrypoint: brainstorm
intent: Guided concept ideation with user decision checkpoints.
required_inputs: [theme_or_open]
interactive_capture_mode: structured_choice
workflow_steps:
  - step_id: discovery
    intent: Gather goals and constraints.
    requires_confirmation: false
  - step_id: concept_selection
    intent: Capture user choice among options.
    requires_confirmation: true
required_capabilities: [read, write, user_prompt_capture]
outputs: [design/gdd/game-concept.md]
source_refs:
  - Claude-Code-Game-Studios/.claude/skills/brainstorm/SKILL.md:1-210
workaround_rules:
  - hazard_category: interactive_capture
    workaround_class: generated_wrapper
    warning_code: W_INTERACTIVE_CAPTURE_WRAPPED
projection_notes:
  - target: codex
    note: Structured capture projected via generated wrapper.
    workaround_class: generated_wrapper
"""
    _validate("skill.schema.json", fixture)


def test_skill_schema_rejects_unapproved_workaround_class() -> None:
    fixture = """
id: setup-engine
user_entrypoint: setup-engine
intent: Configure engine workspace and references.
required_inputs: [engine, version]
interactive_capture_mode: hybrid
workflow_steps:
  - step_id: configure
    intent: Apply selected engine setup.
    requires_confirmation: true
required_capabilities: [read, write]
outputs: [docs/engine-reference]
source_refs: [Claude-Code-Game-Studios/.claude/skills/setup-engine/SKILL.md:1-220]
workaround_rules:
  - hazard_category: slash_commands
    workaround_class: manual_patch
    warning_code: W_SLASH_COMMAND_ROUTED
projection_notes:
  - target: openclaw
    note: Route to CLI-compatible entrypoint.
    workaround_class: protocol_downgrade
"""
    schema = _load_schema("skill.schema.json")
    data = cast(dict[str, Any], yaml.safe_load(fixture))
    with pytest.raises(ValidationError):
        jsonschema.Draft202012Validator(schema).validate(data)


def test_policy_schema_accepts_yaml_positive_fixture() -> None:
    fixture = """
schema_version: "1.0"
kind: policy
id: test-standards
title: Test Standards
enforcement:
  level: required
  applies_to: [workflow, runtime]
rules:
  - code: POL_TESTS_REQUIRED
    statement: Relevant tests must run before completion.
    severity: warning
    failure_mode: block
"""
    _validate("policy.schema.json", fixture)


def test_policy_schema_rejects_invalid_rule_code() -> None:
    fixture = """
schema_version: "1.0"
kind: policy
id: commit-validation-intent
title: Commit Validation Intent
enforcement:
  level: required
  applies_to: [runtime]
rules:
  - code: bad_rule_code
    statement: Block dangerous operations.
    severity: error
    failure_mode: block
"""
    schema = _load_schema("policy.schema.json")
    data = cast(dict[str, Any], yaml.safe_load(fixture))
    with pytest.raises(ValidationError):
        jsonschema.Draft202012Validator(schema).validate(data)


def test_workflow_schema_accepts_yaml_positive_fixture() -> None:
    fixture = """
schema_version: "1.0"
kind: workflow
id: collaboration-protocol
summary: User-directed collaborative sequence.
stages:
  - stage_id: question
    objective: Clarify constraints.
    actor: agent
    approval_gate: none
    fallback_strategy: native_mapping
  - stage_id: approval
    objective: Capture approval before write.
    actor: user
    approval_gate: before_write
    fallback_strategy: protocol_downgrade
invariants:
  approval_before_write: true
  human_decision_owner: true
"""
    _validate("workflow.schema.json", fixture)


def test_workflow_schema_rejects_unknown_fallback_strategy() -> None:
    fixture = """
schema_version: "1.0"
kind: workflow
id: onboarding
summary: Onboarding flow.
stages:
  - stage_id: draft
    objective: Prepare initial draft.
    actor: agent
    approval_gate: before_write
    fallback_strategy: custom_proxy
invariants:
  approval_before_write: true
  human_decision_owner: true
"""
    schema = _load_schema("workflow.schema.json")
    data = cast(dict[str, Any], yaml.safe_load(fixture))
    with pytest.raises(ValidationError):
        jsonschema.Draft202012Validator(schema).validate(data)


def test_agent_schema_model_profiles_are_generic_and_plan_aligned() -> None:
    schema = _load_schema("agent.schema.json")
    profiles = set(schema["properties"]["model_profile"]["enum"])

    assert profiles == {
        "strategic_high",
        "quality_mid",
        "delivery_balanced",
        "utility_fast",
    }
    assert "opus" not in profiles
    assert "sonnet" not in profiles
