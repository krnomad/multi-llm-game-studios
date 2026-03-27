from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "tools/projectors/generate_codex.py"
INSTALLER_PATH = ROOT / "tools/projectors/install_codex_global_agents.py"


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _loads_toml(text: str) -> dict[str, object]:
    return json.loads(json.dumps(tomllib.loads(text)))


def test_codex_projection_build_is_deterministic_and_plan_shaped() -> None:
    generator = _load_module(GENERATOR_PATH, "generate_codex_test")
    first = generator.build_codex_projection(ROOT)
    second = generator.build_codex_projection(ROOT)

    assert first == second
    assert Path("adapters/codex/project/AGENTS.md") in first
    assert Path("adapters/codex/project/.codex/config.toml") in first
    assert Path("adapters/codex/project/.codex/agents/creative-director.toml") in first
    assert Path("adapters/codex/project/.agents/skills/start/SKILL.md") in first
    assert Path("adapters/codex/project/project_manifest.json") not in first


def test_codex_config_and_agents_make_workaround_posture_explicit() -> None:
    generator = _load_module(GENERATOR_PATH, "generate_codex_config")
    rendered = generator.build_codex_projection(ROOT)

    config = _loads_toml(rendered[Path("adapters/codex/project/.codex/config.toml")])
    creative_director = _loads_toml(
        rendered[Path("adapters/codex/project/.codex/agents/creative-director.toml")]
    )
    install_manifest = json.loads(
        rendered[Path("adapters/codex/install/global-agents/package_manifest.json")]
    )

    assert config["support_posture"] == "supported_with_workarounds"
    assert config["local_custom_agents_reliable"] is False
    assert config["global_agent_install_target"] == "~/.codex/agents/"
    assert creative_director["runtime_loading"] == "project_local_with_global_fallback"
    assert creative_director["project_local_custom_agents_reliable"] is False
    structured_choice = creative_director["structured_choice"]
    assert isinstance(structured_choice, dict)
    assert structured_choice["enabled"] is True
    assert structured_choice["strategy"] == "text_first_deterministic_options"
    assert install_manifest["warning_code"] == "W_CODEX_PROJECT_LOCAL_AGENT_LIMITATION"
    assert install_manifest["install_requires_global_scope"] is True


def test_codex_skill_projection_uses_skill_markdown_and_wrapper_guidance() -> None:
    generator = _load_module(GENERATOR_PATH, "generate_codex_skills")
    rendered = generator.build_codex_projection(ROOT)

    start_skill = rendered[Path("adapters/codex/project/.agents/skills/start/SKILL.md")]
    review_skill = rendered[
        Path("adapters/codex/project/.agents/skills/design-review/SKILL.md")
    ]

    assert "# start" in start_skill
    assert "OPTION_A" in start_skill
    assert "Codex support remains workaround-backed" in start_skill
    assert "explicit task intent" in start_skill.lower()
    assert "Structured choice workaround" not in review_skill
    assert "protocol_downgrade" in review_skill


def test_codex_installer_copies_generated_global_agent_tomls(tmp_path: Path) -> None:
    generator = _load_module(GENERATOR_PATH, "generate_codex_write")
    _ = generator.write_codex_projection(ROOT)

    installer = _load_module(INSTALLER_PATH, "install_codex_test")
    installed = installer.install_global_agents(tmp_path, ROOT)

    installed_names = {path.name for path in installed}
    assert installed_names == {
        "creative-director.toml",
        "producer.toml",
        "qa-lead.toml",
        "technical-director.toml",
    }
    for path in installed:
        parsed = _loads_toml(path.read_text(encoding="utf-8"))
        assert parsed["runtime_loading"] == "project_local_with_global_fallback"
