# Agent 平台集成说明

这份说明用于把当前项目接入你的 Agent 平台。你的平台目前支持三类能力：

- 从 Git 下载 Skill。
- 本地上传 RAG 材料。
- 手动编辑系统提示词。

当前项目已经完成模块 1-6，可以支撑客户把模糊 RPA 需求推进到需求澄清、RPA 能力边界判断、流程拆解、异常设计和方案打包。

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

## 2. RAG 上传文件

请把以下文件作为本地 RAG 材料上传：

```text
agent_platform_package/rag_upload/01_training_summary.md
agent_platform_package/rag_upload/02_rpa_boundary_knowledge.md
agent_platform_package/rag_upload/03_negative_examples.md
agent_platform_package/rag_upload/04_logistics_interception_case.md
agent_platform_package/rag_upload/05_requirement_template_fields.md
```

用途说明：

- `01_training_summary.md`: 需求分析方法摘要。
- `02_rpa_boundary_knowledge.md`: RPA 能力边界知识。
- `03_negative_examples.md`: 常见不适合直接 RPA 的反例。
- `04_logistics_interception_case.md`: 物流拦截案例。
- `05_requirement_template_fields.md`: 需求文档字段说明。

RAG 只负责知识解释和案例参考，不负责流程控制。流程控制以 Git Skill 中的规则、schema 和系统提示词为准。

## 3. 系统提示词

请把以下文件内容复制到 Agent 平台的系统提示词编辑区：

```text
agent_platform_package/system_prompt/agent-system-prompt.md
```

系统提示词负责最高层行为约束，例如：

- 优先使用选择题澄清。
- 每题保留“不确定”或“其他，请补充”的路径。
- 不从客户第一句话直接下 RPA 可行性结论。
- 模块 2 只做需求边界澄清和预筛，不做最终可行性判断。
- 模块 3 才做 RPA 能力边界判断。
- 模块 4 只拆业务流程卡片，不生成精确点击路径。
- 模块 5 只做半实施级异常、人审和日志设计。
- 模块 6 只做方案打包，不把未确认内容伪装成开发事实。

## 4. 推荐首轮测试

可以用下面这句话测试 Agent：

```text
我想让机器人自动做物流拦截。
```

期望 Agent 不应直接进入开发方案，而应先问边界问题，例如：

- 物流单号从哪里来？
- 机器人需要在哪个系统里拦截？
- 拦截完成后如何通知结果？
- 是否存在验证码或人工复核？

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
  "clarification_result": {},
  "rpa_boundary_result": {},
  "process_breakdown_result": {},
  "exception_design_result": {},
  "solution_package_result": {}
}
```

模块 6 完成时，`solution_package_result` 应包含：

- 底层事实 JSON。
- 对客版 HTML。
- 对开发版 HTML。
- `module_status`。
- `developer_alignment_status`。
- `confirmed_facts`。
- `inferred_recommendations`。
- `missing_required_items`。
- `conflict_or_uncertainty`。

开发版 HTML 是开发对齐包，不是最终开发说明书。
