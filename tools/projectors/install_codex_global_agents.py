from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "tools/projectors/generate_codex.py"
INSTALL_SOURCE_DIR = ROOT / "adapters/codex/install/global-agents"


def _load_generator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate_codex", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Codex generator module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_global_agents(target_dir: Path, root: Path = ROOT) -> list[Path]:
    generator = _load_generator_module()
    generator.write_codex_projection(root)

    package_manifest = json.loads(
        (INSTALL_SOURCE_DIR / "package_manifest.json").read_text(encoding="utf-8")
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    installed: list[Path] = []
    for agent in package_manifest["agents"]:
        relative_source = Path(agent["source"])
        source_path = INSTALL_SOURCE_DIR / relative_source
        destination_path = target_dir / relative_source.name
        shutil.copyfile(source_path, destination_path)
        installed.append(destination_path)
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install generated Codex global-agent workaround files."
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        help="Directory that Codex scans for globally installed custom agents.",
    )
    args = parser.parse_args()

    installed = install_global_agents(Path(args.target_dir).expanduser().resolve())
    for path in installed:
        print(path)
    print(f"Installed {len(installed)} Codex global-agent files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
