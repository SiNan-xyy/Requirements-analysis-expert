# 平台测试期望输出

## 完整结构化输出外壳

合格输出必须是一个 JSON 对象，而不是三个连续 JSON 对象。

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
  "clarification_result": {}
}
```

其中 `answer_records` 在真实输出中应包含本轮问题的记录；上面为空数组只是说明外壳字段。

## 邮件自动整理：合格输出骨架

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": {
    "business_goal": {
      "value": "自动整理 Outlook/Microsoft 365 邮件，按发件人、主题关键词和正文规则分类到文件夹或标签，并生成清单或日报。",
      "confidence": "high",
      "source": "user_answer"
    },
    "trigger": {
      "value": "新邮件到达时自动触发",
      "confidence": "high",
      "source": "user_answer"
    },
    "completion_condition": {
      "value": "邮件被移动到对应文件夹或打上对应标签，并生成处理记录。",
      "confidence": "high",
      "source": "user_answer"
    },
    "input_data": {
      "value": [
        "发件人或发件域名",
        "邮件主题关键词",
        "邮件正文关键词或语义"
      ],
      "confidence": "high",
      "source": "user_answer"
    },
    "operated_systems": {
      "value": [
        "Outlook",
        "Microsoft 365"
      ],
      "confidence": "high",
      "source": "user_answer"
    },
    "output_result": {
      "value": "目标文件夹或标签、整理清单或日报、逐封邮件处理记录。",
      "confidence": "high",
      "source": "user_answer"
    }
  },
  "rpa_fit_prescreen": {
    "input_stability": "medium",
    "rule_clarity": "medium",
    "action_repeatability": "medium",
    "platform_operability": "high",
    "result_verifiability": "high",
    "candidate_risk_types": [
      "semantic_judgment",
      "unstable_input"
    ],
    "pre_screen_flags": [],
    "recommended_prework": [
      "准备固定分类目录或标签清单。",
      "为每个分类补充典型发件人、主题关键词、正文关键词或样例邮件。",
      "明确低置信度邮件进入待人工确认的规则。",
      "确定日报字段：主题、发件人、分类结果、判断依据、处理时间、是否需人工确认。"
    ]
  },
  "pending_questions": [],
  "stage_summary": "当前需求边界已基本清晰：新邮件到达后，机器人根据发件人、主题和正文规则整理邮件，并记录处理结果。正文语义判断和新类型邮件属于后续能力边界评估需要重点确认的风险，但已有待人工确认机制，当前可进入 RPA 能力边界评估。",
  "next_stage_recommendation": "rpa_boundary_check"
}
```

## 不合格输出特征

如果出现以下情况，需要调整 Skill 或系统提示词：

- 连续输出多个 JSON 对象，而不是一个顶层 wrapper。
- `interaction_state` 使用 `module`、`confidence_overview`、`known_facts`、`notes` 等自由字段。
- `answer_batch` 使用 `answers`、`topic`、`field` 等自由字段。
- 使用 `rpa_prescreen` 代替 `rpa_fit_prescreen`。
- 使用 `candidate_risks` 代替 `candidate_risk_types` 或 `pre_screen_flags`。
- 使用 `prework_recommendations` 代替 `recommended_prework`。
- 使用 `next_action` 代替 `next_stage_recommendation`。
- 使用 `medium_high` 等非枚举等级。
- 在 `candidate_risk_types` 中放完整中文句子，而不是枚举标识。
- 输出 `鐗╂枡`、`鍏堢粺`、`鑷姩`、`椋炰功` 等乱码。
- 在模块 2 直接输出“可以做 RPA”或“不可以做 RPA”的最终结论。
- 开始询问具体点击路径、页面字段、等待时间。

## Module 3 Expected Output

The platform should return a single top-level wrapper containing:

- `interaction_state`
- `answer_batch` when user answers were recorded in the same turn
- `clarification_result` when module 2 facts are still relevant
- `rpa_boundary_result` when module 3 has completed

For module 3, `rpa_boundary_result.decision.classification` must be one of:

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

`candidate_instruction_names` may appear as evidence, but the final decision must also cite input readiness, rule readiness, platform operability, result verifiability, and exception containment.

The e-commerce daily report scenario should normally be `conditionally_suitable`, not automatically `suitable`, until platform-store mapping, metric mapping, date scope, login stability, and result verification are confirmed.

## 电商多平台日报：合格 clarification_result 骨架

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": {
    "business_goal": {
      "value": "自动汇总多个电商平台及固定店铺的日经营数据，并写入腾讯文档形成日报。",
      "confidence": "high",
      "source": "user_answer"
    },
    "trigger": {
      "value": "每天固定时间自动执行",
      "confidence": "high",
      "source": "user_answer"
    },
    "completion_condition": {
      "value": "所有平台数据成功写入腾讯文档固定日报表。",
      "confidence": "high",
      "source": "user_answer"
    },
    "input_data": {
      "value": [
        "销售额或 GMV",
        "支付订单数",
        "退款金额或退款单数",
        "平台下固定店铺的日数据"
      ],
      "confidence": "high",
      "source": "user_answer"
    },
    "operated_systems": {
      "value": [
        "淘宝/天猫",
        "京东",
        "拼多多",
        "抖音电商",
        "快手电商",
        "腾讯文档"
      ],
      "confidence": "high",
      "source": "user_answer"
    },
    "output_result": {
      "value": "腾讯文档固定日报表中生成每日数据记录。",
      "confidence": "high",
      "source": "user_answer"
    }
  },
  "rpa_fit_prescreen": {
    "input_stability": "medium",
    "rule_clarity": "medium",
    "action_repeatability": "high",
    "platform_operability": "high",
    "result_verifiability": "medium",
    "candidate_risk_types": [
      "missing_rules",
      "unstable_input"
    ],
    "pre_screen_flags": [],
    "recommended_prework": [
      "准备平台与店铺清单。",
      "准备各平台指标与腾讯文档字段的映射表。",
      "确认日报日期口径是自然日、前一日还是平台结算日。",
      "确认是否需要把写入结果与源平台数据做自动核对。"
    ]
  },
  "pending_questions": [
    "后续能力边界评估需确认各平台是否有稳定导出入口或接口。",
    "后续能力边界评估需确认登录态、验证码和设备验证情况。"
  ],
  "stage_summary": "当前需求边界已基本清晰：每天定时从多个电商平台和固定店铺获取日经营数据，并按固定模板写入腾讯文档。场景具备重复性和明确输出，但多平台指标口径、日期口径和结果核对方式需要在下一阶段确认。",
  "next_stage_recommendation": "rpa_boundary_check"
}
```
