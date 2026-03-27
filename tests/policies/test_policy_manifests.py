import json
from pathlib import Path
from typing import cast

import jsonschema
import yaml


POLICY_SCHEMA_PATH = Path("common/schema/policy.schema.json")
WORKFLOW_SCHEMA_PATH = Path("common/schema/workflow.schema.json")

COMMIT_POLICY_PATH = Path("common/manifests/policies/commit-validation-intent.yaml")
TEST_STANDARDS_PATH = Path("common/manifests/policies/test-standards.yaml")
APPROVAL_WORKFLOW_PATH = Path(
    "common/manifests/workflows/collaboration-approval-gate.yaml"
)

DISALLOWED_SOURCE_VOCABULARY = {
    "SessionStart",
    "PreToolUse",
    "PostToolUse",
    ".claude/settings.json",
}


Manifest = dict[str, object]
Rule = dict[str, str]
Stage = dict[str, str]


def _load_json(path: Path) -> Manifest:
    return cast(Manifest, json.loads(path.read_text(encoding="utf-8")))


def _load_yaml(path: Path) -> Manifest:
    return cast(Manifest, yaml.safe_load(path.read_text(encoding="utf-8")))


def test_commit_validation_policy_matches_schema_and_canonical_scope() -> None:
    schema = _load_json(POLICY_SCHEMA_PATH)
    manifest = _load_yaml(COMMIT_POLICY_PATH)

    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(manifest)

    assert manifest["enforcement"] == {
        "level": "blocking",
        "applies_to": ["workflow", "runtime"],
    }

    codes = [rule["code"] for rule in cast(list[Rule], manifest["rules"])]
    assert codes == [
        "POL_VALIDATE_DESIGN_DOC_COMPLETENESS",
        "POL_VALIDATE_STRUCTURED_DATA_INTEGRITY",
        "POL_WARN_ON_ACTIONABLE_CODE_QUALITY_SIGNALS",
        "POL_REQUIRE_VISIBLE_FALLBACK_HANDLING",
    ]


def test_commit_validation_policy_normalizes_hook_specific_source_terms() -> None:
    text = COMMIT_POLICY_PATH.read_text(encoding="utf-8")

    for token in DISALLOWED_SOURCE_VOCABULARY:
        assert token not in text

    assert "commit-equivalent approval boundary" in text
    assert "protocol_downgrade" in text
    assert "external_runner" in text


def test_commit_validation_policy_requires_explicit_non_silent_fallbacks() -> None:
    manifest = _load_yaml(COMMIT_POLICY_PATH)
    rules = {rule["code"]: rule for rule in cast(list[Rule], manifest["rules"])}

    fallback_rule = rules["POL_REQUIRE_VISIBLE_FALLBACK_HANDLING"]
    assert fallback_rule["severity"] == "error"
    assert fallback_rule["failure_mode"] == "fallback"
    assert "must not silently omit" in fallback_rule["statement"]
    assert "external_runner" in fallback_rule["statement"]
    assert "protocol_downgrade" in fallback_rule["statement"]


def test_test_standards_policy_matches_schema_and_enforcement_modes() -> None:
    schema = _load_json(POLICY_SCHEMA_PATH)
    manifest = _load_yaml(TEST_STANDARDS_PATH)

    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(manifest)

    assert manifest["enforcement"] == {
        "level": "required",
        "applies_to": ["agent", "workflow", "runtime"],
    }

    rules = {rule["code"]: rule for rule in cast(list[Rule], manifest["rules"])}

    assert rules["POL_UNIT_TESTS_ARE_DETERMINISTIC"]["failure_mode"] == "block"
    assert rules["POL_INTEGRATION_TESTS_CLEAN_UP"]["failure_mode"] == "block"
    assert rules["POL_PERFORMANCE_TESTS_DECLARE_THRESHOLDS"]["severity"] == "error"
    assert rules["POL_BUG_FIXES_INCLUDE_REGRESSION_TESTS"]["failure_mode"] == "fallback"
    assert (
        "external_runner fallback"
        in rules["POL_BUG_FIXES_INCLUDE_REGRESSION_TESTS"]["statement"]
    )


def test_collaboration_workflow_matches_schema_and_stage_order() -> None:
    schema = _load_json(WORKFLOW_SCHEMA_PATH)
    manifest = _load_yaml(APPROVAL_WORKFLOW_PATH)

    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(manifest)

    stages = cast(list[Stage], manifest["stages"])
    assert [stage["stage_id"] for stage in stages] == [
        "question",
        "options",
        "decision",
        "draft",
        "approval",
    ]
    assert manifest["invariants"] == {
        "approval_before_write": True,
        "human_decision_owner": True,
    }


def test_collaboration_workflow_uses_canonical_approval_semantics_not_tool_names() -> (
    None
):
    manifest = _load_yaml(APPROVAL_WORKFLOW_PATH)
    text = APPROVAL_WORKFLOW_PATH.read_text(encoding="utf-8")
    stages = {
        stage["stage_id"]: stage for stage in cast(list[Stage], manifest["stages"])
    }

    assert stages["approval"]["approval_gate"] == "before_write"
    assert stages["approval"]["fallback_strategy"] == "external_runner"
    assert stages["draft"]["fallback_strategy"] == "protocol_downgrade"
    assert "AskUserQuestion" not in text
    assert "PreToolUse" not in text
    assert "Write|Edit" not in text


def test_workflow_preserves_failure_path_when_native_approval_hook_is_missing() -> None:
    manifest = _load_yaml(APPROVAL_WORKFLOW_PATH)
    stages = {
        stage["stage_id"]: stage for stage in cast(list[Stage], manifest["stages"])
    }

    approval_stage = stages["approval"]
    assert approval_stage["actor"] == "user"
    assert approval_stage["approval_gate"] == "before_write"
    assert approval_stage["fallback_strategy"] == "external_runner"

    draft_stage = stages["draft"]
    assert draft_stage["approval_gate"] == "none"
    assert draft_stage["fallback_strategy"] == "protocol_downgrade"
