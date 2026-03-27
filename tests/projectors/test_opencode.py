from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, cast


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = REPO_ROOT / "tools" / "projectors" / "generate_opencode.py"
ADAPTER_ROOT = REPO_ROOT / "adapters" / "opencode" / "project"

EXPECTED_FILES = {
    "AGENTS.md",
    "opencode.json",
    ".opencode/oh-my-opencode.jsonc",
    ".opencode/skills/brainstorm/SKILL.md",
    ".opencode/skills/design-review/SKILL.md",
    ".opencode/skills/setup-engine/SKILL.md",
    ".opencode/skills/start/SKILL.md",
    ".opencode/commands/brainstorm.md",
    ".opencode/commands/design-review.md",
    ".opencode/commands/setup-engine.md",
    ".opencode/commands/start.md",
}


def _load_generator_module() -> Any:
    spec = importlib.util.spec_from_file_location("generate_opencode", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import OpenCode generator")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_jsonc(text: str) -> dict[str, Any]:
    payload = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("//")
    )
    return cast(dict[str, Any], json.loads(payload))


def test_generator_emits_exact_opencode_file_set_into_tmp_path(tmp_path: Path) -> None:
    module = _load_generator_module()
    written_paths = cast(list[Path], module.write_projection(tmp_path))

    assert {
        path.relative_to(tmp_path).as_posix() for path in written_paths
    } == EXPECTED_FILES
    assert {
        path.relative_to(tmp_path).as_posix()
        for path in tmp_path.rglob("*")
        if path.is_file()
    } == EXPECTED_FILES


def test_generator_is_deterministic_when_run_twice(tmp_path: Path) -> None:
    module = _load_generator_module()
    module.write_projection(tmp_path)
    first_snapshot = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    module.write_projection(tmp_path)
    second_snapshot = {
        path.relative_to(tmp_path).as_posix(): path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    assert first_snapshot == second_snapshot


def test_opencode_json_and_omo_mapping_preserve_required_target_shape(
    tmp_path: Path,
) -> None:
    module = _load_generator_module()
    module.write_projection(tmp_path)

    project_config = cast(
        dict[str, Any],
        json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8")),
    )
    compatibility = _read_jsonc(
        (tmp_path / ".opencode" / "oh-my-opencode.jsonc").read_text(encoding="utf-8")
    )

    assert project_config["target"] == "opencode"
    assert project_config["target_posture"] == "highest_fidelity_v0_target"
    assert project_config["skills_directory"] == ".opencode/skills"
    assert project_config["commands_directory"] == ".opencode/commands"
    assert [
        agent["id"] for agent in cast(list[dict[str, Any]], project_config["agents"])
    ] == [
        "creative-director",
        "technical-director",
        "producer",
        "qa-lead",
    ]
    assert [
        skill["id"] for skill in cast(list[dict[str, Any]], project_config["skills"])
    ] == [
        "start",
        "brainstorm",
        "setup-engine",
        "design-review",
    ]
    assert compatibility["source_semantic_mappings"]["slash_command_entrypoints"] == {
        "workaround_class": "native_mapping",
        "warning_code": "W_SLASH_COMMAND_ROUTED",
        "wrapper_required": False,
        "detail": "Canonical user_entrypoint values are projected into OpenCode command aliases that route to packaged skills.",
    }
    assert compatibility["source_semantic_mappings"]["structured_choice_capture"] == {
        "workaround_class": "generated_wrapper",
        "warning_code": "W_INTERACTIVE_CAPTURE_WRAPPED",
        "wrapper_required": True,
        "detail": "Structured choice and hybrid flows use generated Explain -> Capture helper aliases under `.opencode/commands/` when no one-to-one native UI is guaranteed.",
    }
    assert (
        compatibility["source_semantic_mappings"]["approval_before_write_protocol"][
            "wrapper_required"
        ]
        is False
    )


def test_skill_packages_include_projection_and_workaround_metadata(
    tmp_path: Path,
) -> None:
    module = _load_generator_module()
    module.write_projection(tmp_path)

    setup_engine_text = (
        tmp_path / ".opencode" / "skills" / "setup-engine" / "SKILL.md"
    ).read_text(encoding="utf-8")
    brainstorm_text = (
        tmp_path / ".opencode" / "skills" / "brainstorm" / "SKILL.md"
    ).read_text(encoding="utf-8")
    start_alias_text = (tmp_path / ".opencode" / "commands" / "start.md").read_text(
        encoding="utf-8"
    )

    assert "OpenCode package for canonical skill `setup-engine`." in setup_engine_text
    assert (
        "`opencode` -> `native_mapping`: Map setup flow directly while preserving explicit user approval before writes."
        in setup_engine_text
    )
    assert (
        "`task_subcall_delegation` -> `protocol_downgrade` / `W_TASK_DELEGATION_BRIDGED`"
        in setup_engine_text
    )
    assert brainstorm_text.splitlines()[0] == "# brainstorm"
    assert "## Preserved Compatibility Metadata" in brainstorm_text
    assert "Explain -> Capture helper flow" in start_alias_text
    assert "`.opencode/skills/start/SKILL.md`" in start_alias_text


def test_committed_adapter_files_match_generator_output() -> None:
    module = _load_generator_module()
    projection = cast(dict[str, Any], module.build_projection())
    rendered_files = cast(dict[str, str], projection["rendered_files"])

    actual_files = {
        path.relative_to(ADAPTER_ROOT).as_posix()
        for path in ADAPTER_ROOT.rglob("*")
        if path.is_file()
    }
    assert actual_files == EXPECTED_FILES

    for relative_path, expected_content in rendered_files.items():
        actual_content = (ADAPTER_ROOT / relative_path).read_text(encoding="utf-8")
        assert actual_content == expected_content
