# Targets and evidence

Part of [test-session](../../test-session/SKILL.md). Open at setup and before the access check. Every-phase rules: `session-rules.md`.

## Targets, access and accounts

- Target: the charter names it (a site or app, preview or live, or a reading target such as skills or a document) and how to get access. A practice target only exercises the thing under test; report its bugs separately. Live is not a stand-in for a preview.
- Access check: before sending the charter, a read-only check with no saved login (`curl`) that reaches the right version is enough; browser proof comes at the smoke run (step 4 of [run-test-session](../../run-test-session/SKILL.md)). Record: reachable; reachable, browser check at smoke run (say what's unchecked); or unreachable (tell the manager the blocker and scope affected).
- Test accounts: only those the manager or PO provides or approves.

## Evidence folder

The root comes from the house rules or your memory; with neither, use `<your workspace>/qa/`, save it to memory and tell the owner. Settle it before writing any project file.

`<evidence folder>/<project>/` holds `setup.md` and one session folder per session, `<YYYY-MM-DD>-<your name>/`. **Create it with `mkdir`, never `mkdir -p`**, so it fails if it exists; then add a suffix (`-2`) and retry. Writing into a folder you didn't create overwrites another tester's files. A session folder holds `charter.md`, `notes.md`, `report.md`, `retro.md`, `shots/`, `video/` (and `audio/` where sound matters), where your video reviewer can read it.

Shared storage (if house rules ask): add only your own files, record yourself as author, and if it's in an unexpected state, leave it and tell the manager.
