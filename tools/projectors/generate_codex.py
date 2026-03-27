from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TypedDict, cast

import yaml


ROOT = Path(__file__).resolve().parents[2]
WHITELIST_PATH = ROOT / "common" / "docs" / "migration" / "v0-whitelist.md"


class WarningRule(TypedDict):
    code: str
    trigger_condition: str
    recommended_fallback: str


class ProjectionNote(TypedDict):
    target: str
    note: str
    workaround_class: str


class AgentManifest(TypedDict):
    id: str
    title: str
    purpose: str
    capabilities: list[str]
    model_profile: str
    tool_capability_needs: list[str]
    delegation_intent: str
    source_refs: list[str]
    projection_notes: list[ProjectionNote]
    warning_rules: list[WarningRule]


class WorkaroundRule(TypedDict):
    hazard_category: str
    workaround_class: str
    warning_code: str


class WorkflowStep(TypedDict):
    step_id: str
    intent: str
    requires_confirmation: bool


class SkillManifest(TypedDict):
    id: str
    user_entrypoint: str
    intent: str
    required_inputs: list[str]
    interactive_capture_mode: str
    workflow_steps: list[WorkflowStep]
    required_capabilities: list[str]
    outputs: list[str]
    source_refs: list[str]
    workaround_rules: list[WorkaroundRule]
    projection_notes: list[ProjectionNote]


class PolicyRule(TypedDict):
    code: str
    statement: str
    severity: str
    failure_mode: str


class PolicyManifest(TypedDict):
    id: str
    title: str
    rules: list[PolicyRule]


class WorkflowStage(TypedDict):
    stage_id: str
    objective: str
    actor: str
    approval_gate: str
    fallback_strategy: str


class WorkflowManifest(TypedDict):
    id: str
    summary: str
    stages: list[WorkflowStage]


class WarningEntry(TypedDict):
    code: str
    severity: str
    warning_class: str
    trigger_condition: str
    recommended_fallback: str
    workaround_class: str


class WorkaroundEntry(TypedDict):
    hazard_category: str
    canonical_feature: str
    workaround_class: str
    trigger_condition: str
    recommended_fallback: str
    warning_code: str
    applies_to: list[str]


class PlatformFeature(TypedDict):
    feature_id: str
    support: str
    workaround_class: str


class PlatformLimitation(TypedDict):
    code: str
    condition: str
    fallback: str


class PlatformEntry(TypedDict):
    id: str
    posture: str
    limitations: list[PlatformLimitation]
    features: list[PlatformFeature]


class FeatureMatrix(TypedDict):
    support_posture: dict[str, str]
    platforms: list[PlatformEntry]


class WorkaroundMatrix(TypedDict):
    hazard_workarounds: list[WorkaroundEntry]


class WarningTaxonomy(TypedDict):
    warnings: list[WarningEntry]


class Inputs(TypedDict):
    agents: list[AgentManifest]
    skills: list[SkillManifest]
    policies: list[PolicyManifest]
    workflows: list[WorkflowManifest]
    feature_matrix: FeatureMatrix
    workaround_matrix: WorkaroundMatrix
    warning_taxonomy: WarningTaxonomy


def _read_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_manifest_dir(path: Path) -> list[object]:
    return [_read_yaml(item) for item in sorted(path.glob("*.yaml"))]


def _parse_whitelist() -> dict[str, list[str]]:
    included: dict[str, list[str]] = {
        "agents": [],
        "skills": [],
        "shared docs": [],
        "policies": [],
        "workflows": [],
    }
    current_h2 = ""
    current_h3 = ""

    for raw_line in WHITELIST_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_h2 = line[3:].strip()
            current_h3 = ""
            continue
        if line.startswith("### "):
            current_h3 = line[4:].strip()
            continue
        if not line.startswith("- `") or not line.endswith("`"):
            continue

        item = line[3:-1]
        if (
            current_h2 == "Included v0 artifacts (authoritative)"
            and current_h3 in included
        ):
            included[current_h3].append(item)

    return {
        "agents": included["agents"],
        "skills": included["skills"],
        "policies": included["policies"],
        "workflows": included["workflows"],
    }


def _load_inputs(root: Path) -> Inputs:
    common_dir = root / "common"
    compatibility_dir = common_dir / "compatibility"
    manifests_dir = common_dir / "manifests"

    whitelist = _parse_whitelist()
    agent_ids = set(whitelist["agents"])
    skill_ids = set(whitelist["skills"])
    policy_ids = set(whitelist["policies"])
    workflow_ids = set(whitelist["workflows"])

    return {
        "agents": cast(
            list[AgentManifest],
            [
                item
                for item in _load_manifest_dir(manifests_dir / "agents")
                if cast(str, cast(dict[str, object], item)["id"]) in agent_ids
            ],
        ),
        "skills": cast(
            list[SkillManifest],
            [
                item
                for item in _load_manifest_dir(manifests_dir / "skills")
                if cast(str, cast(dict[str, object], item)["id"]) in skill_ids
            ],
        ),
        "policies": cast(
            list[PolicyManifest],
            [
                item
                for item in _load_manifest_dir(manifests_dir / "policies")
                if cast(str, cast(dict[str, object], item)["id"]) in policy_ids
            ],
        ),
        "workflows": cast(
            list[WorkflowManifest],
            [
                item
                for item in _load_manifest_dir(manifests_dir / "workflows")
                if cast(str, cast(dict[str, object], item)["id"]) in workflow_ids
            ],
        ),
        "feature_matrix": cast(
            FeatureMatrix, _read_yaml(compatibility_dir / "feature-matrix.yaml")
        ),
        "workaround_matrix": cast(
            WorkaroundMatrix, _read_yaml(compatibility_dir / "workaround-matrix.yaml")
        ),
        "warning_taxonomy": cast(
            WarningTaxonomy, _read_yaml(compatibility_dir / "warning-taxonomy.yaml")
        ),
    }


def _codex_platform(feature_matrix: FeatureMatrix) -> PlatformEntry:
    return next(
        platform
        for platform in feature_matrix["platforms"]
        if platform["id"] == "codex"
    )


def _warning_lookup(warning_taxonomy: WarningTaxonomy) -> dict[str, WarningEntry]:
    return {item["code"]: item for item in warning_taxonomy["warnings"]}


def _hazard_lookup(workaround_matrix: WorkaroundMatrix) -> dict[str, WorkaroundEntry]:
    return {
        item["hazard_category"]: item
        for item in workaround_matrix["hazard_workarounds"]
        if "codex" in item["applies_to"]
    }


def _codex_projection_note(notes: list[ProjectionNote]) -> ProjectionNote:
    return next(note for note in notes if note["target"] == "codex")


def _toml_string(value: str) -> str:
    return json.dumps(value)


def _toml_list(values: list[str]) -> str:
    return "[" + ", ".join(_toml_string(value) for value in values) + "]"


def _markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _structured_choice_guidance(mode: str) -> list[str]:
    if mode not in {"structured_choice", "hybrid"}:
        return []
    return [
        "## Structured choice workaround",
        "Use explicit text-first options instead of assuming native selectable UI.",
        "Label options deterministically as `OPTION_A`, `OPTION_B`, and so on.",
        "Require the user response to include:",
        "- `CHOSEN_OPTION: OPTION_X`",
        "- `RATIONALE: <brief reason>`",
    ]


def _agent_toml(
    agent: AgentManifest,
    codex_platform: PlatformEntry,
    warning_map: dict[str, WarningEntry],
) -> str:
    note = _codex_projection_note(agent["projection_notes"])
    warning_codes = sorted(
        {rule["code"] for rule in agent["warning_rules"]}
        | {"W_CODEX_PROJECT_LOCAL_AGENT_LIMITATION"}
    )
    supports_wrapped_choices = "structured_choice_capture" in agent["capabilities"]
    lines = [
        f"name = {_toml_string(agent['title'])}",
        f"id = {_toml_string(agent['id'])}",
        f"description = {_toml_string(agent['purpose'])}",
        f"model_profile = {_toml_string(agent['model_profile'])}",
        f"support_posture = {_toml_string(codex_platform['posture'])}",
        'runtime_loading = "project_local_with_global_fallback"',
        f"workaround_class = {_toml_string(note['workaround_class'])}",
        "project_local_custom_agents_reliable = false",
        f"source_refs = {_toml_list(agent['source_refs'])}",
        f"capabilities = {_toml_list(agent['capabilities'])}",
        f"tool_capability_needs = {_toml_list(agent['tool_capability_needs'])}",
        f"delegation_intent = {_toml_string(agent['delegation_intent'])}",
        f"warning_codes = {_toml_list(warning_codes)}",
        "",
        "[projection]",
        f"note = {_toml_string(note['note'])}",
        'install_package = "adapters/codex/install/global-agents"',
        'global_install_target = "~/.codex/agents/"',
        "",
        "[structured_choice]",
        f"enabled = {str(supports_wrapped_choices).lower()}",
        "native_parity = false",
        'strategy = "text_first_deterministic_options"',
        'option_label_pattern = "OPTION_[A-Z]"',
        'response_fields = ["CHOSEN_OPTION", "RATIONALE"]',
        "",
        "[[warnings]]",
        f"code = {_toml_string(warning_codes[0])}",
        f"severity = {_toml_string(warning_map[warning_codes[0]]['severity'])}",
        f"recommended_fallback = {_toml_string(warning_map[warning_codes[0]]['recommended_fallback'])}",
    ]
    for code in warning_codes[1:]:
        lines.extend(
            [
                "",
                "[[warnings]]",
                f"code = {_toml_string(code)}",
                f"severity = {_toml_string(warning_map[code]['severity'])}",
                f"recommended_fallback = {_toml_string(warning_map[code]['recommended_fallback'])}",
            ]
        )
    return "\n".join(lines) + "\n"


def _skill_markdown(
    skill: SkillManifest,
    codex_platform: PlatformEntry,
    hazard_map: dict[str, WorkaroundEntry],
) -> str:
    note = _codex_projection_note(skill["projection_notes"])
    lines = [
        f"# {skill['user_entrypoint']}",
        "",
        "This skill is projected for Codex from canonical manifests under `common/`.",
        "Codex support remains workaround-backed rather than OpenCode-equivalent parity.",
        "",
        "## Support posture",
        f"- {codex_platform['posture']}",
        f"- Workaround class: {note['workaround_class']}",
        f"- Invocation surface: explicit task intent for `{skill['user_entrypoint']}`",
        "",
        "## Intent",
        skill["intent"],
        "",
        "## Required inputs",
        _markdown_list(skill["required_inputs"]),
        "",
        "## Required capabilities",
        _markdown_list(skill["required_capabilities"]),
        "",
        "## Workflow steps",
    ]
    for step in skill["workflow_steps"]:
        confirmation = "yes" if step["requires_confirmation"] else "no"
        lines.extend(
            [
                f"### {step['step_id']}",
                step["intent"],
                f"Requires confirmation: {confirmation}",
                "",
            ]
        )
    lines.extend(_structured_choice_guidance(skill["interactive_capture_mode"]))
    if skill["interactive_capture_mode"] in {"structured_choice", "hybrid"}:
        lines.append("")
    lines.extend(
        [
            "## Outputs",
            _markdown_list(skill["outputs"]),
            "",
            "## Codex projection notes",
            f"- {note['note']}",
            "- Slash-style entry is represented as explicit command/task intent.",
            "",
            "## Workaround rules",
        ]
    )
    for rule in skill["workaround_rules"]:
        hazard = hazard_map[rule["hazard_category"]]
        lines.extend(
            [
                f"- `{rule['warning_code']}` / `{rule['workaround_class']}` / `{rule['hazard_category']}`",
                f"  - {hazard['recommended_fallback']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Source refs",
            _markdown_list(skill["source_refs"]),
        ]
    )
    return "\n".join(lines) + "\n"


def _agents_md(
    codex_platform: PlatformEntry,
    agents: list[AgentManifest],
    skills: list[SkillManifest],
    policies: list[PolicyManifest],
    workflows: list[WorkflowManifest],
) -> str:
    limitation = codex_platform["limitations"][0]
    lines = [
        "# AGENTS.md",
        "",
        "This Codex projection is generated from canonical manifests under `common/`.",
        "",
        "## Support posture",
        f"- Codex: `{codex_platform['posture']}`",
        "- Not OpenCode-equivalent fidelity.",
        f"- Limitation: {limitation['condition']}",
        f"- Required fallback: {limitation['fallback']}",
        "",
        "## Repository layout",
        "- `.codex/config.toml` configures support posture and generated agent files.",
        "- `.codex/agents/*.toml` contains project-local Codex agent definitions.",
        "- `.agents/skills/*/SKILL.md` contains projected skill instructions.",
        "- `adapters/codex/install/global-agents/` contains the first-class global install workaround package.",
        "",
        "## Structured choice contract",
        "- Use text-first deterministic options labeled `OPTION_A`, `OPTION_B`, and so on.",
        "- Require explicit capture fields `CHOSEN_OPTION` and `RATIONALE`.",
        "- Do not claim native selectable UI parity when Codex does not guarantee it.",
        "",
        "## Agents",
        _markdown_list([f"{agent['id']} — {agent['purpose']}" for agent in agents]),
        "",
        "## Skills",
        _markdown_list(
            [f"{skill['id']} — `{skill['user_entrypoint']}`" for skill in skills]
        ),
        "",
        "## Policies",
        _markdown_list([f"{policy['id']}" for policy in policies]),
        "",
        "## Workflows",
        _markdown_list(
            [f"{workflow['id']} — {workflow['summary']}" for workflow in workflows]
        ),
    ]
    return "\n".join(lines) + "\n"


def _config_toml(
    codex_platform: PlatformEntry,
    agents: list[AgentManifest],
    skills: list[SkillManifest],
    policies: list[PolicyManifest],
    workflows: list[WorkflowManifest],
) -> str:
    limitation = codex_platform["limitations"][0]
    lines = [
        'schema_version = "1.0"',
        'target = "codex"',
        f"support_posture = {_toml_string(codex_platform['posture'])}",
        "local_custom_agents_reliable = false",
        'global_agent_workaround_path = "adapters/codex/install/global-agents"',
        'global_agent_install_target = "~/.codex/agents/"',
        'structured_choice_strategy = "text_first_deterministic_options"',
        "",
        "[limitations]",
        f"code = {_toml_string(limitation['code'])}",
        f"condition = {_toml_string(limitation['condition'])}",
        f"fallback = {_toml_string(limitation['fallback'])}",
        "",
        "[generated]",
        f"agents = {_toml_list([f'.codex/agents/{agent["id"]}.toml' for agent in agents])}",
        f"skills = {_toml_list([f'.agents/skills/{skill["id"]}/SKILL.md' for skill in skills])}",
        f"policies = {_toml_list([policy['id'] for policy in policies])}",
        f"workflows = {_toml_list([workflow['id'] for workflow in workflows])}",
    ]
    return "\n".join(lines) + "\n"


def _install_readme(agent_ids: list[str]) -> str:
    return (
        "\n".join(
            [
                "# Codex Global-Agent Install Workaround",
                "",
                "This package is the official workaround for Codex project-local custom-agent loading limitations.",
                "When `.codex/agents/` is not loaded reliably, install the generated agent TOMLs into a globally discoverable Codex directory.",
                "",
                "## Contract",
                "- Codex remains supported with workarounds.",
                "- This package is documented and first-class, not hidden tribal knowledge.",
                "- Structured-choice agents still use deterministic text-first wrappers instead of claiming native parity.",
                "",
                "## Included agents",
                _markdown_list(agent_ids),
                "",
                "## Installer",
                "Run `python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/` or another Codex global-agent directory.",
            ]
        )
        + "\n"
    )


def build_codex_projection(root: Path = ROOT) -> dict[Path, str]:
    inputs = _load_inputs(root)
    codex_platform = _codex_platform(inputs["feature_matrix"])
    warning_map = _warning_lookup(inputs["warning_taxonomy"])
    hazard_map = _hazard_lookup(inputs["workaround_matrix"])
    project_root = Path("adapters/codex/project")
    install_root = Path("adapters/codex/install/global-agents")

    outputs: dict[Path, str] = {}
    outputs[project_root / "AGENTS.md"] = _agents_md(
        codex_platform,
        inputs["agents"],
        inputs["skills"],
        inputs["policies"],
        inputs["workflows"],
    )
    outputs[project_root / ".codex" / "config.toml"] = _config_toml(
        codex_platform,
        inputs["agents"],
        inputs["skills"],
        inputs["policies"],
        inputs["workflows"],
    )

    install_manifest_agents: list[dict[str, str]] = []
    for agent in inputs["agents"]:
        agent_toml = _agent_toml(agent, codex_platform, warning_map)
        project_relative = project_root / ".codex" / "agents" / f"{agent['id']}.toml"
        install_relative = install_root / "agents" / f"{agent['id']}.toml"
        outputs[project_relative] = agent_toml
        outputs[install_relative] = agent_toml
        install_manifest_agents.append(
            {
                "id": agent["id"],
                "title": agent["title"],
                "source": f"agents/{agent['id']}.toml",
            }
        )

    for skill in inputs["skills"]:
        outputs[project_root / ".agents" / "skills" / skill["id"] / "SKILL.md"] = (
            _skill_markdown(
                skill,
                codex_platform,
                hazard_map,
            )
        )

    outputs[install_root / "README.md"] = _install_readme(
        [agent["id"] for agent in inputs["agents"]]
    )
    outputs[install_root / "package_manifest.json"] = (
        json.dumps(
            {
                "schema_version": "1.0",
                "target": "codex",
                "package_type": "global_agent_workaround",
                "support_posture": codex_platform["posture"],
                "warning_code": "W_CODEX_PROJECT_LOCAL_AGENT_LIMITATION",
                "install_requires_global_scope": True,
                "agents": install_manifest_agents,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    return outputs


def _remove_empty_directories(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def _write_files(root: Path, rendered: dict[Path, str]) -> list[Path]:
    expected_paths = {root / relative_path for relative_path in rendered}
    managed_roots = [
        root / "adapters/codex/project",
        root / "adapters/codex/install/global-agents",
    ]

    for managed_root in managed_roots:
        if managed_root.exists():
            for path in sorted(managed_root.rglob("*"), reverse=True):
                if path.is_file() and path not in expected_paths:
                    path.unlink()
            _remove_empty_directories(managed_root)

    written_paths: list[Path] = []
    for relative_path, content in sorted(
        rendered.items(), key=lambda item: str(item[0])
    ):
        absolute_path = root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(content, encoding="utf-8")
        written_paths.append(relative_path)

    for managed_root in managed_roots:
        _remove_empty_directories(managed_root)

    return written_paths


def write_codex_projection(root: Path = ROOT) -> list[Path]:
    return _write_files(root, build_codex_projection(root))


def main() -> int:
    written = write_codex_projection()
    for path in written:
        print(path.as_posix())
    print(f"Generated {len(written)} Codex projection files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
