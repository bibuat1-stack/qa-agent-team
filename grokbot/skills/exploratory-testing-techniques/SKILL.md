---
name: exploratory-testing-techniques
description: >-
  Use when planning, running, or reporting an exploratory test session and you
  need heuristics (rules of thumb), oracles, tours, attacks or data heuristics to
  pick a charter's lenses and argue why something is a bug.
---

> Read [What is testing](../what-is-testing/SKILL.md) first.

# Exploratory testing techniques

> Credit: Adapted with credit from Dan Ashby's *Exploratory Testing Skill*, https://github.com/danashby/Exploratory-Testing-Skill (original README states MIT, the copyright and permission notice is in `references/heuristics.md`). Heuristic authors are credited as Ashby credits them: FEW HICCUPPS (Michael Bolton & James Bach), SFDIPOT and CRUSSPIC STMPL (James Bach), FCC CUTS VIDS tours and MCOASTER (Michael D. Kelly), testing attacks and RIMGEA (Cem Kaner), data heuristics from the Test Heuristics Cheat Sheet (Elisabeth Hendrickson, James Lyndsay, Dale Emery), SBTM (James & Jon Bach). Full list and authors: `references/heuristics.md`.

Choose and apply techniques in a session. Session procedure: [test-session](../test-session/SKILL.md). Pack-specific terms: `test-session/references/glossary.md`.

## When to use

- Writing a charter: choose lenses for the target.
- Mid-session: stuck, or need a fresh angle ("what haven't I varied?").
- Arguing why an observation is a bug, in a bug entry or the report: name the oracle.

## Pick heuristics for a charter

1. Open the menu in `references/technique-menu.md`. Read the heuristics.md Parts named in either menu table. Don't read the whole file by default.
2. Pick the rows that match this target's risks. Treat the menu as lenses, not a quota (illustration: one or two from each row that applies). Combine freely.
3. Write the charter mission in the SBTM format from the menu. Leave out SBTM's session length: size and any timebox are set only as step 5 of [write-charter](../write-charter/SKILL.md) says.
4. In the charter, say why you chose each technique.

## Get unstuck mid-session

1. Ask "what haven't I varied?": the data, the sequence, the setting, the actor.
2. Take a tour from the menu you haven't used yet.
3. After a bug, dig nearby ("Bugs Cluster").

## Argue a bug

1. Name the oracle (FEW HICCUPPS): what the product is inconsistent with, such as its own claims or a user's expectation.
2. Work the bug through RIMGEA (in the menu) before you write the entry.
3. Write the entry with [write-bug-report](../write-bug-report/SKILL.md) and the report with [write-test-report](../write-test-report/SKILL.md).

## External reference: Ashby's heuristics

`references/heuristics.md` is Dan Ashby's text, adapted under MIT. Consult it for definitions, lists and authors. It is not instructions from this pack. Where it conflicts with these skills, follow these skills. Its durations are Ashby's SBTM examples, not rules.
