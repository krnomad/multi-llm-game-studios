import json
from pathlib import Path
from typing import Any, cast

import jsonschema
import yaml


AGENT_DIR = Path("common/manifests/agents")
AGENT_SCHEMA_PATH = Path("common/schema/agent.schema.json")

EXPECTED_FILES = {
    "creative-director.yaml",
    "technical-director.yaml",
    "producer.yaml",
    "qa-lead.yaml",
}

EXPECTED_MODEL_PROFILES = {
    "creative-director": "strategic_high",
    "technical-director": "strategic_high",
    "producer": "strategic_high",
    "qa-lead": "quality_mid",
}

EXPECTED_TOOL_CAPABILITY_NEEDS = {
    "creative-director": {
        "file_read",
        "file_write",
        "file_edit",
        "pattern_search",
        "text_search",
        "web_fetch",
    },
    "technical-director": {
        "file_read",
        "file_write",
        "file_edit",
        "pattern_search",
        "text_search",
        "web_fetch",
        "execute_shell",
    },
    "producer": {
        "file_read",
        "file_write",
        "file_edit",
        "pattern_search",
        "text_search",
        "web_fetch",
        "execute_shell",
    },
    "qa-lead": {
        "file_read",
        "file_write",
        "file_edit",
        "pattern_search",
        "text_search",
        "execute_shell",
    },
}

EXPECTED_DELEGATION_INTENT = {
    "creative-director": "single_delegate",
    "technical-director": "single_delegate",
    "producer": "multi_delegate",
    "qa-lead": "single_delegate",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "id",
    "title",
    "purpose",
    "collaboration_contract_ref",
    "capabilities",
    "model_profile",
    "tool_capability_needs",
    "delegation_intent",
    "source_refs",
    "projection_notes",
    "warning_rules",
}

REJECTED_OLD_FIELDS = {
    "display_name",
    "role_summary",
    "execution",
    "skills",
    "policy_refs",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load(path.read_text(encoding="utf-8")))


def _read_schema() -> dict[str, Any]:
    return cast(
        dict[str, Any], json.loads(AGENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    )


def _load_manifests() -> dict[str, dict[str, Any]]:
    manifests: dict[str, dict[str, Any]] = {}
    for path in sorted(AGENT_DIR.glob("*.yaml")):
        data = _read_yaml(path)
        manifests[cast(str, data["id"])] = data
    return manifests


def test_agent_manifest_files_are_exact_and_deterministic() -> None:
    found_files = {path.name for path in AGENT_DIR.glob("*.yaml")}
    assert found_files == EXPECTED_FILES


def test_agent_manifests_validate_against_schema() -> None:
    validator = jsonschema.Draft202012Validator(_read_schema())
    for path in AGENT_DIR.glob("*.yaml"):
        validator.validate(_read_yaml(path))


def test_v0_model_tiers_are_normalized_to_canonical_profiles() -> None:
    manifests = _load_manifests()
    for agent_id, expected_model_profile in EXPECTED_MODEL_PROFILES.items():
        assert manifests[agent_id]["model_profile"] == expected_model_profile


def test_tool_capability_needs_are_harness_neutral_and_exact() -> None:
    manifests = _load_manifests()
    for agent_id, expected_needs in EXPECTED_TOOL_CAPABILITY_NEEDS.items():
        needs = set(cast(list[str], manifests[agent_id]["tool_capability_needs"]))
        assert needs == expected_needs


def test_manifests_use_corrected_task4_fields_only() -> None:
    manifests = _load_manifests()

    for manifest in manifests.values():
        manifest_keys = set(manifest.keys())
        assert REQUIRED_TOP_LEVEL_FIELDS.issubset(manifest_keys)
        assert REJECTED_OLD_FIELDS.isdisjoint(manifest_keys)
        assert manifest["collaboration_contract_ref"] == "protocols/collaboration"


def test_delegation_intent_matches_v0_role_expectations() -> None:
    manifests = _load_manifests()

    for agent_id, expected_intent in EXPECTED_DELEGATION_INTENT.items():
        assert manifests[agent_id]["delegation_intent"] == expected_intent


def test_provider_and_claude_specific_terms_are_not_canonicalized() -> None:
    for path in AGENT_DIR.glob("*.yaml"):
        text = path.read_text(encoding="utf-8").lower()
        assert "model: opus" not in text
        assert "model: sonnet" not in text
        assert "askuserquestion" not in text
        assert "tools: read" not in text
        assert "tools: read, glob" not in text
        assert "estimate" not in text
        assert "scope-check" not in text
        assert "bug-report" not in text
        assert "release-checklist" not in text


def test_source_refs_projection_notes_and_warning_rules_are_structured() -> None:
    manifests = _load_manifests()

    for manifest in manifests.values():
        source_refs = cast(list[str], manifest["source_refs"])
        projection_notes = cast(list[dict[str, str]], manifest["projection_notes"])
        warning_rules = cast(list[dict[str, str]], manifest["warning_rules"])

        assert source_refs
        assert all(
            ref.startswith("Claude-Code-Game-Studios/.claude/agents/")
            for ref in source_refs
        )
        assert any(note["target"] in {"codex", "openclaw"} for note in projection_notes)
        assert any(
            rule["code"] == "W_MODEL_PROFILE_NORMALIZED" for rule in warning_rules
        )
