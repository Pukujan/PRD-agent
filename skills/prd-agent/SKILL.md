---
name: prd-agent
description: Turn any builder repository or code artifact into a high-converting, story-first marketing page with zero audit clutter.
---

# PRD-agent: Autonomous Story-First Marketing Engine

PRD-agent transforms a technical codebase or artifact repository into an irresistible, human-relatable marketing story that sells.

Traditional AI writing defaults to dry audits: inventorying files, listing mechanics, and creating proof spreadsheets. PRD-agent does the opposite: **Story First, Feature Later**. It attacks the visceral emotional nightmare builders secretly live with, paints the unlocked dream, and introduces features only as the heroes that unlock that dream.

## How to Run (Blind Agent Quickstart)

To generate a story for any repository, run:

```bash
python -m prd_agent <path-to-target-repo>
```

**Autonomous by Default:** The command runs end-to-end without stopping for human input. It will never hang on stdin.

### Output Locations
- **`stories/<repo-name>.md`**: The final marketing pitch. 100% pure story, zero audit tables, zero internal file paths, zero em-dash pauses.
- **`runs/<repo-name>/`**: Backend machine telemetry:
  - `claims.json`: Truth established from the repository.
  - `trends.json`: Cultural zeitgeist, human nightmare, viral hype words, and market stage.
  - `positioning.json`: Positioning spine, nightmare scene, dream scene, and code-verified swap test.

## Common CLI Options

| Flag | Default | Description |
| :--- | :--- | :--- |
| `artifact_path` | *(required)* | Path to the target repository or artifact directory |
| `--readme` | `False` | Write the generated marketing story directly to `<artifact_path>/README.md` |
| `--out PATH` | `stories/<name>.md` | Custom output path for the story markdown |
| `--interactive` | `False` | Stop and prompt the human interactively on open flags |
| `--trends-file PATH` | `None` | Use a local JSON file for trends instead of running a live web search |
| `--no-web` | `False` | Disable live web search (requires `--trends-file`) |
| `--answers-file PATH`| `None` | Pass a JSON file of flag answers for automated flag closure |
| `--hype LEVEL` | `1000` | Narrative calibration dial: 1000 (electric), 750 (venture), 500 (balanced), 250 (truth) |
| `--persona PERSONA` | `solopreneur` | Audience persona: solopreneur (unicorn), enterprise (cto/vp), normie (consumer/magic) |
| `--pack` | `False` | Generate the full multi-asset launch pack under runs/<name>/pack/ |

## Turnkey Runner & Proxy Auto-Discovery

PRD-agent is built for autonomous execution across developer and agent workflows:
- **Proxy Auto-Discovery:** If `ANTHROPIC_BASE_URL` points to a local proxy (such as LiteLLM at `http://127.0.0.1:4000`), it automatically normalizes the path to `/v1/messages`.
- **Key Fallback:** Auto-discovers `HADES_LITELLM_API_KEY` or `OPENCODE_LITELLM_MASTER_KEY` when `ANTHROPIC_API_KEY` is not explicitly set.
- **Model Fallback:** Honors `ANTHROPIC_MODEL` when `PRD_AGENT_MODEL` is unset.
- **Em-Dash Auto-Purge:** Automatically sanitizes em-dashes and double-hyphens before gating so model drafts never fail on punctuation alone.


## The Hype-to-Honesty Dial

- **Level 1000: Electric God-Mode (default):** Maximum kinetic energy, loud optimism, One-Person Unicorn, 100x leverage.
- **Level 750: High-Converting Venture Hype:** Visceral 2:00 AM founder nightmare, unlocked dream, aggressive contrast.
- **Level 500: Balanced Authority:** Confident, dignified engineering reality with zero buzzwords.
- **Level 250: Pure Technical Truth:** Clinical, understated, empirical rigor.

In `--interactive` mode without `--hype`, the pipeline interactively prompts the operator before generation.

## Audience Persona Calibration

- **`solopreneur` (default):** Solo builders, 100x leverage, killing babysitting chores, shipping while sleeping.
- **`enterprise`:** CTOs and VPs, boardroom liability, killing security theater, stopping runaway cloud bills.
- **`normie`:** Everyday consumers, pure effortless magic, zero technical jargon, "flying cars" simplicity.

## Multi-Asset Launch Pack (`--pack`)

Generates `runs/<name>/pack/`:
- `copy.json`: Landing page copy deck with headline, subhead, superpowers, before/after table, and CTAs.
- `launch_thread.md`: 6-8 tweet viral X / Twitter announcement thread with spicy hook and proof.
- `show_hn.md`: High-authenticity Show HN / Product Hunt launch narrative.
- `pitch_deck.md`: 10-slide high-stakes pitch narrative with category shift, secret weapon, and unit economics.

All generated assets strictly enforce zero em-dashes (`—`, `–`, `--`).

## Pipeline Stages

```
artifact repo -> claims.json -> trends.json -> positioning.json -> story.md
```

1. **Intake (`claims.json`):** Reads README, source files, tests, and commits into concrete claims.
2. **Trends (`trends.json`):** Live web search for competitor claims, market sophistication stage (Schwartz), the universal human nightmare, and trending hype words.
3. **Positioning (`positioning.json`):** Derives the spine (discomfort, vision, path), concrete nightmare/dream scenes, and runs the machine swap test against competitors.
4. **Story (`stories/<name>.md`):** Drafts the copy through the vendored copywriting skill, passes it through the anti-audit gate (`checks.py`), and automatically rewrites if any AI tell is tripped.

## Operating Principles for Agents

1. **Story First, Feature Later:** Never open with technical architecture or feature lists. Ground the reader in their own relatable nightmare first.
2. **Zero Audit Clutter:** Proof tables, test lists, and file paths belong exclusively in `runs/`, never in `stories/`.
3. **Zero Em Dashes:** Double-hyphens (`--`) and em dashes in short copy are hard banned by the machine checker. Use periods or commas.
