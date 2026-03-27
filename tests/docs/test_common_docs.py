from pathlib import Path


COLLABORATION_PATH = Path("common/docs/protocols/collaboration.md")
ONBOARDING_PATH = Path("common/docs/workflows/onboarding.md")
ENGINE_SETUP_PATH = Path("common/docs/workflows/engine-setup.md")
DESIGN_REVIEW_PATH = Path("common/docs/workflows/design-review.md")
VALIDATION_INTENT_PATH = Path("common/docs/workflows/validation-intent.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_headings_in_order(text: str, headings: list[str]) -> None:
    position = -1
    for heading in headings:
        next_position = text.find(heading)
        assert next_position != -1, f"Missing heading: {heading}"
        assert next_position > position, f"Heading out of order: {heading}"
        position = next_position


def test_collaboration_doc_preserves_stage_order_and_approval_rules() -> None:
    text = _read(COLLABORATION_PATH)

    _assert_headings_in_order(
        text,
        [
            "## Core Principle",
            "## Stage Order",
            "## Stage Definitions",
            "## Approval Gates",
            "## Iteration Rules",
            "## Harness-Neutral Notes",
            "## Source Examples",
        ],
    )

    stage_line = "`Question -> Options -> Decision -> Draft -> Approval`"
    assert stage_line in text

    question_index = text.index("### Question")
    options_index = text.index("### Options")
    decision_index = text.index("### Decision")
    draft_index = text.index("### Draft")
    approval_index = text.index("### Approval")

    assert (
        question_index < options_index < decision_index < draft_index < approval_index
    )
    assert "May I write this to [filepath]?" in text
    assert "not canonical vocabulary" in text


def test_onboarding_doc_preserves_guided_start_semantics() -> None:
    text = _read(ONBOARDING_PATH)

    _assert_headings_in_order(
        text,
        [
            "## Purpose",
            "## Detect Project State",
            "## Ask Where the User Is",
            "## Routing Paths",
            "## Confirm Before Proceeding",
            "## Hand Off",
            "## Edge Cases",
            "## Canonical Meaning",
            "## Source Examples",
        ],
    )

    for option in [
        "No idea yet",
        "Vague idea",
        "Clear concept",
        "Existing work",
    ]:
        assert option in text

    assert "Never auto-run the next workflow" in text
    assert "`/start`" in text


def test_engine_setup_doc_preserves_recommendation_and_knowledge_gap_semantics() -> (
    None
):
    text = _read(ENGINE_SETUP_PATH)

    _assert_headings_in_order(
        text,
        [
            "## Purpose",
            "## Entry Modes",
            "## Recommendation Contract",
            "## Update Project Configuration",
            "## Populate Technical Preferences",
            "## Determine Knowledge Gap",
            "## Handle Knowledge Gaps",
            "## User Approval Guarantees",
            "## Canonical Meaning",
            "## Source Examples",
        ],
    )

    for risk_level in ["Low risk", "Medium risk", "High risk"]:
        assert risk_level in text

    assert "wait for approval before writing them" in text
    assert "trusted knowledge baseline" in text


def test_design_review_doc_preserves_checklist_and_verdict_contract() -> None:
    text = _read(DESIGN_REVIEW_PATH)

    _assert_headings_in_order(
        text,
        [
            "## Purpose",
            "## Review Inputs",
            "## Design Document Standard Checklist",
            "## Consistency Checks",
            "## Implementability Checks",
            "## Cross-System Checks",
            "## Review Output Contract",
            "## Verdict Contract",
            "## Next Step Guidance",
            "## Canonical Meaning",
            "## Source Examples",
        ],
    )

    for section in [
        "Overview",
        "Player Fantasy",
        "Detailed Rules",
        "Formulas",
        "Edge Cases",
        "Dependencies",
        "Tuning Knobs",
        "Acceptance Criteria",
    ]:
        assert section in text

    assert "APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED" in text
    assert "The review itself is read-only." in text


def test_validation_intent_doc_preserves_approval_and_validation_guarantees() -> None:
    text = _read(VALIDATION_INTENT_PATH)

    _assert_headings_in_order(
        text,
        [
            "## Purpose",
            "## Approval Before Write",
            "## Validation Triggers",
            "## Required Checks",
            "## Blocking vs Warning Behavior",
            "## Canonical Guarantees",
            "## Source Examples",
        ],
    )

    assert (
        "Approval-before-write remains mandatory even when validation passes." in text
    )
    assert (
        "Required design sections and structured-data correctness are high-value default checks."
        in text
    )
    assert ".claude/settings.json" in text
    assert "implementation details, not canonical requirements" in text
