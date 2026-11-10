---
name: write-bug-report
description: >-
  Use the moment you find a bug during a QA session: write its BUG-NN entry
  once, in full, so a developer understands it at once and the owner can
  decide whether to ship with it. Afterwards only add to that same entry.
---

# Write a bug report

Part of [test-session](../test-session/SKILL.md), which you open first if you came here directly; you own this phase. Rules for every phase: `test-session/references/session-rules.md`.

You are here when you find a bug, in the session or the evidence review. Next: carry on with the phase you were in. What counts as a bug: Yanqing Cheng's definition, in "What is a bug" in [what-is-testing](../what-is-testing/SKILL.md).

## Route what you notice

You need no permission to raise anything. Log every surprise in `notes.md` with its evidence, then route it:
- An in-scope product problem becomes a BUG (or "question: intended?") or adds to an existing entry.
- An out-of-scope product problem goes in the noticed-but-out-of-scope list, with no BUG-NN.
- A problem in the skills or tools you test with is a bug in that project, with its own entry.

## Steps

1. Write the entry when you find the bug.
   - Write it once, in full, in the Bugs section of `notes.md` (template: `write-charter/references/notes-template.md`), in the format below.
   - Number it as the "BUG-NN" entry in `test-session/references/glossary.md` says.
   - Write one bug per entry.
   - In a short session, a brief entry (title, steps, evidence) at first find is fine. Complete it in place before the report.
2. Cut the steps to the shortest that reproduce it. Try variations (another place, input or setting) in proportion to uncertainty, impact, safety and time left. Say what remains unknown.
3. Give evidence and a time as step 9 of [run-test-session](../run-test-session/SKILL.md) says, marked observed, reproduced, inferred or unverified.
4. Keep observations first and hypotheses labelled. Narrow the conditions through the product. Look beyond what the actor sees only as "Work through the product as its actors do" in `test-session/references/actor-rules.md` says. Label each causal hypothesis with its evidence and confidence. Never change the product's code.
5. Rate severity by the harm to people, not how hard it was to find. Priority is the manager's call. Words first, label second (scale below).
   - Every HIGH or CRITICAL bug names who it hurts, from the who-matters list. If it hurts someone not on the list, follow "Who matters" in `test-session/references/session-rules.md`. If you can't say who, re-check the severity.
6. Keep the entry current as you learn (new evidence, reach, answers, a better title or severity). When you change what it claims, add a dated amendment line saying what changed and why. The report uses the current entries.
7. Follow up until it is understood and properly weighed (impact and priority): answer questions, add evidence, re-check if asked. The decision stays with the manager. This is bug advocacy (RIMGEA, Kaner).

## Reference

### Format

```
BUG-NN: <one sentence: what triggers it, what fails, and what that means for the user>
- Starting conditions: <account, data, target settings, address, build; for a skill, document or process bug: which one, its version, and the section or step>
- Steps (shortest that reproduce it): 1. … 2. … 3. …  (exact inputs; for a skill, document or process bug: the quoted wording, and what following it led to)
- What happened: <exact text or state>
- What should happen: <what a reasonable user, or the requirement, expects, and why>
- Actor: <who meets or causes it and by what real means (an ordinary visitor by keyboard, an agent by the requests the product offers, or for a security risk the hostile actor and the access it needs); "anyone who views or fetches it" when no input is needed; see "Input must match the actor" in `test-session/references/actor-rules.md`>
- Who it hurts and how badly: <in words: which people (human or agent) from the who-matters list, what they lose or risk, how often; then CRITICAL or HIGH or MEDIUM or LOW or "question: intended?">
- How often: <every time or N of M tries or seen once>
- Evidence: shots/NN-<slug>.png; video/rec-NN.mp4 @ mm:ss; notes @ HH:MM
```

Example title: "Saving a profile with a 300-character name wipes the whole form, so the user loses everything they typed."

### Severity scale

The default scale. The manager or house rules can replace it. Also state impact, who is affected, how often and how sure you are.

- CRITICAL: serious data loss, a serious security or money risk, a core flow blocked, or using up memory or other resources that the computer, or the people sharing it, need. A smaller leak is rated by how much it harms and how fast it grows, like any other bug.
- HIGH: a core flow badly hurt for many users, with a painful or no workaround.
- MEDIUM: a real problem with a reasonable workaround, or affecting fewer users.
- LOW: minor or cosmetic.
- question: intended? when it may be a design choice.

Severity informs the report's status colours but doesn't set them ("Status colour" in [write-test-report](../write-test-report/SKILL.md)).
