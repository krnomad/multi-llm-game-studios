# Codex Global-Agent Install Workaround

## Why this exists

Codex v0 support is `supported_with_workarounds`, not native parity. The repository treats project-local custom-agent loading as unreliable, so the generated global-agent package is the concrete fallback.

## Generated locations

- Project-local Codex agents: `adapters/codex/project/.codex/agents/*.toml`
- Generated install package: `adapters/codex/install/global-agents/`
- Generated install manifest: `adapters/codex/install/global-agents/package_manifest.json`
- Generated install readme: `adapters/codex/install/global-agents/README.md`

## When to use the workaround

Use it when Codex does not reliably discover or load the repo-local files under `.codex/agents/`.

## Concrete install command

Run:

`python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/`

You can replace `~/.codex/agents/` with another global Codex agent directory if your local setup scans a different path.

## What gets installed

The installer copies the generated TOML files listed in `adapters/codex/install/global-agents/package_manifest.json` into the target directory.

## What this does not change

- Codex still remains `supported_with_workarounds`.
- Structured choice flows still use deterministic text-first wrappers.
- This does not upgrade Codex to OpenCode-equivalent fidelity.

## Maintainer flow

1. Update canonical source in `common/`.
2. Run `python3 tools/projectors/generate_all.py`.
3. If Codex needs the workaround, run `python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/`.
4. Run `python3 tools/validate/run_all.py`.

## Operator note

Keep the workaround documented and concrete. It is part of the supported Codex path in this repo, not tribal knowledge.
