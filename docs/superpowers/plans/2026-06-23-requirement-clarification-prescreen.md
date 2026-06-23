# Requirement Clarification Pre-Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build module 2 for the RPA requirements analyst agent: a boundary-only clarification and RPA-fit pre-screen contract that consumes module 1 interaction schema outputs.

**Architecture:** Add a new file-based module at `agent_modules/requirement_clarification/`. JSON schemas define the module output contract and negative example material format. JSON rules define completion and trigger policy. Markdown prompt rules define the agent behavior boundary. Fixtures demonstrate the intended state transitions. Python stdlib tests validate the contracts without adding runtime dependencies.

**Tech Stack:** JSON, Markdown, Python 3 stdlib `unittest` and `json`, no third-party dependencies.

## Global Constraints

- Implement only module 2: boundary-only clarification, RPA-fit pre-screen facts, negative example material, risk trigger rules, fixtures, and contract tests.
- Consume module 1 formats; do not invent an alternate interaction model.
- Do not implement final RPA feasibility assessment.
- Do not implement process breakdown, happy path generation, exception design, HTML reporting, or platform UI rendering.
- Do not conclude risk from the initial user request alone.
- Treat weak risk signals as candidates that require follow-up confirmation.
- Use `clarification_depth = "boundary_only"`.
- Use Chinese text only for user-facing example questions, options, and materials where needed.

---

## File Structure

- Create `agent_modules/requirement_clarification/README.md`: module overview and artifact index.
- Create `agent_modules/requirement_clarification/schemas/clarification-result.schema.json`: output contract for module 2.
- Create `agent_modules/requirement_clarification/schemas/negative-example.schema.json`: contract for each negative example.
- Create `agent_modules/requirement_clarification/materials/negative-examples.v1.json`: eight approved negative examples.
- Create `agent_modules/requirement_clarification/rules/completion-rules.json`: analyzable and stop conditions.
- Create `agent_modules/requirement_clarification/rules/trigger-policy.json`: weak, field-answer, and fixed pre-screen trigger rules.
- Create `agent_modules/requirement_clarification/rules/prompt-rules.md`: prompt boundary rules for module 2.
- Create `agent_modules/requirement_clarification/fixtures/clarification-result-ready.json`: ready-for-module-3 example.
- Create `agent_modules/requirement_clarification/fixtures/semantic-risk-prescreen.json`: semantic matching risk example.
- Create `tests/test_requirement_clarification_contracts.py`: contract tests for module 2.

---

### Task 1: Add Clarification Result Schema And Baseline Fixture

**Files:**
- Create: `agent_modules/requirement_clarification/README.md`
- Create: `agent_modules/requirement_clarification/schemas/clarification-result.schema.json`
- Create: `agent_modules/requirement_clarification/fixtures/clarification-result-ready.json`
- Create: `tests/test_requirement_clarification_contracts.py`

**Interfaces:**
- Consumes module 1 stage names such as `rpa_boundary_check`.
- Produces `clarification_result` with `clarification_depth`, `boundary_facts`, `rpa_fit_prescreen`, `pending_questions`, `stage_summary`, and `next_stage_recommendation`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_requirement_clarification_contracts.py` with:

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class RequirementClarificationContractTests(unittest.TestCase):
    def test_clarification_result_schema_defines_boundary_and_prescreen_fields(self):
        schema = load_json("agent_modules/requirement_clarification/schemas/clarification-result.schema.json")
        props = schema["properties"]
        boundary_required = props["boundary_facts"]["required"]
        prescreen_required = props["rpa_fit_prescreen"]["required"]

        self.assertEqual(props["clarification_depth"]["const"], "boundary_only")
        self.assertIn("business_goal", boundary_required)
        self.assertIn("trigger", boundary_required)
        self.assertIn("completion_condition", boundary_required)
        self.assertIn("input_data", boundary_required)
        self.assertIn("operated_systems", boundary_required)
        self.assertIn("output_result", boundary_required)
        self.assertIn("rule_clarity", prescreen_required)
        self.assertIn("result_verifiability", prescreen_required)

    def test_ready_fixture_points_to_rpa_boundary_check(self):
        fixture = load_json("agent_modules/requirement_clarification/fixtures/clarification-result-ready.json")

        self.assertEqual(fixture["clarification_depth"], "boundary_only")
        self.assertEqual(fixture["next_stage_recommendation"], "rpa_boundary_check")
        self.assertEqual(fixture["rpa_fit_prescreen"]["rule_clarity"], "medium")
        self.assertIn("物流拦截", fixture["stage_summary"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: FAIL with missing `clarification-result.schema.json` or `clarification-result-ready.json`.

- [ ] **Step 3: Create README**

Create `agent_modules/requirement_clarification/README.md` with:

```markdown
# Requirement Clarification Module

This module defines module 2 of the RPA requirements analyst agent: boundary-only clarification plus RPA-fit pre-screening.

It consumes the module 1 interaction schema. It does not decide final RPA feasibility, generate happy paths, design exception branches, or create HTML reports.

## Artifact Index

- `schemas/clarification-result.schema.json`: module 2 output contract.
- `schemas/negative-example.schema.json`: negative example material contract.
- `materials/negative-examples.v1.json`: approved RPA-fit negative examples.
- `rules/completion-rules.json`: analyzable and stop conditions.
- `rules/trigger-policy.json`: risk trigger levels and fixed pre-screen dimensions.
- `rules/prompt-rules.md`: prompt behavior rules for module 2.
- `fixtures/clarification-result-ready.json`: ready-for-module-3 example.
- `fixtures/semantic-risk-prescreen.json`: semantic matching pre-screen example.
```

- [ ] **Step 4: Create clarification result schema**

Create `agent_modules/requirement_clarification/schemas/clarification-result.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/clarification-result.schema.json",
  "title": "ClarificationResult",
  "type": "object",
  "required": [
    "clarification_depth",
    "boundary_facts",
    "rpa_fit_prescreen",
    "pending_questions",
    "stage_summary",
    "next_stage_recommendation"
  ],
  "additionalProperties": false,
  "properties": {
    "clarification_depth": {
      "const": "boundary_only"
    },
    "boundary_facts": {
      "type": "object",
      "required": [
        "business_goal",
        "trigger",
        "completion_condition",
        "input_data",
        "operated_systems",
        "output_result"
      ],
      "additionalProperties": false,
      "properties": {
        "business_goal": { "$ref": "#/$defs/fact" },
        "trigger": { "$ref": "#/$defs/fact" },
        "completion_condition": { "$ref": "#/$defs/fact" },
        "input_data": { "$ref": "#/$defs/fact" },
        "operated_systems": { "$ref": "#/$defs/fact" },
        "output_result": { "$ref": "#/$defs/fact" }
      }
    },
    "rpa_fit_prescreen": {
      "type": "object",
      "required": [
        "input_stability",
        "rule_clarity",
        "action_repeatability",
        "platform_operability",
        "result_verifiability",
        "candidate_risk_types",
        "pre_screen_flags",
        "recommended_prework"
      ],
      "additionalProperties": false,
      "properties": {
        "input_stability": { "$ref": "#/$defs/prescreen_level" },
        "rule_clarity": { "$ref": "#/$defs/prescreen_level" },
        "action_repeatability": { "$ref": "#/$defs/prescreen_level" },
        "platform_operability": { "$ref": "#/$defs/prescreen_level" },
        "result_verifiability": { "$ref": "#/$defs/prescreen_level" },
        "candidate_risk_types": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        },
        "pre_screen_flags": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        },
        "recommended_prework": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "pending_questions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "stage_summary": {
      "type": "string"
    },
    "next_stage_recommendation": {
      "type": "string",
      "enum": ["rpa_boundary_check", "stop_with_gap_report", "stop_with_prework_recommendation"]
    }
  },
  "$defs": {
    "confidence": {
      "type": "string",
      "enum": ["high", "medium", "low", "none"]
    },
    "fact": {
      "type": "object",
      "required": ["value", "confidence", "source"],
      "additionalProperties": false,
      "properties": {
        "value": {},
        "confidence": { "$ref": "#/$defs/confidence" },
        "source": { "type": "string" }
      }
    },
    "prescreen_level": {
      "type": "string",
      "enum": ["high", "medium", "low", "unknown"]
    }
  }
}
```

- [ ] **Step 5: Create ready fixture**

Create `agent_modules/requirement_clarification/fixtures/clarification-result-ready.json` with:

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": {
    "business_goal": {
      "value": "自动完成物流拦截",
      "confidence": "high",
      "source": "user_answer"
    },
    "trigger": {
      "value": "收到飞书机器人消息中的物流单号后开始",
      "confidence": "high",
      "source": "user_answer"
    },
    "completion_condition": {
      "value": "拦截结果已发送回飞书",
      "confidence": "high",
      "source": "user_answer"
    },
    "input_data": {
      "value": ["物流单号"],
      "confidence": "high",
      "source": "user_answer"
    },
    "operated_systems": {
      "value": ["飞书", "影刀商城后台"],
      "confidence": "high",
      "source": "user_answer"
    },
    "output_result": {
      "value": "飞书通知拦截成功或失败",
      "confidence": "high",
      "source": "user_answer"
    }
  },
  "rpa_fit_prescreen": {
    "input_stability": "high",
    "rule_clarity": "medium",
    "action_repeatability": "high",
    "platform_operability": "medium",
    "result_verifiability": "high",
    "candidate_risk_types": [],
    "pre_screen_flags": [],
    "recommended_prework": []
  },
  "pending_questions": [
    "确认商城后台是否存在强验证码"
  ],
  "stage_summary": "当前需求是物流拦截自动化：收到飞书物流单号后，在影刀商城后台执行拦截，并把结果回传飞书。",
  "next_stage_recommendation": "rpa_boundary_check"
}
```

- [ ] **Step 6: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: PASS for both tests.

- [ ] **Step 7: Commit**

Run:

```powershell
git add agent_modules/requirement_clarification/README.md agent_modules/requirement_clarification/schemas/clarification-result.schema.json agent_modules/requirement_clarification/fixtures/clarification-result-ready.json tests/test_requirement_clarification_contracts.py
git commit -m "feat: add clarification result contract"
```

---

### Task 2: Add Negative Example Material Contract And Library

**Files:**
- Create: `agent_modules/requirement_clarification/schemas/negative-example.schema.json`
- Create: `agent_modules/requirement_clarification/materials/negative-examples.v1.json`
- Modify: `tests/test_requirement_clarification_contracts.py`

**Interfaces:**
- Consumes no runtime code.
- Produces eight negative examples with trigger policies and no final feasibility conclusions.

- [ ] **Step 1: Write the failing tests**

Append these methods inside `RequirementClarificationContractTests`:

```python
    def test_negative_example_schema_requires_trigger_policy(self):
        schema = load_json("agent_modules/requirement_clarification/schemas/negative-example.schema.json")

        self.assertIn("trigger_policy", schema["required"])
        trigger_required = schema["properties"]["trigger_policy"]["required"]
        self.assertIn("weak_signals", trigger_required)
        self.assertIn("confirmation_required", trigger_required)
        self.assertIn("never_conclude_from_initial_request_only", trigger_required)

    def test_negative_examples_v1_has_eight_approved_cases(self):
        library = load_json("agent_modules/requirement_clarification/materials/negative-examples.v1.json")
        case_ids = {item["case_id"] for item in library["examples"]}

        self.assertEqual(len(library["examples"]), 8)
        self.assertIn("semantic-material-matching", case_ids)
        self.assertIn("missing-stable-business-rules", case_ids)
        self.assertIn("frequent-strong-verification", case_ids)
        for item in library["examples"]:
            self.assertEqual(item["module_2_action"], "flag_rpa_fit_risk")
            self.assertTrue(item["trigger_policy"]["confirmation_required"])
            self.assertTrue(item["trigger_policy"]["never_conclude_from_initial_request_only"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: FAIL with missing negative example files.

- [ ] **Step 3: Create negative example schema**

Create `agent_modules/requirement_clarification/schemas/negative-example.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/negative-example.schema.json",
  "title": "NegativeExample",
  "type": "object",
  "required": [
    "case_id",
    "title",
    "risk_type",
    "symptoms",
    "why_not_rpa_ready",
    "screening_question",
    "options",
    "better_next_step",
    "module_2_action",
    "trigger_policy"
  ],
  "additionalProperties": false,
  "properties": {
    "case_id": { "type": "string", "minLength": 1 },
    "title": { "type": "string", "minLength": 1 },
    "risk_type": { "type": "string", "minLength": 1 },
    "symptoms": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" }
    },
    "why_not_rpa_ready": { "type": "string", "minLength": 1 },
    "screening_question": { "type": "string", "minLength": 1 },
    "options": {
      "type": "array",
      "minItems": 5,
      "items": { "type": "string" }
    },
    "better_next_step": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" }
    },
    "module_2_action": {
      "const": "flag_rpa_fit_risk"
    },
    "trigger_policy": {
      "type": "object",
      "required": [
        "weak_signals",
        "trigger_from_fields",
        "confirmation_required",
        "never_conclude_from_initial_request_only"
      ],
      "additionalProperties": false,
      "properties": {
        "weak_signals": {
          "type": "array",
          "items": { "type": "string" }
        },
        "trigger_from_fields": {
          "type": "array",
          "items": { "type": "string" }
        },
        "confirmation_required": { "type": "boolean" },
        "never_conclude_from_initial_request_only": { "type": "boolean" }
      }
    }
  }
}
```

- [ ] **Step 4: Create negative examples library**

Create `agent_modules/requirement_clarification/materials/negative-examples.v1.json` with:

```json
{
  "version": "v1",
  "purpose": "Module 2 RPA-fit pre-screen negative examples. These examples trigger clarification questions and pre-screen flags, not final feasibility conclusions.",
  "examples": [
    {
      "case_id": "semantic-material-matching",
      "title": "物料名称不统一，需要人工判断是否同义",
      "risk_type": "semantic_judgment",
      "symptoms": ["不同供应商对同一物料叫法不同", "需要判断两个名称是不是同一种东西", "没有标准命名规则或映射表", "判断依赖人工经验或语义理解"],
      "why_not_rpa_ready": "RPA 擅长执行明确规则，不擅长替业务定义同义关系。",
      "screening_question": "不同名称之间是否已有明确的标准命名或映射规则？",
      "options": ["已有标准命名和映射表", "有部分规则，但仍需人工判断", "主要靠人工判断是不是同一种东西", "暂不确定", "其他，请补充"],
      "better_next_step": ["先统一物料主数据命名规则", "建立供应商名称与标准物料名称的映射表", "规则明确后再考虑 RPA 自动入库"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["名称不统一", "是不是同一种", "人工判断", "同义"],
        "trigger_from_fields": ["business_goal", "input_data.description", "decision_basis"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "missing-stable-business-rules",
      "title": "业务规则说不清，依赖看情况处理",
      "risk_type": "missing_rules",
      "symptoms": ["出现看情况、一般来说、人工会判断", "无法明确什么情况下做或不做", "同一场景不同人处理方式不同", "规则不能写成条件"],
      "why_not_rpa_ready": "RPA 负责稳定执行规则，不负责临场创造规则。",
      "screening_question": "这个流程里的关键判断是否能写成明确条件？",
      "options": ["可以，判断条件已经明确", "大部分可以，少量情况需要人工确认", "目前主要靠人工经验判断", "暂不确定", "其他，请补充"],
      "better_next_step": ["先整理判断规则", "把常见情况分类", "明确每类情况的处理动作", "无法规则化的部分保留人工审核"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["看情况", "人工判断", "人工经验", "说不清"],
        "trigger_from_fields": ["business_goal", "completion_condition", "decision_basis"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "unstable-input-format",
      "title": "输入数据来源或格式不稳定",
      "risk_type": "unstable_input",
      "symptoms": ["输入来自多种形式", "字段名称或顺序经常变化", "同一字段有多种写法", "缺少固定模板"],
      "why_not_rpa_ready": "输入不稳定会导致机器人无法稳定读取字段。",
      "screening_question": "机器人接收的数据格式是否固定？",
      "options": ["固定，有统一表格或字段模板", "基本固定，但偶尔有变化", "不固定，经常需要人工理解", "暂不确定", "其他，请补充"],
      "better_next_step": ["先制定统一输入模板", "固定字段名称和必填项", "对非标准输入增加人工预处理", "必要时先用表单收集数据"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["各种格式", "格式不固定", "经常变化", "截图", "手工整理"],
        "trigger_from_fields": ["input_data.source", "input_data.description"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "unverifiable-result",
      "title": "执行结果缺少明确成功或失败标志",
      "risk_type": "unverifiable_result",
      "symptoms": ["完成后没有页面提示", "没有状态变化", "没有生成文件或记录", "只能靠人工感觉判断是否成功"],
      "why_not_rpa_ready": "RPA 需要知道任务是否完成，否则无法稳定判断继续、重试或报错。",
      "screening_question": "流程完成后是否有明确的成功或失败标志？",
      "options": ["有明确状态、提示、文件或记录", "有提示，但需要进一步确认", "没有明确标志，通常人工判断", "暂不确定", "其他，请补充"],
      "better_next_step": ["明确成功标志", "明确失败标志", "增加日志或结果记录", "让系统输出可读取的处理状态"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["不知道是否成功", "人工确认结果", "没有提示", "凭经验判断"],
        "trigger_from_fields": ["output_result", "completion_condition"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "unstable-system-ui",
      "title": "系统页面或入口不稳定",
      "risk_type": "unstable_platform",
      "symptoms": ["页面经常改版", "按钮位置或名称经常变化", "入口路径不固定", "系统加载速度波动大"],
      "why_not_rpa_ready": "RPA 依赖稳定的系统入口和界面元素。",
      "screening_question": "机器人要操作的系统页面是否相对稳定？",
      "options": ["稳定，页面和按钮很少变化", "基本稳定，偶尔升级", "经常变化或近期有改版计划", "暂不确定", "其他，请补充"],
      "better_next_step": ["确认系统近期升级计划", "优先寻找 API 或数据接口", "固定操作入口", "页面稳定后再开发 RPA"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["经常改版", "页面变化", "入口不固定", "加载不稳定"],
        "trigger_from_fields": ["operated_systems", "platform_notes"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "frequent-strong-verification",
      "title": "强验证码、人脸或手机二次确认频繁出现",
      "risk_type": "human_verification",
      "symptoms": ["每次登录都需要手机验证码", "频繁出现滑块或图形验证码", "需要人脸识别", "需要人工在手机 App 上确认"],
      "why_not_rpa_ready": "频繁强验证会打断机器人独立执行，导致流程无法无人值守。",
      "screening_question": "流程执行过程中是否经常需要人工验证？",
      "options": ["基本不需要验证", "偶尔需要验证码或人工确认", "经常需要手机、人脸或强验证码", "暂不确定", "其他，请补充"],
      "better_next_step": ["申请机器人专用账号", "确认是否可保持登录态", "改用接口或系统授权方式", "保留人工验证节点，不做全自动"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["验证码", "人脸", "手机确认", "二次验证", "滑块"],
        "trigger_from_fields": ["operated_systems", "login_method", "platform_notes"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "open-ended-exceptions",
      "title": "异常情况过多且没有分类规则",
      "risk_type": "open_ended_exceptions",
      "symptoms": ["失败原因很多", "不同失败原因处理方式不同", "目前没有异常分类", "异常主要靠人工临场判断"],
      "why_not_rpa_ready": "RPA 可以处理明确分支，但不适合处理完全开放的异常空间。",
      "screening_question": "异常情况是否已经有分类和对应处理方式？",
      "options": ["已经分类，并有明确处理方式", "有常见异常分类，少量需要人工处理", "异常很多，目前主要靠人工判断", "暂不确定", "其他，请补充"],
      "better_next_step": ["先整理常见异常类型", "明确每类异常处理动作", "无法覆盖的异常统一转人工", "把异常处理纳入后续流程拆解模块"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["失败原因很多", "异常很多", "临场判断", "不好分类"],
        "trigger_from_fields": ["business_goal", "completion_condition", "known_exceptions"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    },
    {
      "case_id": "low-frequency-high-judgment",
      "title": "低频且强人工判断，自动化收益不明显",
      "risk_type": "low_roi",
      "symptoms": ["处理频率低", "每次处理都需要人工判断", "流程变化较大", "自动化后仍需大量人工确认"],
      "why_not_rpa_ready": "当流程低频、规则不稳定、人工判断占比高时，RPA 维护成本可能高于节省的人力。",
      "screening_question": "这个流程是否高频重复，且大部分动作固定？",
      "options": ["高频重复，动作基本固定", "中等频率，部分动作固定", "低频且每次差异较大", "暂不确定", "其他，请补充"],
      "better_next_step": ["先评估处理频率和耗时", "优先自动化高频固定动作", "低频复杂判断保留人工", "必要时只做辅助工具，不做完整 RPA"],
      "module_2_action": "flag_rpa_fit_risk",
      "trigger_policy": {
        "weak_signals": ["偶尔", "低频", "每次不一样", "人工确认"],
        "trigger_from_fields": ["business_goal", "frequency", "decision_basis"],
        "confirmation_required": true,
        "never_conclude_from_initial_request_only": true
      }
    }
  ]
}
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: PASS for all tests.

- [ ] **Step 6: Commit**

Run:

```powershell
git add agent_modules/requirement_clarification/schemas/negative-example.schema.json agent_modules/requirement_clarification/materials/negative-examples.v1.json tests/test_requirement_clarification_contracts.py
git commit -m "feat: add RPA negative example library"
```

---

### Task 3: Add Completion And Trigger Rules

**Files:**
- Create: `agent_modules/requirement_clarification/rules/completion-rules.json`
- Create: `agent_modules/requirement_clarification/rules/trigger-policy.json`
- Create: `agent_modules/requirement_clarification/rules/prompt-rules.md`
- Modify: `tests/test_requirement_clarification_contracts.py`

**Interfaces:**
- Consumes clarification result fields from Task 1.
- Produces rules for analyzable threshold, stop conditions, and trigger levels.

- [ ] **Step 1: Write the failing tests**

Append these methods inside `RequirementClarificationContractTests`:

```python
    def test_completion_rules_preserve_boundary_only_thresholds(self):
        rules = load_json("agent_modules/requirement_clarification/rules/completion-rules.json")

        self.assertEqual(rules["clarification_depth"], "boundary_only")
        self.assertEqual(rules["summarize_threshold"]["minimum_boundary_facts_medium_or_high"], 4)
        self.assertEqual(rules["summarize_threshold"]["minimum_prescreen_facts_answered_or_unknown"], 3)
        self.assertIn("input_data", rules["core_fields"])
        self.assertIn("operated_systems", rules["core_fields"])
        self.assertIn("output_result", rules["core_fields"])

    def test_trigger_policy_never_concludes_from_initial_request(self):
        policy = load_json("agent_modules/requirement_clarification/rules/trigger-policy.json")

        self.assertEqual(policy["trigger_levels"][0]["name"], "weak_keyword_trigger")
        self.assertTrue(policy["global_rules"]["never_conclude_from_initial_request_only"])
        self.assertIn("rule_clarity", policy["fixed_prescreen_dimensions"])
        self.assertIn("result_verifiability", policy["fixed_prescreen_dimensions"])

    def test_prompt_rules_forbid_execution_step_drilling(self):
        text = (ROOT / "agent_modules/requirement_clarification/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Do not ask for exact click paths", text)
        self.assertIn("Do not decide final RPA feasibility", text)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: FAIL with missing rule files.

- [ ] **Step 3: Create completion rules**

Create `agent_modules/requirement_clarification/rules/completion-rules.json` with:

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": [
    "business_goal",
    "trigger",
    "completion_condition",
    "input_data",
    "operated_systems",
    "output_result"
  ],
  "core_fields": [
    "input_data",
    "operated_systems",
    "output_result"
  ],
  "summarize_threshold": {
    "minimum_boundary_facts_medium_or_high": 4,
    "minimum_prescreen_facts_answered_or_unknown": 3,
    "forbidden_answer_statuses": ["needs_free_text", "invalid"]
  },
  "stop_conditions": [
    "three_or_more_required_boundary_facts_unknown_after_retry",
    "two_or_more_core_fields_unknown",
    "business_goal_is_only_make_it_automatic",
    "high_confidence_pre_screen_risk_requires_prework"
  ],
  "next_actions": {
    "ready": "summarize_and_confirm",
    "confirmed": "enter_next_module",
    "insufficient": "stop_with_gap_report",
    "prework_required": "stop_with_prework_recommendation"
  }
}
```

- [ ] **Step 4: Create trigger policy**

Create `agent_modules/requirement_clarification/rules/trigger-policy.json` with:

```json
{
  "global_rules": {
    "never_conclude_from_initial_request_only": true,
    "weak_signals_create_candidate_risks_only": true,
    "field_answer_triggers_are_more_reliable_than_initial_keywords": true,
    "fixed_prescreen_questions_are_required_before_completion": true
  },
  "trigger_levels": [
    {
      "name": "weak_keyword_trigger",
      "confidence": "low",
      "action": "ask_disambiguation_question"
    },
    {
      "name": "field_answer_trigger",
      "confidence": "medium",
      "action": "ask_targeted_risk_question"
    },
    {
      "name": "fixed_prescreen",
      "confidence": "medium",
      "action": "ask_missing_prescreen_question"
    }
  ],
  "fixed_prescreen_dimensions": [
    "input_stability",
    "rule_clarity",
    "action_repeatability",
    "platform_operability",
    "result_verifiability"
  ],
  "skip_or_confirm_policy": {
    "high_confidence_existing_answer": "skip_question",
    "medium_confidence_inference": "ask_confirmation_question",
    "missing_answer": "ask_choice_question"
  }
}
```

- [ ] **Step 5: Create prompt rules**

Create `agent_modules/requirement_clarification/rules/prompt-rules.md` with:

```markdown
# Requirement Clarification Prompt Rules

Use these rules only for module 2.

## Do

- Start with one short summary of the user's likely business goal.
- Ask boundary questions before execution details.
- Ask 3-5 choice questions per round when possible.
- Use module 1 deduplication rules to avoid repeated questions.
- Treat weak risk signals as candidates only.
- Ask targeted risk questions only after a weak or field-answer trigger.
- Ask fixed RPA pre-screen questions before completing the module.
- Summarize boundary facts and pre-screen flags before entering module 3.
- Stop with a gap report when boundary facts are too incomplete.
- Stop with a prework recommendation when obvious standardization is needed.

## Do Not

- Do not decide final RPA feasibility.
- Do not generate a happy path.
- Do not ask for exact click paths.
- Do not ask for field selectors, wait times, or page-level operating details.
- Do not design exception branches beyond high-level classification.
- Do not generate the final requirement document or HTML report.
```

- [ ] **Step 6: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: PASS for all tests.

- [ ] **Step 7: Commit**

Run:

```powershell
git add agent_modules/requirement_clarification/rules/completion-rules.json agent_modules/requirement_clarification/rules/trigger-policy.json agent_modules/requirement_clarification/rules/prompt-rules.md tests/test_requirement_clarification_contracts.py
git commit -m "feat: add clarification trigger rules"
```

---

### Task 4: Add Semantic Risk Fixture And Final Documentation Coverage

**Files:**
- Create: `agent_modules/requirement_clarification/fixtures/semantic-risk-prescreen.json`
- Modify: `agent_modules/requirement_clarification/README.md`
- Modify: `tests/test_requirement_clarification_contracts.py`

**Interfaces:**
- Consumes negative example risk type `semantic_judgment`.
- Produces a fixture showing pre-screen flags without final feasibility conclusion.

- [ ] **Step 1: Write the failing tests**

Append these methods inside `RequirementClarificationContractTests`:

```python
    def test_semantic_risk_fixture_flags_prework_without_final_decision(self):
        fixture = load_json("agent_modules/requirement_clarification/fixtures/semantic-risk-prescreen.json")

        self.assertIn("semantic_judgment", fixture["rpa_fit_prescreen"]["candidate_risk_types"])
        self.assertIn("semantic_judgment", fixture["rpa_fit_prescreen"]["pre_screen_flags"])
        self.assertIn("建立供应商名称与标准物料名称的映射表", fixture["rpa_fit_prescreen"]["recommended_prework"])
        self.assertEqual(fixture["next_stage_recommendation"], "stop_with_prework_recommendation")
        self.assertNotIn("final_feasibility", fixture)

    def test_readme_lists_module_2_artifacts(self):
        text = (ROOT / "agent_modules/requirement_clarification/README.md").read_text(encoding="utf-8")

        expected_paths = [
            "schemas/clarification-result.schema.json",
            "schemas/negative-example.schema.json",
            "materials/negative-examples.v1.json",
            "rules/completion-rules.json",
            "rules/trigger-policy.json",
            "rules/prompt-rules.md",
            "fixtures/semantic-risk-prescreen.json"
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
```

Expected: FAIL with missing semantic fixture or README artifact path.

- [ ] **Step 3: Create semantic risk fixture**

Create `agent_modules/requirement_clarification/fixtures/semantic-risk-prescreen.json` with:

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": {
    "business_goal": {
      "value": "自动处理供应商物料入库",
      "confidence": "high",
      "source": "user_answer"
    },
    "trigger": {
      "value": "收到供应商物料数据后开始",
      "confidence": "medium",
      "source": "user_answer"
    },
    "completion_condition": {
      "value": "物料入库记录创建完成",
      "confidence": "medium",
      "source": "user_answer"
    },
    "input_data": {
      "value": ["供应商物料名称", "物料编码"],
      "confidence": "high",
      "source": "user_answer"
    },
    "operated_systems": {
      "value": ["ERP"],
      "confidence": "medium",
      "source": "user_answer"
    },
    "output_result": {
      "value": "ERP 中生成入库记录",
      "confidence": "medium",
      "source": "user_answer"
    }
  },
  "rpa_fit_prescreen": {
    "input_stability": "medium",
    "rule_clarity": "low",
    "action_repeatability": "medium",
    "platform_operability": "unknown",
    "result_verifiability": "medium",
    "candidate_risk_types": ["semantic_judgment"],
    "pre_screen_flags": ["semantic_judgment"],
    "recommended_prework": [
      "先统一物料主数据命名规则",
      "建立供应商名称与标准物料名称的映射表"
    ]
  },
  "pending_questions": [
    "确认是否已有标准命名或映射表"
  ],
  "stage_summary": "当前需求是供应商物料入库自动化，但物料名称匹配依赖人工语义判断，建议先完成命名规则或映射表。",
  "next_stage_recommendation": "stop_with_prework_recommendation"
}
```

- [ ] **Step 4: Update README**

Replace `agent_modules/requirement_clarification/README.md` with:

```markdown
# Requirement Clarification Module

This module defines module 2 of the RPA requirements analyst agent: boundary-only clarification plus RPA-fit pre-screening.

It consumes the module 1 interaction schema. It does not decide final RPA feasibility, generate happy paths, design exception branches, or create HTML reports.

## Artifact Index

- `schemas/clarification-result.schema.json`: module 2 output contract.
- `schemas/negative-example.schema.json`: negative example material contract.
- `materials/negative-examples.v1.json`: approved RPA-fit negative examples.
- `rules/completion-rules.json`: analyzable and stop conditions.
- `rules/trigger-policy.json`: risk trigger levels and fixed pre-screen dimensions.
- `rules/prompt-rules.md`: prompt behavior rules for module 2.
- `fixtures/clarification-result-ready.json`: ready-for-module-3 example.
- `fixtures/semantic-risk-prescreen.json`: semantic matching pre-screen example.

## Scope

Module 2 asks for requirement boundaries and early RPA-fit signals. It stops before formal feasibility assessment and before process step design.

## Boundary Facts

- Business goal
- Trigger
- Completion condition
- Input data
- Operated systems
- Output result

## RPA Pre-Screen Dimensions

- Input stability
- Rule clarity
- Action repeatability
- Platform operability
- Result verifiability

## Risk Trigger Rule

The module never concludes risk from the initial request alone. Initial weak signals only create candidate risks and follow-up questions.
```

- [ ] **Step 5: Run full verification**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_requirement_clarification_contracts -v
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
git status --short
```

Expected: both test suites PASS. `git status --short` shows only Task 4 files modified plus the existing untracked PPT.

- [ ] **Step 6: Commit**

Run:

```powershell
git add agent_modules/requirement_clarification/fixtures/semantic-risk-prescreen.json agent_modules/requirement_clarification/README.md tests/test_requirement_clarification_contracts.py
git commit -m "docs: finalize requirement clarification module"
```

---

## Self-Review

Spec coverage:

- Boundary-only clarification is implemented by Task 1 and Task 3.
- The six boundary facts are represented in the clarification result schema.
- The five RPA-fit pre-screen dimensions are represented in the clarification result schema and trigger policy.
- The eight negative examples are implemented in Task 2.
- The rule that initial requests cannot produce final risk conclusions is implemented in Task 2 and Task 3.
- Semantic risk prework behavior is demonstrated by Task 4.

Placeholder scan:

- The plan uses exact file paths, exact commands, and concrete JSON/Markdown content.
- No implementation step delegates detail to a future decision.

Type consistency:

- `next_stage_recommendation` values match the schema enum.
- RPA pre-screen values use only `high`, `medium`, `low`, and `unknown`.
- Negative example actions use `flag_rpa_fit_risk`.

