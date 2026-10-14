# PRD-agent

Turn a builder's own artifact into a product story that sells.

Generated marketing copy from a repository reads as an audit: an inventory of what the product
does and what it lacks. This pipeline reads the artifact, establishes what is true, and writes
the page a stranger would read to the end.

## Run it

```bash
python -m pip install -e ".[dev]"
python -m prd_agent ../your-repo --autonomous
```

Without `--autonomous` the run stops at the open flags and asks. With it, the run completes and
ships the flags as a footer on the page.

| Flag | What it does |
|---|---|
| `--autonomous` | Complete the run and ship the flag footer instead of stopping to ask |
| `--out PATH` | Where to write the story. Default `stories/<artifact-name>.md` |
| `--trends-file PATH` | Read `trends.json` from a file instead of running the live web pass |
| `--no-web` | Never run the live web pass. Requires `--trends-file` |
| `--answers-file PATH` | A JSON object of flag id to answer, instead of reading stdin |
| `--evals PATH` | Where to append the worked example. Default `evals/story_evals.json` |

Every run writes `runs/<artifact-name>/claims.json`, `trends.json` and `positioning.json`, so any
stage can be inspected or re-run on its own.

## The four stages

```
artifact repo -> claims.json -> trends.json -> positioning.json -> story.md
                     ^______________ [NEED:] ______________|
```

1. **Intake** reads README, entry points, tests, commit subjects and docs. An unread fact becomes
   an `unknown`. The stage never invents a mechanism.
2. **Trends** runs one live web search for what competitors claim, what register of copy is
   landing, and which conversation is worth attaching to, then picks the market sophistication
   stage (Schwartz).
3. **Positioning** derives the spine (discomfort, vision, path) and the differentiator, and runs
   the swap test in code. A differentiator that a competitor already covers fails and is flagged.
4. **Story** drafts the page through the vendored `copywriting` skill, gates it against that
   skill's own self-check, rewrites a failing draft from the facts, and appends the proof table,
   the open flags and the self-check paragraph in code.

## The model seam

Every stage takes an `LLM`. The shipped provider is a stdlib `urllib` client for the Anthropic
Messages API, so the package has zero runtime dependencies. Tests inject a fake and never touch
the network.

```bash
export ANTHROPIC_API_KEY=...        # required for a real run
export PRD_AGENT_MODEL=...          # optional model override
```

Offline, without a key, the pipeline replays canned responses:

```bash
export PRD_AGENT_LLM=fake
export PRD_AGENT_CANNED_DIR=/path/to/dir/of/numbered/txt/files
```

## What the self-check can and cannot decide

`prd_agent.checks` implements the vendored skill's `references/ai-tells.md`: the hard bans
(contrast reveals, negation lists, trailing pile-ons, self-answered questions, colon reveals,
stock phrases, banned vocabulary, hype punctuation, em dashes in short copy), the frequency caps
counted per section, and the three structural beats. It cannot decide whether the story lands,
whether a sentence that avoids every rule is still empty, or any tell in a shape no rule matches.
The footer says so on every page, and that judgment stays with the owner.

## Licence

The vendored `copywriting` skill is MIT, copyright Corey Haines, from
`coreyhaines31/marketingskills` at commit
`0f8d8996`. The vendored copy, its licence and its
SHA-256 hashes live in `src/prd_agent/vendor/copywriting/`; `PROVENANCE.md` records where it came
from and `tests/test_skill.py` fails if a vendored file changes without its hash being updated.

## What this does not do yet

Trends are searched live and not stored. There is no scraped corpus and no semantic retrieval;
the eval file is searched by keyword overlap. That seam is written down in
`docs/CORPUS_SEAM.md` and deliberately not built.
