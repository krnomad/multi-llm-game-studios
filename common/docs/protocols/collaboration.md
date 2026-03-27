# Collaboration Protocol

## Core Principle

Collaboration is user-driven, not agent-driven. The worker asks, the user decides, the worker drafts, and no file changes are made until the user approves the write.

## Stage Order

Every collaborative task follows this exact stage order:

`Question -> Options -> Decision -> Draft -> Approval`

## Stage Definitions

### Question

Ask for the missing context that affects the outcome. Questions should surface constraints, priorities, scope, and any facts the worker cannot infer safely.

### Options

Present the meaningful paths forward with brief reasoning, tradeoffs, or examples. Options help the user compare choices without surrendering decision ownership.

### Decision

Wait for the user to choose a direction, refine an option, or supply a new one. The selected direction becomes the basis for the next draft.

### Draft

Show the proposed content, plan, summary, or implementation shape before any write occurs. For larger work, the worker may iterate on partial drafts section by section.

### Approval

Get explicit approval before creating or editing files. If multiple files are part of one change, approval must cover the full changeset that will be written.

## Approval Gates

- Ask for permission before any write or edit operation.
- Show a draft or a faithful summary before asking for that permission.
- Keep user ownership of the final decision. Approval is not implied by earlier discussion.
- Do not commit changes unless the user explicitly asks for a commit.

## Iteration Rules

- If the user requests changes, return to Draft and continue iterating.
- If the worker uncovers a new design fork, return to Options and wait for a Decision.
- If the user approves one section at a time, only treat the approved portion as ready to write.

## Harness-Neutral Notes

The protocol requires explicit questions, options, decisions, drafts, and approvals. It does not require a specific tool, UI widget, hook name, or slash command. Source systems may use structured decision tools or command shortcuts, but those are examples of one implementation, not canonical requirements.

## Source Examples

- Claude source docs show this protocol as a fixed sequence and include prompts such as "May I write this to [filepath]?"
- Claude examples may use `AskUserQuestion` for structured choice collection. That tool name is a source example, not canonical vocabulary.
