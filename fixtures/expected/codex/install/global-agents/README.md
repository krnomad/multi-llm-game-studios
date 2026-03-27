# Codex Global-Agent Install Workaround

This package is the official workaround for Codex project-local custom-agent loading limitations.
When `.codex/agents/` is not loaded reliably, install the generated agent TOMLs into a globally discoverable Codex directory.

## Contract
- Codex remains supported with workarounds.
- This package is documented and first-class, not hidden tribal knowledge.
- Structured-choice agents still use deterministic text-first wrappers instead of claiming native parity.

## Included agents
- creative-director
- producer
- qa-lead
- technical-director

## Installer
Run `python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/` or another Codex global-agent directory.
