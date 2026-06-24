# Agent Platform Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the existing RPA requirements analyst modules into files that an Agent platform can consume through Git Skill download, local RAG upload, and system prompt configuration.

**Architecture:** Keep executable workflow rules in a root `SKILL.md` that points to existing `agent_modules/` contracts. Add a dedicated `agent_platform_package/` folder for RAG upload files, system prompt text, and integration guidance. Avoid changing module 1 and module 2 behavior.

**Tech Stack:** Markdown, JSON, existing Python unittest contracts, Git.

## Global Constraints

- Do not change module 1 or module 2 runtime contracts unless a packaging test exposes a broken reference.
- Git Skill content must tell the Agent how to use existing `agent_modules/` files.
- RAG files must contain knowledge and examples, not workflow control logic.
- System prompt must contain top-level behavior constraints, not full schemas.
- Keep Chinese user-facing content readable in UTF-8.
- Keep `.superpowers/sdd/` scratch files ignored.

---

### Task 1: Add Git Skill Entry

**Files:**
- Create: `SKILL.md`
- Create: `agent_platform_package/skill/README.md`

**Interfaces:**
- Consumes: existing `agent_modules/interaction_schema/` and `agent_modules/requirement_clarification/`
- Produces: a Git-downloadable Skill entry that tells the Agent which module references to load and how to proceed.

- [ ] **Step 1: Create root Skill file**

Create `SKILL.md` with frontmatter:

```yaml
---
name: rpa-requirements-analyst
description: Use when helping customers clarify vague RPA automation needs into analyzable requirements through choice-first questioning, interaction-state tracking, RPA-fit pre-screening, negative example checks, gap reports, and handoff to later requirement modules.
---
```

Then add concise instructions:

```markdown
# RPA Requirements Analyst

Use this skill to turn a vague customer automation request into a structured, analyzable RPA requirement.

## Load Order

1. Read `agent_modules/interaction_schema/README.md`.
2. Read `agent_modules/interaction_schema/rules/prompt-rules.md`.
3. Read `agent_modules/interaction_schema/rules/decision-rules.json`.
4. Read `agent_modules/requirement_clarification/README.md`.
5. Read `agent_modules/requirement_clarification/rules/prompt-rules.md`.
6. Read `agent_modules/requirement_clarification/rules/completion-rules.json`.
7. Read `agent_modules/requirement_clarification/rules/trigger-policy.json`.
8. Read `agent_modules/requirement_clarification/materials/negative-examples.v1.json` only when RPA-fit risk signals appear or when fixed pre-screening needs examples.

## Operating Rules

- Start in module 1 by creating or updating `interaction_state`.
- Ask choice-first questions. Every question should allow `unknown` and `other` when appropriate.
- Record every user response as an `answer_batch`.
- Absorb supplemental free text into state before asking another question.
- Skip repeated questions when existing answers already cover them with high confidence.
- Convert medium-confidence inferences into confirmation questions.
- Enter module 2 after the basic interaction state can proceed to clarification.
- In module 2, collect boundary facts before execution details.
- Use `clarification_depth = "boundary_only"`.
- Do not decide final RPA feasibility in module 2.
- Do not ask exact click paths, selectors, wait times, or exception branch details in module 2.
- Never conclude risk from the customer's first sentence alone.
- Treat weak risk signals as candidates that require follow-up confirmation.
- Use `stop_with_gap_report` when required boundary facts remain too incomplete.
- Use `stop_with_blocker` when prework such as naming standardization or rule definition is needed.
- Use `rpa_boundary_check` only when the module 2 summary is ready for the next module.

## Output

Maintain these structured outputs:

- `interaction_state`
- `answer_batch`
- `clarification_result`
```

- [ ] **Step 2: Create skill package README**

Create `agent_platform_package/skill/README.md`:

```markdown
# Git Skill Package

Use the repository root as the Git Skill source because `SKILL.md` lives at the root and references `agent_modules/`.

The Agent platform should download this repository as a skill. The skill will use:

- `SKILL.md`
- `agent_modules/interaction_schema/`
- `agent_modules/requirement_clarification/`
```

- [ ] **Step 3: Verify references**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts -v
python -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: both suites pass.

- [ ] **Step 4: Commit**

Run:

```powershell
git add SKILL.md agent_platform_package/skill/README.md docs/superpowers/plans/2026-06-24-agent-platform-package.md
git commit -m "feat: add agent platform skill entry"
```

### Task 2: Add RAG Upload Materials

**Files:**
- Create: `agent_platform_package/rag_upload/01_training_summary.md`
- Create: `agent_platform_package/rag_upload/02_rpa_boundary_knowledge.md`
- Create: `agent_platform_package/rag_upload/03_negative_examples.md`
- Create: `agent_platform_package/rag_upload/04_logistics_interception_case.md`
- Create: `agent_platform_package/rag_upload/05_requirement_template_fields.md`

**Interfaces:**
- Consumes: existing module rules, negative examples, and prior training-document summaries.
- Produces: local Markdown files suitable for RAG upload.

- [ ] **Step 1: Create RAG files**

Create five Markdown files with these responsibilities:

- `01_training_summary.md`: demand analysis method, start/end/input/system/output framing.
- `02_rpa_boundary_knowledge.md`: what RPA is good at and where prework is needed.
- `03_negative_examples.md`: explain the eight negative examples in readable Chinese.
- `04_logistics_interception_case.md`: logistics interception example as a positive module 2 case.
- `05_requirement_template_fields.md`: explain requirement document fields and how they relate to Agent output.

- [ ] **Step 2: Verify RAG files are knowledge-only**

Run:

```powershell
rg "must output|next_action|state_patch|json schema" agent_platform_package/rag_upload
```

Expected: no workflow-control leakage except explanatory references.

- [ ] **Step 3: Commit**

Run:

```powershell
git add agent_platform_package/rag_upload
git commit -m "docs: add RAG upload materials"
```

### Task 3: Add System Prompt And Integration Guide

**Files:**
- Create: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Create: `agent_platform_package/integration_guide.md`

**Interfaces:**
- Consumes: Skill and RAG package files.
- Produces: copy-pasteable system prompt and platform setup instructions.

- [ ] **Step 1: Create system prompt**

Create a concise Chinese system prompt with:

- Agent role as RPA requirements analyst.
- Choice-first interaction.
- Every question keeps an open supplement option.
- No final feasibility decision in module 2.
- No risk conclusion from first sentence.
- Stop behavior for gaps and blockers.
- Handoff to `rpa_boundary_check` after module 2 readiness.

- [ ] **Step 2: Create integration guide**

Create an integration guide with:

- Git Skill source: repository URL.
- Skill files used by the platform.
- RAG upload file list and purpose.
- System prompt copy location.
- Recommended first test scenario.
- Expected module 2 outputs.

- [ ] **Step 3: Verify full package**

Run:

```powershell
rg --files agent_platform_package
python -m unittest tests.test_interaction_schema_contracts -v
python -m unittest tests.test_requirement_clarification_contracts -v
git status --short
```

Expected: package files exist, both suites pass, status only shows Task 3 files before commit.

- [ ] **Step 4: Commit**

Run:

```powershell
git add agent_platform_package/system_prompt/agent-system-prompt.md agent_platform_package/integration_guide.md
git commit -m "docs: add agent platform integration guide"
```

## Self-Review

- Skill entry covers Git skill download and existing module references.
- RAG files are separated from control logic.
- System prompt is concise and platform-friendly.
- Integration guide tells the user where to upload or paste every artifact.
