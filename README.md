# PRD-agent

Turn a builder's own artifact into a product story that sells.

Generated marketing copy from a repository reads as an audit: an inventory of what the product
does and what it lacks. This pipeline reads the artifact, establishes what is true, and writes
the page a stranger would read to the end.

## Run it

```bash
python -m pip install -e ".[dev]"
python -m prd_agent ../your-repo
```

PRD-agent runs **autonomously by default**: it reads the artifact, searches the web, derives positioning, and outputs the pure marketing story into `stories/<artifact-name>.md`.

| Flag | What it does |
|---|---|
| `--interactive` | Stop at open flags and prompt on stdin instead of running autonomously |
| `--out PATH` | Where to write the story (default: `stories/<artifact-name>.md`) |
| `--trends-file PATH` | Read `trends.json` from a file instead of running the live web pass |
| `--no-web` | Never run the live web pass. Requires `--trends-file` |
| `--answers-file PATH` | A JSON object of flag id to answer, instead of reading stdin |
| `--evals PATH` | Where to append the worked example (default: `evals/story_evals.json`) |
| `--hype LEVEL` | Narrative calibration dial: `1000` (electric), `750` (venture), `500` (balanced), `250` (truth) |
| `--persona PERSONA` | Target buyer persona: `solopreneur` (unicorn/builder), `enterprise` (cto/vp), `normie` (consumer/magic) |
| `--pack` | Generate the full multi-asset launch pack under `runs/<artifact-name>/pack/` |

The output in `stories/<artifact-name>.md` is pure pitch: zero audit tables, zero internal code paths, zero em dashes. Every run writes truth telemetry to `runs/<artifact-name>/claims.json`, `trends.json` and `positioning.json`, keeping verification segregated from marketing copy.

## The Hype-to-Honesty Dial

Calibrate how loud the story goes depending on your target audience:

- **Level 1000: Electric God-Mode (default)**: Maximum kinetic energy, loud optimism, One-Person Unicorn, 100x leverage, and supersonic momentum.
- **Level 750: High-Converting Venture Hype**: Sharp 2:00 AM founder nightmare, unlocked dream, and punchy competitive contrast.
- **Level 500: Balanced Authority**: Confident, dignified engineering reality. Direct problem and solution with zero fluff.
- **Level 250: Pure Technical Truth**: Clinical, understated, empirical rigor. Code, benchmarks, and data speak for themselves.

In `--interactive` mode without `--hype`, `prd-agent` interactively prompts you to choose the dial before generation.

## Audience Persona Calibration

Tailor the vocabulary, nightmares, and dream states to who is holding the wallet:

- **`solopreneur` (default)**: Infinite leverage, autonomous shipping speed, killing administrative drag, out-building 50-person legacy teams as a One-Person Unicorn.
- **`enterprise`**: Boardroom liability, killing security theater, stopping runaway cloud API bills, eliminating zero-day leaks, and breaking vendor cartels.
- **`normie`**: Pure everyday magic, zero jargon, zero terminal commands, effortless lifestyle elevation, and "flying cars" simplicity.

In `--interactive` mode without `--persona`, `prd-agent` prompts you to choose your buyer persona.

## Multi-Asset Launch Pack (`--pack`)

Passing `--pack` generates the complete go-to-market launch arsenal in `runs/<artifact-name>/pack/`:

1. **`copy.json`**: Complete landing page copy deck with hero headline, subhead, 4-5 superpower feature breakdowns, before/after contrast table, social proof hooks, and high-converting CTAs.
2. **`launch_thread.md`**: 6-8 tweet viral X / Twitter announcement thread with pattern-interrupt hook, 3:00 AM nightmare drama, architectural breakthrough, and proof benchmarks.
3. **`show_hn.md`**: Authentic Show HN / Product Hunt launch drop covering founder origin, architecture, dogfooding insights, and discussion invitation.
4. **`pitch_deck.md`**: 10-slide high-stakes venture narrative covering the category shift, the bleeding wound, the secret weapon moat, and unit economics.

All generated assets strictly enforce the zero em-dash policy (`—`, `–`, `--`) and inherit the active hype dial and audience persona.

## The four stages

```
artifact repo -> claims.json -> trends.json -> positioning.json -> story.md
```

1. **Intake** reads README, entry points, tests, commit subjects and docs into concrete claims.
2. **Trends** runs a live web search for what competitors claim, market sophistication stage (Schwartz), the universal human nightmare, and viral hype words.
3. **Positioning** derives the spine (discomfort, vision, path), concrete nightmare/dream scenes, and runs the machine swap test against competitors.
4. **Story** drafts the page through the vendored `copywriting` skill, gates it against the anti-audit self-check in `checks.py`, rewrites any draft tripping hard bans, and produces pure pitch copy without audit clutter.

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
stock phrases, banned vocabulary, hype punctuation, em dashes in short copy, double-hyphen pauses,
audit jargon, code paths in prose, and features before story), the frequency caps
counted per section, and the three structural beats. It cannot decide whether the story lands,
whether a sentence that avoids every rule is still empty, or any tell in a shape no rule matches.
That judgment stays with the owner.

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
