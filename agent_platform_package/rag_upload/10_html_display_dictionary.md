# HTML 展示中文词典

本材料用于 RAG 检索，帮助 Agent 生成对客版和实施对齐版 HTML 时减少英文、机器字段和 IT 技术术语。内部 JSON 字段可以保留英文，但 HTML 展示应中文优先。

## 报告命名

| 原名称 | 推荐展示 |
|---|---|
| customer report | 对客方案报告 |
| developer report | 实施对齐报告 |
| development ready | 可进入搭建 |
| needs confirmation | 需补充确认 |
| blocked | 暂不可进入搭建 |
| not recommended | 暂不建议直接自动化 |

建议将“开发版 HTML”面向业务实施场景时命名为“实施对齐报告”，避免让业务专员误以为是程序开发文档。

## 状态词典

| 内部值 | HTML 展示 |
|---|---|
| `ready_for_development` | 可进入搭建 |
| `needs_confirmation` | 需补充确认 |
| `not_recommended` | 暂不建议直接自动化 |
| `blocked` | 暂不可进入搭建 |
| `suitable` | 适合优先考虑 RPA |
| `conditionally_suitable` | 条件满足后适合 |
| `not_ready` | 信息不足，暂不能判断 |
| `not_suitable_for_direct_rpa` | 不适合直接做无人值守 RPA |

## 字段词典

| 内部字段 | HTML 展示 |
|---|---|
| `confirmed_facts` | 已确认信息 |
| `inferred_recommendations` | 建议方案，待确认 |
| `missing_required_items` | 搭建前必补信息 |
| `conflict_or_uncertainty` | 冲突或不确定点 |
| `candidate_yingdao_capabilities` | 可参考的影刀能力 |
| `process_breakdown_result` | 流程拆解结果 |
| `exception_design_result` | 异常处理设计 |
| `rpa_boundary_result` | RPA 适配判断 |
| `solution_package_result` | 方案打包结果 |
| `developer_alignment_status` | 搭建准备状态 |
| `module_status` | 当前模块状态 |
| `source_traceability` | 来源追溯 |

## 来源标签词典

| 内部表达 | HTML 展示 |
|---|---|
| customer_confirmed | 客户已确认 |
| rag_supported | RAG 材料支持 |
| agent_inferred | Agent 推断，待确认 |
| missing_required | 搭建前必补 |
| implementation_verified | 需实施环境验证 |

## 技术词替换建议

| 不推荐展示 | 推荐展示 |
|---|---|
| selector | 页面元素定位 |
| parameter | 配置项 |
| JSON wrapper | 结构化结果 |
| enum | 固定选项 |
| capability family | 能力方向 |
| happy path | 正常流程 |
| exception branch | 异常处理分支 |
| retry policy | 重试规则 |
| validation | 校验 |
| source of truth | 唯一事实源 |

## 对客版表达要求

对客版应避免：

- 大量英文状态。
- 指令参数。
- 复杂字段名。
- 内部模块名。
- 技术实现细节。

对客版应突出：

- 业务目标。
- 当前是否适合继续。
- 客户还需要确认什么。
- 自动化大致会怎么工作。
- 风险和人工接管方式。

## 实施对齐版表达要求

实施对齐版可以比对客版更细，但仍应中文优先。

应展示：

- 已确认信息。
- 搭建前必补信息。
- 流程步骤。
- 每步可参考的影刀能力。
- 分支和异常来源。
- 需要客户确认的点。
- 验收口径。

不应展示：

- 未翻译的英文枚举作为标题。
- 大段机器 JSON。
- 精确点击路径、选择器、等待秒数和指令参数。
- 未确认却写成定案的异常策略。

## 示例

不推荐：

“developer_alignment_status: needs_confirmation”

推荐：

“搭建准备状态：需补充确认”

不推荐：

“candidate_yingdao_capabilities: web automation, loop, condition judgment”

推荐：

“可参考的影刀能力：网页操作、循环处理、条件判断”

