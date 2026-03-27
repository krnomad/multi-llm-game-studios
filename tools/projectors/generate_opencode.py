from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "adapters" / "opencode" / "project"

WHITELIST_PATH = REPO_ROOT / "common" / "docs" / "migration" / "v0-whitelist.md"
AGENTS_DIR = REPO_ROOT / "common" / "manifests" / "agents"
SKILLS_DIR = REPO_ROOT / "common" / "manifests" / "skills"
POLICIES_DIR = REPO_ROOT / "common" / "manifests" / "policies"
WORKFLOW_PATH = (
    REPO_ROOT
    / "common"
    / "manifests"
    / "workflows"
    / "collaboration-approval-gate.yaml"
)
FEATURE_MATRIX_PATH = REPO_ROOT / "common" / "compatibility" / "feature-matrix.yaml"
WORKAROUND_MATRIX_PATH = (
    REPO_ROOT / "common" / "compatibility" / "workaround-matrix.yaml"
)
WARNING_TAXONOMY_PATH = REPO_ROOT / "common" / "compatibility" / "warning-taxonomy.yaml"

DOC_PATHS = {
    "collaboration-protocol": REPO_ROOT
    / "common"
    / "docs"
    / "protocols"
    / "collaboration.md",
    "onboarding": REPO_ROOT / "common" / "docs" / "workflows" / "onboarding.md",
    "engine-setup": REPO_ROOT / "common" / "docs" / "workflows" / "engine-setup.md",
    "design-review-workflow": REPO_ROOT
    / "common"
    / "docs"
    / "workflows"
    / "design-review.md",
    "validation-intent": REPO_ROOT
    / "common"
    / "docs"
    / "workflows"
    / "validation-intent.md",
}

DOC_TITLES = {
    "collaboration-protocol": "Collaboration Protocol",
    "onboarding": "Onboarding Workflow",
    "engine-setup": "Engine Setup Workflow",
    "design-review-workflow": "Design Review Workflow",
    "validation-intent": "Validation Intent Workflow",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load(path.read_text(encoding="utf-8")))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_whitelist() -> dict[str, list[str]]:
    included: dict[str, list[str]] = {
        "agents": [],
        "skills": [],
        "shared docs": [],
        "policies": [],
    }
    current_h2 = ""
    current_h3 = ""

    for raw_line in _read_text(WHITELIST_PATH).splitlines():
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
        "shared_docs": included["shared docs"],
        "policies": included["policies"],
    }


def _load_agents(agent_ids: list[str]) -> list[dict[str, Any]]:
    agents: list[dict[str, Any]] = []
    for agent_id in agent_ids:
        agents.append(_read_yaml(AGENTS_DIR / f"{agent_id}.yaml"))
    return agents


def _load_skills(skill_ids: list[str]) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for skill_id in skill_ids:
        skills.append(_read_yaml(SKILLS_DIR / f"{skill_id}.yaml"))
    return skills


def _load_policies(policy_ids: list[str]) -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = []
    for policy_id in policy_ids:
        policies.append(_read_yaml(POLICIES_DIR / f"{policy_id}.yaml"))
    return policies


def _load_shared_docs(doc_ids: list[str]) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for doc_id in doc_ids:
        docs.append(
            {
                "id": doc_id,
                "title": DOC_TITLES[doc_id],
                "path": str(DOC_PATHS[doc_id].relative_to(REPO_ROOT)),
                "content": _read_text(DOC_PATHS[doc_id]),
            }
        )
    return docs


def _select_target_projection_note(
    manifest: dict[str, Any], target: str
) -> dict[str, str]:
    for note in cast(list[dict[str, str]], manifest.get("projection_notes", [])):
        if note["target"] == target:
            return note
    return {
        "target": target,
        "note": "Feature-matrix native mapping applies for this target.",
        "workaround_class": "native_mapping",
    }


def _load_opencode_platform() -> dict[str, Any]:
    feature_matrix = _read_yaml(FEATURE_MATRIX_PATH)
    for platform in cast(list[dict[str, Any]], feature_matrix["platforms"]):
        if platform["id"] == "opencode":
            return platform
    raise ValueError("OpenCode platform entry missing from feature matrix")


def _load_warning_lookup() -> dict[str, dict[str, str]]:
    taxonomy = _read_yaml(WARNING_TAXONOMY_PATH)
    return {
        warning["code"]: cast(dict[str, str], warning)
        for warning in cast(list[dict[str, Any]], taxonomy["warnings"])
    }


def _load_workaround_lookup() -> dict[str, dict[str, str]]:
    matrix = _read_yaml(WORKAROUND_MATRIX_PATH)
    return {
        rule["hazard_category"]: cast(dict[str, str], rule)
        for rule in cast(list[dict[str, Any]], matrix["hazard_workarounds"])
    }


def _render_jsonc(data: dict[str, Any]) -> str:
    return (
        "// Generated by tools/projectors/generate_opencode.py; do not edit manually.\n"
        + json.dumps(data, indent=2)
        + "\n"
    )


def _render_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2) + "\n"


def _render_agents_md(
    agents: list[dict[str, Any]],
    skills: list[dict[str, Any]],
    policies: list[dict[str, Any]],
    workflow: dict[str, Any],
    platform: dict[str, Any],
) -> str:
    lines = [
        "# AGENTS.md",
        "",
        "This OpenCode / Oh My OpenCode v0 slice is generated from canonical manifests under `common/`. Treat this file as the instruction surface for the projected repo.",
        "",
        "## Collaboration Contract",
        "",
        f"- Stage order: `{' -> '.join(stage['stage_id'].title() for stage in cast(list[dict[str, Any]], workflow['stages']))}`",
        f"- Approval before write: `{str(cast(dict[str, bool], workflow['invariants'])['approval_before_write']).lower()}`",
        f"- Human decision owner: `{str(cast(dict[str, bool], workflow['invariants'])['human_decision_owner']).lower()}`",
        "- Do not commit changes unless the user explicitly asks for a commit.",
        "",
        "## OpenCode v0 Mapping",
        "",
        f"- Target posture: `{platform['posture']}`",
        "- Native mapping is preferred for this target whenever canonical semantics are available directly.",
        "- Canonical skill entrypoints are packaged under `.opencode/skills/<id>/SKILL.md`.",
        "- Command aliases and helper templates are packaged under `.opencode/commands/` when entrypoint routing or text capture needs an explicit surface.",
        "- Lower-fidelity workaround metadata is preserved in `.opencode/oh-my-opencode.jsonc` rather than silently dropped.",
        "",
        "## Skill Entrypoints",
        "",
    ]

    for skill in skills:
        lines.append(
            f"- `{skill['user_entrypoint']}` -> `.opencode/skills/{skill['id']}/SKILL.md` ({skill['interactive_capture_mode']})"
        )

    lines.extend(["", "## Agents", ""])
    for agent in agents:
        lines.extend(
            [
                f"### {agent['title']} (`{agent['id']}`)",
                "",
                f"- Purpose: {agent['purpose']}",
                f"- Model profile: `{agent['model_profile']}`",
                f"- Delegation intent: `{agent['delegation_intent']}`",
                "- Capabilities:",
            ]
        )
        for capability in cast(list[str], agent["capabilities"]):
            lines.append(f"  - `{capability}`")
        lines.append("- Tool capability needs:")
        for need in cast(list[str], agent["tool_capability_needs"]):
            lines.append(f"  - `{need}`")
        lines.append("- Warning rules:")
        for rule in cast(list[dict[str, str]], agent["warning_rules"]):
            lines.append(f"  - `{rule['code']}`: {rule['recommended_fallback']}")
        lines.append("")

    lines.extend(["## Policy Guards", ""])
    for policy in policies:
        enforcement = cast(dict[str, Any], policy["enforcement"])
        lines.extend(
            [
                f"### {policy['title']} (`{policy['id']}`)",
                "",
                f"- Enforcement level: `{enforcement['level']}`",
                f"- Applies to: {', '.join(cast(list[str], enforcement['applies_to']))}",
                "- Rules:",
            ]
        )
        for rule in cast(list[dict[str, str]], policy["rules"]):
            lines.append(
                f"  - `{rule['code']}` ({rule['severity']}/{rule['failure_mode']}): {rule['statement']}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _render_skill_md(
    skill: dict[str, Any],
    warning_lookup: dict[str, dict[str, str]],
    workaround_lookup: dict[str, dict[str, str]],
) -> str:
    projection_note = _select_target_projection_note(skill, "opencode")

    lines = [
        f"# {skill['user_entrypoint']}",
        "",
        f"OpenCode package for canonical skill `{skill['id']}`.",
        "",
        "## Intent",
        "",
        cast(str, skill["intent"]),
        "",
        "## Inputs",
        "",
    ]
    for required_input in cast(list[str], skill["required_inputs"]):
        lines.append(f"- `{required_input}`")

    lines.extend(
        [
            "",
            "## Interaction Contract",
            "",
            f"- Entrypoint: `{skill['user_entrypoint']}`",
            f"- Interactive capture mode: `{skill['interactive_capture_mode']}`",
            f"- OpenCode projection: `{projection_note['workaround_class']}` — {projection_note['note']}",
            "",
            "## Workflow Steps",
            "",
        ]
    )
    for step in cast(list[dict[str, Any]], skill["workflow_steps"]):
        confirmation = "yes" if step["requires_confirmation"] else "no"
        lines.append(
            f"1. `{step['step_id']}` — {step['intent']} (requires confirmation: {confirmation})"
        )

    lines.extend(["", "## Required Capabilities", ""])
    for capability in cast(list[str], skill["required_capabilities"]):
        lines.append(f"- `{capability}`")

    lines.extend(["", "## Outputs", ""])
    for output in cast(list[str], skill["outputs"]):
        lines.append(f"- `{output}`")

    lines.extend(["", "## Preserved Compatibility Metadata", ""])
    for rule in cast(list[dict[str, str]], skill["workaround_rules"]):
        hazard = workaround_lookup[rule["hazard_category"]]
        warning = warning_lookup[rule["warning_code"]]
        lines.append(
            f"- `{rule['hazard_category']}` -> `{rule['workaround_class']}` / `{rule['warning_code']}`: {hazard['recommended_fallback']} [{warning['severity']}]"
        )

    lines.extend(["", "## Projection Notes", ""])
    for note in cast(list[dict[str, str]], skill["projection_notes"]):
        lines.append(
            f"- `{note['target']}` -> `{note['workaround_class']}`: {note['note']}"
        )

    return "\n".join(lines).rstrip() + "\n"


def _render_command_alias(skill: dict[str, Any]) -> str:
    capture_mode = cast(str, skill["interactive_capture_mode"])
    helper_note = (
        "Use the Explain -> Capture helper flow: explain the available options in plain text, then ask the user to choose or refine one explicitly."
        if capture_mode in {"structured_choice", "hybrid"}
        else "This alias is a thin command surface for a read-only or direct skill flow."
    )
    lines = [
        f"# /{skill['user_entrypoint']}",
        "",
        f"Alias command for `.opencode/skills/{skill['id']}/SKILL.md`.",
        "",
        "## Route",
        "",
        f"- Skill package: `.opencode/skills/{skill['id']}/SKILL.md`",
        f"- Entrypoint id: `{skill['user_entrypoint']}`",
        f"- Capture mode: `{capture_mode}`",
        "",
        "## Alias Behavior",
        "",
        f"- {helper_note}",
        "- Preserve approval-before-write and user decision ownership from `AGENTS.md`.",
        "- Keep output deterministic and aligned to the canonical workflow step order.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_projection() -> dict[str, Any]:
    whitelist = _parse_whitelist()
    agents = _load_agents(whitelist["agents"])
    skills = _load_skills(whitelist["skills"])
    policies = _load_policies(whitelist["policies"])
    shared_docs = _load_shared_docs(whitelist["shared_docs"])
    workflow = _read_yaml(WORKFLOW_PATH)
    platform = _load_opencode_platform()
    warning_lookup = _load_warning_lookup()
    workaround_lookup = _load_workaround_lookup()

    opencode_config = {
        "schema_version": "1.0",
        "target": "opencode",
        "target_posture": platform["posture"],
        "instructions_file": "AGENTS.md",
        "project_config_surface": "opencode.json",
        "skills_directory": ".opencode/skills",
        "commands_directory": ".opencode/commands",
        "agents": [
            {
                "id": agent["id"],
                "title": agent["title"],
                "model_profile": agent["model_profile"],
                "delegation_intent": agent["delegation_intent"],
                "tool_capability_needs": agent["tool_capability_needs"],
                "source_manifest": str(
                    (AGENTS_DIR / f"{agent['id']}.yaml").relative_to(REPO_ROOT)
                ),
            }
            for agent in agents
        ],
        "skills": [
            {
                "id": skill["id"],
                "entrypoint": skill["user_entrypoint"],
                "interactive_capture_mode": skill["interactive_capture_mode"],
                "path": f".opencode/skills/{skill['id']}/SKILL.md",
                "command_alias": f".opencode/commands/{skill['user_entrypoint']}.md",
                "required_capabilities": skill["required_capabilities"],
                "source_manifest": str(
                    (SKILLS_DIR / f"{skill['id']}.yaml").relative_to(REPO_ROOT)
                ),
            }
            for skill in skills
        ],
        "shared_docs": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "source_path": doc["path"],
            }
            for doc in shared_docs
        ],
        "policies": [
            {
                "id": policy["id"],
                "title": policy["title"],
                "enforcement": policy["enforcement"],
                "rule_codes": [
                    rule["code"] for rule in cast(list[dict[str, str]], policy["rules"])
                ],
            }
            for policy in policies
        ],
        "workflow": {
            "id": workflow["id"],
            "stages": workflow["stages"],
            "invariants": workflow["invariants"],
        },
    }

    oh_my_opencode = {
        "schema_version": "1.0",
        "target": "opencode",
        "config_kind": "oh-my-opencode",
        "posture": platform["posture"],
        "model_profile_mapping": {
            agent["id"]: {
                "model_profile": agent["model_profile"],
                "delegation_intent": agent["delegation_intent"],
            }
            for agent in agents
        },
        "permissions": {
            "approval_before_write": cast(dict[str, bool], workflow["invariants"])[
                "approval_before_write"
            ],
            "human_decision_owner": cast(dict[str, bool], workflow["invariants"])[
                "human_decision_owner"
            ],
            "commit_requires_explicit_user_request": True,
        },
        "feature_support": platform["features"],
        "source_semantic_mappings": {
            "slash_command_entrypoints": {
                "workaround_class": "native_mapping",
                "warning_code": "W_SLASH_COMMAND_ROUTED",
                "wrapper_required": False,
                "detail": "Canonical user_entrypoint values are projected into OpenCode command aliases that route to packaged skills.",
            },
            "structured_choice_capture": {
                "workaround_class": "generated_wrapper",
                "warning_code": "W_INTERACTIVE_CAPTURE_WRAPPED",
                "wrapper_required": True,
                "detail": "Structured choice and hybrid flows use generated Explain -> Capture helper aliases under `.opencode/commands/` when no one-to-one native UI is guaranteed.",
            },
            "approval_before_write_protocol": {
                "workaround_class": "native_mapping",
                "warning_code": "W_APPROVAL_PROTOCOL_ENFORCED",
                "wrapper_required": False,
                "detail": "Approval-before-write remains explicit through workflow metadata and AGENTS instructions.",
            },
        },
        "agents": [
            {
                "id": agent["id"],
                "native_feature": "agent_manifests",
                "projection": {
                    "target": "opencode",
                    "workaround_class": "native_mapping",
                    "note": "Agent manifest semantics are supported natively on OpenCode for v0.",
                },
                "warning_rules": agent["warning_rules"],
                "preserved_non_native_metadata": agent["projection_notes"],
            }
            for agent in agents
        ],
        "skills": [
            {
                "id": skill["id"],
                "projection": _select_target_projection_note(skill, "opencode"),
                "skill_path": f".opencode/skills/{skill['id']}/SKILL.md",
                "command_alias": f".opencode/commands/{skill['user_entrypoint']}.md",
                "workaround_rules": skill["workaround_rules"],
            }
            for skill in skills
        ],
        "policies": [
            {
                "id": policy["id"],
                "enforcement": policy["enforcement"],
                "rules": policy["rules"],
            }
            for policy in policies
        ],
        "workflow": {
            "id": workflow["id"],
            "stages": workflow["stages"],
            "invariants": workflow["invariants"],
        },
        "warnings": {
            code: warning_lookup[code]
            for code in sorted(
                {
                    rule["code"]
                    for agent in agents
                    for rule in cast(list[dict[str, str]], agent["warning_rules"])
                }
                | {
                    rule["warning_code"]
                    for skill in skills
                    for rule in cast(list[dict[str, str]], skill["workaround_rules"])
                }
                | {"W_SLASH_COMMAND_ROUTED", "W_APPROVAL_PROTOCOL_ENFORCED"}
            )
        },
    }

    rendered_files: dict[str, str] = {
        "AGENTS.md": _render_agents_md(agents, skills, policies, workflow, platform),
        "opencode.json": _render_json(opencode_config),
        ".opencode/oh-my-opencode.jsonc": _render_jsonc(oh_my_opencode),
    }

    for skill in skills:
        rendered_files[f".opencode/skills/{skill['id']}/SKILL.md"] = _render_skill_md(
            skill, warning_lookup, workaround_lookup
        )
        rendered_files[f".opencode/commands/{skill['user_entrypoint']}.md"] = (
            _render_command_alias(skill)
        )

    return {
        "output_root": DEFAULT_OUTPUT_ROOT,
        "rendered_files": rendered_files,
    }


def write_projection(output_root: Path = DEFAULT_OUTPUT_ROOT) -> list[Path]:
    projection = build_projection()
    rendered_files = cast(dict[str, str], projection["rendered_files"])

    output_root.mkdir(parents=True, exist_ok=True)

    written_paths: list[Path] = []
    for relative_path, content in rendered_files.items():
        destination = output_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        written_paths.append(destination)

    expected_paths = {output_root / relative_path for relative_path in rendered_files}
    for existing in sorted(output_root.rglob("*"), reverse=True):
        if existing.is_file() and existing not in expected_paths:
            existing.unlink()
        elif existing.is_dir() and not any(existing.iterdir()):
            existing.rmdir()

    return sorted(written_paths)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the OpenCode / Oh My OpenCode v0 projection."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Destination directory for the generated OpenCode project slice.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    output_root = args.output_root.resolve()

    if output_root.exists() and not output_root.is_dir():
        raise SystemExit(f"Output root is not a directory: {output_root}")

    written_paths = write_projection(output_root)
    print(
        f"Generated {len(written_paths)} OpenCode projection files under {output_root}"
    )
    for path in written_paths:
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
