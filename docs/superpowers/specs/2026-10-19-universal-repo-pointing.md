# Specification: Universal Remote Repository Pointing & GitHub Action

- **Date:** 2026-10-19
- **Status:** Draft
- **Task ID:** PRA-0012
- **Issue:** https://github.com/Pukujan/PRD-agent/issues/28

---

## 1. Goal

Enable ANY repository, external developer, or blind agent to point directly to the `PRD-agent` GitHub repository (`https://github.com/Pukujan/PRD-agent`) and produce an automated, high-stakes manifesto and README with zero local setup friction.

---

## 2. Remote Repository Detection & Intake

### 2.1 Remote URL Recognition
`is_remote_url(source: str) -> bool` identifies if a target string is a remote Git repository rather than a local path:
1. `https://github.com/<owner>/<repo>`
2. `http://github.com/<owner>/<repo>`
3. `git@github.com:<owner>/<repo>.git`
4. `github.com/<owner>/<repo>`
5. `owner/repo` (where `owner` and `repo` match `^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$` AND the path does not exist on the local filesystem)

### 2.2 Normalization
`normalize_remote_url(source: str) -> str`:
- Translates `owner/repo` to `https://github.com/owner/repo.git`.
- Translates `github.com/owner/repo` to `https://github.com/owner/repo.git`.
- Retains existing `https://` or `git@` schemes.

### 2.3 Managed Shallow Clone
`resolve_artifact(source: str | Path, workdir: Path | None = None) -> ArtifactContext`:
- If `source` is an existing local directory:
  - Returns direct local path, `is_remote=False`.
- If `source` is a remote URL:
  - Clones shallowly via `git clone --depth 1 <normalized_url> <target_temp_dir>`.
  - Returns `target_temp_dir`, `is_remote=True`, with automatic cleanup on context manager exit.
  - On clone failure (e.g. non-existent repository, network timeout), raises `StageError("failed to clone remote repository '<url>': <error>")`.

---

## 3. GitHub Action (`action.yml`)

A root `action.yml` turns `PRD-agent` into a reusable composite GitHub Action:

```yaml
name: "PRD Agent"
description: "Turn any repository into an irresistible marketing manifesto and README."
inputs:
  anthropic_api_key:
    description: "Anthropic API Key or proxy master key"
    required: false
  anthropic_base_url:
    description: "Custom API base URL (e.g. LiteLLM proxy)"
    required: false
  model:
    description: "LLM model override"
    required: false
  readme:
    description: "Overwrite target repository README.md"
    required: false
    default: "false"
  hype:
    description: "Calibration voice: electric, venture, technical"
    required: false
    default: "electric"
  persona:
    description: "Audience persona: solopreneur, enterprise, normie"
    required: false
    default: "solopreneur"
  pack:
    description: "Generate multi-asset launch pack"
    required: false
    default: "false"
  target_path:
    description: "Path to target repository code (default: current directory)"
    required: false
    default: "."
outputs:
  story_path:
    description: "Path to the generated marketing story"
    value: ${{ steps.run-prd.outputs.story_path }}
  five_lines:
    description: "The 5-line executive battle cry"
    value: ${{ steps.run-prd.outputs.five_lines }}
```

Any GitHub repository can then add a one-file workflow:
```yaml
- uses: Pukujan/PRD-agent@main
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    readme: true
```

---

## 4. BDD Scenarios

### Scenario 1: CLI Remote Intake via GitHub URL
- **Given:** A valid public GitHub repository URL (`https://github.com/SouthpawIN/turbofit`).
- **When:** `python -m prd_agent https://github.com/SouthpawIN/turbofit --no-web --trends-file <fixture>` is executed.
- **Then:** PRD-agent clones the repo to a temporary workspace, completes intake, outputs the 5-Line Executive Hook to stdout, and writes `stories/turbofit.md`.

### Scenario 2: Shorthand `owner/repo` Resolution
- **Given:** Shorthand string `SouthpawIN/turbofit` where no local folder `SouthpawIN/turbofit` exists.
- **When:** `resolve_artifact("SouthpawIN/turbofit")` is called.
- **Then:** It normalizes to `https://github.com/SouthpawIN/turbofit.git` and clones cleanly.

### Scenario 3: Nonexistent Remote Repo Failure Mode
- **Given:** A nonexistent remote repository `https://github.com/Pukujan/nonexistent-xyz-repo-404`.
- **When:** `resolve_artifact(...)` is invoked.
- **Then:** Fails closed with `StageError` containing clear error description without crashing unhandled.

### Scenario 4: GitHub Action Metadata Validity
- **Given:** Root `action.yml`.
- **When:** Inspected against GitHub Action composite schema.
- **Then:** Has valid name, description, inputs, runs steps, and outputs.
