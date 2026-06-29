# Continuous RPA Agent Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the RPA requirements agent so it supports captcha-aware capability boundaries, module-level questioning, automatic module transitions, and a unified Chinese landing report.

**Architecture:** The project is a document-and-contract package. The implementation updates RAG Markdown files, module rules, JSON schemas, fixtures, platform prompts, and Python contract tests together so the agent platform can ingest the updated behavior safely.

**Tech Stack:** Markdown RAG materials, JSON rules and schemas, Python `unittest`, PowerShell commands.

## Global Constraints

- Keep all user-facing materials Chinese-first.
- Do not modify the existing untracked `agent_modules.zip`.
- Preserve backward compatibility where practical, especially for platform package consumers.
- Do not treat captcha as an automatic RPA blocker.
- Module transitions should be automatic when the current module has enough facts to enter the next module.
- Module 6 default deliverable is one unified HTML report plus one structured fact source.

---

### Task 1: Add Captcha Capability RAG

**Files:**
- Create: `agent_platform_package/rag_upload/12_captcha_capability_boundary.md`
- Modify: `agent_platform_package/integration_guide.md`
- Modify: `docs/rag-material-review-v1.md`
- Modify: `agent_modules/rpa_boundary_check/materials/source-material-manifest.json`
- Modify: `agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json`
- Test: `tests/test_platform_package_contracts.py`

**Interfaces:**
- Consumes: captcha workbook facts from `C:/Users/司南/Downloads/验证码问题及对应指令汇总表.xlsx`
- Produces: RAG file `12_captcha_capability_boundary.md` and retrieval policy entries for module 3

- [ ] **Step 1: Add failing tests for captcha RAG registration**

Add assertions in `tests/test_platform_package_contracts.py` that the RAG upload list includes `12_captcha_capability_boundary.md`, and that the file text contains `验证码不是天然不可做`, `适配指令`, `费用`, `准确率`, `人工兜底`.

- [ ] **Step 2: Run the targeted test and verify failure**

Run: `python -m unittest tests.test_platform_package_contracts -v`

Expected: FAIL because the new RAG file and references do not exist yet.

- [ ] **Step 3: Create the captcha RAG file**

Create `agent_platform_package/rag_upload/12_captcha_capability_boundary.md` with sections for decision principles, captcha type inventory, supported instruction examples, unsupported or uncertain types, required questions, and output wording.

- [ ] **Step 4: Register the RAG in platform and module material manifests**

Update the integration guide, material review doc, source manifest, and retrieval policy so module 3 retrieves captcha material before making a human verification conclusion.

- [ ] **Step 5: Run the targeted test and verify pass**

Run: `python -m unittest tests.test_platform_package_contracts -v`

Expected: PASS.

### Task 2: Upgrade Module 3 RPA Boundary Rules

**Files:**
- Modify: `agent_modules/rpa_boundary_check/rules/decision-rules.json`
- Modify: `agent_modules/rpa_boundary_check/rules/prompt-rules.md`
- Modify: `agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json`
- Modify: `agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json`
- Modify: `agent_modules/rpa_boundary_check/fixtures/ecommerce-daily-report-boundary-result.json`
- Test: `tests/test_rpa_boundary_check_contracts.py`

**Interfaces:**
- Consumes: `12_captcha_capability_boundary.md`
- Produces: captcha-aware `capability_notes`, risk notes, and recommended questions

- [ ] **Step 1: Add failing tests for captcha boundary behavior**

Add assertions that module 3 rules contain `captcha_assessment`, do not classify captcha as an automatic blocker, and that schema enum supports `requires_captcha_type_confirmation`, `requires_captcha_instruction_validation`, `requires_paid_captcha_approval`, `requires_human_verification_fallback`.

- [ ] **Step 2: Run the targeted test and verify failure**

Run: `python -m unittest tests.test_rpa_boundary_check_contracts -v`

Expected: FAIL on missing captcha contract.

- [ ] **Step 3: Update decision rules and prompt rules**

Change the blocking rule from “frequent human verification is not suitable” to a conditional rule: only unsupported, unapproved, no-fallback, high-frequency verification is a hard blocker. Add questions for captcha type, frequency, payment acceptance, accuracy acceptance, human fallback, and compliance authorization.

- [ ] **Step 4: Update schema and fixtures**

Extend `capability_notes` enum with captcha notes and add representative captcha-aware notes to fixtures where relevant.

- [ ] **Step 5: Run the targeted test and verify pass**

Run: `python -m unittest tests.test_rpa_boundary_check_contracts -v`

Expected: PASS.

### Task 3: Add Continuous Questioning And Automatic Transitions

**Files:**
- Modify: `agent_modules/requirement_clarification/rules/prompt-rules.md`
- Modify: `agent_modules/rpa_boundary_check/rules/prompt-rules.md`
- Modify: `agent_modules/process_breakdown/rules/breakdown-rules.json`
- Modify: `agent_modules/process_breakdown/rules/prompt-rules.md`
- Modify: `agent_modules/exception_design/rules/exception-rules.json`
- Modify: `agent_modules/exception_design/rules/prompt-rules.md`
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Test: `tests/test_requirement_clarification_contracts.py`
- Test: `tests/test_process_breakdown_contracts.py`
- Test: `tests/test_exception_design_contracts.py`

**Interfaces:**
- Consumes: module outputs from previous stages
- Produces: module-specific question policies and `next_module` transition behavior

- [ ] **Step 1: Add failing tests for module-specific questions and auto-transition wording**

Assert that modules 2 to 5 prompt rules contain explicit question triggers and that the system prompt contains automatic transition guidance without requiring the user to type `继续`.

- [ ] **Step 2: Run targeted module tests and verify failure**

Run: `python -m unittest tests.test_requirement_clarification_contracts tests.test_process_breakdown_contracts tests.test_exception_design_contracts -v`

Expected: FAIL on missing new wording.

- [ ] **Step 3: Update module prompt rules**

Module 2 asks only for boundary-ready facts. Module 3 asks for RPA capability facts. Module 4 asks for implementation path, repeated object, branch conditions, field mapping, and instruction candidates. Module 5 asks for exception confirmation and labels inferred exceptions as pending confirmation.

- [ ] **Step 4: Update system prompt**

Add automatic transition rules: when a module is ready, summarize why and immediately enter the next module's questions. Preserve existing machine-readable contract phrases used by tests.

- [ ] **Step 5: Run targeted module tests and verify pass**

Run: `python -m unittest tests.test_requirement_clarification_contracts tests.test_process_breakdown_contracts tests.test_exception_design_contracts -v`

Expected: PASS.

### Task 4: Merge Customer And Developer Report Into Unified Report

**Files:**
- Modify: `agent_modules/solution_packaging/rules/packaging-rules.json`
- Modify: `agent_modules/solution_packaging/rules/prompt-rules.md`
- Modify: `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`
- Modify: `agent_modules/solution_packaging/README.md`
- Modify: `agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json`
- Modify: `agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json`
- Modify: `agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json`
- Modify: `agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json`
- Modify: `agent_platform_package/testing/expected_outputs.md`
- Modify: `agent_platform_package/testing/module_1_to_6_flow_test.md`
- Modify: `agent_platform_package/testing/platform_test_checklist.md`
- Modify: `SKILL.md`
- Test: `tests/test_solution_packaging_contracts.py`

**Interfaces:**
- Consumes: module 2 to 5 structured outputs
- Produces: `unified_view_model`, `render_outputs.unified_html`, and one Chinese report contract

- [ ] **Step 1: Add failing tests for unified report output**

Assert that the solution package schema requires `unified_view_model` and `render_outputs.unified_html`, while legacy customer/developer fields remain optional compatibility fields.

- [ ] **Step 2: Run solution packaging tests and verify failure**

Run: `python -m unittest tests.test_solution_packaging_contracts -v`

Expected: FAIL on missing unified report contract.

- [ ] **Step 3: Update module 6 rules and schema**

Make the default report `RPA 单需求落地分析报告`. Require Chinese sections for customer-readable summary, RPA boundary, main flow, branch flow, exception handling with source labels, instruction recommendations, prework, implementation JSON, and pending confirmations.

- [ ] **Step 4: Update fixtures and platform docs**

Add unified view model and unified HTML metadata to fixtures. Update testing docs and root skill README to describe the unified report.

- [ ] **Step 5: Run solution packaging tests and verify pass**

Run: `python -m unittest tests.test_solution_packaging_contracts -v`

Expected: PASS.

### Task 5: Full Verification And Commit

**Files:**
- Test: `tests/*.py`

**Interfaces:**
- Consumes: all prior tasks
- Produces: committed and pushed upgrade

- [ ] **Step 1: Run the full unit test suite**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 2: Scan for encoding artifacts and placeholders**

Run: `rg -n "TODO|TBD|鐢|寮|鈥|馃|�" agent_modules agent_platform_package docs SKILL.md tests`

Expected: no new placeholder or mojibake in edited materials.

- [ ] **Step 3: Review git diff**

Run: `git diff --stat` and `git diff --check`

Expected: no whitespace errors, changes limited to planned files.

- [ ] **Step 4: Commit and push**

Run:

```powershell
git add agent_modules agent_platform_package docs SKILL.md tests
git commit -m "feat: upgrade continuous rpa agent flow"
git push origin master
```

Expected: branch pushed to GitHub.

## Self-Review

- Spec coverage: all design requirements map to Tasks 1 to 4.
- Placeholder scan: this plan intentionally contains no TBD/TODO wording.
- Type consistency: new output names are consistently `unified_view_model` and `render_outputs.unified_html`.
