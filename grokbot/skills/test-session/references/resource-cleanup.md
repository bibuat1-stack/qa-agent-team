# Resource cleanup

Part of [test-session](../../test-session/SKILL.md). Open before you start a browser, dev server or recording, before taking a lease, and at the end of every session. The computer may be shared, so leave it as you found it.

## Resource cleanup (leave the computer as you found it)

- Before you start: run `free -m`. Under your memory floor (from machine setup)? Tell the manager and hold. Prefer a cloud runner for long or heavy runs.
- Track what you start: every background process (recorder, logger, dev server) writes a pid file in the session folder (`video/rec-01.pid`) and gets a line in `notes.md`. A process your own script starts must be stopped by that script even when it fails. Close every tab you open.
- Leases and locks: follow your host's lease (Grok Bot box: "Leases" in `machine-setup/references/grok-bot-box.md`). Name the holder `<your name>-<session folder name>` so your runs never release each other's lease, and release by lease id or that name.
- Waiting for a lease: wait your turn, log start and end in `notes.md`, do safe work meanwhile, and ask the manager if the wait puts the mission at risk.
- **Stop only your own processes, by pid**, never by a name or pattern another session could share. Report anything else that hogs memory.
- Run only helpers you own and track, within capacity and lease limits; stop each when it reports back.

At the end of every session (after the evidence review, before the report), and if you stop early, fail or time out:
1. For each pid file, stop the process (`kill -INT` for recordings, so the file finalizes) and confirm with `ps` it's gone. If the pid was a wrapper shell, find the real process by your file's full path and stop it by pid. Close Playwright contexts. Do this before releasing any lease.
2. Close the browsers and tabs you opened; leave at most one blank tab.
3. Delete scratch files outside the evidence folder (downloads, temp builds, extracted frames).
4. Keep `charter.md`, `notes.md`, `report.md`, `retro.md`, `shots/`, cited clips and anything the brief requires; delete unused recordings.
5. Release every lease you took.
6. Run `free -m` and write one "cleanup done" line in `notes.md` (each pid and whether it's gone, what you deleted, memory before and after). Copy it into the report, or send it to the manager if there's no report.
