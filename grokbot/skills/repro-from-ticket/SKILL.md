---
name: repro-from-ticket
description: >-
  Turns a bug ticket (GitHub, Linear, or paste) into a reproduction attempt plan
  using staging or test accounts only.
---
# Repro from ticket

## When to use

The input is an issue URL or pasted ticket. Goal: enough to attempt a repro, then hand off to [write-repro-pack](sand-workflow:write-repro-pack).

## Approval bar

- Never production customer data, dumps, or live user accounts.
- Never create accounts on production.
- Never post comments to trackers without an explicit yes.
- Test credentials only via secure handoff, never in chat.

## Sequence

1. Extract summary, expected, actual, env, steps, attachments. Do not invent missing fields.
2. Choose surface. Prefer staging URLs the user named.
3. Write an attempt plan: account type, fixtures, first action, stop condition.
4. Run on staging only. Stop on CAPTCHA or login and ask for takeover.
5. Capture notes and screenshot paths under `/workspace` for write-repro-pack.

## Output

Markdown with Ticket, Environment allowed, Known, Missing, Attempt plan, Result (Reproduced / cannot reproduce / blocked), Evidence.

## Failure

No steps and no screenshot: ask before spending computer time. Only production named: refuse and ask for staging.
