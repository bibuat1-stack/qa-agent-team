---
name: write-repro-pack
description: >-
  Writes a complete bug reproduction pack (steps, expected vs actual,
  environment, evidence) for engineering handoff.
---
# Write repro pack

## When to use

You have attempted a repro or the user supplied complete steps and need a handoff artifact.

## Approval bar

- No production customer PII, tokens, or secret log dumps.
- No tracker or Slack posts without explicit yes.
- Prefer `/workspace` screenshot paths.

## Required sections

If unknown, write `unknown`. Do not invent.

1. Title
2. Environment
3. Account (fresh test / seeded fixture, never real customer)
4. Preconditions
5. Exact numbered steps
6. Expected
7. Actual
8. Evidence paths
9. Frequency
10. Minimal test case
11. Not tried

## Quality bar

A stranger should reproduce without asking you. If they would need a secret or production row, strip it and list the blocker.
