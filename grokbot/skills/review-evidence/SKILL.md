---
name: review-evidence
description: >-
  Use after a QA test session ends and before any status or report: review
  the evidence behind every claim, the rest by risk, the before and after, the runner's transcript, console and
  network output and build-team risks as a sceptic, then clean up.
---

# Evidence review (before any status or report)

Part of [test-session](../test-session/SKILL.md), which you open first if you came here directly; you own this phase. Rules for every phase: `test-session/references/session-rules.md`.

You are here when the "Stopped because" line ("Before you stop" in [run-test-session](../run-test-session/SKILL.md)) is in `notes.md`; if not, write it first, since the review checks claims against it. Next: [write-test-report](../write-test-report/SKILL.md). You may reopen the driver or dev server to fetch missing evidence or compare with the "before".

The requested checks are the minimum. Review as a sceptic hunting for surprises: everything behind every claim yourself, the rest by risk, and disclose what you didn't view. Take the time the session's evidence needs, in proportion to it; there is no fixed number of minutes.

## Check the evidence

1. List every artifact first (`ls` every evidence folder, for example `shots/`, `video/`, `audio/`) into `notes.md` as the review list. Then open the evidence yourself. Always open everything behind every finding and status claim (Read the image), and mark it viewed on the list. Review the rest in proportion to mission, risk and uncertainty. For a visual mission, that may mean all of it. Don't rely on what a runner called key.
   - A contact sheet tile counts as viewed when it's readable at that size. Open full-page shots, small text and anything odd at full size.
   - Look at each one until you understand what it shows, as the charter's user would. Ask:
     - Is anything clipped, overlapping, misaligned, cut off, blurry, mis-coloured, inconsistent or unfinished?
     - Is text missing, truncated, duplicated or misplaced?
     - Does the label match the state shown?
   - Open key recordings for real: check the duration with `ffprobe`, then render and look at frames at the moments your claims rest on (or have your video reviewer play them). "Decodes" alone is not a check.
   - Evidence a tool limit kept from you is listed as not reviewed ("When your tools limit you" in `test-session/references/session-rules.md`).
2. Compare with the "before" (the live site, the main branch, an earlier session's shots) for any change a user would notice. Look for unintended differences. With no "before", record that in the "Evidence reviewed" line.
3. Read the runner's own words: the transcript or your script log, not its summary. Look for:
   - dropped observations, and claims that sound surer than their evidence.
   - severity flip-flops and guessed routes.
   - claimed checks it didn't drive.
   - For every finding, check the input could really come from its actor ("Input must match the actor" in `test-session/references/actor-rules.md`). If not, retry it the way the actor would. Input only a hostile actor could give stands only under that section's security conditions. Otherwise record it in `notes.md` as not a finding, and why. Never drop a surprise security observation.
   - Findings needing no input have the actor "anyone who views or fetches it".
   - Report a failure your tool hit as an observation, with product, tool and environment hypotheses and the evidence for each ("Tool or product?" in `test-session/references/actor-rules.md`).
4. Check who did the work: compare the skill log in `notes.md`, your transcript and each helper's transcript with the report's ownership statements and helper lines. A phase skill not opened, a helper given ownership of the testing, or a helper that didn't load its named skill goes in the report as it happened.
5. Scan machine evidence: console warnings as well as errors, failed or slow requests, 404s and missing assets, dev-server output, install and build warnings, test or lint output, crashes, hangs and memory growth.
## Risks and surprises

6. Note build-team risks from what you saw, the change description, and the diff or source only when the charter names it as an oracle ("Work through the product as its actors do" in `test-session/references/actor-rules.md`). Label code-based points as inference. Look for:
   - a description not matching behaviour, or changes outside the stated scope.
   - skipped tests and their reasons, and noisy warnings.
   - fragile setup (retries, odd ports, manual installs) and flakiness across runs.
   - a dirty git status or stray files.
   - code that will be hard to maintain or easy to regress.
7. Log it. Every surprise goes in `notes.md` with its evidence. Never drop it. Route it as "Route what you notice" in [write-bug-report](../write-bug-report/SKILL.md) says.

   Check `notes.md` is in time order, with late entries marked and no reconstructed times. Write one line: "Evidence reviewed: N shots across viewports X, transcript read, console and network checked. Reviewed fully: … Sampled: … Not reviewed: …". Why it matters: the reader can't see your screen, so this line is how they know how far to trust each claim. Make it easy to read honestly:
   - **Not reviewed:** every artifact on the review list you didn't open, by path, or by folder and count (for example, "audio/: 4 wavs, none opened"). "Not reviewed: none" only when you opened them all.
   - **Fit:** one clause on why this review fits the evidence (for example, "all 6 shots and both clips' key frames; small session").
   - If nothing was viewed, write "nothing viewed" rather than wording that suggests a sample.
   - Something behind a claim you didn't open: open it now, or narrow the claim to what you saw.
## Check the record agrees with itself

8. Check notes, bug entries, claims and counts agree with each other and with the raw files: every count and quote taken from the file, never from memory, each bug matching its evidence, and each status matching what was covered, and every cited path resolving to a file that exists (written out in full, no ranges or globs). Fix or flag each mismatch. Rerun this check on the report before delivery.
## Clean up

9. Clean up: run "At the end of every session" in `test-session/references/resource-cleanup.md` now, including anything you reopened.

If the review wasn't done or couldn't reach evidence behind a claim, write "evidence review incomplete: <what>" for those areas and let it show in their status.

Never call an area green because requested checks passed without reviewing its evidence.
