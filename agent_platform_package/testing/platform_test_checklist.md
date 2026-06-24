# 平台测试检查清单

用于验证 Agent 平台是否正确加载 Git Skill、RAG 和系统提示词。

## 基础加载

- Git Skill 能从仓库分支加载。
- Agent 能读取根目录 `SKILL.md`。
- Agent 能按 Load Order 引用 `agent_modules/` 下的规则文件。
- RAG 能检索 `agent_platform_package/rag_upload/` 中的材料。
- 系统提示词已复制 `agent_platform_package/system_prompt/agent-system-prompt.md`。

## 交互行为

- 客户输入模糊需求后，Agent 先问边界问题，不直接给开发方案。
- 每轮优先 3 到 5 个选择题。
- 每题保留“暂不确定”或“其他，请补充”。
- 用户补充的信息会被吸收，不重复提问。
- 中等置信度推断会转成确认题。

## 模块 2 边界

- 不问具体点击路径。
- 不问页面选择器。
- 不问等待时间。
- 不设计异常分支细节。
- 不做最终 RPA 可行性结论。
- 不从第一句话直接下风险结论。

## 输出契约

最终结构化结果只能返回一个 JSON 对象，顶层必须包含：

- `interaction_state`
- `answer_batch`
- `clarification_result`

不得连续输出三个相邻 JSON 对象。

`interaction_state` 必须使用模块 1 标准字段，不得使用：

- `module`
- `confidence_overview`
- `known_facts`
- `deduplication`
- `notes`

`answer_batch` 必须使用：

- `answer_records`
- `state_patch`
- `impact`

不得使用：

- `answers`
- `topic`
- `field`

模块 2 最终输出必须包含：

- `clarification_depth`
- `boundary_facts`
- `rpa_fit_prescreen`
- `pending_questions`
- `stage_summary`
- `next_stage_recommendation`

模块 2 最终输出不得使用这些替代字段：

- `rpa_prescreen`
- `candidate_risks`
- `prework_recommendations`
- `next_action`

预筛等级只能是：

- `high`
- `medium`
- `low`
- `unknown`

不得输出：

- `medium_high`
- `medium_low`
- 自定义等级
