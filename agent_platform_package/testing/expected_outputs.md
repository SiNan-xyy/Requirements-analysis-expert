# 平台测试期望输出

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

- 使用 `rpa_prescreen` 代替 `rpa_fit_prescreen`。
- 使用 `candidate_risks` 代替 `candidate_risk_types` 或 `pre_screen_flags`。
- 使用 `prework_recommendations` 代替 `recommended_prework`。
- 使用 `next_action` 代替 `next_stage_recommendation`。
- 使用 `medium_high` 等非枚举等级。
- 在模块 2 直接输出“可以做 RPA”或“不可以做 RPA”的最终结论。
- 开始询问具体点击路径、页面字段、等待时间。

