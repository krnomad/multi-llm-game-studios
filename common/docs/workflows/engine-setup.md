# Engine Setup Workflow

## Purpose

Engine setup pins the project's engine choices, fills in default technical preferences, and addresses knowledge gaps before downstream design or implementation work depends on outdated assumptions.

## Entry Modes

### Explicit engine input

If the user already knows the engine and version they want, confirm the choice and use it as the basis for the rest of the workflow.

### Guided recommendation

If the user has not chosen an engine yet, gather enough context to recommend one or two suitable options. Relevant inputs include game type, target platforms, team size, experience level, language preferences, licensing constraints, and any existing concept document.

## Recommendation Contract

- Tie recommendations to the user's stated needs.
- Present top options with concise reasoning and tradeoffs.
- Let the user choose. Recommendation is advisory, not mandatory.

## Update Project Configuration

Once the engine is chosen, update the project's canonical engine, language, build, and asset-pipeline settings in the project configuration layer used by the current harness.

## Populate Technical Preferences

Fill in engine-appropriate defaults for naming conventions, testing defaults, and other technical preferences. Present those defaults to the user and wait for approval before writing them.

## Determine Knowledge Gap

Compare the chosen engine version against the worker's trusted knowledge baseline.

- Low risk: version is comfortably within known coverage
- Medium risk: version is near the edge of known coverage
- High risk: version is beyond known coverage

Explain the risk level to the user and why it matters.

## Handle Knowledge Gaps

### Low risk

Reference material is optional but still useful. A lightweight version record is enough.

### Medium or high risk

Version-pinned reference material is required before the worker relies on engine-specific APIs or upgrade assumptions. Gather current official references, summarize breaking changes and deprecated APIs, and keep that material tied to the chosen version.

## User Approval Guarantees

- Do not save default preferences until the user approves them.
- Do not present inferred engine choices as final decisions.
- Keep knowledge-gap handling visible so the user understands when extra verification is required.

## Canonical Meaning

The canonical workflow is engine selection, preference drafting, knowledge-gap assessment, and version-aware reference capture. A source system may expose this through `setup-engine` and web lookups, but those exact command names and mechanisms are implementation examples, not canonical requirements.

## Source Examples

- The Claude source uses `setup-engine` for both recommendation mode and explicit engine input.
- The source flow updates project settings, drafts technical preferences, classifies knowledge-gap risk, and fetches current engine references when the chosen version exceeds the model's trusted coverage.
