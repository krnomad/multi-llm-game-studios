import json
from pathlib import Path
from typing import cast

import jsonschema
import yaml


SKILLS_DIR = Path("common/manifests/skills")
SKILL_SCHEMA_PATH = Path("common/schema/skill.schema.json")

EXPECTED_SKILL_FILES = {
    "start.yaml",
    "brainstorm.yaml",
    "setup-engine.yaml",
    "design-review.yaml",
}

EXPECTED_CAPTURE_MODES = {
    "start": "structured_choice",
    "brainstorm": "structured_choice",
    "setup-engine": "hybrid",
    "design-review": "none",
}

APPROVED_WORKAROUND_CLASSES = {
    "native_mapping",
    "generated_wrapper",
    "external_runner",
    "protocol_downgrade",
}

EXPECTED_PHASE_IDS = {
    "start": [
        "detect_state",
        "capture_starting_point",
        "route_path",
        "confirm_next_step",
    ],
    "brainstorm": [
        "parse_context",
        "creative_discovery",
        "concept_generation",
        "loop_and_pillars",
        "feasibility_alignment",
        "persist_concept",
        "propose_next_steps",
    ],
    "setup-engine": [
        "parse_mode",
        "choose_engine",
        "resolve_version",
        "draft_configuration_changes",
        "draft_technical_preferences",
        "classify_knowledge_risk",
        "produce_reference_docs",
        "summarize_handoff",
    ],
    "design-review": [
        "load_review_inputs",
        "evaluate_quality_dimensions",
        "issue_verdict",
        "recommend_next_action",
    ],
}

FORBIDDEN_RAW_TOKENS = {
    "AskUserQuestion",
    "WebSearch",
    "WebFetch",
    "Task",
}

FORBIDDEN_SLASH_COMMAND_SYNTAX = {
    "`/start`",
    "`/brainstorm`",
    "`/setup-engine`",
    "`/design-review`",
}


def _load_schema() -> dict[str, object]:
    return cast(
        dict[str, object], json.loads(SKILL_SCHEMA_PATH.read_text(encoding="utf-8"))
    )


def _load_manifest(path: Path) -> dict[str, object]:
    return cast(dict[str, object], yaml.safe_load(path.read_text(encoding="utf-8")))


def test_skill_manifest_file_set_is_exact_v0_scope() -> None:
    found = {path.name for path in SKILLS_DIR.glob("*.yaml")}
    assert found == EXPECTED_SKILL_FILES


def test_skill_manifests_validate_against_skill_schema() -> None:
    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)

    for path in sorted(SKILLS_DIR.glob("*.yaml")):
        validator.validate(_load_manifest(path))


def test_skill_manifests_preserve_capture_modes_and_workflow_step_order() -> None:
    for path in sorted(SKILLS_DIR.glob("*.yaml")):
        manifest = _load_manifest(path)
        skill_id = cast(str, manifest["id"])
        workflow_steps = cast(list[dict[str, object]], manifest["workflow_steps"])

        assert manifest["interactive_capture_mode"] == EXPECTED_CAPTURE_MODES[skill_id]
        step_ids = [cast(str, step["step_id"]) for step in workflow_steps]
        assert step_ids == EXPECTED_PHASE_IDS[skill_id]


def test_skill_manifests_have_required_workaround_metadata_for_non_native_targets() -> (
    None
):
    for path in sorted(SKILLS_DIR.glob("*.yaml")):
        manifest = _load_manifest(path)
        rules = cast(list[dict[str, object]], manifest["workaround_rules"])
        projections = cast(list[dict[str, object]], manifest["projection_notes"])

        assert rules
        assert projections

        classes = {cast(str, rule["workaround_class"]) for rule in rules}
        assert classes.issubset(APPROVED_WORKAROUND_CLASSES)
        assert "protocol_downgrade" in classes

        for rule in rules:
            assert cast(str, rule["hazard_category"])
            assert cast(str, rule["warning_code"]).startswith("W_")

        for note in projections:
            assert note["target"] in {"opencode", "codex", "openclaw"}
            assert cast(str, note["workaround_class"]) in APPROVED_WORKAROUND_CLASSES
            assert cast(str, note["note"])


def test_skill_manifests_reject_raw_claude_only_tokens() -> None:
    for path in sorted(SKILLS_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        for raw_name in FORBIDDEN_RAW_TOKENS:
            assert raw_name not in text
        for slash_syntax in FORBIDDEN_SLASH_COMMAND_SYNTAX:
            assert slash_syntax not in text


def test_skill_manifests_do_not_use_rejected_old_shape_fields() -> None:
    forbidden_keys = {
        "description:",
        "invocation:",
        "workflow:",
        "tool_contract:",
        "compatibility:",
    }

    for path in sorted(SKILLS_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        for key in forbidden_keys:
            assert key not in text


def test_design_review_manifest_is_read_only() -> None:
    manifest = _load_manifest(SKILLS_DIR / "design-review.yaml")
    capabilities = set(cast(list[str], manifest["required_capabilities"]))

    assert "write" not in capabilities
    assert "edit" not in capabilities
    assert "read-only" in cast(str, manifest["intent"]).lower()
