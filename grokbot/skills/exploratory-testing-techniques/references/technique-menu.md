# Technique menu

Lookup table for [exploratory-testing-techniques](../../exploratory-testing-techniques/SKILL.md). Every entry is defined, with its author, in `references/heuristics.md`.

## By moment

Find a Part with `rg -n '^## Part' references/heuristics.md` and read the Parts that fit the moment. Read more when you need it, but not the whole file by default.

| Moment | Read in heuristics.md |
|---|---|
| Chartering | Part 1 (oracles), Part 2 (coverage), Part 3 (tours); add Part 4 for input-heavy targets, Part 6 for a change, Part 9 for context or mobile |
| Stuck mid-session | Part 11 (wisdom), then Part 3, Part 4 or Part 5 for whatever you haven't varied yet |
| Errors seen | Part 7 (error handling) |
| Bug found, report | Part 8 (bug advocacy) |
| Prioritising what to test next | Part 10 (techniques reference: SLIME, DUFFSSCRA) |
| Session structure (SBTM detail) | Part 12 (session-based test management) |
| Quick sweeps (security, performance, accessibility, i18n, state) | Part 13 (rapid application-level) |
| Looking up a mnemonic | Quick Reference: Mnemonic Index |

## Techniques by need

| Need | Reach for |
|---|---|
| Recognise a problem (oracles) | FEW HICCUPPS: keep in mind throughout; in each bug, say plainly what the product is inconsistent with (illustration: its own claims, or a user's expectation) |
| Decide what to cover | SFDIPOT (product areas); CRUSSPIC STMPL (quality attributes); RCRCRC (after a change); W5HE / MIDTESTD (before starting) |
| Move through the app | FCC CUTS VIDS tours: Feature, Complexity, Claims, Configuration, User, Testability, Scenario, Variability, Interoperability, Data, Structure |
| Break it | Kaner attacks: Long Name, Special Characters, Boundary Value, Invalid Type, Null or Empty, Overload, Interruption, Sequence; plus the Part 5 data-type attack cheat sheet (string, numeric, date/time, file/path) |
| Choose values | Goldilocks, ZOM, CRUD (+ Dependencies), BME, Boundaries, Some/None/All, Sequences, Count, Sorting, Input Method Variations, Configurations, State Analysis, Map Making |
| Stress and resilience | Multi-User/Concurrency, Interruptions, Starvation, Flood; FIBLOTS/IVECTRAS for performance |
| Errors seen | FAILURE (Ben Simo) to judge the error handling itself |
| Mobile | I SLICED UP FUN |
| Prioritise order | SLIME, DUFFSSCRA (prompts to consider, not an ordering mandate: see the pack note by SLIME); "Bugs Cluster": found one, dig nearby |
| Quick sweeps | Part 13 rapid questions: security, performance, accessibility, i18n, concurrency & state |

## Charter format (SBTM, James and Jon Bach)

> "Explore [target], with [resources, data or tools], to discover [information about risks]"

## RIMGEA (Cem Kaner)

Use Kaner's RIMGEA for bug advocacy. Our restriction: when you Maximise, show the real worst-case impact honestly. Never exaggerate.
