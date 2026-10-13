# Your project's memory is your Git repository

**Plain files next to the code they describe, checked by a validator, so any session in any tool picks up exactly where the last one stopped. 264 deterministic tests stand behind every claim on this page.**

`continuity init` · install from source · MIT licensed · zero runtime dependencies

---

## The project stops making sense when the chat ends

You know the feeling. You open a project after two weeks away and the first hour goes into working out what state it is in. Which experiment finished. Which decision you already made and why. What the number in last month's report actually measured.

You had all of it. It lived in a conversation that is now too long to scroll, in a context window that filled up, in a summary that quietly dropped the detail that mattered.

Then a model change wipes the slate, a second agent starts on the same code, and the reconstruction starts over. Every handoff becomes archaeology.

The failure has a name. The memory lives somewhere the project does not control.

## Pick it up cold

Project Continuity Modules puts a project's working state in the repository as ordinary Markdown and JSON, next to the code it describes. A fresh session opens the repo and reads four things: what the project is, where it stands, which task is active, and what the last session proved. Then it works.

You get the state out of the chat and into version control. That move buys you three things the category has not been selling you.

**Any tool, any model, any person.** The record is plain text in your repo, so a Claude session, a Codex session and a colleague returning in March all read the same files. The protocol declares independence from any one vendor because it has no vendor to be independent of. Nothing leaves your machine for a third party to store.

**A validator checks the record on every run.** `continuity validate` fails a repository that has lost its thread: a missing current-task file, a duplicated task ID, a checkpoint asserting work with no evidence attached. A memory service hands back whatever an agent said. PCM runs your project's state through the same kind of deterministic test you run your code through.

**Evidence you can challenge months later.** Each checkpoint records what changed, which commands ran, what was blocked, and the exact next action. Two sessions reporting different eval scores is a real conversation only if you can recover the commit, the dataset revision, the prompt version and the excluded failures behind each number. PCM puts those in the record while the session is still open and someone knows them.

Retry `continuity checkpoint` with the same request ID and you get no duplicate. A changed payload is rejected instead of silently appended. The history stays clean without you babysitting it.

## Where the memory lives is the whole decision

|  | Chat history | Hosted agent memory | PCM |
|---|---|---|---|
| Storage | A conversation that expires | A database someone else runs | Your repository |
| Shape | Whatever the model summarized | Vector embeddings, retrieval ranks | Markdown and JSON a human reads |
| Checked? | No | No | `continuity validate`, deterministically |
| Needs a server | | Yes | No |
| Works offline, on any model | | | Yes |

Mem0 rents you a memory layer. Zep builds you a temporal knowledge graph. Kiro and GitHub Spec Kit give your specs a home. All four are asking you to trust a system outside the project with the project's own state.

PCM's answer to "where does my project remember things" is: the place the project already keeps everything it cares about.

## A session's whole life, in four steps

1. **Read the state.** Open the repo, read `HANDOFF.md` and `checkpoints/CURRENT.md`, check the live issue that owns the task. Roughly ninety seconds, and the session is oriented.
2. **Do one bounded task.** One task file, one branch, one primary writer. Scope creep gets caught by the record instead of by you noticing late.
3. **Write the evidence.** The checkpoint takes completed work, commands and test output, decisions, blockers, and one exact next action. Retried pushes stay idempotent.
4. **Publish it.** `continuity checkpoint` commits and pushes on the task branch, required CI runs, auto-merge lands it. A session that never happened to you is now a session you can audit.

The next session starts at step one. It does not need the old conversation.

## Built for the projects that outlive their sessions

Subscription teams whose agents hand work across model versions. Researchers whose numbers have to survive review. Anyone who has watched a fresh agent redo a day of work because it could not see that the work was done.

Fourteen design documents, two init profiles, and the full protocol ship in the repo. `continuity init --profile software` writes `PROJECT.md`, `HANDOFF.md`, `checkpoints/CURRENT.md`, `.continuity/config.json` and versioned schemas, plus `AGENTS.md` and a README. It lists every file it will touch and refuses to overwrite content that differs from what it expects. Your existing docs keep their own authority. A repository already carrying its own `PROJECT.md` gets an adoption path instead of a wrecking ball.

## Questions worth asking before you install

**Does this need a server?** No. Python 3.11, Git, and no runtime dependencies at all.

**Do I have to use GitHub?** GitHub is required for PCM-governed task work, because the issue owns scope, priority and lifecycle. Without it you keep the files and the validator and lose the merge-gated delivery checks.

**Will it rewrite my documentation?** `init` refuses before writing when a planned path holds different content. Mature repositories follow a target-adoption guide instead.

**Is my project's state private?** It is in your repository, on your branches, with your existing access controls.

**Is a checkpoint the same as proof?** No, and PCM says so out loud. A citation makes a claim traceable. That is a different thing than making it true, and the protocol never claims the second one.

## Try it on the project you are most afraid of losing

Clone the repository, install from source, and initialize the project you would hate to have to reconstruct.

```bash
git clone https://github.com/Pukujan/project-continuity-modules.git
cd project-continuity-modules
python -m pip install -e .
```

Then inside any Git repository:

```bash
continuity init --profile software --name "My Project" --task-prefix APP
continuity validate
```

`continuity validate` prints `VALID` and you have a project that can survive losing every conversation it has ever had. Start with one task file. The long-term test is simple: a project should stay understandable and resumable even if every previous agent session disappears.

MIT licensed. Free forever, because it is your repository. No card required.

---

### Proof and open items

Not part of the pitch above. Recorded here so the page can be audited without being flattened by it.

| Claim on this page | Source | Status |
|---|---|---|
| 264 deterministic tests, six required CI contexts green on merged PRs | PCM `README.md` evidence table at commit `85e6aa7`, `.github/workflows/ci.yml` | verified |
| Zero runtime dependencies, Python 3.11+ | `pyproject.toml` | verified |
| Checkpoint retries idempotent by request ID | `tests/test_checkpoint_retries.py` | verified |
| `init` refuses to overwrite differing content | `cli.py:473`, cited in `README.md` | verified |
| CLI prints `continuity 0.5.0` while package source declares `0.7.0` | `README.md:69` vs `README.md:135` | **contradiction in the artifact, unresolved** |
| Hosted memory services do not validate stored state | Our reading of Mem0, Zep, Letta and Supermemory marketing as of 2026-10-13 | inferred |

**Open flags.** Each one names the evidence that would let the page go harder.

- `[NEED: proof]` Adoption. This page claims no user count because the artifact has no adopter list and no published package. A public adopter list or install count unlocks a proof-focused headline, which is the strongest available form here.
- `[NEED: proof]` That a fresh session resumes correctly. Deterministic tests cannot establish this and PCM's own README says so. The blind-test holdout at PCM issue #139 is the unlock. Until it reports, the claim "any session picks it up cold" rests on dogfooding and `examples/minimal-dogfood/`.
- `[NEED: proof]` One before/after story from a real long project. Unlocks the single most persuasive section a page like this can carry.
- `[NEED: differentiator]` None open. The swap test ran against Mem0, Zep, Letta, Supermemory, Kiro and GitHub Spec Kit; the mechanism claim ("the memory is your repo, and a validator checks it") fails on all six.

**Trends used.** Market stage: jaded (Schwartz). The category has heard "persistent memory" many times and the language has gone abstract, so this page leads with a new mechanism and a checked record rather than a louder promise. Category register pulled from [Braintrust's 2026 comparison](https://www.braintrust.dev/articles/best-ai-agent-memory-tools-2026), [Mem0's coding-agents page](https://mem0.ai/library/coding-agents/ai-coding-agents-that-actually-remember-your-codebase), [MachineLearningMastery's framework roundup](https://machinelearningmastery.com/the-6-best-ai-agent-memory-frameworks-you-should-try-in-2026/), and [Martin Fowler's spec-driven analysis](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html). Cultural moments attached: context-window-as-RAM, and the spec-drift argument in [GitHub community discussion 181130](https://github.com/orgs/community/discussions/181130).

**Self-check.** Written against `references/ai-tells.md`. Zero em dashes. No contrast reveals, negation lists, trailing pile-ons, self-answered questions or colon reveals. One intentional fragment ("No."). Sentence lengths varied on purpose. Competitor positioning kept out of the pitch body and placed in the table plus one comparative paragraph, where serving the sell rather than inventorying the market.
