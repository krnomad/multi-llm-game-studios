from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "tools/projectors/generate_codex.py"
PROJECT_ROOT = ROOT / "adapters/codex/project"
INSTALL_ROOT = ROOT / "adapters/codex/install/global-agents"


def _load_generator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate_codex", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Codex generator module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_toml(path: Path) -> dict[str, object]:
    return json.loads(json.dumps(tomllib.loads(path.read_text(encoding="utf-8"))))


def main() -> int:
    generator = _load_generator_module()
    expected = generator.build_codex_projection(ROOT)

    for relative_path, expected_text in sorted(
        expected.items(), key=lambda item: str(item[0])
    ):
        actual_path = ROOT / relative_path
        assert actual_path.exists(), f"Missing projected file: {relative_path}"
        actual_text = actual_path.read_text(encoding="utf-8")
        assert actual_text == expected_text, f"Drift detected in {relative_path}"

    required_paths = [
        PROJECT_ROOT / "AGENTS.md",
        PROJECT_ROOT / ".codex/config.toml",
        PROJECT_ROOT / ".codex/agents/creative-director.toml",
        PROJECT_ROOT / ".codex/agents/technical-director.toml",
        PROJECT_ROOT / ".codex/agents/producer.toml",
        PROJECT_ROOT / ".codex/agents/qa-lead.toml",
        PROJECT_ROOT / ".agents/skills/start/SKILL.md",
        PROJECT_ROOT / ".agents/skills/brainstorm/SKILL.md",
        PROJECT_ROOT / ".agents/skills/setup-engine/SKILL.md",
        PROJECT_ROOT / ".agents/skills/design-review/SKILL.md",
    ]
    for path in required_paths:
        assert path.exists(), (
            f"Missing plan-required Codex file: {path.relative_to(ROOT)}"
        )

    config = _read_toml(PROJECT_ROOT / ".codex/config.toml")
    install_manifest = json.loads(
        (INSTALL_ROOT / "package_manifest.json").read_text(encoding="utf-8")
    )
    assert config["support_posture"] == "supported_with_workarounds"
    assert config["local_custom_agents_reliable"] is False
    assert (
        config["global_agent_workaround_path"] == "adapters/codex/install/global-agents"
    )
    assert install_manifest["install_requires_global_scope"] is True
    assert install_manifest["warning_code"] == "W_CODEX_PROJECT_LOCAL_AGENT_LIMITATION"

    for agent_path in sorted((PROJECT_ROOT / ".codex/agents").glob("*.toml")):
        agent_payload = _read_toml(agent_path)
        assert agent_payload["runtime_loading"] == "project_local_with_global_fallback"
        assert agent_payload["project_local_custom_agents_reliable"] is False
        structured_choice = agent_payload["structured_choice"]
        assert isinstance(structured_choice, dict)
        assert structured_choice["native_parity"] is False

    for skill_path in sorted((PROJECT_ROOT / ".agents/skills").glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        assert "Codex support remains workaround-backed" in text
        assert "explicit task intent" in text.lower()

    print("Codex smoke validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
