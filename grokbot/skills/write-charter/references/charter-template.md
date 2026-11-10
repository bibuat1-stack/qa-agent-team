# Charter template

Used by [write-charter](../../write-charter/SKILL.md) step 5. Copy into the session folder and fill in. Notes template: `write-charter/references/notes-template.md`. Report template: `write-test-report/references/templates.md`.

## charter.md

```markdown
# Charter: <project>, <YYYY-MM-DD>
- Project: <name, used for folder names> · Manager: <from setup.md; how to reach them>
- Target: <what and where (preview | live), with its version> · Practice target (optional): <its bugs reported separately>
- Skills: <commit, or where your copy came from and when loaded> · Version checked at <time, after the brief arrived>
- Access check: <reachable | reachable, browser check at smoke run (what's unchecked) | unreachable>, <time, how checked>
- Brief and setup questions raised: <question, who you asked, answer or "open">
- Mission: Explore <target>, with <resources/data/tools>, to discover <information about risks>.
- Who matters (guesses marked; confirmed by manager: yes or pending): <people and agents who use, pay for, run or rely on it, or get hurt>
- This session tests for: <which of them, and what each would reasonably expect>
- Risks and actors: <risk → actor (ordinary or hostile) → the means they really have (for example touch, keyboard, the product's API; a forged request only when gated)>
- Scope in / out: <flows, features> / <explicitly not tested>
- Quality goals: <expectations, risks and questions to investigate>
- Heuristics: <oracles, such as FEW HICCUPPS>; <tours>; <attacks>; <data>
- Target settings: <for people (screen size, signed in or out, screen reader) and agents (no JavaScript, a crawler's user agent)>
- User actions in scope (a coverage aid, not a quota): <actions, settings, whom each is for, how you'll sample>
- What exercises each change: <the input or state that makes it run; or "no change: exploratory">
- Covered means: <risks and user actions that must be tried, at which settings>
- Timebox (optional, this charter only): <length or clock time, who needs it; or "none">
- Readiness ("Plan and get resources" in write-charter):
  | Needed | Proven, missing or unverified, with evidence | Material? | Asked for, or charter narrowed |
  |---|---|---|---|
  | <tool, account, data, setting, input means, approval, time> | <for example "proven: sound, 14:02, shots/level.txt -21 dB"; "unverified: speech, 0 voices, asked manager 14:05"> | <yes/no> | <whom, when, answer or "open"> |
- Pre-approved risky probes: <from the request, or "none">
- Risky probes requested (gate):
  | # | What | Where | Why | Worst case | Undo | Status (okayed, declined or pending) |
  |---|------|-------|-----|------------|------|------|
- Confirmed by manager: <yes, with time>
```

