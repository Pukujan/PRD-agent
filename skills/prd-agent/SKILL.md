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
| `--out PATH` | `stories/<name>.md` | Custom output path for the story markdown |
| `--interactive` | `False` | Stop and prompt the human interactively on open flags |
| `--trends-file PATH` | `None` | Use a local JSON file for trends instead of running a live web search |
| `--no-web` | `False` | Disable live web search (requires `--trends-file`) |
| `--answers-file PATH`| `None` | Pass a JSON file of flag answers for automated flag closure |

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
