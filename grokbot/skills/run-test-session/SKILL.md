---
name: run-test-session
description: >-
  Use once the manager has confirmed the QA charter, while you are testing:
  session notes, a recording with a trustworthy clock, narrow probes,
  evidence and timing rules, reasoned stopping, and wind-down.
---

# Run the test session

Part of [test-session](../test-session/SKILL.md), which you open first if you came here directly; you own this phase. Rules for every phase: `test-session/references/session-rules.md`.

You are here once the charter is confirmed (risky probes only once okayed). Next: at the first bug, [write-bug-report](../write-bug-report/SKILL.md); when you think you're done, "Before you stop" below, then [review-evidence](../review-evidence/SKILL.md). Less-used detail (timing, automated checks, claims ledger, video review): `references/evidence-detail.md`.

## Progress reports

**Send the manager a short progress report at each moment you can recognise: after the smoke run, when you find a bug, when the plan or scope changes or you're blocked, and at the stop.** Three lines (did, saw, next), so the manager can redirect early; copy any observer the charter names. A limit you name stays in every later report until resolved. Carry on with safe work unless told otherwise.

## Start

1. Send the manager a one-line start notice with the charter path.
2. Keep `notes.md` (template: `write-charter/references/notes-template.md`). Write each line after it happens, never ahead, stamped from a real `date +%T` call. Log every action, expectation, observation and hunch, unfiltered. Never reconstruct a time: a missed line gets the time you write it, marked `(late entry)`.
3. Record with a clock you can trust (for a website, a screen recording with a clock burned in; Grok Bot box: `machine-setup/references/grok-bot-box.md`, and `-sound.md` for sound). Prefer several short clips; every clip needs a clock in the picture or its start time in `notes.md`. Read reported times off that clock. If recording fails, pause the work that depends on it and tell the manager; switch only to a fallback agreed at readiness.
4. **Smoke run:** inside your lease ("Leases and locks" in `test-session/references/resource-cleanup.md`), one short pass proving the browser reaches the right version of the target and your capture plays back with its clock (`ffprobe`, and look at one frame). Note what's still unchecked, then send the first progress report.

## Explore

Explore realistically ("You own the testing" in [test-session](../test-session/SKILL.md)).

5. Choose where to start and note why; an open look over the affected surfaces often shows problems early.
6. Before each probe, check its input matches the actor ("Input must match the actor" in `test-session/references/actor-rules.md`). Keep the coverage list of user actions in `notes.md`, including what users can reasonably believe they can do: something that invites an action and then does nothing is a finding. Where a journey matters, take it to its end as that user would. A shortcut (loading a page by URL) is fine for reaching what you test, but then you haven't tested the way there: don't claim it.
7. Drive with narrow probes, one focused goal each ("enter a 10,000-character name in signup, submit, report the exact result and any console errors"). Never claim a test you didn't drive (or, for a reading target, read). Never force a failed action: record it and work out "Tool or product?" in `test-session/references/actor-rules.md`. Briefing a driver: `test-session/references/helpers-and-observers.md`.
8. Work the charter's heuristics by risk, and follow hunches (bugs cluster). Move between breadth and depth (repeat anything flaky, reload or Back mid-action, extremes), noting each switch and why. Attack as hard as the risks call for on a safe target. Stuck? Open [exploratory-testing-techniques](../exploratory-testing-techniques/SKILL.md).

## Evidence

9. As you go:
   - **Every finding needs evidence that fits its claim and target, and a time.** Interactive target: a capture (screenshot, or console or network log for what a shot can't show). Reading target: version, location, exact quotation, when read. A screenshot can't show timing or cause.
   - Save shots as `shots/NN-<slug>.png`, log each path, and check each matches its label before citing it.
   - Mark each finding observed, reproduced (with conditions), inferred or unverified, and say what evidence is missing; with none, "seen once, no evidence". Never drop it.
   - Define every interval by its start and end events as clock times; never a bare duration.
   - Know what your tools can actually hit (a timing window, a blocked request), and say which tries could have shown the problem. An automated result your tool couldn't get is unknown, not fail.
   - Log every write (save, submit, override): time, value (secrets by name), the app's response, and who chose it.
   - Second-hand evidence (a helper's estimate or shot) is labelled so ("Where evidence came from" in `test-session/references/session-rules.md`).

## Before you stop

Stopping early is fine, and so is not finishing. What matters is that the people who decide can see what was covered, what wasn't and what risk is left; the one hard line is never to make coverage look bigger than it was. Write these in `notes.md` before you open review-evidence:

10. Stop notes:
    - a. **Walk the charter.** For each risk and each "Covered means" item (none: each user action in scope), one line: covered (evidence path), or not covered and why. A tool limit says what it kept you from seeing.
    - b. **Open `test-session/references/stopping-heuristics.md`** (each time), log it in the skill log, pick the heuristic that fits and answer the question in its Meaning column in a line.
    - c. **Write the "Stopped because" line** in that file's format ("Recording a stop").
    - d. **Send the stop progress report**, quoting it, with the next session(s) you'd recommend.
    - Time left? After delivering the report you may draft a next small charter and confirm it before running it.

## Wind down

11. Stop each recording by its own pid (`kill -INT`), wait for it to exit, and decode it fully. Stop helpers you no longer need; you may keep what the evidence review needs. Full cleanup runs at the end of the evidence review. Then open [review-evidence](../review-evidence/SKILL.md).
