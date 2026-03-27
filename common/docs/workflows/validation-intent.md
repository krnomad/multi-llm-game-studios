# Validation Intent Workflow

## Purpose

Validation protects quality at decision boundaries. The goal is to catch missing required sections, malformed project data, and obvious policy violations before a change is treated as ready to commit, push, or rely on as canonical project input.

## Approval Before Write

Validation does not replace user approval. The worker must still show the draft or an accurate summary, ask for permission, and wait for explicit approval before creating or editing files.

## Validation Triggers

Validation can run at several moments, depending on the current harness:

- before a write is finalized into version control
- before a push or other publication step
- immediately after certain file edits
- at session start or recovery time to surface project-state gaps

The canonical layer defines the intent of these checks, not the exact hook names or config files that invoke them.

## Required Checks

### Design document completeness

Design documents should be checked for required sections before commit or equivalent approval gates.

### Structured data validity

Machine-readable project data should be checked for valid syntax and basic integrity before it is accepted.

### Code quality warnings

Implementation changes may be checked for obvious anti-patterns such as unowned TODO markers or hardcoded balance values that should live in data.

### Project-state gap detection

A harness may surface missing setup, missing design docs, or other recoverable workflow gaps at session boundaries so the user can choose the right next step.

## Blocking vs Warning Behavior

- Blocking checks stop the risky operation until the problem is fixed.
- Warning checks surface concerns without stopping progress.
- The harness should explain which outcome occurred and why.

## Canonical Guarantees

- Approval-before-write remains mandatory even when validation passes.
- Validation should focus on actionable quality signals, not tool-specific ceremony.
- Required design sections and structured-data correctness are high-value default checks.
- Session or workflow checks may recommend the next step, but they do not remove user choice.

## Source Examples

- The Claude source uses hooks around commit, push, asset validation, and session boundaries to run checks and show warnings or blocks.
- Source files may mention `.claude/settings.json` or specific hook script names. Those are implementation details, not canonical requirements.
