# Onboarding Workflow

## Purpose

Onboarding helps a user identify their starting point, understand the next sensible step, and choose that step intentionally. It is for first-session or early-session guidance when the project state is still unclear.

## Detect Project State

Before opening the conversation, gather context silently when the environment allows it. Check whether an engine is configured, whether a core concept document exists, whether source code or prototypes already exist, and whether design or production artifacts are already present. Use those findings to tailor guidance, not to replace the user's self-assessment.

## Ask Where the User Is

Present four starting points clearly:

- No idea yet
- Vague idea
- Clear concept
- Existing work

Wait for the user's answer before routing them.

## Routing Paths

### No idea yet

Recommend concept discovery before technical setup. The next path should focus on guided ideation, then engine choice, then system mapping, prototyping, and sprint planning.

### Vague idea

Ask the user to share the seed of the idea, validate it as a usable starting point, then recommend concept development before engine setup and downstream planning.

### Clear concept

Ask a few follow-up questions about genre, core mechanic, engine preference, and scope. Then offer two paths: formalize the concept first, or proceed to engine setup first.

### Existing work

Share the relevant state findings, identify what already exists, and recommend gap analysis before deciding the next workflow. If the engine is not configured yet, call that out as an early dependency.

## Confirm Before Proceeding

After presenting the recommended path, ask which step the user wants to take first. Never auto-run the next workflow just because it was recommended.

## Hand Off

The onboarding workflow is complete once the user has a clear next action and either chooses to invoke that action or asks the worker to help with it.

## Edge Cases

- If the user claims to have existing work but the project is effectively empty, gently redirect them to a better starting path.
- If the user chooses a fresh-start path but existing artifacts are present, mention what was found and ask whether they want to continue from existing work instead.
- If the project is already configured and the concept already exists, skip the full onboarding script and offer a resume-work suggestion.
- If none of the four paths fit, let the user describe their situation in their own words and adapt.

## Canonical Meaning

The canonical requirement is a guided start flow that diagnoses the user's state, presents clear paths, and waits for user choice before moving on. A source system may expose this flow through `/start`, but the command name itself is not part of the canonical contract.

## Source Examples

- The Claude source implements this workflow through the `/start` skill.
- The source flow checks configuration and artifact state silently, then presents the four starting paths before recommending a next step.
