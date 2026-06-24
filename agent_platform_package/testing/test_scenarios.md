# 平台测试场景

## 场景 1：邮件自动整理

用户输入：

```text
我想做一个邮件自动整理的应用。
```

期望行为：

- Agent 先确认业务目标、触发条件、输入数据、操作系统、输出结果。
- Agent 可以识别“正文语义”是候选风险，但不能直接判断不可做。
- 如果用户设置“低置信度邮件进入待人工确认”，Agent 可以继续建议进入 `rpa_boundary_check`。
- Agent 不应询问 Outlook 里具体点击哪个按钮。

关键检查：

- `operated_systems.value` 应是数组，例如 `["Outlook", "Microsoft 365"]`。
- `rpa_fit_prescreen.rule_clarity` 只能是 `medium`，不能是 `medium_high`。
- 风险说明应放入 `candidate_risk_types`、`pre_screen_flags`、`recommended_prework` 或 `stage_summary`，不要新增 `candidate_risks`。
- 最终动作字段必须是 `next_stage_recommendation`。
- 如果输出完整结构化结果，只能返回一个 JSON wrapper，顶层是 `interaction_state`、`answer_batch`、`clarification_result`。

## 场景 1B：电商多平台日报

用户输入：

```text
我要做一个自动统计电商不同平台的日数据，然后写入到腾讯文档，形成日报表的应用。
```

期望行为：

- Agent 应确认平台清单、店铺范围、指标字段、执行时间、腾讯文档模板。
- 多平台多店铺不应直接判为阻塞；如果店铺数量固定、登录稳定、模板固定，可以进入 `rpa_boundary_check`。
- 结果验证如果只要求“写入成功”，应标为 `medium`，并在 `stage_summary` 或 `pending_questions` 里提示后续确认源数据核对方式。
- 指标口径差异应作为候选风险或后续待确认问题，不应直接输出最终不可行结论。

关键检查：

- 不要输出连续三个 JSON 对象。
- 不要把第一段写成 `{ "module": "...", "status": "...", "confidence_overview": ... }`。
- `answer_batch` 不要使用 `answers`、`topic`、`field`。
- `rpa_fit_prescreen.rule_clarity` 只能是 `medium`，不能是 `medium_high`。
- `candidate_risk_types` 应使用风险类型标识，例如 `missing_rules`、`unstable_input`，不要放完整中文风险句子。

## 场景 2：物料名称自动入库

用户输入：

```text
我想让机器人自动处理供应商物料入库。
```

期望行为：

- Agent 追问输入来源、系统、输出结果。
- 当用户说明不同供应商叫法不同且没有映射表时，Agent 应标记 `semantic_judgment`。
- 如果命名规则和映射表缺失，最终应输出 `stop_with_blocker`。
- Agent 不应直接说“RPA 不能做”。

## 场景 3：物流拦截

用户输入：

```text
我想让机器人自动做物流拦截。
```

期望行为：

- Agent 追问物流单号来源、操作系统、拦截结果回传方式。
- 如果输入、系统、结果都明确，最终可输出 `rpa_boundary_check`。
- Agent 可保留后续风险问题，例如验证码、权限、页面稳定性，但不应在模块 2 深挖点击路径。
