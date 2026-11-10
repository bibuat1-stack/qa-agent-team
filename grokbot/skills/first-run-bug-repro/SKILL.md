---
name: first-run-bug-repro
description: >-
  Walks first-run setup for Bug Repro (tracker, staging URL, test-account
  handoff) before any live repro.
---
# First-run: Bug Repro

## When to use

First message after install, or the user says set up.

## Approval bar

- Staging URL required before computer-use against a product.
- Test credentials via secure handoff only.
- No production URL as the default target.
- Do not write secrets into skills, shared memory, or chat.

## Sequence

1. State the job: ticket or screenshot to repro pack. Staging plus fresh test account. Never production customer data. Never post back without yes.
2. Ask for tracker: GitHub, Linear, or paste-only.
3. Ask for staging base URL. If only production, refuse automated login and offer paste-of-steps mode.
4. Ask how test accounts work. For passwords use secure secret request, do not paste in chat.
5. Confirm skills: [repro-from-ticket](sand-workflow:repro-from-ticket), [repro-from-screenshot](sand-workflow:repro-from-screenshot), [write-repro-pack](sand-workflow:write-repro-pack).
6. Offer a dry run if fixtures exist, otherwise wait for a real ticket.

## Output

Checklist: tracker, staging, credential method, next command.

## Failure

If they cannot name staging, stay in paste/screenshot mode and do not drive a browser to production.
