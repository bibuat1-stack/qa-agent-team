# Evidence detail

Part of [run-test-session](../../run-test-session/SKILL.md). Open when the charter involves timing, automated checks, a video-review helper, or a finding whose times will be reported.

- **Timing-dependent behaviour:** measure what your tools actually do (the real gap between actions), and log each try as inside or outside the window. Keep every try and revise the timing model when results challenge it. Can't hit the window? "When your tools limit you" in `test-session/references/session-rules.md`.
- **Accidents count:** a mis-click or setup accident that produces the state under test is a try: time it and report it.
- **Automated checks** (links, for example): each result is pass, fail or unknown. Fail only when the evidence shows the problem; a result your tool couldn't get is unknown, with why. Give counts separately, check an important unknown once by hand, and don't hammer past a block.
- **Claims ledger** (in `notes.md`): mark each time or fact a finding rests on video-verified, server-verified or tester-reported.
- **Headless recording:** record the page itself with its clock burned in, and log each event's clock time from your script (Grok Bot box: "Recording a headless browser" in `machine-setup/references/grok-bot-box.md`).
- **Video-review helper** (optional, a watchVideo subagent): it can check clips for flicker, layout jumps, slow loads and error toasts. Its findings are second-hand: mark them as from video review.
