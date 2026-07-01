# Platform Compatible Question Controls Design

## 背景

实测发现，多选题命中率低，且补充输入框没有出现。当前交互层把“多选 + 补充”编码为 `multiple_choice_with_text`，但目标 Agent 平台很可能只稳定识别 `single_choice` 和 `multiple_choice` 两类控件。结果是模型即使输出了扩展题型，平台前端也可能无法正确渲染。

同时，当前规则里容易把“不确定”和“其他，请补充”混在一起。两者业务含义不同，后续对需求记忆体、缺口、追问和模块 gate 的影响也不同。

## 目标

- 让题型协议兼容平台稳定控件。
- 提高可并存事实问题的多选命中率。
- 每个问题都同时提供“不确定”和“其他”。
- 默认显示“请补充”输入框。
- 明确区分 `unknown` 和 `other` 的状态流转。
- 避免把 unknown 当作补充答案，或把 other 当作未知缺口。

## 非目标

- 不设计新的前端组件库。
- 不依赖平台必须支持未知的 `*_with_text` 题型。
- 不让补充输入框替代选择题。
- 不在本次改造中重做模块 2-6 的业务逻辑。

## 设计方案

### 1. 题型只保留平台稳定类型

`question.type` 只允许：

- `single_choice`
- `multiple_choice`

不再使用：

- `single_choice_with_text`
- `multiple_choice_with_text`

补充输入框不再通过题型表达，而通过独立字段表达。

### 2. 新增常驻补充输入字段

每个问题都带：

```json
{
  "supplement_text": {
    "enabled": true,
    "always_visible": true,
    "label": "请补充",
    "placeholder": "如选项不完整，或需要说明特殊情况，请在这里补充"
  }
}
```

`free_text` 可以作为兼容字段保留，但新规则以 `supplement_text` 为主。

### 3. 每题固定包含 unknown 和 other

每个问题的选项必须包含：

```json
{
  "label": "不确定",
  "value": "unknown"
}
```

```json
{
  "label": "其他",
  "value": "other"
}
```

两者不能互相替代。

### 4. unknown 与 other 的语义

`unknown` 表示客户暂时不知道、无法确认、需要回去查。

处理规则：

- `answer_status = "unknown"`
- 不要求填写补充输入框。
- 必填信息 unknown 时进入需求记忆体 `gaps`。
- 根据阻塞程度影响 gate：`partial_ready` 或 `blocked`。
- 不直接进入 `confirmed_facts`。

`other` 表示客户知道答案，但选项没有覆盖。

处理规则：

- 如果有补充内容：`answer_status = "answered_with_supplement"`。
- 如果没有补充内容：`answer_status = "needs_free_text"`。
- 有补充内容时可进入事实或候选事实，取决于置信度和上下文。
- 不应直接形成 gap，除非客户选择 other 后没有补充。

### 5. 普通选项加补充

客户可以选择普通选项，同时填写补充说明。

处理规则：

- 普通选项按正常答案吸收。
- 补充文本作为 `supplement_text` 记录。
- 如果补充文本改变了答案边界，进入确认或记忆体更新。
- 如果只是说明特殊情况，作为事实备注或推断依据保留。

### 6. 多选强制触发场景

以下问题必须使用 `multiple_choice`：

- 操作平台或系统
- 数据来源
- 输入字段
- 输出字段
- 处理对象范围，例如平台、店铺、文件、账号、邮件类别
- 异常处理方式
- 通知方式
- 人工兜底方式
- 验证码处理方式
- 可同时存在的能力、风险、前置准备项

互斥问题才使用 `single_choice`，例如：

- 触发方式的主类型
- 当前是否已有固定模板
- 是否接受人工复核
- 当前需求是否继续推进

## 数据结构示例

```json
{
  "question_id": "operated_systems",
  "stage": "intake",
  "question": "这个自动化需要操作哪些平台或系统？可以多选。",
  "type": "multiple_choice",
  "importance": "required",
  "blocks_stage_progression": true,
  "allow_unknown": true,
  "target_field": "operated_systems",
  "options": [
    {
      "label": "电商平台后台",
      "value": "ecommerce_platform_backend"
    },
    {
      "label": "在线表格",
      "value": "online_spreadsheet"
    },
    {
      "label": "不确定",
      "value": "unknown"
    },
    {
      "label": "其他",
      "value": "other"
    }
  ],
  "supplement_text": {
    "enabled": true,
    "always_visible": true,
    "label": "请补充",
    "placeholder": "如选项不完整，或需要说明特殊情况，请在这里补充"
  }
}
```

## 状态流转

| 用户行为 | answer_status | 记忆体处理 | gate 影响 |
| --- | --- | --- | --- |
| 选择普通选项，无补充 | answered | 进入 confirmed fact 或 state patch | 按事实完整度判断 |
| 选择普通选项，有补充 | answered_with_supplement | 事实 + 补充说明 | 可能减少后续追问 |
| 选择 unknown，无补充 | unknown | 进入 gap 或待确认缺口 | 可能 partial_ready 或 blocked |
| 选择 unknown，有补充 | unknown_with_note | 低置信度说明，需确认 | 不直接作为开发事实 |
| 选择 other，无补充 | needs_free_text | 追问补充文本 | 当前题未完成 |
| 选择 other，有补充 | answered_with_supplement | 吸收为候选答案或事实 | 按补充质量判断 |

## 测试策略

- schema 测试：`question.type` 只允许 `single_choice` 和 `multiple_choice`。
- schema 测试：每个问题必须支持 `supplement_text`。
- fixture 测试：多平台问题必须是 `multiple_choice`，并包含 unknown、other、常驻 supplement_text。
- policy 测试：平台、数据源、字段、异常、通知、人工兜底、验证码必须使用 `multiple_choice`。
- answer-batch 测试：unknown 与 other 产生不同 `answer_status`。
- memory 测试：unknown 进入 gap，other + 补充不直接进入 gap。
- prompt 测试：禁止输出 `multiple_choice_with_text`。

## 部署影响

平台 Skill 更新后，系统提示词和交互 schema 会要求 Agent 使用平台兼容题型。若平台支持 `supplement_text`，应渲染为默认显示的输入框；若平台暂不支持，也至少能稳定渲染 `single_choice` / `multiple_choice`，并通过“其他”选项文案兜底。

## 风险

- 如果平台完全不支持自定义 `supplement_text` 字段，输入框仍可能无法由结构化字段渲染，需要平台侧映射该字段。
- 如果模型忽略 policy，仍可能输出单选；需要测试用例和系统提示词共同约束。
- 如果用户选择 unknown 又写补充，Agent 需要避免过度自信地吸收为事实。

## 成功标准

- 多选场景稳定输出 `type = "multiple_choice"`。
- 每题都有“不确定”和“其他”。
- 每题都有默认显示的 `supplement_text`。
- unknown 不再触发补充必填。
- other 无补充时才触发补充追问。
- 最终记忆体中 unknown 和 other 的处理路径可追踪、可测试。
