# Memory Driven Agent Stability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace brittle context-dependent module handoff with a memory-driven fact ledger, gate-based module flow, stable question typing, and stable unified report structure.

**Architecture:** Add a global requirement memory layer consumed by all modules. Modules read and update fact IDs, gap IDs, inference IDs, and gate states instead of relying on perfect upstream JSON. Existing module schemas remain, but flow control is driven by memory gate rules and report generation references memory facts.

**Tech Stack:** Markdown templates, JSON schemas and rules, Python `unittest`, existing `agent_modules` and `agent_platform_package` structure.

## Global Constraints

- Output quality is more important than minimizing changed files.
- Do not rely on the model always producing perfect module JSON.
- The requirement memory is the current demand's source of truth; RAG remains general knowledge only.
- Final reports must not label inferred content as customer-confirmed.
- Question type selection must support multiple-choice with free-text supplementation.
- Reports must use a stable unified Chinese structure across scenarios.

---

### Task 1: Requirement Memory Contract

**Files:**
- Create: `agent_modules/requirement_memory/README.md`
- Create: `agent_modules/requirement_memory/schemas/requirement-memory.schema.json`
- Create: `agent_modules/requirement_memory/rules/update-rules.json`
- Create: `agent_modules/requirement_memory/rules/prompt-rules.md`
- Create: `agent_modules/requirement_memory/templates/requirement_memory_template.md`
- Create: `agent_modules/requirement_memory/fixtures/ecommerce-memory.md`
- Modify: `SKILL.md`
- Test: `tests/test_requirement_memory_contracts.py`

**Interfaces:**
- Consumes: user answers, module outputs, RAG-backed recommendations.
- Produces: fact IDs `Fxxx`, inference IDs `Ixxx`, gap IDs `Gxxx`, conflict IDs `Cxxx`, retired IDs `Rxxx`, decision IDs `Dxxx`, and module gate states.

- [ ] **Step 1: Add failing tests for memory contract**

Create `tests/test_requirement_memory_contracts.py` with tests asserting the schema has sections for current stage, confirmed facts, inferred items, gaps, conflicts, retired questions, decisions, and gate states.

- [ ] **Step 2: Run failing memory tests**

Run: `python -m unittest tests.test_requirement_memory_contracts -v`

Expected: FAIL because memory module files do not exist.

- [ ] **Step 3: Add memory schema and template**

Create a schema that allows a Markdown-backed memory representation and defines required IDs, source labels, confidence labels, and development usability flags.

- [ ] **Step 4: Add memory update rules**

Rules must state: confirmed facts require explicit customer or upstream source, inferred items cannot be used for development, gaps must track blocking stage, conflicts must retire or supersede old facts, and every round starts by reading memory.

- [ ] **Step 5: Register module in root Skill**

Update `SKILL.md` load order so requirement memory is loaded before modules 2 to 6.

- [ ] **Step 6: Run memory tests**

Run: `python -m unittest tests.test_requirement_memory_contracts -v`

Expected: PASS.

### Task 2: Gate-Based Module Flow

**Files:**
- Create: `agent_modules/requirement_memory/rules/gate-rules.json`
- Modify: `agent_modules/requirement_clarification/rules/completion-rules.json`
- Modify: `agent_modules/rpa_boundary_check/rules/decision-rules.json`
- Modify: `agent_modules/process_breakdown/rules/breakdown-rules.json`
- Modify: `agent_modules/exception_design/rules/exception-rules.json`
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Test: `tests/test_requirement_memory_contracts.py`
- Test: `tests/test_requirement_clarification_contracts.py`
- Test: `tests/test_rpa_boundary_check_contracts.py`
- Test: `tests/test_process_breakdown_contracts.py`
- Test: `tests/test_exception_design_contracts.py`

**Interfaces:**
- Consumes: requirement memory facts and gaps.
- Produces: `ready`, `partial_ready`, or `blocked` gate states for module transitions.

- [ ] **Step 1: Add failing tests for gate rules**

Assert module 2 to 3, 3 to 4, 4 to 5, and 5 to 6 gates are defined with minimum facts and allowed carry-forward gaps.

- [ ] **Step 2: Run targeted tests**

Run: `python -m unittest tests.test_requirement_memory_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts tests.test_exception_design_contracts -v`

Expected: FAIL on missing gate contracts.

- [ ] **Step 3: Implement gate rules**

Define minimum facts for each transition, optional facts, allowed carry-forward gaps, and hard blockers.

- [ ] **Step 4: Update module rules to consume gates**

Each module rule file must say that module flow is decided by memory gate state, not by perfect upstream JSON shape.

- [ ] **Step 5: Update system prompt**

Add a Chinese-first rule: every turn reads memory, updates memory, then decides gate state.

- [ ] **Step 6: Run targeted tests**

Expected: PASS.

### Task 3: Stable Question Type Policy

**Files:**
- Modify: `agent_modules/interaction_schema/rules/decision-rules.json`
- Modify: `agent_modules/interaction_schema/rules/prompt-rules.md`
- Modify: `agent_modules/interaction_schema/schemas/question.schema.json`
- Create: `agent_modules/interaction_schema/fixtures/multiple-choice-with-text-required.json`
- Test: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: memory gaps and current module question plan.
- Produces: stable `single_choice_with_text` or `multiple_choice_with_text` questions.

- [ ] **Step 1: Add failing tests for multi-choice triggers**

Assert platform, data source, output field, exception handling, notification method, human fallback, and captcha handling questions require `multiple_choice_with_text`.

- [ ] **Step 2: Run interaction tests**

Run: `python -m unittest tests.test_interaction_schema_contracts -v`

Expected: FAIL.

- [ ] **Step 3: Update question policy**

Add rules: mutually exclusive questions use single choice with text; coexisting facts use multiple choice with text; every question includes an other/free-text path.

- [ ] **Step 4: Add fixture**

Create a representative multi-choice-with-text fixture for operated systems or exception handling.

- [ ] **Step 5: Run interaction tests**

Expected: PASS.

### Task 4: Stable Unified Report Template

**Files:**
- Modify: `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`
- Modify: `agent_modules/solution_packaging/rules/packaging-rules.json`
- Modify: `agent_modules/solution_packaging/rules/prompt-rules.md`
- Modify: `agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json`
- Create: `agent_modules/solution_packaging/fixtures/inventory-monitor-solution-package.json`
- Modify: `agent_platform_package/testing/expected_outputs.md`
- Test: `tests/test_solution_packaging_contracts.py`

**Interfaces:**
- Consumes: requirement memory fact IDs, module outputs, RAG capability cards.
- Produces: stable report sections and traceable HTML content.

- [ ] **Step 1: Add failing tests for fixed report sections**

Assert every fixture includes the 10 fixed report sections: overall conclusion, requirement understanding, RPA fit, scope, process with candidate capabilities, exceptions with source labels, fact layering, prework gaps, PoC/next steps, and Chinese development JSON summary.

- [ ] **Step 2: Run solution packaging tests**

Run: `python -m unittest tests.test_solution_packaging_contracts -v`

Expected: FAIL.

- [ ] **Step 3: Update schema and packaging rules**

Require `unified_view_model.fixed_sections`, `source_labels`, and `development_json_summary`.

- [ ] **Step 4: Update fixtures**

Update ecommerce fixture and add inventory monitor fixture as a second scenario baseline.

- [ ] **Step 5: Run solution packaging tests**

Expected: PASS.

### Task 5: End-to-End Stability Regression Suite

**Files:**
- Create: `agent_platform_package/testing/stability_regression_scenarios.md`
- Create: `tests/test_stability_regression_contracts.py`
- Modify: `agent_platform_package/testing/platform_test_checklist.md`

**Interfaces:**
- Consumes: memory, gates, question policy, report schema.
- Produces: cross-scenario stability checks.

- [ ] **Step 1: Add failing stability tests**

Tests should assert scenario names and expected stable artifacts exist for: ecommerce daily report, inventory monitor, email sorting, logistics interception, material synonym judgment, and captcha-heavy platform collection.

- [ ] **Step 2: Run stability tests**

Run: `python -m unittest tests.test_stability_regression_contracts -v`

Expected: FAIL.

- [ ] **Step 3: Add stability scenario doc**

Document expected question behavior, memory updates, gate state, RPA boundary, report sections, and source-label expectations for each scenario.

- [ ] **Step 4: Update platform checklist**

Add deployment acceptance checks for memory-driven flow and output consistency.

- [ ] **Step 5: Run stability tests**

Expected: PASS.

### Task 6: Full Verification And Push

**Files:**
- Test: `tests/*.py`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: pushed implementation branch.

- [ ] **Step 1: Run full tests**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 2: Run text quality scan**

Run: `rg -n "TODO|TBD|�|UNSOURCED_FACT" agent_modules agent_platform_package docs tests SKILL.md`

Expected: no placeholders or unsourced markers in deliverables.

- [ ] **Step 3: Check diff**

Run: `git diff --check` and `git diff --stat`

Expected: no whitespace errors.

- [ ] **Step 4: Commit and push**

Run:

```powershell
git add SKILL.md agent_modules agent_platform_package docs tests
git commit -m "feat: add memory driven agent stability"
git push origin codex/continuous-rpa-agent-upgrade
```

Expected: branch pushed.

## Self-Review

- Spec coverage: tasks cover memory, gates, question typing, report structure, regression tests, and verification.
- Placeholder scan: no implementation placeholder is left for task content.
- Type consistency: IDs consistently use `F/I/G/C/R/D` prefixes and gate states use `ready`, `partial_ready`, `blocked`.
