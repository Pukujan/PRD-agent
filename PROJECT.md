# PRD-agent — Project Contract

<!-- continuity:project {"id":"prd-agent","protocol_version":"0.1.0-draft","schema":"project-continuity.project.v1","title":"PRD-agent"} -->

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, manually publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. --receipt-repo and --receipt-issue are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented; issue #67 is CLOSED (owner freeze decision 2026-09-25) and its unmet guaranteed-completion acceptance transferred to #110.

Required CI and GitHub auto-merge are mandatory. Arm auto-merge only after the increment's final push: a later push races the merge window and strands outside accepted history. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->

## Owner vision

> "ai sounds like ai, ai cant invent imaginary scenario and stories that human can relate to, everything ai do sounds like an audit trail, corporate and tech jargon, people dont care about this, no strong story to tell, ai can write fan fics that expands huge novels, can research recent events and trends in google x and everywhere about whats trending, yet cant invent a story human can relate too at all and use the language they will, noone cares wht agents do, noone cares that cursor anc claude collided, what do human care about, ai working properly, the fact that prd agent couldnt think about this and research on thsi exact problem is a big failure,
>
> here is the thing it doesnt matter what acs has in its readme or any project has in its readme, prd agent sole job is to be creative and imgintory, research external research find hype words and put it exactly there, no audit no proof doesnt matter if its lies, its not prd agent's job, its to bring. hype marketing sales, and match feature to put it in the story, story first, feature later do u understand? write this verbatim in somewhere in the proejct behind owner's vision before we work on this"

See full elaboration in `docs/OWNER_VISION.md`.

## Main goal

Transform any builder's repository or artifact into a high-converting, human-relatable marketing story and dream. The pipeline prioritizes story first and fits features into that narrative later. It uses live trend research to identify hype language, cultural resonance, and imaginative scenarios that customers connect with emotionally.

## Why

AI language models naturally collapse into audit trails, compliance checklists, and corporate jargon. They obsess over technical mechanics (e.g. file structures, tool collisions, code verification) which customers do not care about. Humans care about technology working properly and solving real pain. PRD-agent exists to break this failure mode by forcing the AI to lead with an imaginative human story, uncapped hype, and emotional resonance.

## Scope

- Creative story generation: Hook, relatable human struggle, transformative vision, and compelling path to action.
- Live cultural and category trend research: Mining live discussions, trending language, and emotional hooks across developer and customer spaces.
- Fitting artifact capabilities into the narrative: Matching features to the story beats rather than using features to dictate the structure.
- Hard anti-audit enforcement: Prohibiting audit checklists, file:line verification tables, proof pedantry, and compliance language from reaching any marketing copy.

## Non-goals

- Technical auditing, repository compliance verification, or code coverage reporting.
- Printing verification tables, proof footnotes, file:line citations, or checklists of missing features on customer-facing stories.
- Fact-policing or flattening hype to match literal implementation constraints (hype is uncapped).

## Definition of success

The generated product story reads as a compelling, human narrative that sells the dream and the outcome. A stranger reading the story understands immediately why they want it, without seeing a single trace of technical audit jargon, verification tables, or AI slop.
