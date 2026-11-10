# Project setup

Part of [write-charter](../../write-charter/SKILL.md). Run when the project has no `setup.md`. Every charter rests on knowing who decides, what the target is, who matters and what's risky; settle it once. Take answers from the brief, house rules or docs, and ask the requester only what's unclear.

1. Manager: who confirms charters and okays risky tests. A manager already recorded wins over a new requester (pass the request on); otherwise the house rules' choice, else whoever sent the request.
2. Target: this request's, and any default (such as staging).
3. Who matters: who uses, pays for, supports, runs or relies on it, and who gets hurt if it breaks, agents included. A bug matters because it bugs someone (Bach and Bolton; agents count, as in "What is a bug" in [what-is-testing](../../what-is-testing/SKILL.md)). Mark guesses and send the list with the charter to confirm.
4. Default quality goals and what's usually out of scope; each charter can override them.
5. Suggested target settings, from who matters and the risks (for example a common desktop and phone size, signed out).
6. Risky: defaults in "Risky-probe gate" in `test-session/references/session-rules.md`; ask what else counts here.
7. Reports go to the manager or where they say; skill feedback to whoever the house rules name.
8. Create `<evidence folder>/<project>/` ("Evidence folder" in `test-session/references/targets-and-evidence.md`) and write `setup.md`, guesses marked.
9. Prove any tool only this project needs (a native-app driver, a device), as in "Plan and get resources" in write-charter.
