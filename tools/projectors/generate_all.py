from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

TARGETS = (
    ("OpenCode", REPO_ROOT / "tools" / "projectors" / "generate_opencode.py"),
    ("Codex", REPO_ROOT / "tools" / "projectors" / "generate_codex.py"),
    ("OpenClaw", REPO_ROOT / "tools" / "projectors" / "generate_openclaw.py"),
)


def main() -> int:
    for index, (label, script_path) in enumerate(TARGETS, start=1):
        print(f"==> [{index}/{len(TARGETS)}] Generating {label}", flush=True)
        _ = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=REPO_ROOT,
            check=True,
        )

    print("All target projections generated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
