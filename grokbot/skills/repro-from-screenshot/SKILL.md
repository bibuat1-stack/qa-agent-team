---
name: repro-from-screenshot
description: >-
  Turns a screenshot or screen recording into a hypothesized repro path for
  staging verification.
---
# Repro from screenshot

## When to use

Primary artifact is an image or screen recording. Pair with [repro-from-ticket](sand-workflow:repro-from-ticket) if a ticket also exists.

## Approval bar

Staging/test accounts only. No production data. No posting without yes. No secrets in chat.

## Sequence

1. Describe only what is visible.
2. Infer surface from chrome and label inferences.
3. Hypothesize 1 to 3 shortest paths.
4. List what the screenshot does not show.
5. Propose next staging action or ask for steps.
6. Pass evidence into [write-repro-pack](sand-workflow:write-repro-pack). Do not claim reproduction until actually reproduced.

## Output

Visible, Inferred, Not visible, Hypotheses, Next.

## Failure

Unreadable or not product UI: say so and stop.
