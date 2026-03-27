from __future__ import annotations

import importlib.util
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast


ROOT = Path(__file__).resolve().parents[2]
FIXTURES_ROOT = ROOT / "fixtures" / "expected"


class OpenCodeGenerator(Protocol):
    def write_projection(self, output_root: Path) -> list[Path]: ...


class CodexGenerator(Protocol):
    def build_codex_projection(self, root: Path) -> dict[Path, str]: ...


class OpenClawGenerator(Protocol):
    OPENCLAW_DIR: Path
    WORKSPACE_DIR: Path

    def generate(self) -> list[Path]: ...


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module at {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _snapshot_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _read_fixture_tree(fixture_root: Path) -> dict[str, str]:
    return _snapshot_tree(fixture_root)


def _assert_matches_fixture(
    actual: Mapping[str, str], fixture_root: Path, label: str
) -> None:
    expected = _read_fixture_tree(fixture_root)
    assert set(actual) == set(expected), (
        f"{label} fixture file set drift: expected {sorted(expected)}, found {sorted(actual)}"
    )

    for relative_path in sorted(expected):
        assert actual[relative_path] == expected[relative_path], (
            f"{label} fixture content drift detected in {relative_path}"
        )


def test_opencode_projection_matches_expected_fixture(tmp_path: Path) -> None:
    module = cast(
        OpenCodeGenerator,
        cast(
            object,
            _load_module(
                ROOT / "tools" / "projectors" / "generate_opencode.py",
                "generate_opencode_drift",
            ),
        ),
    )
    output_root = tmp_path / "opencode"

    _ = module.write_projection(output_root)

    _assert_matches_fixture(
        _snapshot_tree(output_root),
        FIXTURES_ROOT / "opencode",
        "OpenCode",
    )


def test_codex_projection_matches_expected_fixture() -> None:
    module = cast(
        CodexGenerator,
        cast(
            object,
            _load_module(
                ROOT / "tools" / "projectors" / "generate_codex.py",
                "generate_codex_drift",
            ),
        ),
    )
    rendered = module.build_codex_projection(ROOT)
    actual = {
        relative_path.relative_to("adapters/codex").as_posix(): content
        for relative_path, content in rendered.items()
    }

    _assert_matches_fixture(actual, FIXTURES_ROOT / "codex", "Codex")


def test_openclaw_projection_matches_expected_fixture(tmp_path: Path) -> None:
    module = cast(
        OpenClawGenerator,
        cast(
            object,
            _load_module(
                ROOT / "tools" / "projectors" / "generate_openclaw.py",
                "generate_openclaw_drift",
            ),
        ),
    )
    output_root = tmp_path / "openclaw"

    original_openclaw_dir = module.OPENCLAW_DIR
    original_workspace_dir = module.WORKSPACE_DIR
    module.OPENCLAW_DIR = output_root
    module.WORKSPACE_DIR = output_root / "workspace"

    try:
        _ = module.generate()
    finally:
        module.OPENCLAW_DIR = original_openclaw_dir
        module.WORKSPACE_DIR = original_workspace_dir

    _assert_matches_fixture(
        _snapshot_tree(output_root),
        FIXTURES_ROOT / "openclaw",
        "OpenClaw",
    )
