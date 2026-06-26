# 平台测试检查清单

用于验证 Agent 平台是否正确加载 Git Skill、RAG 材料和系统提示词，并确认模块 1-4 的输出合同是否稳定。

## 基础加载

- Git Skill 可以从当前仓库分支加载。
- Agent 可以读取根目录 `SKILL.md`。
- Agent 可以引用 `agent_modules/` 下的规则、schema、fixtures。
- RAG 可以检索 `agent_platform_package/rag_upload/` 中的材料。
- 系统提示词使用 `agent_platform_package/system_prompt/agent-system-prompt.md`。

## 交互行为

- 客户输入模糊需求后，Agent 先问边界问题，不直接给开发方案。
- 每轮优先使用选择题。
- 每题保留“不确定”或“其他，请补充”路径。
- 用户补充的信息会被吸收，不重复追问同义问题。
- 中等置信度推断会变成确认题。

## 输出合同

- 结构化结果只能返回一个顶层 JSON 对象。
- 根据当前阶段按需包含 `interaction_state`、`answer_batch`、`clarification_result`、`rpa_boundary_result`、`process_breakdown_result`。
- `answer_batch` 必须使用 `answer_records`、`state_patch`、`impact`。
- 模块 2 必须使用 `rpa_fit_prescreen`，不得替换成 `rpa_prescreen`。
- 模块 3 的 `decision.classification` 必须使用受控枚举。
- 模块 4 必须输出业务流程卡片，不得输出精确点击路径或指令参数。

## 模块边界

- 模块 2 不问具体点击路径、页面选择器、等待时间、异常分支细节。
- 模块 3 不重复模块 2 的边界澄清，不生成流程拆解。
- 模块 4 不覆盖模块 3 的边界判断，不设计异常分支，不生成 HTML。

## 可读性

- 中文输出必须可读。
- 不得出现历史编码乱码。
- 若输出乱码，应优先检查 RAG 文档、测试材料和系统提示词是否被错误编码保存。
