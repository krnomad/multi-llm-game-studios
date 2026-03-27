import re
from pathlib import Path
from typing import Any, cast

import yaml


WARNING_TAXONOMY_PATH = Path("common/compatibility/warning-taxonomy.yaml")
WORKAROUND_MATRIX_PATH = Path("common/compatibility/workaround-matrix.yaml")
FEATURE_MATRIX_PATH = Path("common/compatibility/feature-matrix.yaml")

APPROVED_WORKAROUND_CLASSES = {
    "native_mapping",
    "generated_wrapper",
    "external_runner",
    "protocol_downgrade",
}

REQUIRED_HAZARD_CATEGORIES = {
    "model_tiers",
    "interactive_capture",
    "slash_commands",
    "hook_event_semantics",
    "permissions",
    "orchestration_assumptions",
    "skill_references",
    "approval_before_write_protocol",
    "skill_metadata",
    "task_subcall_delegation",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load(path.read_text(encoding="utf-8")))


def test_warning_codes_are_stable_unique_and_machine_testable() -> None:
    taxonomy = _read_yaml(WARNING_TAXONOMY_PATH)
    warnings = cast(list[dict[str, Any]], taxonomy["warnings"])

    codes = [item["code"] for item in warnings]
    assert len(codes) == len(set(codes))
    assert all(re.match(r"^W_[A-Z0-9_]+$", code) for code in codes)


def test_warning_taxonomy_fields_and_enums_are_strict() -> None:
    taxonomy = _read_yaml(WARNING_TAXONOMY_PATH)
    warnings = cast(list[dict[str, Any]], taxonomy["warnings"])
    allowed_severity = set(cast(list[str], taxonomy["allowed_severity"]))

    for item in warnings:
        assert item["severity"] in allowed_severity
        assert item["workaround_class"] in APPROVED_WORKAROUND_CLASSES
        assert item["warning_class"]
        assert item["trigger_condition"]
        assert item["recommended_fallback"]


def test_workaround_matrix_covers_required_v0_hazards_with_explicit_classes() -> None:
    matrix = _read_yaml(WORKAROUND_MATRIX_PATH)
    entries = cast(list[dict[str, Any]], matrix["hazard_workarounds"])

    found_categories = {entry["hazard_category"] for entry in entries}
    assert REQUIRED_HAZARD_CATEGORIES.issubset(found_categories)

    for entry in entries:
        assert entry["workaround_class"] in APPROVED_WORKAROUND_CLASSES
        assert entry["warning_code"]
        assert entry["recommended_fallback"]


def test_workaround_warnings_are_all_defined_in_taxonomy() -> None:
    taxonomy = _read_yaml(WARNING_TAXONOMY_PATH)
    matrix = _read_yaml(WORKAROUND_MATRIX_PATH)

    warning_codes = {
        cast(str, item["code"])
        for item in cast(list[dict[str, Any]], taxonomy["warnings"])
    }
    matrix_codes = {
        cast(str, entry["warning_code"])
        for entry in cast(list[dict[str, Any]], matrix["hazard_workarounds"])
    }

    assert matrix_codes.issubset(warning_codes)


def test_feature_matrix_support_posture_matches_required_targeting() -> None:
    matrix = _read_yaml(FEATURE_MATRIX_PATH)

    assert matrix["support_posture"] == {
        "opencode": "highest_fidelity_v0_target",
        "codex": "supported_with_workarounds",
        "openclaw": "repo_cli_compatibility_only",
    }


def test_feature_matrix_encodes_codex_project_local_agent_limitation() -> None:
    matrix = _read_yaml(FEATURE_MATRIX_PATH)
    codex_platform = next(
        item
        for item in cast(list[dict[str, Any]], matrix["platforms"])
        if cast(str, item["id"]) == "codex"
    )
    limitations = cast(list[dict[str, Any]], codex_platform.get("limitations", []))

    assert any(
        item["code"] == "W_CODEX_PROJECT_LOCAL_AGENT_LIMITATION" for item in limitations
    )
    assert any("project-local" in item["condition"].lower() for item in limitations)


def test_feature_matrix_uses_only_approved_workaround_classes() -> None:
    matrix = _read_yaml(FEATURE_MATRIX_PATH)

    for platform in cast(list[dict[str, Any]], matrix["platforms"]):
        for feature in cast(list[dict[str, Any]], platform["features"]):
            assert feature["workaround_class"] in APPROVED_WORKAROUND_CLASSES


def test_compatibility_contract_avoids_provider_tier_names() -> None:
    feature_matrix_text = FEATURE_MATRIX_PATH.read_text(encoding="utf-8").lower()
    workaround_matrix_text = WORKAROUND_MATRIX_PATH.read_text(encoding="utf-8").lower()

    assert "opus" not in feature_matrix_text
    assert "sonnet" not in feature_matrix_text
    assert "opus" not in workaround_matrix_text
    assert "sonnet" not in workaround_matrix_text


def test_hook_event_semantics_externalize_enforcement_for_non_native_targets() -> None:
    matrix = _read_yaml(WORKAROUND_MATRIX_PATH)
    taxonomy = _read_yaml(WARNING_TAXONOMY_PATH)

    hook_entry = next(
        entry
        for entry in cast(list[dict[str, Any]], matrix["hazard_workarounds"])
        if cast(str, entry["hazard_category"]) == "hook_event_semantics"
    )
    warning_entry = next(
        item
        for item in cast(list[dict[str, Any]], taxonomy["warnings"])
        if cast(str, item["code"]) == "W_HOOK_EVENT_DOWNGRADED"
    )

    assert hook_entry["workaround_class"] == "external_runner"
    assert "external runner" in cast(str, hook_entry["recommended_fallback"]).lower()
    assert warning_entry["workaround_class"] == "external_runner"
    assert "external runner" in cast(str, warning_entry["recommended_fallback"]).lower()
