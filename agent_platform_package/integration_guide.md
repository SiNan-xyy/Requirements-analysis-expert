# Agent 平台集成说明

这份说明用于把当前项目接入 Agent 平台。平台当前支持：

- 从 Git 下载 Skill。
- 本地上传 RAG 材料。
- 手动编辑系统提示词。

当前项目已覆盖模块 1 到模块 6，可支持客户把模糊 RPA 需求推进到需求澄清、RPA 能力边界判断、流程拆解、异常设计和方案打包。

## 1. Git Skill 配置

Git 仓库地址：

```text
https://github.com/SiNan-xyy/Requirements-analysis-expert.git
```

建议使用分支：

```text
master
```

Skill 入口文件：

```text
SKILL.md
```

Agent 平台从 Git 下载后，应先读取根目录 `SKILL.md`，再按其中的 Load Order 读取 `agent_modules/` 下的模块说明、规则、schema 和 fixtures。

当前 Git Skill 覆盖：

- Module 1: `agent_modules/interaction_schema/`
- Module 2: `agent_modules/requirement_clarification/`
- Module 3: `agent_modules/rpa_boundary_check/`
- Module 4: `agent_modules/process_breakdown/`
- Module 5: `agent_modules/exception_design/`
- Module 6: `agent_modules/solution_packaging/`

运行要求：

- Agent 每一轮都应先按 Git Skill 判断当前模块，再读取对应模块规则。
- Agent 不应只依赖系统提示词自行发挥；模块边界、JSON 字段、题型规则和流转规则必须以 Git Skill 为准。
- 如果平台支持工具调用日志，建议检查每个模块输出前是否读取过当前模块 Skill 材料。

## 2. RAG 上传文件

请把以下文件作为本地 RAG 材料上传：

```text
agent_platform_package/rag_upload/01_training_summary.md
agent_platform_package/rag_upload/02_rpa_boundary_knowledge.md
agent_platform_package/rag_upload/03_negative_examples.md
agent_platform_package/rag_upload/04_logistics_interception_case.md
agent_platform_package/rag_upload/05_requirement_template_fields.md
agent_platform_package/rag_upload/06_yingdao_common_capability_cards.md
agent_platform_package/rag_upload/07_online_spreadsheet_capabilities.md
agent_platform_package/rag_upload/08_report_collection_and_daily_report_scenario.md
agent_platform_package/rag_upload/09_branch_exception_confirmation_rules.md
agent_platform_package/rag_upload/10_html_display_dictionary.md
agent_platform_package/rag_upload/11_report_quality_rules.md
agent_platform_package/rag_upload/12_captcha_capability_boundary.md
```

用途说明：

- `01_training_summary.md`: 需求分析方法摘要。
- `02_rpa_boundary_knowledge.md`: RPA 能力边界知识。
- `03_negative_examples.md`: 常见不适合直接 RPA 的反例。
- `04_logistics_interception_case.md`: 物流拦截案例。
- `05_requirement_template_fields.md`: 需求文档字段说明。
- `06_yingdao_common_capability_cards.md`: 影刀常用能力中文卡片，用业务语言说明可参考能力。
- `07_online_spreadsheet_capabilities.md`: 腾讯文档与在线表格能力、确认项和风险。
- `08_report_collection_and_daily_report_scenario.md`: 报表采集与日报生成场景，电商日报只是样例。
- `09_branch_exception_confirmation_rules.md`: 分支与异常的客户确认规则。
- `10_html_display_dictionary.md`: HTML 展示中文词典，降低英文和技术术语。
- `11_report_quality_rules.md`: 报告质量规则，确保问答投入转化为报告价值。
- `12_captcha_capability_boundary.md`: 验证码能力边界规则，说明验证码不是天然不可做，需结合适配指令、费用、准确率、人工兜底和授权合规判断。

RAG 只负责知识解释和案例参考，不负责流程控制。流程控制以 Git Skill 中的规则、schema 和系统提示词为准。

建议在平台中把 RAG 使用说明写入系统提示词：每个模块输出前必须检索对应 RAG；没有检索到可用材料时，必须明示“未检索到可用 RAG 依据”，不能假装引用材料。

模块与 RAG 对应关系：

- 模块 2 需求澄清：`01_training_summary.md`、`03_negative_examples.md`、`04_logistics_interception_case.md`、`05_requirement_template_fields.md`。
- 模块 3 RPA 能力边界：`02_rpa_boundary_knowledge.md`、`03_negative_examples.md`、`06_yingdao_common_capability_cards.md`、`07_online_spreadsheet_capabilities.md`、`12_captcha_capability_boundary.md`。
- 模块 4 流程拆解：`06_yingdao_common_capability_cards.md`、`07_online_spreadsheet_capabilities.md`、`08_report_collection_and_daily_report_scenario.md`。
- 模块 5 异常设计：`09_branch_exception_confirmation_rules.md`、`12_captcha_capability_boundary.md`，并结合模块 3 和模块 4 的上游结果。
- 模块 6 方案打包：`10_html_display_dictionary.md`、`11_report_quality_rules.md`、`05_requirement_template_fields.md`。

## 3. 系统提示词

请把以下文件内容复制到 Agent 平台的系统提示词编辑区：

```text
agent_platform_package/system_prompt/agent-system-prompt.md
```

系统提示词负责最高层行为约束，例如：

- 最高优先级规则：Git Skill 规则 > 本系统提示词 > RAG 材料 > Agent 自行推断。
- 每轮先遵循 Git Skill，再检索对应 RAG，最后输出结构化结果。
- 每轮必须读取上一轮 `requirement_memory` 和 `requirement_memory_document`，并输出更新后的记忆体和中文记忆文档。
- 区分客户已确认、RAG 建议、Agent 推断待确认、开发前必须补充确认。
- 优先使用选择题澄清。
- 根据题目含义切换 `single_choice` 和 `multiple_choice`：唯一答案使用单选，平台、系统、数据来源、字段、对象范围、异常处理等多答案问题使用多选。
- 每题必须同时保留“不确定”和“其他”路径；补充说明通过始终可见的 `supplement_text` 承载，不要把补充要求写进“其他”标签。
- 所有补充选项必须加入输入框，由 `supplement_text` 承载。
- 不从客户第一句话直接给 RPA 可行性结论。
- 模块 2 只做需求边界澄清和预筛，不做最终可行性判断。
- 模块 3 做 RPA 能力边界判断，验证码按条件能力项处理。
- 模块 4 拆业务流程卡片，不生成精确点击路径。
- 模块 5 做半实施级异常、人工复核和日志设计。
- 模块 6 输出一份统一中文落地分析报告，不把未确认内容伪装成开发事实。
- 当当前模块已满足进入下一模块的条件时，自动说明原因并进入下一模块提问，不要求用户手动发送“继续”。

## 4. 推荐首轮测试

可以用下面这句话测试 Agent：

```text
我想让机器人自动做物流拦截。
```

期望 Agent 不应直接进入开发方案，而应先问边界问题，例如：

- 物流单号从哪里来？
- 机器人需要在哪个系统里拦截？
- 拦截完成后如何通知结果？
- 是否存在验证码、扫码或人工复核？

## 5. 端到端测试路径

建议至少测试三类需求：

1. 条件适合 RPA：电商多平台日报。
2. 有语义风险但可控：邮件自动分类。
3. 不建议直接 RPA：物料名称同义判断、缺少稳定规则的主数据治理场景。

相关测试说明：

```text
agent_platform_package/testing/test_scenarios.md
agent_platform_package/testing/expected_outputs.md
agent_platform_package/testing/module_1_to_6_flow_test.md
agent_platform_package/testing/platform_test_checklist.md
```

## 6. 最终输出期望

Agent 在不同阶段按需输出一个顶层 JSON 对象，可包含：

```json
{
  "interaction_state": {},
  "answer_batch": {},
  "requirement_memory": {},
  "requirement_memory_document": "",
  "clarification_result": {},
  "rpa_boundary_result": {},
  "process_breakdown_result": {},
  "exception_design_result": {},
  "solution_package_result": {}
}
```

`requirement_memory` 和 `requirement_memory_document` 是跨模块记忆体：

- `requirement_memory` 用于机器读取，记录事实、推断、缺口、冲突、废弃问题、模块判断和 gate 状态。
- `requirement_memory_document` 用中文 Markdown 展示同一份记忆，便于业务人员核查和下一轮重新读取。
- 每轮开始必须先读取上一轮记忆体；每轮结束必须输出更新后的记忆体。
- 后续报告只能使用已经进入记忆体的事实、缺口、判断或待确认建议。

模块 6 完成时，`solution_package_result` 应包含：

- 底层事实 JSON。
- 统一中文 HTML 报告。
- `module_status`。
- `developer_alignment_status`。
- `confirmed_facts`。
- `inferred_recommendations`。
- `missing_required_items`。
- `conflict_or_uncertainty`。

统一中文 HTML 报告同时面向提需人、业务实施人员和 RPA 搭建人员，要求业务可读、实施可对齐，但不是最终开发说明书。
