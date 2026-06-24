# Agent 平台集成说明

这份说明用于把当前项目放入 Agent 平台。你的平台支持三类能力：

- 从 Git 下载 Skill
- 本地上传 RAG
- 手动编辑系统提示词

## 1. Git Skill 配置

Git 仓库地址：

```text
https://github.com/SiNan-xyy/Requirements-analysis-expert.git
```

如果平台支持选择分支，建议先使用：

```text
codex/agent-platform-package
```

如果你希望使用主分支，需要先把该分支合并并推送到 `master`。

Skill 入口文件：

```text
SKILL.md
```

Skill 依赖的规则目录：

```text
agent_modules/interaction_schema/
agent_modules/requirement_clarification/
```

平台下载 Git Skill 后，Agent 应首先读取 `SKILL.md`，再按其中 Load Order 读取模块规则。

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

- `01_training_summary.md`：需求分析方法摘要。
- `02_rpa_boundary_knowledge.md`：RPA 能力边界知识。
- `03_negative_examples.md`：常见不适合直接 RPA 的反例。
- `04_logistics_interception_case.md`：物流拦截案例。
- `05_requirement_template_fields.md`：需求文档字段解释。

RAG 只负责知识解释和案例参考，不负责流程控制。流程控制以 Git Skill 中的规则为准。

## 3. 系统提示词

请复制以下文件内容到 Agent 平台的系统提示词编辑区：

```text
agent_platform_package/system_prompt/agent-system-prompt.md
```

系统提示词负责最高层行为约束，例如：

- 选择题优先。
- 每题保留补充选项。
- 不从第一句话直接下结论。
- 模块 2 不做最终 RPA 可行性判断。
- 信息不足时输出缺口。
- 前置治理问题使用 `stop_with_blocker`。

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

## 5. 模块 2 期望输出

当客户回答足够清楚时，Agent 应形成 `clarification_result`，至少包含：

- `clarification_depth`: `boundary_only`
- `boundary_facts`
- `rpa_fit_prescreen`
- `pending_questions`
- `stage_summary`
- `next_stage_recommendation`

当需求可以进入后续能力边界评估时：

```text
next_stage_recommendation = rpa_boundary_check
```

当关键字段不足时：

```text
next_stage_recommendation = stop_with_gap_report
```

当前置治理问题阻塞继续分析时：

```text
next_stage_recommendation = stop_with_blocker
```

## 6. 后续扩展方式

后续继续开发模块 3 到模块 8 时，建议保持同样分类：

- 执行逻辑、状态机、输出契约：放入 Git Skill。
- 案例、培训材料、解释性知识：上传 RAG。
- 高层行为边界：写入系统提示词。

