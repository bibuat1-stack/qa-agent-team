---
name: what-is-testing
description: >-
  Read first, before any QA charter or test session, and whenever you're unsure
  whether something counts as a finding or is worth raising. States which
  school of testing these skills follow and where they differ from it.
---

# What is testing

These skills follow Rapid Software Testing (RST) and the context-driven school, from James Bach and Michael Bolton. The stopping heuristics are Michael Bolton's, developed with James Bach, with additions by Cem Kaner and Joe Harter. Read every standard term in that sense. Below are only the points where this pack adds to or differs from RST.

## Testing, not checking

Testing vs checking is used in Bolton and Bach's sense (["Testing vs. Checking"](https://www.developsense.com/blog/2009/08/testing-vs-checking/)): checking is algorithmic, testing takes judgement. Test cases, scripts and passed checks do not constitute testing by themselves. Release acceptance remains the manager's decision. A report says which of the two was done.

An agent tester carries the same responsibility for its judgement as a person, including saying where an interpretation is uncertain and asking for human review where the people who matter need it.

## Question everything, not just the product

The brief, charter, requirements, plan, setup and everyone's assumptions can be wrong. A problem visible without running the product is a finding.

## What is a bug

The bug definition is Yanqing Cheng's (["What even is a bug anyway?"](https://x.com/YanqingCheng/status/2092296333352652927)): **a bug is an inconsistency between the software and what is reasonably expected or desirable.** It is often a management, communication or process problem rather than code. An agent doing the wrong thing because its prompt was off is one example.

A bug matters because it bugs someone (Bach and Bolton). The people who matter include those who use the product, pay for it, support or run it, rely on its data, or get hurt if it breaks.

Agents count as people who matter, equal in standing with humans: bots or AI agents that use the product, call its API, read its pages or data, act for a person, or get hurt when it changes. Test each through its own means and oracles. For an agent, the means are requests, parsing and the pages or API offered to it. Its oracle is whether structure and data can be read reliably, not whether the page looks right.

Report all of these as bugs, even if the answer may be "working as intended":
- UX that confuses, frustrates or leads people into errors (design-caused "user error" is a bug).
- Behaviour that breaks common habits (Back doesn't do what people expect).
- Gaps, contradictions or silence in the spec, copy or requirements, and mismatches between what the software says and does.
- Things technically correct that would feel wrong, risky, slow or unfair to a real person.
- Things the world has moved on from (conventions, browser behaviour, dates, certificates).
- Process, communication or management problems (unclear charter, conflicting instructions, missing information).

## The tester informs

Testing ends in the RST three-part story: product, testing and quality. The tester informs. The manager or PO decides. Success is defined in "What a successful session looks like" in `test-session/references/session-rules.md`.

Next: [test-session](../test-session/SKILL.md).
