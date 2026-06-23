# Requirement Clarification And RPA Pre-Screen Design

## Goal

Build module 2 for the RPA requirements analyst agent: a boundary-only clarification loop that turns a vague automation idea into a requirement that is ready for RPA capability-boundary evaluation.

Module 2 must collect enough basic facts to make the requirement analyzable, and it must surface early RPA-fit risk signals. It must not perform the full RPA feasibility assessment, process breakdown, exception design, or HTML blueprint generation.

## Position In The Agent Workflow

Module 1 already defines the interaction foundation:

- Interaction state
- Choice question schema
- Answer batch and state patch model
- Decision rules
- Deduplication and answer absorption

Module 2 consumes those contracts. It produces structured requirement facts, stage summaries, pending questions, and RPA pre-screen flags.

The downstream modules remain separate:

- Module 3: formal RPA capability-boundary evaluation
- Module 4: happy-path process breakdown
- Module 5: branch and exception design
- Module 6: requirement blueprint generation
- Module 7: HTML report generation
- Module 8: quality audit

## Core Principle

Module 2 asks about **requirement boundaries**, not execution details.

It answers:

```text
What is the need?
Where does it start?
Where does it end?
What input does the robot need?
Which systems are involved?
What output proves completion?
Does the need show early signs of not being RPA-ready?
```

It does not ask:

```text
Which button is clicked first?
What is the exact page field selector?
What happens when the query returns zero rows?
How many times should login retry?
How should each exception branch jump?
Which screenshot is required at each step?
```

Those questions belong to later modules.

## Module 2 Scope

Module 2 includes:

- Initial intent extraction from a vague user request
- Boundary-only clarification questions
- Multi-round clarification until the requirement is analyzable
- RPA-fit pre-screen questions
- Lightweight negative example library for common "not directly RPA-ready" patterns
- Candidate risk signal extraction from user answers
- Stage summary and user confirmation before moving to module 3

Module 2 excludes:

- Final "can RPA do this?" conclusion
- Risk scoring as a feasibility decision
- Full RPA capability-boundary report
- Detailed process step design
- Happy-path generation
- Exception-path generation
- HTML report output
- Platform UI rendering

## Definition Of Analyzable

A requirement is analyzable when it has enough information to enter module 3.

Module 2 uses two layers:

1. Requirement boundary facts
2. RPA-fit pre-screen facts

### Requirement Boundary Facts

The six boundary facts are:

| Field | Question It Answers | Source In Training Material |
| --- | --- | --- |
| `business_goal` | What does the robot help complete? | Demand analysis purpose |
| `trigger` | When does the robot start? | PDF "起点" |
| `completion_condition` | Where does the robot stop? | PDF "终点" |
| `input_data` | What does the robot need before starting? | PDF Input |
| `operated_systems` | Which systems or platforms does the robot operate? | PDF System and Word "应用系统" |
| `output_result` | What result proves completion? | PDF Output and Word "流程数据传输" |

### RPA-Fit Pre-Screen Facts

The five RPA pre-screen facts are:

| Field | Question It Answers |
| --- | --- |
| `input_stability` | Is the input source fixed and format relatively stable? |
| `rule_clarity` | Can the key judgment be written as explicit rules? |
| `action_repeatability` | Are the actions repeated and stable enough to automate? |
| `platform_operability` | Can the target platform be clicked, typed into, read from, or accessed through an interface? |
| `result_verifiability` | Is there a clear success or failure signal? |

Module 2 may also record early risk signals:

| Field | Meaning |
| --- | --- |
| `candidate_risk_types` | Possible RPA-fit risks that need module 3 review |
| `pre_screen_flags` | Confirmed early warning tags from clarification answers |
| `recommended_prework` | Non-binding suggestions before formal evaluation |

## Completion Rules

Module 2 may enter `summarize_and_confirm` when:

- At least four of six boundary facts are answered with medium or high confidence.
- `input_data`, `operated_systems`, and `output_result` are not all missing.
- At least three of five RPA pre-screen facts are answered or explicitly marked unknown.
- No required answer is in `needs_free_text` or `invalid`.

Module 2 may enter `ready_for_next_module` after the user confirms the stage summary.

Module 2 must stop with a gap report when:

- Three or more required boundary facts remain unknown after retry.
- Two or more of `input_data`, `operated_systems`, and `output_result` are unknown.
- The user cannot describe the business goal beyond a vague wish such as "make it automatic".
- A high-confidence pre-screen risk shows the requirement is not ready for flow design, such as "rules are mainly artificial judgment and cannot be written down".

Stopping with a gap report is not a final rejection. It means the user needs to standardize rules, inputs, or outputs before continuing.

## Clarification Depth Control

Module 2 must use:

```json
{
  "clarification_depth": "boundary_only"
}
```

Allowed question examples:

- What starts this automation?
- Where does the input data come from?
- Which system does the robot operate?
- What result should be produced?
- Can the key judgment be written as rules?
- Is the input format stable?

Disallowed question examples:

- Which exact button does the robot click after login?
- What selector should the robot use for the query field?
- How many seconds should it wait after clicking search?
- What should happen when one specific page popup appears?

If a user voluntarily provides execution details, module 2 may absorb them into state as supplemental information, but it must not continue drilling into that level.

## Trigger Logic For RPA Risk Questions

Module 2 must not guess risk from the first sentence.

Risk detection follows this sequence:

```text
User initial request
  -> Extract business intent
  -> Detect weak candidate risk signals
  -> Ask boundary clarification questions
  -> Absorb answers and supplemental text
  -> Trigger targeted risk questions only when signals are present
  -> Ask fixed RPA pre-screen questions if not already answered
  -> Produce pre-screen flags, not final feasibility conclusions
```

### Trigger Levels

#### Level 1: Weak Keyword Trigger

Weak signals may come from the user's first sentence or later answers.

Examples:

- "判断是不是同一种"
- "名称不统一"
- "看情况"
- "人工判断"
- "识别内容"
- "各种格式"
- "经常变"
- "验证码"
- "人脸"
- "失败原因很多"

Weak triggers only produce:

```json
{
  "candidate_risk_types": ["semantic_judgment"],
  "confidence": "low",
  "action": "ask_disambiguation_question"
}
```

They must not produce a final risk conclusion.

#### Level 2: Field Answer Trigger

Risk questions become more reliable after the user answers boundary questions.

Examples:

- If `input_data.description` mentions supplier names that need manual matching, trigger semantic judgment screening.
- If `decision_basis` says "看情况", trigger missing rules screening.
- If `operated_systems` mentions frequent captcha or face recognition, trigger human verification screening.
- If `output_result` has no status, file, message, or log, trigger result verifiability screening.

#### Level 3: Fixed RPA Pre-Screen

Even without weak signals, module 2 should ask a small number of RPA pre-screen questions before completion.

Default fixed pre-screen questions:

1. Is the input format stable?
2. Can the key judgment be written as explicit rules?
3. Is the action repeated and stable?
4. Is the target platform operable by robot or interface?
5. Is the result verifiable?

The agent must skip or convert a fixed question into a confirmation question if earlier answers already cover it.

## Negative Example Library V1

The library is a lightweight material set for module 2 pre-screening. It is not a formal RAG system yet. It should be implemented as local structured material first, then can later be promoted into RAG.

Each negative example has:

- `case_id`
- `title`
- `risk_type`
- `symptoms`
- `why_not_rpa_ready`
- `screening_question`
- `options`
- `better_next_step`
- `module_2_action`
- `trigger_policy`

### Example 1: Semantic Material Matching

```json
{
  "case_id": "semantic-material-matching",
  "title": "物料名称不统一，需要人工判断是否同义",
  "risk_type": "semantic_judgment",
  "symptoms": [
    "不同供应商对同一物料叫法不同",
    "需要判断两个名称是不是同一种东西",
    "没有标准命名规则或映射表",
    "判断依赖人工经验或语义理解"
  ],
  "why_not_rpa_ready": "RPA 擅长执行明确规则，不擅长替业务定义同义关系。关键判断无法规则化时，机器人容易误判。",
  "screening_question": "不同名称之间是否已有明确的标准命名或映射规则？",
  "options": [
    "已有标准命名和映射表",
    "有部分规则，但仍需人工判断",
    "主要靠人工判断是不是同一种东西",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "先统一物料主数据命名规则",
    "建立供应商名称与标准物料名称的映射表",
    "规则明确后再考虑 RPA 自动入库"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["名称不统一", "是不是同一种", "人工判断", "同义"],
    "trigger_from_fields": [
      "business_goal",
      "input_data.description",
      "decision_basis"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 2: Missing Stable Business Rules

```json
{
  "case_id": "missing-stable-business-rules",
  "title": "业务规则说不清，依赖看情况处理",
  "risk_type": "missing_rules",
  "symptoms": [
    "业务描述中出现看情况、一般来说、人工会判断",
    "无法明确什么情况下做、什么情况下不做",
    "同一场景不同人处理方式不同",
    "规则不能写成条件"
  ],
  "why_not_rpa_ready": "RPA 负责稳定执行规则，不负责临场创造规则。规则缺失时，自动化会把不确定性放大。",
  "screening_question": "这个流程里的关键判断是否能写成明确条件？",
  "options": [
    "可以，判断条件已经明确",
    "大部分可以，少量情况需要人工确认",
    "目前主要靠人工经验判断",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "先整理判断规则",
    "把常见情况分类",
    "明确每类情况的处理动作",
    "无法规则化的部分保留人工审核"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["看情况", "人工判断", "人工经验", "说不清"],
    "trigger_from_fields": [
      "business_goal",
      "completion_condition",
      "decision_basis"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 3: Unstable Input Format

```json
{
  "case_id": "unstable-input-format",
  "title": "输入数据来源或格式不稳定",
  "risk_type": "unstable_input",
  "symptoms": [
    "输入可能来自聊天消息、表格、邮件、截图等多种形式",
    "字段名称或顺序经常变化",
    "同一字段有多种写法",
    "缺少固定模板"
  ],
  "why_not_rpa_ready": "输入不稳定会导致机器人无法稳定读取字段，后续流程即使固定也容易失败。",
  "screening_question": "机器人接收的数据格式是否固定？",
  "options": [
    "固定，有统一表格或字段模板",
    "基本固定，但偶尔有变化",
    "不固定，经常需要人工理解",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "先制定统一输入模板",
    "固定字段名称和必填项",
    "对非标准输入增加人工预处理",
    "必要时先用表单收集数据"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["各种格式", "格式不固定", "经常变化", "截图", "手工整理"],
    "trigger_from_fields": [
      "input_data.source",
      "input_data.description"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 4: Unverifiable Result

```json
{
  "case_id": "unverifiable-result",
  "title": "执行结果缺少明确成功或失败标志",
  "risk_type": "unverifiable_result",
  "symptoms": [
    "完成后没有页面提示",
    "没有状态变化",
    "没有生成文件或记录",
    "只能靠人工感觉判断是否成功"
  ],
  "why_not_rpa_ready": "RPA 需要知道任务是否完成。结果不可验证时，机器人无法稳定判断是否继续、重试或报错。",
  "screening_question": "流程完成后是否有明确的成功或失败标志？",
  "options": [
    "有明确状态、提示、文件或记录",
    "有提示，但需要进一步确认",
    "没有明确标志，通常人工判断",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "明确成功标志",
    "明确失败标志",
    "增加日志或结果记录",
    "让系统输出可读取的处理状态"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["不知道是否成功", "人工确认结果", "没有提示", "凭经验判断"],
    "trigger_from_fields": [
      "output_result",
      "completion_condition"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 5: Unstable System UI

```json
{
  "case_id": "unstable-system-ui",
  "title": "系统页面或入口不稳定",
  "risk_type": "unstable_platform",
  "symptoms": [
    "页面经常改版",
    "按钮位置或名称经常变化",
    "入口路径不固定",
    "系统加载速度波动大"
  ],
  "why_not_rpa_ready": "RPA 依赖稳定的系统入口和界面元素。页面频繁变化会导致脚本维护成本高。",
  "screening_question": "机器人要操作的系统页面是否相对稳定？",
  "options": [
    "稳定，页面和按钮很少变化",
    "基本稳定，偶尔升级",
    "经常变化或近期有改版计划",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "确认系统近期升级计划",
    "优先寻找 API 或数据接口",
    "固定操作入口",
    "页面稳定后再开发 RPA"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["经常改版", "页面变化", "入口不固定", "加载不稳定"],
    "trigger_from_fields": [
      "operated_systems",
      "platform_notes"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 6: Frequent Strong Verification

```json
{
  "case_id": "frequent-strong-verification",
  "title": "强验证码、人脸或手机二次确认频繁出现",
  "risk_type": "human_verification",
  "symptoms": [
    "每次登录都需要手机验证码",
    "频繁出现滑块或图形验证码",
    "需要人脸识别",
    "需要人工在手机 App 上确认"
  ],
  "why_not_rpa_ready": "频繁强验证会打断机器人独立执行，导致流程无法无人值守。",
  "screening_question": "流程执行过程中是否经常需要人工验证？",
  "options": [
    "基本不需要验证",
    "偶尔需要验证码或人工确认",
    "经常需要手机、人脸或强验证码",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "申请机器人专用账号",
    "确认是否可保持登录态",
    "改用接口或系统授权方式",
    "保留人工验证节点，不做全自动"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["验证码", "人脸", "手机确认", "二次验证", "滑块"],
    "trigger_from_fields": [
      "operated_systems",
      "login_method",
      "platform_notes"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 7: Open-Ended Exceptions

```json
{
  "case_id": "open-ended-exceptions",
  "title": "异常情况过多且没有分类规则",
  "risk_type": "open_ended_exceptions",
  "symptoms": [
    "失败原因很多",
    "不同失败原因处理方式不同",
    "目前没有异常分类",
    "异常主要靠人工临场判断"
  ],
  "why_not_rpa_ready": "RPA 可以处理明确分支，但不适合处理完全开放的异常空间。异常无分类时，机器人无法稳定闭环。",
  "screening_question": "异常情况是否已经有分类和对应处理方式？",
  "options": [
    "已经分类，并有明确处理方式",
    "有常见异常分类，少量需要人工处理",
    "异常很多，目前主要靠人工判断",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "先整理常见异常类型",
    "明确每类异常处理动作",
    "无法覆盖的异常统一转人工",
    "把异常处理纳入后续流程拆解模块"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["失败原因很多", "异常很多", "临场判断", "不好分类"],
    "trigger_from_fields": [
      "business_goal",
      "completion_condition",
      "known_exceptions"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

### Example 8: Low Frequency High Judgment

```json
{
  "case_id": "low-frequency-high-judgment",
  "title": "低频且强人工判断，自动化收益不明显",
  "risk_type": "low_roi",
  "symptoms": [
    "处理频率低",
    "每次处理都需要人工判断",
    "流程变化较大",
    "自动化后仍需大量人工确认"
  ],
  "why_not_rpa_ready": "当流程低频、规则不稳定、人工判断占比高时，RPA 维护成本可能高于节省的人力。",
  "screening_question": "这个流程是否高频重复，且大部分动作固定？",
  "options": [
    "高频重复，动作基本固定",
    "中等频率，部分动作固定",
    "低频且每次差异较大",
    "暂不确定",
    "其他，请补充"
  ],
  "better_next_step": [
    "先评估处理频率和耗时",
    "优先自动化高频固定动作",
    "低频复杂判断保留人工",
    "必要时只做辅助工具，不做完整 RPA"
  ],
  "module_2_action": "flag_rpa_fit_risk",
  "trigger_policy": {
    "weak_signals": ["偶尔", "低频", "每次不一样", "人工确认"],
    "trigger_from_fields": [
      "business_goal",
      "frequency",
      "decision_basis"
    ],
    "confirmation_required": true,
    "never_conclude_from_initial_request_only": true
  }
}
```

## Module 2 Output Contract

Module 2 writes a `clarification_result` object:

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": {
    "business_goal": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "trigger": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "completion_condition": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "input_data": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "operated_systems": {
      "value": [],
      "confidence": "medium",
      "source": "user_answer"
    },
    "output_result": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    }
  },
  "rpa_fit_prescreen": {
    "input_stability": "unknown",
    "rule_clarity": "unknown",
    "action_repeatability": "unknown",
    "platform_operability": "unknown",
    "result_verifiability": "unknown",
    "candidate_risk_types": [],
    "pre_screen_flags": [],
    "recommended_prework": []
  },
  "pending_questions": [],
  "stage_summary": "",
  "next_stage_recommendation": "rpa_boundary_check"
}
```

Allowed values for each RPA pre-screen dimension:

- `high`
- `medium`
- `low`
- `unknown`

These are not final feasibility scores. They are pre-screen signals for module 3.

## Prompt Behavior

Module 2 should:

- Start with one short summary of what it thinks the user wants.
- Ask 3-5 choice questions per round when possible.
- Use module 1's deduplication rules to avoid repeated questions.
- Ask boundary questions before detailed RPA risk questions unless the user gives a strong signal.
- Treat weak risk signals as candidates only.
- Convert high-confidence already-supplied answers into skipped questions.
- Convert medium-confidence inferences into confirmation questions.
- Stop with a gap report when the boundary facts are too incomplete.
- Stop with a prework recommendation when an obvious RPA-readiness prerequisite is missing.

Module 2 should not:

- Decide final RPA feasibility.
- Generate a happy path.
- Ask for exact click paths.
- Ask exception-branch details beyond a high-level "are exceptions classified?" pre-screen.
- Generate the final requirement document or HTML report.

## Example Interaction

User:

```text
我想让机器人自动处理供应商物料入库。
```

Module 2:

```text
我理解你想把供应商物料入库这件事自动化。先确认几个边界信息：

1. 物料数据通常从哪里来？
A. 固定 Excel/表格
B. 系统消息
C. 邮件或附件
D. 人工输入
E. 暂不确定
F. 其他，请补充

2. 机器人要在哪个系统里完成入库？
A. ERP
B. 网页后台
C. Excel/WPS
D. 多个系统
E. 暂不确定
F. 其他，请补充

3. 入库完成后有什么明确结果？
A. 系统状态更新
B. 生成入库记录
C. 发送通知
D. 没有明确标志
E. 暂不确定
F. 其他，请补充
```

If the user later says:

```text
不同供应商名称不一样，需要判断是不是同一种物料。
```

Module 2 should not decide final infeasibility. It should trigger a semantic matching pre-screen question:

```text
不同名称之间是否已有明确的标准命名或映射规则？
A. 已有标准命名和映射表
B. 有部分规则，但仍需人工判断
C. 主要靠人工判断是不是同一种东西
D. 暂不确定
E. 其他，请补充
```

## Acceptance Criteria

Module 2 design is accepted when:

- It uses module 1 schemas and decision rules instead of inventing a new interaction format.
- It defines boundary-only clarification and excludes execution-step drilling.
- It defines the six boundary facts needed for a requirement to become analyzable.
- It defines the five RPA-fit pre-screen dimensions.
- It includes the negative example library v1 with eight risk cases.
- It defines trigger logic that never concludes risk from the initial request alone.
- It differentiates weak triggers, field-answer triggers, and fixed pre-screen questions.
- It outputs pre-screen flags for module 3 instead of final feasibility conclusions.
- It has clear stop conditions for insufficient information and obvious prework requirements.

