# Report template

Used by [write-test-report](../../write-test-report/SKILL.md). Adapted with credit from Dan Ashby (https://github.com/danashby/Exploratory-Testing-Skill); RIMGEA by Cem Kaner.

## report.md

Prose, except the header block and bug list. Drop or shorten what the manager doesn't need.

```markdown
# QA report: <project>, <YYYY-MM-DD>
Findings summary: <one line, plain words: what was observed and who it affects, within what was sampled>
Evidence: <evidence folder>/<project>/<YYYY-MM-DD>-<your name>/
Independent: <yes or no> · Target actually tested: <live, preview address, or local with commit> (unreachable: name the blocker and affected scope)
I directed and watched the testing. I viewed the evidence. I wrote the report. (correct any that isn't true)
Helpers: <none, or each helper: its job, skill loaded, validated in its transcript yes/no>
Evidence reviewed: <the "Evidence reviewed" line from notes.md; if the review wasn't done or some evidence couldn't be reviewed, say so, and which areas it affects>

## Summary

| Product area | Status colour (information only, not acceptance) | How deeply tested (deep, quick look only, or not touched) | Bugs and blockers (incl. environment) |
|---|---|---|---|
| <feature or page> | <colour: one line why, for its users> | <depth> | BUG-01, BUG-03; <blocker> |

(Colour meanings: "Status colour" in write-test-report. Never a pass rate.)

## 1. The brief
What the charter asked for, what was in and out of scope, and the quality goals.

## 2. Tools used
Driver, capture, recording, review, target settings.

## 3. What I did
The story in time order from notes.md: what I did, expected and saw (exact text, timings, errors), what I tried next and why. Inline evidence, for example "At 09:06 (video/rec-01.mp4 @ 04:20) …". Mark BUG-NN where each appears.

## 4. What I didn't do or couldn't do
Readiness gaps: <what was missing, how proven, what I asked and the answer, what it cost; or "nothing">.
Skipped, out of scope, blocked and tool limits, each with why and how it was proven. Risky probes: "<probe>: not run: approval declined | pending". Coverage against Covered means: what was and wasn't covered.

## 5. What happened
Results per check (PASS, FAIL or UNKNOWN), then the bug list:

BUG-NN entries in the write-bug-report format.

Recommendations for the owner to decide, in their priority scheme or your recommended order, with why; any causal hypothesis labelled as one.

## 6. What was interesting
Oddities, hunches, near-misses and noticed-but-out-of-scope items.

## 7. What we learned
About the product, the risks, and the testing itself. Suggested next charters.

Stopped because: <copied from notes.md; format in test-session references/stopping-heuristics.md, "Recording a stop">
Cleanup: <the "cleanup done" line from notes.md>

```
