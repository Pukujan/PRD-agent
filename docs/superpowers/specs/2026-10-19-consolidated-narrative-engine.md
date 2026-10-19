# Consolidated Narrative Engine Specification

**Date:** 2026-10-19  
**Task:** PRA-0011  
**Status:** In Review  
**Protocol:** Spec-Driven Development (SDD) & Behavior-Driven Development (BDD)

---

## 1. Problem & Context

Prior to this specification, `PRD-agent` evolved two parallel and disconnected narrative control tracks:
1. **The Hype-to-Honesty Dial (`hype.py`):** 4 numeric tiers (1000, 750, 500, 250) dictating adjectives and tone.
2. **The Belief Inversion Engine (`schemas.py`, `trends.py`, `positioning.py`):** A 4-step conflict engine (`false_dogma`, `rebellion_belief`, `cultural_enemy`, `weaponized_mechanisms`).

### The Consequence
When external or "blind" agents (e.g. Claude sessions, Custom GPTs, or subagents with no internal knowledge of PRD-agent) were asked to generate marketing narratives, they scrambled these two routes into robotic meta-prompt leakage:
```text
Level 1000, solopreneur, belief inversion:
The false dogma says... TurboFit buries that dogma. It audits PolyStrata, SALT-core, TurboHaul Manager...
```
The output leaked prompt directives, used middle-school essay openers, dumped unformatted alphabet-soup identifiers, and produced dense, unreadable walls of text.

Furthermore, external repositories had no frictionless way to "point to PRD-agent" and receive an immediate, turnkey manifesto without knowing internal CLI flags.

---

## 2. The Consolidated Architecture

We consolidate the fragmented routes into a single **Unified Narrative Protocol** based on two orthogonal components:

```
┌─────────────────────────────────────────────────────────────┐
│                    THE TENSION SPINE                        │
│                                                             │
│   1. False Dogma / Cultural Enemy                           │
│      (The cynical shortcut the industry settled for)        │
│                    │                                        │
│                    ▼                                        │
│   2. The Visceral Nightmare                                 │
│      (The 2:00 AM human pain of living under that enemy)    │
│                    │                                        │
│                    ▼                                        │
│   3. The Rebellion Truth / Flying Car                       │
│      (The sovereign reality where the builder has command)  │
│                    │                                        │
│                    ▼                                        │
│   4. The Weaponized Mechanism                               │
│      (How verified code claims mathematically guarantee it) │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │ (driven at chosen intensity)
┌────────────────────────────┴────────────────────────────────┐
│                    MANIFESTO VOICE                          │
│                                                             │
│   - electric  (formerly 1000 / solopreneur):                │
│     Supersonic leverage, solo unicorn, 100x velocity.       │
│   - venture   (formerly 750 / enterprise):                  │
│     Category creation, market shift, operational liability. │
│   - technical (formerly 500 / 250):                         │
│     Verifiable receipts, empirical truth, zero buzzwords.   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Dual-Format Deliverables

Every automated execution produces two synchronous formats:

### Format A: The 5-Line Executive Manifesto (`five_lines`)
A high-voltage, 5-sentence battle cry optimized for README intros, social hooks, and executive summaries:
1. **The Callout:** Attack the status quo / false dogma with vivid imagery.
2. **The Truth:** Assert the sovereign reality.
3. **The Weapon:** Introduce the product mechanism as an impenetrable shield.
4. **The Superpower:** State the empirical transformation (speed, leverage, independence).
5. **The Battle Cry:** Direct call to action.

### Format B: The 5-Beat Full Narrative (`stories/<name>.md`)
The complete, beautifully formatted long-form manifesto:
- `# [Magnetic Hero Headline]`
- `**[Subheadline]**`
- `## 1. The Token Tollbooth (The Status Quo)`
- `## 2. The 2:00 AM Nightmare (The Human Breaking Point)`
- `## 3. The Sovereign Reality (The Flying Car)`
- `## 4. The Machine Under the Hood (Weaponized Mechanisms)`
- `## 5. Take the Wheel (Immediate CTA)`

---

## 4. Universal Turnkey Ingestion: "Point Any Repo to PRD-agent"

To enable any repository or agent to point to PRD-agent and immediately succeed:

### 1. Terminal / Workstation Turnkey
```bash
python -m prd_agent <path-or-repo> --readme
```
- Automatically discovers keys and proxies.
- Executes intake -> trends -> positioning -> story -> pack.
- **Stdout Streaming:** Automatically prints the 5-Line Executive Hook directly to terminal stdout upon completion, while writing the full story to `<path>/README.md` and pack to `runs/<name>/pack/`.

### 2. Blind Chat Agent Turnkey (`PROMPT.md`)
A standalone root file [`PROMPT.md`](file:///d:/development/PRD-agent/PROMPT.md) in the PRD-agent repository provides the exact inoculation instructions for chat agents (e.g. Claude Projects, Custom GPTs). It enforces the 5 Hard Bans:
- **Ban 1:** Never print meta-labels (`Level 1000`, `belief inversion`).
- **Ban 2:** Never write template starters (`The false dogma says...`).
- **Ban 3:** Never dump raw alphabet-soup identifiers without translating to human superpowers.
- **Ban 4:** Never write monolithic paragraphs (max 3 sentences per paragraph).
- **Ban 5:** Zero em-dashes (`—`, `–`, `--`).

---

## 5. BDD Behavioral Scenarios

### Scenario 1: Consolidated Pipeline Execution
- **Given:** A technical repository artifact (e.g. `turbofit` or `artifact-mini`).
- **When:** `prd_agent.run(...)` is invoked.
- **Then:** The resulting `story` contains a clean 5-Beat Manifesto and a 5-Line Executive Hook, with zero meta-labels and zero raw alphabet-soup dumps.

### Scenario 2: Terminal Output Visibility
- **Given:** A blind agent invoking `python -m prd_agent <path>`.
- **When:** The run completes.
- **Then:** Stdout displays the 5-Line Executive Manifesto enclosed in an ASCII banner before exiting with code 0.

### Scenario 3: Backwards Compatibility
- **Given:** Legacy flags `--hype 1000` or `--persona solopreneur`.
- **When:** Passed to the CLI or pipeline.
- **Then:** They automatically map to the consolidated `ManifestoVoice.ELECTRIC` without error.

---

## 6. Hidden Holdout Verification

A hidden holdout test on `D:\development\turbofit`:
- The consolidated engine runs against `turbofit`.
- Evaluates that output contains:
  1. Zero em-dashes (`assert_no_em_dashes`).
  2. Zero meta-labels (`"Level 1000"` not in story, `"belief inversion"` not in story).
  3. Zero template openers (`"The false dogma says"` not in story).
  4. Proper conversion of technical quants (`Qwen 3.8 27B`, `Maple Preview`) into weaponized human superpowers.
