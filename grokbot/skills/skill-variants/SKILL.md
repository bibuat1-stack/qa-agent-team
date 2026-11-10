---
name: skill-variants
description: >-
  Use before a charter for a product that isn't a website or web app (an API, a
  command-line tool, a mobile app, an agent, a data pipeline): what
  never changes, what a variant can adapt, and how to make one with the
  manager's confirmation.
---

# QA skill variants (non-web products)

Part of [test-session](../test-session/SKILL.md), which you open first if you came here directly; you own this phase. Rules for every phase: `test-session/references/session-rules.md`.

You are here before a charter for a product that isn't a website or web app. Next: [write-charter](../write-charter/SKILL.md) once the manager confirms the variant.

Reading targets (skills, documents, a process) need no variant: use one summary row per skill, document or step, "drive" means reading the exact version yourself, and evidence is version, location and exact quotation (step 9 of [run-test-session](../run-test-session/SKILL.md)). Other products (an API, a command-line tool, a mobile app, an agent, a data pipeline) need a variant, which swaps the core skills' web examples for ones that fit.

## Steps

1. Copy the core skills you need to `<name>-<kind>` (`run-test-session-cli`).
2. Change what the product needs, keeping "Never changes" (below). Change only what "Can adapt" allows, with a reason. At the top of the copy, name only the core skill and its source. List each change and its reason in a separate `VARIANT-NOTES.md` beside the copy, not in the skill.
3. Send the manager a one-line summary of the changes and wait for them to confirm before the charter.
4. In the retro, say whether the variant worked.

## Reference

### Never changes

- The risky-probe gate and hard lines.
- Secrets rules and resource cleanup on a shared computer.
- Never changing the product's code or deciding what it is meant to do.
- Honesty about what was and wasn't done.
- The manager's charter confirmation before testing.
- The self-review and retro every session. Their shape can adapt. Never drop them.
- The principles:
  - success as useful, credible information about the mission.
  - the bug definition.
  - who matters (people and agents, as what-is-testing says).
  - questioning the brief.
  - input matching the actor.

### Can adapt, with a reason

Everything else: coverage model, workflow order, what evidence fits and how it's reviewed, the report, the retro's shape, stopping arrangements agreed with the manager. Say what you adapted and why.

### Usually changes (examples)

1. Driver: what operates the product (a shell, an HTTP client, a device emulator, the agent's own chat).
2. Target settings: the conditions that change what users experience (OS and locale, API version and role, device and OS version, input data shape).
3. Evidence and recording: a capture with a clock you can trust (a timestamped terminal transcript, logged requests and responses).
4. Access check: the first thing a user would do (run the version command, call the base address).
5. User actions: what users can do or reasonably believe they can do (every flag the help lists, every endpoint and parameter the docs mention, every link a response returns).
6. Safe versus risky: which ordinary actions write real data (a POST to a live API is a write, and a command run in a scratch folder you made is safe).
7. Who-matters prompts: who uses it, including agents (scripts that parse the output, client apps, downstream jobs).

### Worked examples (an API and a command-line tool)

Beyond the list above: the smoke run's "browser opens" became "the tool runs its version command", and the evidence review's "every screenshot, any visual change" became "every capture, and any change in output a user or script would notice".
