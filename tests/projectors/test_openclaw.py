import importlib.util
import json
from pathlib import Path
from typing import Protocol, cast


ROOT = Path(__file__).resolve().parents[2]
OPENCLAW_DIR = ROOT / "adapters" / "openclaw"
WORKSPACE_DIR = OPENCLAW_DIR / "workspace"
GENERATOR = ROOT / "tools" / "projectors" / "generate_openclaw.py"


class OpenClawGeneratorModule(Protocol):
    OPENCLAW_DIR: Path
    WORKSPACE_DIR: Path

    def generate(self) -> list[Path]: ...


def _load_module(path: Path, name: str) -> OpenClawGeneratorModule:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(OpenClawGeneratorModule, cast(object, module))


def _run_generator(output_root: Path) -> None:
    module = _load_module(GENERATOR, f"generate_openclaw_{output_root.name}")
    original_openclaw_dir = module.OPENCLAW_DIR
    original_workspace_dir = module.WORKSPACE_DIR
    module.OPENCLAW_DIR = output_root
    module.WORKSPACE_DIR = output_root / "workspace"
    try:
        _ = module.generate()
    finally:
        module.OPENCLAW_DIR = original_openclaw_dir
        module.WORKSPACE_DIR = original_workspace_dir


def test_openclaw_generator_creates_repo_and_cli_only_workspace(tmp_path: Path) -> None:
    output_root = tmp_path / "openclaw"
    _run_generator(output_root)

    config = json.loads((output_root / "openclaw.json5").read_text(encoding="utf-8"))
    assert config["support_posture"] == "repo_cli_compatibility_only"
    assert config["native_parity"] == "not_supported_in_v0"
    assert config["supported_surfaces"] == ["repository_layout", "cli_invocation"]
    assert config["unsupported_surfaces"] == [
        "gateway_integration",
        "channel_native_runtime",
        "runtime_hook_parity",
    ]


def test_openclaw_projection_preserves_expected_workspace_packaging(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "openclaw"
    workspace_root = output_root / "workspace"
    _run_generator(output_root)

    assert (workspace_root / "AGENTS.md").is_file()
    assert (workspace_root / "SOUL.md").is_file()

    agent_files = {path.name for path in (workspace_root / "agents").glob("*.md")}
    skill_files = {
        path.relative_to(workspace_root).as_posix()
        for path in (workspace_root / "skills").glob("*/SKILL.md")
    }

    assert agent_files == {
        "creative-director.md",
        "technical-director.md",
        "producer.md",
        "qa-lead.md",
    }
    assert skill_files == {
        "skills/start/SKILL.md",
        "skills/brainstorm/SKILL.md",
        "skills/setup-engine/SKILL.md",
        "skills/design-review/SKILL.md",
    }


def test_openclaw_projection_marks_non_native_semantics_with_fallbacks(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "openclaw"
    workspace_root = output_root / "workspace"
    _run_generator(output_root)

    config = json.loads((output_root / "openclaw.json5").read_text(encoding="utf-8"))
    assert config["fallback_contract"] == {
        "delegation": "single_step_or_staged_cli_checkpoint",
        "interactive_capture": "generated_wrapper_or_explicit_cli_prompts",
        "policy_guards": "external_runner_metadata",
        "slash_invocation": "explicit_command_or_task_entrypoint",
        "workflow_approval_gates": "external_runner_metadata",
    }
    assert config["external_runner"] == {
        "policies": ["commit-validation-intent", "test-standards"],
        "workflows": ["collaboration-approval-gate"],
    }

    soul_text = (workspace_root / "SOUL.md").read_text(encoding="utf-8")
    assert "gateway-native or channel-native runtime behavior" in soul_text
    assert (
        "Route unsupported semantics through wrapper metadata or external runners"
        in soul_text
    )

    policy_text = (
        workspace_root / "policies" / "commit-validation-intent.md"
    ).read_text(encoding="utf-8")
    workflow_text = (
        workspace_root / "workflows" / "collaboration-approval-gate.md"
    ).read_text(encoding="utf-8")
    assert "external runner metadata" in policy_text.lower()
    assert "must be executed by a wrapper or operator" in workflow_text


def test_openclaw_projection_is_deterministic_across_repeated_runs(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "openclaw"
    workspace_root = output_root / "workspace"
    _run_generator(output_root)
    first = (output_root / "openclaw.json5").read_text(encoding="utf-8")
    first_agent = (workspace_root / "agents" / "producer.md").read_text(
        encoding="utf-8"
    )
    first_skill = (workspace_root / "skills" / "setup-engine" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    _run_generator(output_root)
    second = (output_root / "openclaw.json5").read_text(encoding="utf-8")
    second_agent = (workspace_root / "agents" / "producer.md").read_text(
        encoding="utf-8"
    )
    second_skill = (workspace_root / "skills" / "setup-engine" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert first == second
    assert first_agent == second_agent
    assert first_skill == second_skill
