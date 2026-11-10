# Actor rules

Part of [test-session](../../test-session/SKILL.md). Open when you name a risk's actor or an oracle, when an action fails, when you write a finding, and in the evidence review. Every-phase rules: `session-rules.md`.

## Work through the product as its actors do

Test through the means the product's actors have (its interface, the requests and pages it offers an agent), watching the runtime evidence their environment shows (console, network, build output). **Read code, repo data, diffs or server logs only when the charter names them as an oracle**, and agree first before reading other people's data. Report the symptom and its evidence; a cause the charter didn't ask for is a labelled hypothesis at most (step 4 of [write-bug-report](../../write-bug-report/SKILL.md)).

## Input must match the actor

Each risk has an actor: a person or agent who could cause the problem, or meets it by using or viewing the product. **Use only input that actor could really give, through the means they really have. Every finding names its actor.**

- Ordinary users and agents: pointer, touch, keyboard, assistive technology, or the requests the product offers an agent. A control is usable if their means reach it. Forced clicks, injected events, editing the page or its storage, and calling code directly don't count; a result reached only that way is not a finding for them.
- Tool or product? When an action fails, report what you saw promptly, with how sure you are. Then choose isolation experiments by value and cost (another driver, machine or account; a trace; a minimal repro), each one evidence for competing causes, not proof. Call it a tool limit only when evidence shows your tool caused it. Another means succeeding doesn't clear the failure: if the pointer fails but the keyboard works, the pointer failure stands and the keyboard route is a workaround.
- Some findings need nobody to act (wrong content, contrast, broken layout, a leak): their actor is anyone who views or fetches it.
- Security risks (a hostile actor bypassing the interface): forced input is the point, but only when the charter names the risk and actor, and only through the risky-probe gate. Show the actor has the access it needs, and report only the impact you demonstrated.
- **Always report a security surprise** found by ordinary testing, with actor, evidence and confidence. The charter limits investigation, never reporting. Ask before probing further.

For example, a script force-clicks a disabled "Launch" button and the page crashes. No visitor can press it, so it isn't a finding for visitors; it matters only in a chartered, gated tampering session.
