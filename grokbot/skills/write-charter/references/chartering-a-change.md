# Chartering a change

Part of [write-charter](../../write-charter/SKILL.md). A fix, PR, feature, configuration, data, dependency or environment change, or a removal, gets its own charter. Re-running the original check is checking; revisiting the failure under varied conditions is testing (Bolton, ["When A Bug Isn't Really Fixed"](https://developsense.com/blog/2011/01/when-a-bug-isnt-really-fixed), ["Making Progress on Regression Testing"](https://developsense.com/blog/2024/07/making-progress-on-regression-testing)).

1. The mission is the change; size scope to what it touches and who it could hurt.
2. Confirm the change is in the version under test (build, commit or URL); if you can't, it's a readiness gap.
3. Learn what changed (description, diff, notes), ask if unclear, and write what exercises it (step 6 of write-charter).
4. Explore the change and its neighbourhood: nearby features, other settings, data from before the change.
5. For claimed fixes, use the original BUG-NN entries as oracles: try the original conditions and others, and add what you saw under the original entry ("not reproduced in 5 tries at the original conditions on desktop; not tried on phone"). New problems get new numbers.
