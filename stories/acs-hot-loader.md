# Any number of agents on your repo, one boss on a 30-minute lease

The decision seat fills by live join order, lapses on a clock, and reopens through a FIFO queue. A boss that goes stale loses the crown and rejoins at the back of the line.

Install with `acs_install.py` from `modules/coordination/multi-agent-hotload/v0.1.0/`.

## Two agents, one file, and no rule for who decides

You added the second session because the first one was the bottleneck. Then a third. Now three of them hold the same repository, and each one carries its own idea of what has already been decided.

Watch it happen on a Tuesday afternoon. Cursor writes the migration, Codex rewrites the same file from its own memory of the schema, and a session that has been asleep for two hours wakes up and approves a change nobody asked for. All three believe they hold authority, because nothing in your setup ever takes the seat away from the one that started first.

The state that is supposed to keep them aligned sits in per-tool memory and chat history you cannot inspect, plus a CLAUDE.md or AGENTS.md that every agent pastes in and none of them is bound by. When a change lands wrong, there is no file you can open that says who was allowed to say yes.

## The seat has a name, a clock, and a queue

Any number of agents on one repository, with one named decision boss at a time. The seat fills by live join order: the first continuer takes boss, then coder1, then coder2. Which tool launched the session carries no authority, and a seed list is a hint at most.

The lease runs 30 minutes by default. When it lapses, the seat goes vacant and the claimants line up in a FIFO queue. The front of the queue takes boss. An old boss that returns rejoins at the end of the line, and its former crown buys it nothing.

A zombie boss that wakes without the seat rejects boss-only actions and drops to worker or re-queues.

A watchdog runs on its own, about every 10 minutes, with no agent attached. It flags a stale seat, and it never hands out the crown.

## Work moves as a proposal

An agent proposes. The boss answers ACCEPT or REJECT. The proposer claims a branch and opens a PR. Nothing goes straight to the protected default branch from a session's own hands.

CI gates the merge on continuity validate, continuity preflight, the pin drift check, the pack test suite, the watchdog exercise and a secret scan. The state your agents coordinate over is checked by the same gate that lets the install through.

## Five steps to a repo with a boss on a clock

1. **Install the pack with the stack it declares mandatory.** PCM, the full CGM including human-output-naming, OIO, and the coordination runtime. A slim subset is an incomplete install. Component versions come from the release train, by the pack's own rule.
2. **Let the adapter gate pass before anything is written.** `hotload_check.py` fails closed until the pins, the helper checkout revision and the adapter validation all pass, and `PROMPT_INJECT.md` is written only on success.
3. **Start your sessions and continue them.** The first continuer takes the decision boss seat, then coder1, then coder2. The order is the live order, and you watch it settle.
4. **Move the day's work as proposals.** Propose, take the ACCEPT or REJECT, claim a branch, open the PR. The decision is attached to a seat with a holder and an expiry.
5. **Let the lease lapse.** When the clock runs out, the seat goes vacant, the claim queue decides, and the boss that comes back rejoins at the back. Authority changes hands on a timer, in the open, inside the repo you already diff.

## Put the first boss on a clock

The pack is at `modules/coordination/multi-agent-hotload/v0.1.0/`. Install it, let the gate pass, and start your sessions. The first continuer takes the seat, and thirty minutes later the repository decides who holds it next.

**Install the coordination pack**

---

### Proof and open items

Not part of the pitch above. Recorded here so the page can be audited without being flattened by it.

| Claim on this page | Source | Status |
|---|---|---|
| ACS ships a coordination pack at modules/coordination/multi-agent-hotload/v0.1.0/ as it... | modules/coordination/multi-agent-hotload/v0.1.0/README.md | verified |
| A complete install requires the full PCM + full CGM (all eight modules including human-... | modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md | claimed |
| Roles fill by live join/continue order (first continuer is decision boss, then coder1,... | modules/coordination/multi-agent-hotload/v0.1.0/ROLES.md | claimed |
| The decision boss holds a lease measured in minutes, default 30. | modules/coordination/multi-agent-hotload/v0.1.0/examples/assignment.example.json | verified |
| After lease expiry the seat goes vacant, claimants form a FIFO claim queue, the front t... | modules/coordination/multi-agent-hotload/v0.1.0/ROLES.md | claimed |
| A zombie boss that wakes without the seat must reject boss-only actions and drop to wor... | modules/coordination/multi-agent-hotload/v0.1.0/ROLES.md | claimed |
| A separate agent-less watchdog runs about every 10 minutes and only flags a stale seat... | .github/workflows/ci.yml | verified |
| CI gates merges with continuity validate, continuity preflight, the pin drift check, th... | .github/workflows/ci.yml | verified |
| No secrets are committed to the repository. | .github/workflows/ci.yml | claimed |
| The OIO issue-log intake surface is installed by OIO's own installer, which refuses to... | .github/scripts/oio_installer.py | verified |
| The OIO installer runs on Windows as well as POSIX. | .github/scripts/oio_installer.py | verified |
| Issue logs are triaged automatically into type, filer origin, priority, impact, release... | .github/scripts/oio_triage.py | verified |
| The issue intake form carries core-tier fields plus an optional investigation tier (sym... | .github/ISSUE_TEMPLATE/observational-issue.yml | verified |
| The OIO close-on-merge and status-drift workflows are pinned to the certified OIO 0.2.0... | .github/workflows/oio-close-on-merge.yml | verified |
| The mesh-sync workflow requires the current mesh versions of the sibling stack reposito... | .github/workflows/stay-on-mesh.yml | verified |
| Two TLA+ models (install and seat) model-check the install rule and the seat protocol. | modules/coordination/multi-agent-hotload/v0.1.0/formal/install.cfg | claimed |
| The seat protocol guarantees at most one boss lease, FIFO queueing, append-only history... | modules/coordination/multi-agent-hotload/v0.1.0/formal/README.md | claimed |
| A test taxonomy — acceptance, spec, unit, metamorphic, differential, protocol, failure-... | modules/coordination/multi-agent-hotload/v0.1.0/SPEC.md | claimed |
| A blind multi-agent holdout run (HLD-0002) was executed and scored per criterion. | modules/coordination/multi-agent-hotload/v0.1.0/SPEC.md | claimed |
| Work becomes a PR through propose → boss ACCEPT/REJECT → claim a branch → PR, with noth... | modules/coordination/multi-agent-hotload/v0.1.0/PROPOSALS.md | claimed |
| hotload_check.py fails closed unless the assignment pins, the helper checkout revision... | modules/coordination/multi-agent-hotload/v0.1.0/PROMPT_INJECT.md | claimed |
| A one-command installer, acs_install.py, prepares the adopter surface and never clones,... | modules/coordination/multi-agent-hotload/v0.1.0/README.md | claimed |
| Component versions are not restated in the pack; they come from the release train via s... | modules/coordination/multi-agent-hotload/v0.1.0/SPEC.md | claimed |
| The CGM adapter pins the full content-generation contract at 0.5.12 with eight modules... | .content-system/system-version.json | verified |
| The pack pins PCM CLI 0.6.0 at commit 4e2385474b4af9249ca009cbdcb38c4498932475. | .content-system/project-brief.json | claimed |
| check_pins.py scans every declared projection for the pinned PCM/CGM commits, version f... | .github/workflows/ci.yml | verified |
| The multi-agent hotloader is shipped, delivered by PR #12. | README.md | claimed |
| benchmarks against rival hotloaders | no source in the artifact | **unknown** |
| exact CPU overhead of watchdog | no source in the artifact | **unknown** |

**Swap test.** Passed. No named competitor's language covers this line (closest: none at 0% against a 60% threshold).

**Open flags.** Each one names the evidence that would let the page go harder.

- `[NEED: proof]` After lease expiry the seat goes vacant, claimants form a FIFO queue, the front takes boss, and a returning old boss rejoins at the end with no reclaim (C-005); a zombie boss without the seat must reject boss-only actions (C-006).. Read scripts/seat_protocol.py and run the protocol and failure-path test files that SPEC.md §8 maps to these rules, capturing a run log. [N-001]
- `[NEED: mechanism]` hotload_check.py fails closed unless pins, helper checkout revision and adapter validation all pass and writes PROMPT_INJECT.md only on success (C-021); acs_install.py prepares the surface and never clones, fetches or vendors helper source (C-022).. Read hotload_check.py and acs_install.py, then run both against a deliberately stale-pin fixture and show no write, no network call and a non-zero exit. [N-002]
- `[NEED: differentiator]` Component versions are not restated in the pack and come from the release train via stack-mesh.json (C-023) — but PROMPT_INJECT.md restates a CGM 0.5.12 pin at one commit while .content-system/system-version.json records a different commit for that same version (C-024), and the PCM pin is 0.6.0 while the example assignment and SPEC.md treat 0.7.0 as current (C-025).. Read pins.json, stack-mesh.json and check_pins.py, and reconcile the two 0.5.12 commits and the 0.6.0/0.7.0 gap — until then 'follows the train, no hand copies' cannot be asserted, only reported as the pack's claim. [N-003]
- `[NEED: proof]` Two TLA+ models check the install rule and the seat protocol, and the seat protocol guarantees at most one boss lease, FIFO queueing, append-only history, no watchdog appointment, no zombie action and monotonic time (C-016, C-017).. A recorded TLC run for install.tla and seat.tla with the invariant list, plus wiring the models into CI — formal/README.md itself says they are not wired today. [N-004]
- `[NEED: proof]` A blind multi-agent holdout run (HLD-0002) was executed and scored per criterion (C-019), and the test taxonomy backing the contract is passing rather than planned (C-018).. The holdout harness, run record and per-criterion scores, plus a CI run result for the acceptance, protocol, failure-path and scenario suites. [N-005]
- `[NEED: proof]` The pack is shipped and delivered by PR #12 (C-027), and a complete install requires eight modules including human-output-naming (C-002) — while HOTLOAD.md's own required-modules table lists seven rows.. The PR #12 merge record on the default branch, and the module-count logic in acs_install.py or check_pins.py showing which eight modules the gate actually enforces. [N-006]
- `[NEED: audience]` Who adopts this and at what moment — no owner answers were supplied, so the team-versus-solo split and the trigger event are inferred from the pack's own prose rather than observed.. One owner interview or one adopter record naming team size, the number of concurrent agent sessions, and the incident that made them install the coordination runtime. [N-007]
- `[NEED: proof]` The pack's relative standing against rival hotloaders and the CPU overhead of the watchdog are recorded as unknowns and are therefore absent from this positioning entirely.. A comparative benchmark run against at least one named rival hotloader and a measured watchdog cost per interval. [N-008]

**Trends used.** Market stage: jaded (Schwartz). The category has heard 'agent memory' and 'spec-driven' many times and the language has gone flat and abstract. Mem0, Zep, Letta and Supermemory all claim to remember; Kiro and Spec Kit all claim specs as source of truth. A bigger claim about remembering more will not land. Schwartz's jaded stage calls for a NEW MECHANISM, and PCM has one: the memory is your Git repository, the files are plain text, and a validator checks them. Lead with the mechanism.

Sources read for the category register and the cultural moment: https://mem0.ai/library/coding-agents/ai-coding-agents-that-actually-remember-your-codebase, https://www.braintrust.dev/articles/best-ai-agent-memory-tools-2026, https://machinelearningmastery.com/the-6-best-ai-agent-memory-frameworks-you-should-try-in-2026/, https://github.com/rohitg00/agentmemory, https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, https://kiro.dev/docs/specs/, https://github.com/orgs/community/discussions/181130, https://mem0.ai/library/context-engineering/context-window-is-ram-not-storage-why-most-agent-failures-happen-how-to-fix-them-in-2026, https://arxiv.org/html/2602.00180v1.

Searched at 2026-10-13.

**Self-check.** Run by `prd_agent.checks` against the vendored `copywriting` skill's `references/ai-tells.md`. 0 hard bans in 6 sections (contrast reveals 0, negation lists 0, trailing pile-ons 0, self-answered questions 0, colon reveals 0, stock phrases 0, banned words 0, hype punctuation 0, em dashes in short copy 0). Frequency caps, counted per section: fragment 0/1, reflexive_three 0/1, cap_vocabulary 0/1, em_dash_long 0/1. Structural beats present: discomfort, vision, path. What this check cannot decide: whether the story lands, whether a sentence that avoids every rule is still empty, and any tell written in a shape no rule here matches. That judgment is the owner's.
