# 平台测试期望输出

## 通用结构化输出外壳

合格输出必须是一个顶层 JSON 对象。Agent 可以根据当前阶段按需包含以下对象，但不得连续输出多个相邻 JSON：

- `interaction_state`
- `answer_batch`
- `clarification_result`
- `rpa_boundary_result`
- `process_breakdown_result`

示例外壳：

```json
{
  "interaction_state": {
    "stage": "clarification",
    "status": "ready_for_next_module",
    "completion_level": "workable",
    "answered_question_ids": [],
    "pending_question_ids": [],
    "last_summary": "",
    "next_action": "enter_next_module"
  },
  "answer_batch": {
    "answer_records": [],
    "state_patch": {},
    "impact": {
      "blocks_stage_progression": false,
      "adds_pending_question": false,
      "pending_question_ids": [],
      "review_notes": []
    }
  },
  "clarification_result": {},
  "rpa_boundary_result": {},
  "process_breakdown_result": {}
}
```

真实输出可以只包含当前阶段需要的对象，但必须保持一个顶层 JSON wrapper。

## Module 1 Expected Output

模块 1 负责记录选择题答案、自由补充、状态补丁和下一步动作。

必须使用：

- `answer_batch.answer_records`
- `answer_batch.state_patch`
- `answer_batch.impact`
- `interaction_state.next_action`

不得使用自由字段替代标准字段，例如：

- `answers`
- `topic`
- `field`

## Module 2 Expected Output

模块 2 输出 `clarification_result`，只做边界澄清和 RPA 预筛，不做最终可行性结论。

必须包含：

- `clarification_depth`
- `boundary_facts`
- `rpa_fit_prescreen`
- `pending_questions`
- `stage_summary`
- `next_stage_recommendation`

`boundary_facts` 必须覆盖：

- `business_goal`
- `trigger`
- `completion_condition`
- `input_data`
- `operated_systems`
- `output_result`

`rpa_fit_prescreen` 必须覆盖：

- `input_stability`
- `rule_clarity`
- `action_repeatability`
- `platform_operability`
- `result_verifiability`

## Module 3 Expected Output

模块 3 输出 `rpa_boundary_result`，判断需求是否适合进入流程拆解。

`rpa_boundary_result.decision.classification` 只能是：

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

判断必须同时参考：

- 输入准备度
- 规则准备度
- 平台可操作性
- 结果可验证性
- 异常可收敛性

候选影刀指令可以作为证据，但不能单独决定是否适合 RPA。

## Module 4 Expected Output

模块 4 输出 `process_breakdown_result`。

`process_breakdown_result.breakdown_depth` 必须是：

- `business_process_cards_with_candidate_capabilities`

每张流程卡片描述业务阶段和候选影刀能力族，不得包含：

- 选择器
- 精确点击路径
- 等待时间
- 重试次数
- 指令参数

模块 4 必须保留：

- `assumptions`
- `validation_points`
- `cross_step_dependencies`
- `open_questions`
- `prework_dependencies`
- required/recommended/optional 的上游分类差异

英文验收锚点：

- Preserve cross-step dependencies through `cross_step_dependencies`.
- Preserve validation points through `validation_points`.
- Preserve follow-up questions through `open_questions`.
- Preserve prior mandatory vs optional guidance, and do not erase the required/recommended/optional distinction.

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
