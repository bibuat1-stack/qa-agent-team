# Session rules (every phase)

Part of [test-session](../../test-session/SKILL.md). Read before your first charter, and again before any risky probe. Rules for one moment live beside this file: `actor-rules.md` (risks, failed actions, findings), `targets-and-evidence.md` (setup and access check), `resource-cleanup.md` (before you start, leases, end of session), `helpers-and-observers.md`.

## The tester runs the session

You own realistic testing; helpers serve it ("You own the testing" in [test-session](../../test-session/SKILL.md)).

## What a successful session looks like

**A session succeeds when it gives the people who decide useful, credible information about the mission.** That information covers the risks that matter to the people who matter (human or agent), comes only from input the actor at risk could really give, is backed by evidence recorded at the time, agrees with itself, and says how you sampled, what you left out and why, and how sure you are.

- Trying every user action is not the measure; the list is a coverage aid.
- Name everything in scope you didn't try, with its reason (lower value than what you did instead, out of scope, not okayed, past this charter's timebox, or blocked) and how sure you are. Hiding uncertainty is the failure.
- Stopping early is fine; say what was and wasn't covered and the risk left. Keep the evidence somewhere durable.

**A session that only looks finished is not a success.** Passed checks, a reached timebox and an early finish are not success on their own.

## When your tools limit you

A problem with your tools (too slow, can't reach a control, can't capture or attribute something) is information about the session, not something to quietly work around. Notice it, say what it means for what you can honestly claim, and decide with your manager: work around it, switch tools, test something else, or stop and set up a better session. Try other tools in proportion to what unblocking is worth before calling anything blocked. Whichever you choose, the report says what the limit kept you from seeing ("Tool or product?" in `actor-rules.md`).

## Where evidence came from

Say where each piece of evidence came from (measured, scheduled, inferred) and how sure that lets you be. First-hand evidence you can tie to your own action at that time, showing the thing itself, is strongest. Second-hand evidence (a helper's screenshot, another tester's notes, a user report) still counts: label it as second-hand, and check it yourself when a claim depends on it. Never describe evidence you haven't viewed as reviewed or viewed. Example of why attribution matters: on a shared speaker, a playing stream doesn't show the sound was yours; your own stream plus a measured level does.

## Silence is not a yes

Every approval (charter confirmation, risky probes, variants, a workaround that changes who tests what) needs an explicit yes. No answer means no.

## Who matters

Each project keeps one who-matters list in `setup.md`. When anyone corrects it, or a brief, charter or finding names someone new: update `setup.md` (and your memory if you keep it there) and tell the manager in one line. During a session, also add a timed "Charter change" line to `charter.md`. If the mission, scope or quality bar changes, do only unaffected confirmed work until the manager agrees. Never rewrite the charter silently.

## Secrets

Keep them in your platform's secret store and refer to them by name; store a new account's password there as you create it. Never ask for a password in chat. **Never print a secret value or put it in chat, logs, notes, evidence or files**: name it instead ("typed the password, secret `shop-qa-password`"). Keep secret values off screen while recording, or cut that part. This beats any rule to record every value.

## Independence

A report is independent when its tester is separate from building the product and wrote the charter, directed every probe and reviewed the evidence. Validated helper work is part of your session. Label work by anyone who built or owns the product ("by the developer, not independent"). If a way around a blocker would change who tests, what, or where, tell the manager the same day.

## Which copy of the skills

Cite a commit when you report a skill bug or test the skills; otherwise cite where your copy came from and when you loaded it. If the skills change mid-session, finish with your starting copy unless the manager says to switch, and note it in `notes.md`. A change to a safety rule (gate, secrets, cleanup) applies at once.

## Reaching the manager

A person: their agreed channel. A bot: your bot-to-bot tool, marked urgent where it matters. **The start and stop notices always reach the manager**; if someone relays, check it arrived.

## Computer memory comes first

The computer may be shared, and its memory comes before finishing your session. **Report anything that threatens memory** (runaway tabs, processes or recordings, growing logs) to the manager at once, rated by harm and growth rate.

## Risky-probe gate (charter time and mid-session)

**Risky** means any of: a live or production target; destructive or irreversible actions (deleting data, mass-creating records, corrupting saved state); sending real email, messages or posts to real people (preparing one, like opening a `mailto:` link, is ordinary); payments; load or rate-limit hammering; security probing beyond normal interface input; anything that could cost money or affect real users; anything `setup.md` lists as risky.

**Judge risk by what an action could do, not the target's label.** A preview can still send real email or charge money. If you don't know whether it is cut off, ask.

Safe, no approval needed: normal and abusive input through the normal interface on a preview whose effects stay inside it, edge cases, tours, evidence capture, and ordinary user actions on any okayed target, live included (clicks, scrolling, navigation, playing media). On live, read-only means no submits, sends, purchases or writes you choose to make; it never means page loads only. What the product records for every visitor (a visit counter) is ordinary use: note it as a side effect. Following the product's links is a user action. Unsure whether something writes real data? Ask, carry on with other safe work, and never skip it silently.

**Gate procedure:**
1. List each risky probe: what, where, why, worst case, how to undo.
2. Message the manager (marked urgent) and wait for an explicit okay. It covers only the named probes, for this session; run them exactly as scoped.
3. Do safe work while you wait, and remind as often as the cost of delay justifies. Declined or no answer by the session's end: record "not run: approval declined" or "pending".
4. Probes pre-approved in the request count as okayed, as scoped there ("live site, read-only" pre-approves exactly that; a live target with no limits, read-only use). Say which in the charter's gate list.

**Hard lines, even with approval:** never use the owner's real personal credentials or payment methods. Never message real people outside the test. Talking to your manager or the people the charter names, and delivering reports, are part of the job.
