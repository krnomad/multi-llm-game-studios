# v0 Whitelist (Locked Scope)

This document is the authoritative v0 extraction scope. If an artifact is not listed under **Included v0 artifacts**, it is out of scope.

## Included v0 artifacts (authoritative)

### agents

- `creative-director`
- `technical-director`
- `producer`
- `qa-lead`

### skills

- `start`
- `brainstorm`
- `setup-engine`
- `design-review`

### shared docs

- `collaboration-protocol`
- `onboarding`
- `engine-setup`
- `design-review-workflow`

### policies

- `commit-validation-intent`
- `test-standards`

### workflows

- `collaboration-approval-gate`

## Excluded from v0 (explicit)

- `team-*`
- `engine-specialist`
- `session-lifecycle-hooks`
- `asset-hooks`
- `statusline`
- `openclaw-gateway-channel-native-features`

## Enforcement intent

- Additions to the v0 set are not implicit; they require an explicit whitelist update.
- Tests under `tests/docs/` must fail when an unapproved artifact appears in the documented v0 set.
