from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, cast


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECTION_ROOT = REPO_ROOT / "adapters" / "opencode" / "project"
GENERATOR_PATH = REPO_ROOT / "tools" / "projectors" / "generate_opencode.py"


def _load_generator_module() -> Any:
    spec = importlib.util.spec_from_file_location("generate_opencode", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load OpenCode generator module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_jsonc(path: Path) -> dict[str, Any]:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        lines.append(line)
    return cast(dict[str, Any], json.loads("\n".join(lines)))


def main() -> None:
    generator = _load_generator_module()
    projection = cast(dict[str, Any], generator.build_projection())
    rendered_files = cast(dict[str, str], projection["rendered_files"])

    actual_files = {
        path.relative_to(PROJECTION_ROOT).as_posix()
        for path in PROJECTION_ROOT.rglob("*")
        if path.is_file()
    }
    expected_files = set(rendered_files.keys())
    if actual_files != expected_files:
        raise SystemExit(
            f"Unexpected OpenCode file set: expected {sorted(expected_files)}, found {sorted(actual_files)}"
        )

    for relative_path, expected_content in rendered_files.items():
        path = PROJECTION_ROOT / relative_path
        actual_content = path.read_text(encoding="utf-8")
        if actual_content != expected_content:
            raise SystemExit(f"Generated content drift detected in {relative_path}")

    project_config = cast(
        dict[str, Any],
        json.loads((PROJECTION_ROOT / "opencode.json").read_text(encoding="utf-8")),
    )
    compatibility = _read_jsonc(PROJECTION_ROOT / ".opencode" / "oh-my-opencode.jsonc")
    agents_md = (PROJECTION_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    if project_config["target"] != "opencode":
        raise SystemExit("opencode.json target must be opencode")
    if compatibility["posture"] != "highest_fidelity_v0_target":
        raise SystemExit(
            "Compatibility posture must match OpenCode highest-fidelity target"
        )
    if "Question -> Options -> Decision -> Draft -> Approval" not in agents_md:
        raise SystemExit("AGENTS.md is missing the collaboration stage order")

    skill_ids = [
        skill["id"] for skill in cast(list[dict[str, Any]], project_config["skills"])
    ]
    for skill_id in skill_ids:
        skill_path = PROJECTION_ROOT / ".opencode" / "skills" / skill_id / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        if "## Preserved Compatibility Metadata" not in text:
            raise SystemExit(f"Missing compatibility metadata section in {skill_path}")
        if "`opencode` -> `native_mapping`" not in text:
            raise SystemExit(f"Missing native OpenCode projection note in {skill_path}")

    command_aliases = [
        skill["command_alias"]
        for skill in cast(list[dict[str, Any]], project_config["skills"])
    ]
    for relative_alias_path in command_aliases:
        alias_path = PROJECTION_ROOT / relative_alias_path
        alias_text = alias_path.read_text(encoding="utf-8")
        if "## Alias Behavior" not in alias_text:
            raise SystemExit(f"Missing alias behavior section in {alias_path}")

    structured_capture = compatibility["source_semantic_mappings"][
        "structured_choice_capture"
    ]
    if structured_capture["wrapper_required"] is not True:
        raise SystemExit("Structured choice capture must be marked as helper-wrapped")

    print("OpenCode projection smoke validation passed")


if __name__ == "__main__":
    main()
