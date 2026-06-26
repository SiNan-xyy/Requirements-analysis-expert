# Platform Flow Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the platform-facing testing materials readable and add an explicit module 1 to module 4 flow test guide so the existing agent package is easier to validate on the target platform.

**Architecture:** Keep the module contracts unchanged. This plan only hardens platform-facing testing documentation and adds contract tests that verify readability and the handoff chain across modules 1-4.

**Tech Stack:** Markdown documentation, JSON fixtures, Python `unittest`, PowerShell commands.

## Global Constraints

- Do not change module 1-4 business behavior or schemas unless a test proves the flow contract is broken.
- Keep platform-facing Chinese text readable UTF-8.
- Keep exactly one top-level JSON wrapper guidance for platform outputs.
- Module 4 remains business-process-card level; do not introduce selectors, click paths, wait times, retries, or exact Yingdao command parameters.
- Preserve required/recommended/optional classification language.
- Preserve the module flow: interaction schema -> requirement clarification -> RPA boundary check -> process breakdown -> exception design.

---

## File Structure

- `agent_platform_package/testing/expected_outputs.md`: replace damaged historical examples with readable platform acceptance examples for modules 1-4.
- `agent_platform_package/testing/platform_test_checklist.md`: replace damaged checklist text with readable platform loading, interaction, output, and readability checks.
- `agent_platform_package/testing/module_1_to_4_flow_test.md`: create a readable guide for manually validating the end-to-end module flow.
- `tests/test_platform_package_contracts.py`: create platform-package contract tests for document readability and flow-guide content.

---

### Task 1: Platform Testing Document Readability

**Files:**
- Modify: `agent_platform_package/testing/expected_outputs.md`
- Modify: `agent_platform_package/testing/platform_test_checklist.md`
- Create: `tests/test_platform_package_contracts.py`

**Interfaces:**
- Consumes: existing module contracts and platform wrapper rules.
- Produces: readable platform testing docs and tests that prevent common mojibake fragments from returning.

- [ ] **Step 1: Write the failing readability test**

Add `tests/test_platform_package_contracts.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PLATFORM_DOCS = [
    "agent_platform_package/testing/expected_outputs.md",
    "agent_platform_package/testing/platform_test_checklist.md",
]

COMMON_MOJIBAKE_FRAGMENTS = (
    "骞冲",
    "娴嬭",
    "鑷",
    "鐗",
    "鍏堢",
    "椋炰功",
    "閭",
    "閼",
    "閻",
    "妞",
    "瀹",
    "鍙ｅ緞",
)


class PlatformPackageContractTests(unittest.TestCase):
    def test_platform_testing_docs_are_readable(self):
        for relative_path in PLATFORM_DOCS:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                self.assertIn("JSON", text)
                self.assertIn("interaction_state", text)
                self.assertIn("clarification_result", text)
                self.assertIn("rpa_boundary_result", text)
                self.assertIn("process_breakdown_result", text)
                for fragment in COMMON_MOJIBAKE_FRAGMENTS:
                    self.assertNotIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new test and confirm it fails**

Run:

```powershell
python -m unittest tests.test_platform_package_contracts -v
```

Expected: FAIL because the current platform docs contain mojibake fragments.

- [ ] **Step 3: Rewrite `expected_outputs.md` as readable platform guidance**

Replace the file with a readable structure:

```markdown
# 平台测试期望输出

## 通用结构化输出外壳

合格输出必须是一个顶层 JSON 对象。Agent 可以根据当前阶段按需包含以下对象，但不得连续输出多个相邻 JSON：

- `interaction_state`
- `answer_batch`
- `clarification_result`
- `rpa_boundary_result`
- `process_breakdown_result`

## Module 1 Expected Output

模块 1 负责记录选择题答案、自由补充、状态补丁和下一步动作。

必须使用：

- `answer_batch.answer_records`
- `answer_batch.state_patch`
- `answer_batch.impact`
- `interaction_state.next_action`

不得使用自由字段替代标准字段，例如 `answers`、`topic`、`field`。

## Module 2 Expected Output

模块 2 输出 `clarification_result`，只做边界澄清和 RPA 预筛，不做最终可行性结论。

必须包含：

- `clarification_depth`
- `boundary_facts`
- `rpa_fit_prescreen`
- `pending_questions`
- `stage_summary`
- `next_stage_recommendation`

`boundary_facts` 必须覆盖业务目标、触发条件、完成条件、输入数据、操作系统、输出结果。

## Module 3 Expected Output

模块 3 输出 `rpa_boundary_result`，判断是否适合进入流程拆解。

`decision.classification` 只能是：

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

判断必须同时参考输入准备度、规则准备度、平台可操作性、结果可验证性和异常可收敛性。

## Module 4 Expected Output

模块 4 输出 `process_breakdown_result`。

`process_breakdown_result.breakdown_depth` 必须是：

- `business_process_cards_with_candidate_capabilities`

每张流程卡片描述业务阶段和候选影刀能力族，不得包含选择器、精确点击路径、等待时间、重试次数或指令参数。

模块 4 必须保留：

- `assumptions`
- `validation_points`
- `cross_step_dependencies`
- `open_questions`
- `prework_dependencies`
- required/recommended/optional 的上游分类差异

## 合格场景期望

电商日报场景通常应先判定为 `conditionally_suitable`，直到平台-店铺清单、指标映射、日期口径、登录稳定性和结果核验方式确认后，再进入更细设计。

邮件整理场景如果涉及正文语义判断，应保留低置信度人工确认或待确认分类，不应直接当作完全无人值守流程。

## 不合格输出特征

- 连续输出多个 JSON 对象。
- 用 `rpa_prescreen` 替代 `rpa_fit_prescreen`。
- 用 `candidate_risks` 替代 `candidate_risk_types`。
- 用 `prework_recommendations` 替代 `recommended_prework`。
- 在模块 2 直接输出“可以做 RPA”或“不可以做 RPA”的最终结论。
- 在模块 3 或模块 4 开始询问具体点击路径、页面选择器、等待时间或指令参数。
- 中文输出不可读或出现乱码。
```

- [ ] **Step 4: Rewrite `platform_test_checklist.md` as readable checklist**

Replace the file with:

```markdown
# 平台测试检查清单

用于验证 Agent 平台是否正确加载 Git Skill、RAG 材料和系统提示词，并确认模块 1-4 的输出合同是否稳定。

## 基础加载

- Git Skill 可以从当前仓库分支加载。
- Agent 可以读取根目录 `SKILL.md`。
- Agent 可以引用 `agent_modules/` 下的规则、schema、fixtures。
- RAG 可以检索 `agent_platform_package/rag_upload/` 中的材料。
- 系统提示词使用 `agent_platform_package/system_prompt/agent-system-prompt.md`。

## 交互行为

- 客户输入模糊需求后，Agent 先问边界问题，不直接给开发方案。
- 每轮优先使用选择题。
- 每题保留“不确定”或“其他，请补充”路径。
- 用户补充的信息会被吸收，不重复追问同义问题。
- 中等置信度推断会变成确认题。

## 输出合同

- 结构化结果只能返回一个顶层 JSON 对象。
- 根据当前阶段按需包含 `interaction_state`、`answer_batch`、`clarification_result`、`rpa_boundary_result`、`process_breakdown_result`。
- `answer_batch` 必须使用 `answer_records`、`state_patch`、`impact`。
- 模块 2 必须使用 `rpa_fit_prescreen`，不得替换成 `rpa_prescreen`。
- 模块 3 的 `decision.classification` 必须使用受控枚举。
- 模块 4 必须输出业务流程卡片，不得输出精确点击路径或指令参数。

## 模块边界

- 模块 2 不问具体点击路径、页面选择器、等待时间、异常分支细节。
- 模块 3 不重复模块 2 的边界澄清，不生成流程拆解。
- 模块 4 不覆盖模块 3 的边界判断，不设计异常分支，不生成 HTML。

## 可读性

- 中文输出必须可读。
- 不得出现历史编码乱码。
- 若输出乱码，应优先检查 RAG 文档、测试材料和系统提示词是否被错误编码保存。
```

- [ ] **Step 5: Run readability test and commit**

Run:

```powershell
python -m unittest tests.test_platform_package_contracts -v
```

Expected: PASS.

Commit:

```powershell
git add agent_platform_package/testing/expected_outputs.md agent_platform_package/testing/platform_test_checklist.md tests/test_platform_package_contracts.py
git commit -m "docs: clean platform testing materials"
```

---

### Task 2: Module 1-4 Flow Test Guide

**Files:**
- Create: `agent_platform_package/testing/module_1_to_4_flow_test.md`
- Modify: `tests/test_platform_package_contracts.py`

**Interfaces:**
- Consumes: module 1-4 handoff contract names.
- Produces: a manual platform test guide and automated assertions that the guide names each handoff gate.

- [ ] **Step 1: Extend the test for flow-guide required content**

Add this test to `tests/test_platform_package_contracts.py`:

```python
    def test_module_1_to_4_flow_guide_names_handoff_gates(self):
        text = (ROOT / "agent_platform_package/testing/module_1_to_4_flow_test.md").read_text(encoding="utf-8")

        expected_terms = [
            "模块 1",
            "模块 2",
            "模块 3",
            "模块 4",
            "enter_next_module",
            "rpa_boundary_check",
            "process_breakdown",
            "exception_design",
            "suitable",
            "conditionally_suitable",
            "business_process_cards_with_candidate_capabilities",
        ]

        for term in expected_terms:
            with self.subTest(term=term):
                self.assertIn(term, text)
```

- [ ] **Step 2: Run the new test and confirm it fails**

Run:

```powershell
python -m unittest tests.test_platform_package_contracts -v
```

Expected: FAIL because `module_1_to_4_flow_test.md` does not exist yet.

- [ ] **Step 3: Create flow guide**

Create `agent_platform_package/testing/module_1_to_4_flow_test.md`:

```markdown
# 模块 1-4 流程测试说明

## 测试目标

验证 Agent 是否能把一个模糊需求从交互采集流转到流程拆解，并保持每个模块的职责边界。

## 推荐测试输入

客户输入：

> 我要做一个自动统计电商不同平台的日数据，然后写入到腾讯文档，形成日报表的应用。

## 模块 1：交互与答案记录

模块 1 应先用选择题收集信息，并记录为 `answer_batch` 和 `interaction_state`。

通过条件：

- `answer_batch.answer_records` 记录用户选择。
- `answer_batch.state_patch` 更新业务目标、触发条件、操作系统等字段。
- `interaction_state.next_action` 在必答信息完成后进入 `enter_next_module`。

失败信号：

- 直接输出方案。
- 不记录 `state_patch`。
- 重复询问用户已经高置信回答过的问题。

## 模块 2：需求边界澄清

模块 2 消费模块 1 的状态，输出 `clarification_result`。

通过条件：

- `boundary_facts` 覆盖业务目标、触发条件、完成条件、输入数据、操作系统、输出结果。
- `rpa_fit_prescreen` 覆盖输入稳定性、规则清晰度、动作重复性、平台可操作性、结果可验证性。
- 当边界足够清晰时，`next_stage_recommendation` 为 `rpa_boundary_check`。

失败信号：

- 在模块 2 直接下最终 RPA 可行性结论。
- 询问点击路径、选择器、等待时间。
- 把 `rpa_fit_prescreen` 写成 `rpa_prescreen`。

## 模块 3：RPA 能力边界判断

模块 3 消费 `clarification_result`，输出 `rpa_boundary_result`。

通过条件：

- `decision.classification` 是 `suitable`、`conditionally_suitable`、`not_ready`、`not_suitable_for_direct_rpa` 之一。
- 对电商日报场景，未完全确认字段映射、日期口径、登录稳定性、核验方式前，通常应为 `conditionally_suitable`。
- 如果可以进入下一步，`next_stage_recommendation` 为 `process_breakdown`。

失败信号：

- 只因为有影刀指令就判定适合。
- 重复模块 2 的边界澄清。
- 直接生成流程卡片或开发步骤。

## 模块 4：流程拆解

模块 4 消费 `clarification_result` 和 `rpa_boundary_result`，输出 `process_breakdown_result`。

通过条件：

- 只接受 `suitable` 或 `conditionally_suitable` 作为来源判断。
- `breakdown_depth` 是 `business_process_cards_with_candidate_capabilities`。
- `process_cards` 是业务流程卡片，包含业务目的、输入、操作摘要、输出、候选影刀能力族、依赖和前置条件。
- 保留 `assumptions`、`validation_points`、`cross_step_dependencies`、`open_questions`。
- 下一阶段建议为 `exception_design`。

失败信号：

- 输出精确点击路径、选择器、等待时间、重试次数或指令参数。
- 直接设计异常分支。
- 生成 HTML。

## 流转总览

1. 模块 1 完成答案记录后进入 `enter_next_module`。
2. 模块 2 边界足够清晰后进入 `rpa_boundary_check`。
3. 模块 3 判定 `suitable` 或 `conditionally_suitable` 后进入 `process_breakdown`。
4. 模块 4 生成业务流程卡片后进入 `exception_design`。

## 人工验收结论

若以上四段全部通过，可以认为模块 1-4 主链路通畅；若任一模块失败，应先修复该模块合同，再继续开发模块 5。
```

- [ ] **Step 4: Run flow guide test and commit**

Run:

```powershell
python -m unittest tests.test_platform_package_contracts -v
```

Expected: PASS.

Commit:

```powershell
git add agent_platform_package/testing/module_1_to_4_flow_test.md tests/test_platform_package_contracts.py
git commit -m "docs: add module flow test guide"
```

---

### Task 3: Full Verification

**Files:**
- Modify: none unless verification exposes a defect.

**Interfaces:**
- Consumes: all module 1-4 contract tests.
- Produces: final evidence that platform docs and flow contracts pass together.

- [ ] **Step 1: Run platform tests**

Run:

```powershell
python -m unittest tests.test_platform_package_contracts -v
```

Expected: PASS.

- [ ] **Step 2: Run module 1-4 contract tests**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts tests.test_platform_package_contracts -v
```

Expected: PASS, with only the optional `jsonschema` skip allowed if the dependency is unavailable.

- [ ] **Step 3: Run readability scan**

Run:

```powershell
rg -n "骞冲|娴嬭|鑷|鐗|鍏堢|椋炰功|閭|閼|閻|妞|瀹|鍙ｅ緞" agent_platform_package/testing
```

Expected: no output.

- [ ] **Step 4: Commit verification report only if files changed**

If no files changed, do not commit. If a small fix was needed, commit with:

```powershell
git add <changed-files>
git commit -m "test: verify platform flow hardening"
```

---

## Self-Review

- Spec coverage: Task 1 fixes platform test document readability; Task 2 adds module 1-4 flow guide; Task 3 verifies all contracts and readability.
- Placeholder scan: no deferred implementation markers are present.
- Type consistency: all module names and output fields match the existing module contracts.
