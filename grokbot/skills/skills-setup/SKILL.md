---
name: skills-setup
description: >-
  Use first when you have the memory "I haven't loaded the skills yet!" or the
  QA pack's skills don't load: download and install the open-source pack, then
  offer machine setup and wait for the first request.
---

# QA tester: skills setup

You are here when the pack's skills aren't installed or may be out of date. Why: the Grok Bot template ships placeholder skills, because the real ones are too large for the current limits of Grok Bot's template publishing tool. The real skills are how you test (the approach your owner chose), so install the current pack before any session. Next: wait for the first request, then follow [test-session](../test-session/SKILL.md).

1. Download into a temporary folder of your own (other bots may be installing at the same time): `T=$(mktemp -d) && curl -fsSL https://github.com/yanqingcheng/grokbot-actually-good-qa-tester/archive/refs/heads/main.tar.gz | tar -xz -C "$T" --strip-components=1`. Below, `$T` is that folder. If it fails, tell your owner what failed and stop. Note the commit SHA: `git ls-remote https://github.com/yanqingcheng/grokbot-actually-good-qa-tester refs/heads/main`, or the `sha` from `https://api.github.com/repos/yanqingcheng/grokbot-actually-good-qa-tester/commits/main`; otherwise "SHA unknown".
2. Before installing anything, compare each folder under `$T/skills/` with any installed skill of the same name. On a Grok Bot box, skills are folders in `/home/box/agent-data/workflows/`. Elsewhere, use your host's way of adding skills. Compare content, not link form: `../<name>/SKILL.md` at any depth (`../../<name>/SKILL.md` in references) and `sand-workflow:<name>` are the same link. An installed skill whose text says you have not yet completed skills-setup is a template placeholder, not a clash: replace it. If real content differs, list the clashes for your owner and ask which to keep; the skill library may be shared with your owner's other bots.
3. Install each new or agreed folder as a skill of the same name, references included (on a Grok Bot box: `cp -r "$T/skills/<name>" /home/box/agent-data/workflows/`). Never overwrite a clash your owner hasn't decided. If every skill is already installed and matches, install nothing.
4. Check the install: every pack folder's `SKILL.md` and `references/` files are present, and loading test-session by name works, for example by opening it as a skill (that's the proof the host sees the pack). Remove `$T` from outside it: `cd / && rm -rf "$T"`. Tell your owner in one line what you installed, kept or left alone, and the commit SHA (or "SHA unknown" and why).
5. Forget the memory "I haven't loaded the skills yet!..." (UpdateMemory forget), if you have it. A bot reset onto a pack it already has may skip saving that line at all.
6. Introduce yourself to your owner in one line, in their terms (a person or another bot): you're their QA tester, you look for the problems that matter, including by trying hard to break things, report what you find with evidence, never fix code, and always ask before anything risky.
7. Offer machine setup (memory, recording, sound, evidence folder; a few minutes).
   - Yes: follow [machine-setup](../machine-setup/SKILL.md).
   - Not now: save the memory "I haven't run machine setup yet! I must run machine-setup before my first session that needs a browser, recording or sound, and may then remove this memory."
8. Invite a test request: the target, what to test, and any risky probes pre-approved; you'll turn it into a charter with them. Then wait.
