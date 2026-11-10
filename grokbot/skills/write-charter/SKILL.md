---
name: write-charter
description: >-
  Use when a QA test request arrives and before any testing starts: set up a new project, question
  the brief, plan and get resources, write charter.md (SBTM charter) and get
  the manager's confirmation.
---

# Write the charter

Part of [test-session](../test-session/SKILL.md), which you open first if you came here directly; you own this phase. Rules for every phase: `test-session/references/session-rules.md`.

You are here when a request has arrived and testing hasn't started. Next: [run-test-session](../run-test-session/SKILL.md) once the manager confirms.

Before confirmation, do only what the charter needs: a read-only access check, readiness checks and reading. Prove early any tool the mission's core depends on (for example, sound for a music app); probes start after confirmation.

## Project setup

No `setup.md` for this project yet? Follow `references/project-setup.md` first.

## Chartering a change

A fix or other change under test: also follow `references/chartering-a-change.md`.

## Steps

### Understand the request

1. Question the brief, even when it's pre-confirmed or someone else wrote the charter, and send your questions to the manager. A visible problem (no target, unreachable environment, contradictions, no users or quality bar) is a finding: raise it now. Questions about these skills go to the manager, not the PO.
2. Re-check `setup.md` and update it if anything changed. Check which copy of the skills is installed after the brief arrived, and record "Version checked at <time>" in the charter ("Which copy of the skills" in `test-session/references/session-rules.md`).
3. Who matters: check the list against the brief, add anyone new (guesses marked), and write whom this session tests for and what each would reasonably expect. Judge bugs against those expectations, not only the spec.
4. Ask about scope and quality goals when unclear (what's in and out, which bar matters now). Stay in scope by default, so the session answers its mission; ask before expanding, and always report what you notice.

### Draft the charter

5. Draft `charter.md` from `references/charter-template.md`:
   - mission in SBTM form (`exploratory-testing-techniques/references/technique-menu.md`), scope and quality goals.
   - heuristics, with why; the main risks, each with its actor ("Input must match the actor" in `test-session/references/actor-rules.md`); oracles (code or diffs only if they are one).
   - user actions in scope at which settings, judged by what users do. Phones and screen readers default to emulated, labelled so in findings.
   - **Covered means:** an explicit list of what must be tried for the mission to count as covered. The stop notes walk it, so a clear one makes stopping honest.
   - timebox (optional), agreed in this charter only. One from an earlier round was set for a different mission; without one, stopping heuristics decide.
   - **Keep it small.** A small session done well tells the people who decide more than a big one done thinly. Aim for one risk or user action, about 15–25 minutes, one browser setup; split bigger missions and propose the order.
6. For each change under test, write what actually exercises it (the input or state that runs the new path), or "no change: exploratory".
7. Mark each probe safe or risky; risky ones go in the gate list ("Risky-probe gate" in `test-session/references/session-rules.md`).

### Plan and get resources

8. Fill in the Readiness table, in proportion (in a short round, the smoke run can prove the rest). Access check: "Access check" in `test-session/references/targets-and-evidence.md`.
   1. From your saved machine state, list what the mission needs: tools, accounts and data, settings, the actor's input means, approvals, time.
   2. Before any trial starts a browser, recorder or server, apply `test-session/references/resource-cleanup.md`. Grok Bot box recipes: `machine-setup/references/grok-bot-box.md` (and `-sound.md`).
   3. Try each item safely and mark it proven (with kept proof), missing (what you tried or asked) or unverified.
   4. Accept only fallbacks just as good for the mission; a weaker one is a scope cut.
   5. Anything material missing? Ask for it or an agreed narrower charter, recorded as a "Charter change" line ("When your tools limit you" in `test-session/references/session-rules.md`). Never substitute input the actor couldn't give, or start a session that can't meet its mission.
   6. A pending approval blocks only what it covers. Cost to the owner (paid APIs) must be agreed here.

### Write, review and confirm

9. Create the session folder `<YYYY-MM-DD>-<your name>` with plain `mkdir`, never `-p`, so you never write into another tester's folder ("Evidence folder" in `test-session/references/targets-and-evidence.md`), and write `charter.md`.
10. Self-review in `charter.md`: Could it succeed? Is it small, with Covered means? Version checked at, who matters, access check, what exercises each change, readiness gaps asked, risks with actors, every risky probe gated? Would a reasonable manager agree?
11. **Get the manager's confirmation. Always.**
    - Clear request: one line ("Charter at <path>: <mission>. Okay to start?").
    - Something to decide (ambiguity, guessed scope, gaps, gate requests, unconfirmed who-matters): about five lines plus every gate request in full.
    - Pre-confirmed and unchanged: still do steps 1–4, send a one-line "starting" message with any questions, and start. Changed terms need a new yes.
    - Asked for a ship or SAFE call? Say the report gives findings and risk for their decision.
    - Otherwise wait. Silence is not a yes. Each risky probe waits for its own okay.

A checklist with no goal, people or quality bar is not a charter: ask for those first, because without them you can't judge what matters.
