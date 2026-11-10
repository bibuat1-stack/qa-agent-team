# Stopping heuristics

Used by "Before you stop" in [run-test-session](../../run-test-session/SKILL.md), which says how to notify the manager. Applies to a test, a probe group or a session.

> Credit: Michael Bolton's stopping heuristics (DevelopSense), developed with James Bach in Rapid Software Testing. Mission Rejected was suggested by Cem Kaner, and the split of "Pause That Refreshes" into "Change in Priorities" and "Lights are Off" by Joe Harter. Sources: "When Do We Stop a Test?" (developsense.com/blog/2009/09/when-do-we-stop-test), "When Do We Stop Testing? One More Sure Thing" (developsense.com/blog/2009/10/when-do-we-stop-testing-one-more-sure), "Why Does Testing Take So Long?" (developsense.com/presentations/2009-06-WhenDoWeStopTesting.pdf) and "Signing Off" (developsense.com/blog/2018/03/signing-off). Dale Emery and James Lyndsay contributed to the discussion. Names are Bolton's. The "Our rule" column is AGQT policy, not Bolton's.

Each heuristic is fallible: ask its question before relying on it, and name the one you used. Stopping never says the product is good enough ("The tester informs, the manager decides" in [write-test-report](../../write-test-report/SKILL.md)). Meanings are paraphrased from Bolton.

| Heuristic | Meaning (Bolton) | Our rule |
|---|---|---|
| Time's Up! | The charter's timebox (if any) has run out. Did you get what you needed? | Only a timebox in this charter, checked with `date`. Hand the rest over as follow-up; ask for more time if the risk calls for it. |
| Piñata | The first sufficiently dramatic problem. Is it the most important, or is more inside? | Send the bug progress report ("Progress reports" in run-test-session) at once, then continue unaffected work or stop, and record which. |
| Dead Horse | Too buggy to be worth more testing, or coming changes will invalidate it. | Only with evidence (the bugs, the planned change). "Probably all broken" is an assumption. |
| Mission Accomplished | The mission's questions are answered. Has testing raised new ones? | First walk Covered means and each named focus in `notes.md`: explored with evidence, or a gap with its reason. Not while the core is untested or a PO answer it needs is pending. |
| Mission Revoked | The manager says stop. | Stop and record who and when. Important reasons to continue? Say so once, with evidence; it's their call. |
| Mission Rejected (Kaner) | Continuing would cause a problem for someone, especially an ethical one. | Stop that work at once and tell the manager why; never reject quietly. Continue unaffected work while they decide. |
| I Feel Stuck! | Something seems to block you. Feeling stuck or being stuck? | Prove what's missing or record it as unverified; never present an unverified "can't" as proven. |
| Pause That Refreshes (Change in Priorities, Lights are Off, after Harter) | Suspend to rest or reflect, because something matters more, or you're going through the motions. | A pause is not a stop: log it with the time. Prefer pausing to ask when a resource or scope change could unblock the mission. Out of ideas? Change approach before claiming you're done. |
| Flatline | The same result whatever you do: crashed, hung or very stable. | A crash or hang is a finding. Stop that line when more variation isn't worth it, writing what you varied. |
| Customary Conclusion | You stop where you usually stop (all acceptance checks pass). | Never enough alone: passed checks are not success. |
| Change Tack | Switch approach. Is the new tack better, or just new? | Record the switch and why; it stops one line, not the session. |
| No More Interesting Questions | No remaining question is worth its cost. Is a Black Swan waiting? | Name the questions considered and why each isn't worth more time. |
| Cost vs. Value | The foundation of the others: continuing costs more than the information is worth. | Say what more testing would cost and might find. A cost to the owner not agreed at readiness is a reason to stop that line and tell the manager. |
| Avoidance/Indifference | Someone doesn't want more information. Is someone avoiding a problem? | In others, tell the manager; in yourself, reassess or change tack. |

## Recording a stop

Write it in `notes.md` when it happens, then copy it into the report:

`Stopped because: <heuristic>: <why it applied, with evidence> · Time used: <minutes> of <this charter's timebox, or "no timebox"> · Not covered: <what, with why> · Charter change (if any): <what, agreed when> · Risk remaining: <what and for whom> · Next: <recommended small charter(s)> · Manager informed: <when (straight away)>`

Stopping one line while the session continues is a Change Tack note. Ending the session always means the stop progress report, straight away.

Illustration: `Stopped because: Mission Accomplished: the mission's risks explored on desktop and phone, sampling in notes 14:02–14:40 · Time used: 38 of 40 min · Not covered: speech on phone (voices unverified, asked 14:05, manager agreed 14:12 to drop it) · Charter change: phone speech out of scope, agreed 14:12 · Risk remaining: phone visitors may hear the wrong voice · Next: phone speech once voices are proven · Manager informed: 14:41`
