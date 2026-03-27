from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OPENCLAW_DIR = ROOT / "adapters" / "openclaw"
WORKSPACE_DIR = OPENCLAW_DIR / "workspace"

EXPECTED_AGENT_FILES = {
    "creative-director.md",
    "technical-director.md",
    "producer.md",
    "qa-lead.md",
}

EXPECTED_SKILL_DIRS = {
    "start",
    "brainstorm",
    "setup-engine",
    "design-review",
}

EXPECTED_POLICY_FILES = {
    "commit-validation-intent.md",
    "test-standards.md",
}

EXPECTED_WORKFLOW_FILES = {"collaboration-approval-gate.md"}

EXPECTED_DOC_FILES = {
    "docs/protocols/collaboration.md",
    "docs/workflows/onboarding.md",
    "docs/workflows/engine-setup.md",
    "docs/workflows/design-review.md",
}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    _assert((WORKSPACE_DIR / "AGENTS.md").is_file(), "Missing workspace/AGENTS.md")
    _assert((WORKSPACE_DIR / "SOUL.md").is_file(), "Missing workspace/SOUL.md")

    agent_files = {path.name for path in (WORKSPACE_DIR / "agents").glob("*.md")}
    skill_dirs = {
        path.name for path in (WORKSPACE_DIR / "skills").iterdir() if path.is_dir()
    }
    policy_files = {path.name for path in (WORKSPACE_DIR / "policies").glob("*.md")}
    workflow_files = {path.name for path in (WORKSPACE_DIR / "workflows").glob("*.md")}
    doc_files = {
        path.relative_to(WORKSPACE_DIR).as_posix()
        for path in (WORKSPACE_DIR / "docs").glob("**/*.md")
    }

    _assert(
        agent_files == EXPECTED_AGENT_FILES, f"Unexpected agent files: {agent_files}"
    )
    _assert(skill_dirs == EXPECTED_SKILL_DIRS, f"Unexpected skill dirs: {skill_dirs}")
    _assert(
        policy_files == EXPECTED_POLICY_FILES,
        f"Unexpected policy files: {policy_files}",
    )
    _assert(
        workflow_files == EXPECTED_WORKFLOW_FILES,
        f"Unexpected workflow files: {workflow_files}",
    )
    _assert(doc_files == EXPECTED_DOC_FILES, f"Unexpected doc files: {doc_files}")

    config = json.loads((OPENCLAW_DIR / "openclaw.json5").read_text(encoding="utf-8"))
    _assert(config["platform"] == "openclaw", "Config platform must be openclaw")
    _assert(
        config["support_posture"] == "repo_cli_compatibility_only",
        "OpenClaw support posture must stay repo_cli_compatibility_only",
    )
    _assert(
        config["native_parity"] == "not_supported_in_v0",
        "OpenClaw native parity must stay explicitly unsupported",
    )
    _assert(
        config["fallback_contract"]["policy_guards"] == "external_runner_metadata",
        "Policy guards must route through external runner metadata",
    )
    _assert(
        config["fallback_contract"]["workflow_approval_gates"]
        == "external_runner_metadata",
        "Workflow approval gates must route through external runner metadata",
    )
    _assert(
        "gateway_integration" in config["unsupported_surfaces"],
        "Gateway integration must remain unsupported",
    )

    soul_text = (WORKSPACE_DIR / "SOUL.md").read_text(encoding="utf-8")
    _assert(
        "repository-readable and CLI-usable workspace" in soul_text,
        "SOUL must state repo/CLI-only scope",
    )
    _assert(
        "Do not claim or emulate gateway-native or channel-native runtime behavior."
        in soul_text,
        "SOUL must state gateway/channel-native limits",
    )
    _assert(
        "external runner" in soul_text.lower(),
        "SOUL must mention external runner fallback",
    )

    print("OpenClaw smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
