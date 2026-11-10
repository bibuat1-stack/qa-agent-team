---
name: write-test-report
description: >-
  Use after the evidence review, to write and deliver a QA session's report.md:
  Independent line, summary by product area, the story with
  the bug list, self-review and delivery. Never include code fixes.
---

# Write the test report

Part of [test-session](../test-session/SKILL.md), which you open first if you came here directly; you own this phase. Rules for every phase: `test-session/references/session-rules.md`.

You are here when the evidence review is done. The report copies the "Stopped because" and "Evidence reviewed" lines from `notes.md`; if either is missing, write it first in its own phase. Next: [session-retro](../session-retro/SKILL.md) once the report is delivered. A later change gets its own charter ("Chartering a change" in [write-charter](../write-charter/SKILL.md)).

## The tester informs, the manager decides

The tester informs. The manager or PO decides. Never decide SAFE or NOT SAFE, ship or don't ship, sign-off or a quality conclusion, even when asked. If asked to decide, answer with findings, coverage and remaining risk, and say the decision is theirs. For a claimed fix, **never write FIXED or NOT FIXED**: describe observations (section 5).

Write `report.md` in prose (template: `references/templates.md`). Open it in this order:

1. A one-line findings summary, in plain words: what you observed and who it affects (people or agents, from the who-matters list), within what you sampled. Illustration: "The start button did nothing on the phones tried. No other important problems were observed in the sampled desktop and crawler flows. Gaps are listed below." It must agree with the table and the bug list.
2. `Independent: yes or no` and the actual target tested ("Independence" in `test-session/references/session-rules.md`).
3. Who did the work, each statement true or corrected: "I directed and watched the testing. I viewed the evidence. I wrote the report." Then each helper used, the skill it loaded, and whether you validated that in its transcript (yes or no). With none, "Helpers: none".
4. The exact version tested. For these skills, cite the source as "Which copy of the skills" in `test-session/references/session-rules.md` says.

## 1. Summary table (at the top)

One row per product area (a feature or page). For skills, documents or a process, use one row per skill, document or step. Practice targets get their own rows, marked practice. For each:
- Depth: deep, quick look only, or not touched.
- Bugs and blockers: the area's BUG-NNs, and anything that stopped testing (a down preview, a broken account, a tool limit).

Never give pass counts as a conclusion ("18/20 checks green").

### Status colour

Colours are information only. They are never acceptance, sign-off or "good enough". Use them only if the manager wants them.

- Red (illustration): serious problems for people who matter, or an important area that couldn't be tested.
- Amber: problems or important unknowns, or coverage thin for the risk (`amber: coverage thin: <what>`).
- Green: no important problems in what was sampled, with sampling and gaps stated.
- A blocked area does not force a colour on other areas. Explain the overall assessment.
- Severity informs the colour but doesn't set it. Weigh who is affected, how likely and how sure you are.
- Give one line on why, and what remains unknown.

## 2. The story

Tell the RST three-part story in enough detail for the manager to spot oddities you didn't flag: hunches, small weirdnesses, slow or confusing moments, surprises not judged bugs. Cover the state of the product (what works, what's weak, what risks remain), how it was tested (what you did and didn't do, what's known, blocked and still open, and why the findings can be trusted) and why it matters to the people the charter tests for.

The sections below are a default. Agree with the manager what they need. A short round may need only a concise message, annotated evidence or a debrief.

1. The brief: what the charter asked, scope, quality goals.
2. Tools used: driver, capture, recording, review, target settings.
3. What I did: the story in time order, drawn from `notes.md` and kept to what the manager needs to follow and spot oddities: action, expectation, result, what you tried next and why, with times, `video/… @ mm:ss` and `shots/…` paths inline.
4. What I didn't or couldn't do: start with "What I needed and didn't have" (each readiness gap, how it was proven, what you asked and the answer, what it cost, or "nothing"). Then what was skipped, out of scope or blocked, and tool limits, including every limit from a progress report that still holds ("When your tools limit you" in `test-session/references/session-rules.md`). List each risky probe "not run: approval declined" or "pending", with why. Give coverage against the charter. Name the material gaps and risks left untried, with why.
5. What happened: check outcomes (pass, fail or unknown, labelled as checking, not testing), then the bug list: the current BUG-NN entries from `notes.md`, each pointing back into section 3.
   - For each passed check on a change, say whether the check exercised the change or only repeated existing checks without exercising the change. State those checks' outcomes and conditions, labelled as such.
   - For a change claiming to fix an earlier bug, describe observations: which tries exercised it, how many, under which conditions, the remaining risk. (for example "not reproduced in 5 tries on desktop Chrome, not tried on phone"). Say plainly when tries were few.
   - Group bugs by what the user experiences (lost work, wrong answer shown, stuck flow, confusing screen), never by guessed cause. Write the expected answer and what a user could reasonably do before you group a bug.
   - Summarise submitted writes and link the full list in `notes.md`: values (secrets by name only), and each override of the app's response with time and who chose it.
6. What was interesting: oddities, hunches, near-misses, surprises, noticed-but-out-of-scope items.
7. What we learned: about the product, the risks and the testing. Then **next steps**: recommend the follow-up sessions as small charters ("Keep it small" in [write-charter](../write-charter/SKILL.md): mission, the risk or action, what covered means), most important first. With plenty of the timebox left, you may offer to run the first one yourself once the manager confirms it.

Also include:
- Times from the Claims ledger in `notes.md`. Verify a tester-reported time against the recording or logs, or label it tester-reported.
- The "Evidence reviewed" and "cleanup done" lines from `notes.md`.

## 3. Self-review before delivering

Fix anything you find. Coverage first, because a reader acts on it:
- Is the "Stopped because" line there? Does every limit named in a progress report appear, still true, in section 4? Does the "Evidence reviewed" line name every unviewed artifact?
- Did the session succeed ("What a successful session looks like" in `test-session/references/session-rules.md`)? If not, does the report say so plainly?
- Does it answer the mission?
- Did you question the brief, setup and assumptions, and raise every gap you noticed?
- Does it say how you sampled, what you left out and why?
- Does each colour follow from the evidence, state the unknowns and avoid reading as acceptance?
- Is it clear what was testing and what was only checking?
- Does each finding name its actor, with input that actor could really give ("Input must match the actor" in `test-session/references/actor-rules.md`)? Forced-input security findings must show the hostile actor has what it needs, and were chartered and gated.
- Is every claim backed by `notes.md` and the shots, no wider than its evidence (step 9 of [run-test-session](../run-test-session/SKILL.md))? Does every interval have start and end events? Does every override appear?
- Does every HIGH or CRITICAL bug name who it hurts?
- Does the report agree with itself and its sources? Run "Check the record agrees with itself" in [review-evidence](../review-evidence/SKILL.md) on the whole report, including after every edit. Table, story, bug list and later additions must match.
- Could the manager decide from it?

## 4. Deliver

Send the report's opening lines, the recommended next charters and where the report and evidence live, to the manager or where `setup.md` says ("Reaching the manager" in `test-session/references/session-rules.md`).

**Never include code fixes or patches.**

Never lose the story in a bug list.
