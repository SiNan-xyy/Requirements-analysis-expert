# 平台测试检查清单

用于验证 Agent 平台是否正确加载 Git Skill、RAG 材料和系统提示词，并确认模块 1-6 的输出合同稳定。

## 基础加载

- Git Skill 可以从当前仓库 `master` 分支加载。
- Agent 可以读取根目录 `SKILL.md`。
- Agent 可以引用 `agent_modules/` 下的规则、schema 和 fixtures。
- RAG 可以检索 `agent_platform_package/rag_upload/` 中的材料。
- 系统提示词使用 `agent_platform_package/system_prompt/agent-system-prompt.md`。

## 交互行为

- 客户输入模糊需求后，Agent 先问边界问题，不直接给开发方案。
- 每轮优先使用选择题。
- 每题保留“不确定”或“其他，请补充”的路径。
- 用户补充的信息会被吸收，不重复追问同义问题。
- 中等置信度推断会变成确认题。
- 不从客户第一句话直接判断 RPA 是否可做。

## 输出合同

- 结构化结果只能返回一个顶层 JSON 对象。
- 根据当前阶段按需包含 `interaction_state`、`answer_batch`、`clarification_result`、`rpa_boundary_result`、`process_breakdown_result`、`exception_design_result`、`solution_package_result`。
- `interaction_state` 必须使用标准字段，不得使用 `module`、`known_facts`、`deduplication` 等自由替代字段。
- `answer_batch` 必须使用 `answer_records`、`state_patch`、`impact`。
- 模块 2 必须使用 `rpa_fit_prescreen`，不得替换成 `rpa_prescreen`。
- 模块 3 的 `decision.classification` 必须使用受控枚举。
- 模块 4 必须输出业务流程卡片，不得输出精确点击路径或指令参数。
- 模块 5 必须输出半实施级异常卡片、人审策略和日志策略。
- 模块 6 必须输出 `solution_package_result`，并区分模块完成状态和开发就绪状态。

## 模块边界

- 模块 2 不问具体点击路径、页面选择器、等待时间、异常分支细节。
- 模块 3 不重复模块 2 的边界澄清，不生成流程拆解。
- 模块 4 不覆盖模块 3 的边界判断，不设计异常分支，不生成 HTML。
- 模块 5 不生成最终方案包，不生成精确指令参数。
- 模块 6 不把推断内容写成客户已确认事实，不生成最终开发说明书。

## 模块 6 检查点

- `solution_package_result.fact_base.confirmed_facts` 只包含已确认事实。
- `inferred_recommendations` 必须 `requires_confirmation = true` 且 `can_be_used_for_development = false`。
- 当存在 high 阻塞缺失项时，不得输出 `developer_alignment_status = ready_for_development`。
- 对客 HTML 和对开发 HTML 必须来自同一份结构化事实源。
- 对开发 HTML 是开发对齐包，不是最终构建指南。
- 不得出现精确点击路径、选择器、等待 N 秒、重试 N 次、影刀指令参数等实现细节。

## 可读性

- 中文输出必须可读。
- 不得出现历史编码乱码。
- 如果 RAG 材料或测试材料出现乱码，应忽略乱码文本并用可读中文重述含义。

## 建议测试场景

- 物流拦截：验证模块 2 是否先问边界问题。
- 电商多平台日报：验证模块 3 是否输出条件适合，并保留字段映射、指标口径、日期口径和校验方式缺口。
- 邮件自动分类：验证语义判断风险是否进入低置信度或人工复核路径。
- 物料名称同义判断：验证不建议直接 RPA 时是否输出治理建议，而不是伪造自动化方案。
