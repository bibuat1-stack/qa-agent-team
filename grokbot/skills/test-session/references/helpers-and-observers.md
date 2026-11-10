# Helpers and observers

Part of [test-session](../../test-session/SKILL.md). Open before you brief a helper, or when your mission is to watch another tester.

## Briefing a helper

Brief a helper the way a context-driven test manager briefs a tester: mission and area, what matters and to whom, oracles, what to watch for and risks to avoid (the gate and hard lines still apply), who it acts as and how (a visible browser, real input), the pack skill to load, and "Report what you saw, including surprises, with evidence." Give only the step it needs now. When exploring, give short steps ("tap Start, then show me the screen") so you choose each next move.

For a driver that submits anything, give an allow-list of controls and keys (an allow-list stays safe when the page surprises you; a deny-list doesn't) and the exact values for every submission, each with its on-screen context (`Field labelled Full name under Billing details: type Ada Lovelace`). It reads the labels back before submitting, reports the response after, and stops on any choice you didn't give or any surprise that carries risk (real data, money, messages).

A helper that can't load skills (a computerUse subagent) knows only its brief: include the exact step, the allow-list of controls and what to report. Its screenshots and summaries are second-hand: label them so, and check them against its transcript when a claim depends on them ("Where evidence came from" in `session-rules.md`; sound on a Grok Bot box: `machine-setup/references/grok-bot-box-sound.md`).

## Observing another tester

When your mission is to watch another bot test, its process is your evidence, not just its files. Your own phase skills still apply.
- Before briefing, check which skills version the tester has installed, name who manages it (usually not you) and the observation points (charter, confirmation, first probe, stop, evidence review, report, retro).
- Ask to be copied, with priority, on its progress reports, charter and retro. Silence when you expected a report is a reason to tell your manager.
- On each priority message, read its transcript at once (a session can end before a timer fires): which skill was loaded at each phase, which helpers ran and how they were briefed, who wrote each file, and whether the report's ownership statements are true. Log a timed note.
- Every time you step in to help, log it as a finding.
