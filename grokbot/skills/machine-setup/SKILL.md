---
name: machine-setup
description: >-
  Use when you have the memory "I haven't run machine setup yet!", or before a
  session needs a browser, recording or sound on a computer you haven't set up:
  memory floor, recording, sound, evidence folder, and proving the basic tools.
---

# QA tester: machine setup

You are here when this computer isn't set up for testing. Next: back to where you came from.

## Why

Your reports are only as good as your evidence: an honest capture of what a real person sees and hears, at a time you can trust, without harming a computer others may share.

## What you need to be able to do

1. Leave the computer healthy: know its memory floor (free memory needed before a browser, server or recording), take any lease, clean up only what you started.
2. Drive a real browser at desktop size and at phone size with touch.
3. Record the screen with a trustworthy clock in the picture.
4. When the product makes sound, record sound you can attribute to your own browser.
5. Review your own recordings before relying on them.
6. Know the evidence folder root ("Evidence folder" in `test-session/references/targets-and-evidence.md`).

## Where the specifics come from

1. Read `test-session/references/resource-cleanup.md`, `test-session/references/targets-and-evidence.md` and any house rules first.
2. This computer's specifics (memory floor, lease tool, sound server, recorder, evidence root) come from the house rules and machine notes (default `<evidence folder>/machine-notes.md`), then your saved machine state; check each still holds. Where they say nothing, probe the computer and propose values to the owner.
3. Machine choices belong to the computer's owner, not the requester. Ask only for what's new, missing or no longer true.
4. Memory floor with no rule: measure one harmless browser page and a short recording, stop them, and propose a margin above that.

## When another bot already set this computer up

If its machine notes are recent and verified (someone checked the evidence, not just the summary), reuse proofs of what can't differ between bots (browser sizes, recording method, sound path). Always re-check what can change: free memory, the lease, a tools smoke run, the sound server. Re-prove everything after a restart or if the notes are old or unverified.

## Prove your tools

Prove each ability on something harmless you control (a blank page, a small local page that plays a sound), the way a session will use it: sound proof is sound from the browser you test with, captured as a session would, not a tone played straight to the speaker. Never use a real product nobody asked you to test. Work in `<evidence folder>/machine-setup/<YYYY-MM-DD>-<your name>/` (plain `mkdir`) with a `notes.md`, keep the proofs there, and follow the session rules for memory, lease and cleanup.

- A failed proof or missing tool is a recorded gap, not something to pretend away: note what you tried and tell the owner.
- Review a recording yourself: look at frames from its start, middle and end, and check the burned-in clock against your log times.

Grok Bot box recipes: `references/grok-bot-box.md` (Chrome, recording with a clock, leases) and `references/grok-bot-box-sound.md` (sound, speech voices). On other hosts, skip them.

## Save

1. Save the floor (with its reason), recording method and evidence root to memory and to the machine notes (where house rules say, else `<evidence folder>/machine-setup/<YYYY-MM-DD>-<your name>/notes.md`, linked from `<evidence folder>/machine-notes.md`).
2. Record what's proven (with the proof folder) and what's missing, and tell the owner in one line. A missing capability the work needs is a finding: ask for it.
3. Replace the memory "I haven't run machine setup yet!": forget it if nothing is missing, else "Machine setup ran <date>; missing: <gaps>; proof: <folder>. Re-check these before a session that needs them."
