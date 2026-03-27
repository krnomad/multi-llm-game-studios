import re
from pathlib import Path


WHITELIST_PATH = Path("common/docs/migration/v0-whitelist.md")


def _parse_whitelist() -> dict[str, set[str]]:
    lines = WHITELIST_PATH.read_text(encoding="utf-8").splitlines()

    included_sections: dict[str, set[str]] = {
        "agents": set(),
        "skills": set(),
        "shared docs": set(),
        "policies": set(),
        "workflows": set(),
    }
    excluded: set[str] = set()

    current_h2 = ""
    current_h3 = ""
    item_pattern = re.compile(r"^- `([^`]+)`$")

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("## "):
            current_h2 = line[3:].strip()
            current_h3 = ""
            continue
        if line.startswith("### "):
            current_h3 = line[4:].strip()
            continue

        match = item_pattern.match(line)
        if not match:
            continue

        item = match.group(1)
        if (
            current_h2 == "Included v0 artifacts (authoritative)"
            and current_h3 in included_sections
        ):
            included_sections[current_h3].add(item)
        elif current_h2 == "Excluded from v0 (explicit)":
            excluded.add(item)

    return {
        "agents": included_sections["agents"],
        "skills": included_sections["skills"],
        "shared_docs": included_sections["shared docs"],
        "policies": included_sections["policies"],
        "workflows": included_sections["workflows"],
        "excluded": excluded,
    }


def test_v0_whitelist_included_artifacts_exact() -> None:
    parsed = _parse_whitelist()

    assert parsed["agents"] == {
        "creative-director",
        "technical-director",
        "producer",
        "qa-lead",
    }
    assert parsed["skills"] == {
        "start",
        "brainstorm",
        "setup-engine",
        "design-review",
    }
    assert parsed["shared_docs"] == {
        "collaboration-protocol",
        "onboarding",
        "engine-setup",
        "design-review-workflow",
    }
    assert parsed["policies"] == {
        "commit-validation-intent",
        "test-standards",
    }
    assert parsed["workflows"] == {
        "collaboration-approval-gate",
    }


def test_v0_whitelist_excluded_artifacts_exact() -> None:
    parsed = _parse_whitelist()

    assert parsed["excluded"] == {
        "team-*",
        "engine-specialist",
        "session-lifecycle-hooks",
        "asset-hooks",
        "statusline",
        "openclaw-gateway-channel-native-features",
    }


def test_v0_whitelist_has_no_overlap_between_included_and_excluded() -> None:
    parsed = _parse_whitelist()
    included_union = (
        parsed["agents"]
        | parsed["skills"]
        | parsed["shared_docs"]
        | parsed["policies"]
        | parsed["workflows"]
    )

    assert included_union.isdisjoint(parsed["excluded"])
