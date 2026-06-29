# RAG Material Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the uploadable RAG package with Chinese, business-friendly materials that support Yingdao capability recommendations, online spreadsheet handling, report collection scenarios, branch/exception confirmation, and HTML report quality.

**Architecture:** Add focused Markdown RAG files under `agent_platform_package/rag_upload`, each with one responsibility and Chinese-first wording. Update platform-facing documentation so users know which files to upload and how the new materials should be used. Keep machine-facing JSON/schema identifiers unchanged elsewhere.

**Tech Stack:** Markdown documentation, Git, Python unittest contract tests, ripgrep readability scans.

## Global Constraints

- 后续所有材料以中文为准。
- 面向客户和业务实施人员的材料降低英文、IT 技术名词和机器字段暴露。
- RAG 材料必须区分客户已确认、RAG 支撑、Agent 推断待确认。
- 影刀指令推荐只表达“可参考能力/指令方向”，不生成精确点击路径、选择器、等待时间或指令参数。
- HTML 展示层必须中文优先，英文枚举只保留在结构化 JSON 或必要的机器合同中。
- 不直接上传原始 Excel；先抽取为可读、可检索、可人工审查的中文 RAG。

---

### Task 1: Add Yingdao Common Capability Cards

**Files:**
- Create: `agent_platform_package/rag_upload/06_yingdao_common_capability_cards.md`

**Interfaces:**
- Consumes: Existing source ideas from Yingdao instruction libraries and the RAG review document.
- Produces: Reusable Chinese capability cards for Module 3, Module 4, Module 5, and Module 6.

- [ ] **Step 1: Create the capability card RAG file**

Add cards for opening webpages, waiting for elements, clicking, filling, reading page text, table reading/writing, loops, condition judgment, notification, logging, and screenshots.

- [ ] **Step 2: Verify readability**

Run: `python -c "from pathlib import Path; s=Path('agent_platform_package/rag_upload/06_yingdao_common_capability_cards.md').read_text(encoding='utf-8'); bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in s for x in bad)"`

Expected: no output.

### Task 2: Add Online Spreadsheet Capability RAG

**Files:**
- Create: `agent_platform_package/rag_upload/07_online_spreadsheet_capabilities.md`

**Interfaces:**
- Consumes: User feedback that Tencent Docs can be opened, read by row/column, and written to specified row/column.
- Produces: Special-purpose online spreadsheet guidance for report generation and implementation alignment.

- [ ] **Step 1: Create the online spreadsheet RAG file**

Include Tencent Docs/online spreadsheet opening, Sheet positioning, row/column/cell reading, row/column/cell writing, write verification, permissions, login, template changes, and required customer confirmations.

- [ ] **Step 2: Verify readability**

Run: `python -c "from pathlib import Path; s=Path('agent_platform_package/rag_upload/07_online_spreadsheet_capabilities.md').read_text(encoding='utf-8'); bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in s for x in bad)"`

Expected: no output.

### Task 3: Add Report Collection Scenario RAG

**Files:**
- Create: `agent_platform_package/rag_upload/08_report_collection_and_daily_report_scenario.md`

**Interfaces:**
- Consumes: Existing ecommerce report test case as an example, generalized into report collection and daily report generation.
- Produces: Scenario-level guidance for Module 4 flow cards and Module 6 reports.

- [ ] **Step 1: Create the scenario RAG file**

Cover report source list, login, date scope, metric reading, aggregation, target report writing, validation, notification, and example branch rules.

- [ ] **Step 2: Verify readability**

Run: `python -c "from pathlib import Path; s=Path('agent_platform_package/rag_upload/08_report_collection_and_daily_report_scenario.md').read_text(encoding='utf-8'); bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in s for x in bad)"`

Expected: no output.

### Task 4: Add Branch and Exception Confirmation Rules

**Files:**
- Create: `agent_platform_package/rag_upload/09_branch_exception_confirmation_rules.md`

**Interfaces:**
- Consumes: User feedback that exceptions must not look self-invented without customer confirmation.
- Produces: Source-level labels for customer confirmed, RAG suggested, and Agent inferred exceptions.

- [ ] **Step 1: Create the confirmation rules RAG file**

Define which branches can be suggested by default and which must be customer-confirmed before being written as a decision.

- [ ] **Step 2: Verify readability**

Run: `python -c "from pathlib import Path; s=Path('agent_platform_package/rag_upload/09_branch_exception_confirmation_rules.md').read_text(encoding='utf-8'); bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in s for x in bad)"`

Expected: no output.

### Task 5: Add HTML Chinese Display Dictionary

**Files:**
- Create: `agent_platform_package/rag_upload/10_html_display_dictionary.md`

**Interfaces:**
- Consumes: User preference that developer-facing HTML should be all Chinese and business-friendly.
- Produces: Display wording for customer and implementation reports.

- [ ] **Step 1: Create the display dictionary RAG file**

Map internal status, module names, field groups, evidence labels, and implementation readiness language to Chinese.

- [ ] **Step 2: Verify readability**

Run: `python -c "from pathlib import Path; s=Path('agent_platform_package/rag_upload/10_html_display_dictionary.md').read_text(encoding='utf-8'); bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in s for x in bad)"`

Expected: no output.

### Task 6: Add Report Quality Rules

**Files:**
- Create: `agent_platform_package/rag_upload/11_report_quality_rules.md`

**Interfaces:**
- Consumes: User expectation that time spent in Q&A must be reflected in valuable reports.
- Produces: Quality rules for report depth, traceability, RAG usage, and fact separation.

- [ ] **Step 1: Create the report quality RAG file**

Define mandatory report sections, fact/source labels, process card depth, capability display, and prohibited over-certainty.

- [ ] **Step 2: Verify readability**

Run: `python -c "from pathlib import Path; s=Path('agent_platform_package/rag_upload/11_report_quality_rules.md').read_text(encoding='utf-8'); bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in s for x in bad)"`

Expected: no output.

### Task 7: Update Platform Package Documentation

**Files:**
- Modify: `agent_platform_package/integration_guide.md`
- Modify: `agent_platform_package/testing/platform_test_checklist.md`
- Modify: `docs/rag-material-review-v1.md`

**Interfaces:**
- Consumes: New RAG file list from Tasks 1-6.
- Produces: Updated upload instructions and review status.

- [ ] **Step 1: Update integration guide RAG list**

Add files `06` through `11` to the local upload instructions.

- [ ] **Step 2: Update platform checklist**

Add checks that HTML reports use Chinese display terms, show recommended Yingdao capabilities, and mark inferred exceptions as pending confirmation.

- [ ] **Step 3: Update review document status**

Mark the six proposed RAG files as implemented in the review document.

### Task 8: Validate and Commit

**Files:**
- Test all modified docs and existing contracts.

**Interfaces:**
- Consumes: All new and modified RAG/package docs.
- Produces: Verified branch ready for push.

- [ ] **Step 1: Run readability scan**

Run: `python -c "from pathlib import Path; files=list(Path('agent_platform_package/rag_upload').glob('*.md'))+[Path('agent_platform_package/integration_guide.md'),Path('agent_platform_package/testing/platform_test_checklist.md'),Path('docs/rag-material-review-v1.md')]; bad=['PLACEHOLDER_MARKER','BROKEN_ENCODING_MARKER']; assert not any(x in p.read_text(encoding='utf-8') for p in files for x in bad)"`

Expected: no output.

- [ ] **Step 2: Run contract tests**

Run: `python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts tests.test_exception_design_contracts tests.test_solution_packaging_contracts -v`

Expected: all tests pass.

- [ ] **Step 3: Commit and push**

Run:

```bash
git add agent_platform_package/rag_upload docs/rag-material-review-v1.md agent_platform_package/integration_guide.md agent_platform_package/testing/platform_test_checklist.md docs/superpowers/plans/2026-06-29-rag-material-expansion.md
git commit -m "docs: expand chinese rag material package"
git push origin master
```
