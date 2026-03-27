from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

VALIDATORS = (
    (
        "Schema and warning contracts",
        [sys.executable, "-m", "pytest", "tests/schema", "tests/warnings", "-q"],
    ),
    (
        "Canonical manifest tests",
        [sys.executable, "-m", "pytest", "tests/manifests", "-q"],
    ),
    (
        "Canonical policy tests",
        [sys.executable, "-m", "pytest", "tests/policies", "-q"],
    ),
    (
        "Core docs tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/docs/test_v0_whitelist.py",
            "tests/docs/test_common_docs.py",
            "tests/docs/test_operator_docs.py",
            "-q",
        ],
    ),
    ("OpenCode", REPO_ROOT / "tools" / "validate" / "smoke_opencode.py"),
    ("Codex", REPO_ROOT / "tools" / "validate" / "smoke_codex.py"),
    ("OpenClaw", REPO_ROOT / "tools" / "validate" / "smoke_openclaw.py"),
    (
        "Projector tests",
        [sys.executable, "-m", "pytest", "tests/projectors", "-q"],
    ),
    (
        "Drift tests",
        [sys.executable, "-m", "pytest", "tests/drift", "-q"],
    ),
)


def main() -> int:
    for index, (label, command_or_path) in enumerate(VALIDATORS, start=1):
        print(f"==> [{index}/{len(VALIDATORS)}] Validating {label}", flush=True)
        if isinstance(command_or_path, list):
            _ = subprocess.run(command_or_path, cwd=REPO_ROOT, check=True)
        else:
            _ = subprocess.run(
                [sys.executable, str(command_or_path)],
                cwd=REPO_ROOT,
                check=True,
            )

    print("All target validations passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
