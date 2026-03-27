import json
import tomllib
from pathlib import Path
from typing import TypedDict, cast

import yaml


DOCS_DIR = Path("docs")
FEATURE_MATRIX_PATH = Path("common/compatibility/feature-matrix.yaml")
WORKAROUND_MATRIX_PATH = Path("common/compatibility/workaround-matrix.yaml")
V0_WHITELIST_PATH = Path("common/docs/migration/v0-whitelist.md")
CODEX_CONFIG_PATH = Path("adapters/codex/project/.codex/config.toml")
OPENCLAW_CONFIG_PATH = Path("adapters/openclaw/openclaw.json5")
CODEX_INSTALL_MANIFEST_PATH = Path(
    "adapters/codex/install/global-agents/package_manifest.json"
)

MULTI_HARNESS_OVERVIEW_PATH = DOCS_DIR / "multi-harness-overview.md"
SUPPORT_LEVELS_PATH = DOCS_DIR / "support-levels.md"
AUTHORING_GUIDE_PATH = DOCS_DIR / "canonical-authoring-guide.md"
CODEX_INSTALL_DOC_PATH = DOCS_DIR / "codex-global-install.md"
WORKAROUND_MATRIX_DOC_PATH = DOCS_DIR / "workaround-matrix.md"


class SupportPostureMap(TypedDict):
    opencode: str
    codex: str
    openclaw: str


class FeatureMatrixDoc(TypedDict):
    support_posture: SupportPostureMap


class WorkaroundMatrixDoc(TypedDict):
    approved_workaround_classes: list[str]


class CodexConfig(TypedDict):
    support_posture: str


class OpenClawConfig(TypedDict):
    support_posture: str


class InstallManifest(TypedDict):
    package_type: str
    install_requires_global_scope: bool
    warning_code: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_feature_matrix(path: Path) -> FeatureMatrixDoc:
    return cast(FeatureMatrixDoc, yaml.safe_load(path.read_text(encoding="utf-8")))


def _load_workaround_matrix(path: Path) -> WorkaroundMatrixDoc:
    return cast(WorkaroundMatrixDoc, yaml.safe_load(path.read_text(encoding="utf-8")))


def test_operator_docs_exist() -> None:
    for path in [
        MULTI_HARNESS_OVERVIEW_PATH,
        SUPPORT_LEVELS_PATH,
        AUTHORING_GUIDE_PATH,
        CODEX_INSTALL_DOC_PATH,
        WORKAROUND_MATRIX_DOC_PATH,
    ]:
        assert path.is_file(), f"Missing operator doc: {path}"


def test_overview_and_authoring_docs_match_repo_commands_and_paths() -> None:
    overview = _read(MULTI_HARNESS_OVERVIEW_PATH)
    authoring = _read(AUTHORING_GUIDE_PATH)

    for text in [overview, authoring]:
        assert "common/" in text
        assert "python3 tools/projectors/generate_all.py" in text
        assert "python3 tools/validate/run_all.py" in text

    assert "adapters/opencode/project/" in overview
    assert "adapters/codex/project/" in overview
    assert "adapters/openclaw/" in overview
    assert "Treat `adapters/` as generated output" in overview
    assert "common/docs/migration/v0-whitelist.md" in overview
    assert "Generated adapter files under `adapters/` are outputs" in authoring
    assert "common/docs/migration/v0-whitelist.md" in authoring
    assert "Do not hand-edit `adapters/opencode/project/`" in authoring
    assert "Do not hand-edit `adapters/codex/project/`" in authoring
    assert "Do not hand-edit `adapters/openclaw/workspace/`" in authoring


def test_support_levels_doc_matches_feature_matrix_and_adapter_configs() -> None:
    text = _read(SUPPORT_LEVELS_PATH)
    feature_matrix = _load_feature_matrix(FEATURE_MATRIX_PATH)
    codex_config = cast(
        CodexConfig,
        cast(object, tomllib.loads(CODEX_CONFIG_PATH.read_text(encoding="utf-8"))),
    )
    openclaw_config = cast(
        OpenClawConfig,
        cast(object, json.loads(OPENCLAW_CONFIG_PATH.read_text(encoding="utf-8"))),
    )

    support_posture = feature_matrix["support_posture"]
    assert f"`{support_posture['opencode']}`" in text
    assert f"`{support_posture['codex']}`" in text
    assert f"`{support_posture['openclaw']}`" in text

    assert codex_config["support_posture"] == support_posture["codex"]
    assert openclaw_config["support_posture"] == support_posture["openclaw"]
    assert (
        "project-local custom agents are not treated as a reliable native loading surface"
        in text
    )
    assert "gateway-native behavior, channel-native UI, or runtime hook parity" in text
    assert "OpenCode is the primary v0 projection target" in text


def test_codex_install_doc_matches_generated_workaround_assets() -> None:
    text = _read(CODEX_INSTALL_DOC_PATH)
    install_manifest = cast(
        InstallManifest,
        cast(
            object,
            json.loads(CODEX_INSTALL_MANIFEST_PATH.read_text(encoding="utf-8")),
        ),
    )

    assert "supported_with_workarounds" in text
    assert "adapters/codex/project/.codex/agents/*.toml" in text
    assert "adapters/codex/install/global-agents/" in text
    assert "package_manifest.json" in text
    assert (
        "python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/"
        in text
    )
    assert install_manifest["package_type"] == "global_agent_workaround"
    assert install_manifest["install_requires_global_scope"] is True
    assert install_manifest["warning_code"] == "W_CODEX_PROJECT_LOCAL_AGENT_LIMITATION"


def test_workaround_doc_matches_approved_classes_and_examples() -> None:
    text = _read(WORKAROUND_MATRIX_DOC_PATH)
    workaround_matrix = _load_workaround_matrix(WORKAROUND_MATRIX_PATH)

    classes = workaround_matrix["approved_workaround_classes"]
    positions = [text.index(f"`{name}`") for name in classes]
    assert positions == sorted(positions)

    assert "W_INTERACTIVE_CAPTURE_WRAPPED" in text
    assert "W_SLASH_COMMAND_ROUTED" in text
    assert "W_HOOK_EVENT_DOWNGRADED" in text
    assert "`hook_event_semantics` maps to `external_runner`" in text
    assert "W_APPROVAL_PROTOCOL_ENFORCED" in text
    assert "external_runner_metadata" in text
    assert (
        "OpenClaw `policy_guards` and `workflow_approval_gates` are `externalized`"
        in text
    )


def test_docs_do_not_normalize_generated_adapter_edits_as_primary_workflow() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            MULTI_HARNESS_OVERVIEW_PATH,
            SUPPORT_LEVELS_PATH,
            AUTHORING_GUIDE_PATH,
            CODEX_INSTALL_DOC_PATH,
            WORKAROUND_MATRIX_DOC_PATH,
        ]
    )

    assert "Edit canonical files in `common/` only." in combined
    assert "do not hand-edit them as the normal workflow" in combined
    assert "OpenCode-equivalent fidelity" in combined


def test_docs_reference_v0_whitelist_as_scope_lock() -> None:
    whitelist_text = _read(V0_WHITELIST_PATH)
    combined = "\n".join(
        _read(path)
        for path in [
            MULTI_HARNESS_OVERVIEW_PATH,
            SUPPORT_LEVELS_PATH,
            AUTHORING_GUIDE_PATH,
        ]
    )

    assert "v0 Whitelist" in whitelist_text
    assert "common/docs/migration/v0-whitelist.md" in combined
