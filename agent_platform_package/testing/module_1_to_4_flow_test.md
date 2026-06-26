# 模块 1-4 流程测试说明

## 测试目标

验证 Agent 是否能把一个模糊需求从交互采集流转到流程拆解，并保持每个模块的职责边界。

## 推荐测试输入

客户输入：

> 我要做一个自动统计电商不同平台的日数据，然后写入到腾讯文档，形成日报表的应用。

## 模块 1：交互与答案记录

模块 1 应先用选择题收集信息，并记录为 `answer_batch` 和 `interaction_state`。

通过条件：

- `answer_batch.answer_records` 记录用户选择。
- `answer_batch.state_patch` 更新业务目标、触发条件、操作系统等字段。
- `interaction_state.next_action` 在必答信息完成后进入 `enter_next_module`。

失败信号：

- 直接输出方案。
- 不记录 `state_patch`。
- 重复询问用户已经高置信回答过的问题。

## 模块 2：需求边界澄清

模块 2 消费模块 1 的状态，输出 `clarification_result`。

通过条件：

- `boundary_facts` 覆盖业务目标、触发条件、完成条件、输入数据、操作系统、输出结果。
- `rpa_fit_prescreen` 覆盖输入稳定性、规则清晰度、动作重复性、平台可操作性、结果可验证性。
- 当边界足够清晰时，`next_stage_recommendation` 为 `rpa_boundary_check`。

失败信号：

- 在模块 2 直接下最终 RPA 可行性结论。
- 询问点击路径、选择器、等待时间。
- 把 `rpa_fit_prescreen` 写成 `rpa_prescreen`。

## 模块 3：RPA 能力边界判断

模块 3 消费 `clarification_result`，输出 `rpa_boundary_result`。

通过条件：

- `decision.classification` 是 `suitable`、`conditionally_suitable`、`not_ready`、`not_suitable_for_direct_rpa` 之一。
- 对电商日报场景，未完全确认字段映射、日期口径、登录稳定性、核验方式前，通常应为 `conditionally_suitable`。
- 如果可以进入下一步，`next_stage_recommendation` 为 `process_breakdown`。

失败信号：

- 只因为有影刀指令就判定适合。
- 重复模块 2 的边界澄清。
- 直接生成流程卡片或开发步骤。

## 模块 4：流程拆解

模块 4 消费 `clarification_result` 和 `rpa_boundary_result`，输出 `process_breakdown_result`。

通过条件：

- 只接受 `suitable` 或 `conditionally_suitable` 作为来源判断。
- `breakdown_depth` 是 `business_process_cards_with_candidate_capabilities`。
- `process_cards` 是业务流程卡片，包含业务目的、输入、操作摘要、输出、候选影刀能力族、依赖和前置条件。
- 保留 `assumptions`、`validation_points`、`cross_step_dependencies`、`open_questions`。
- 下一阶段建议为 `exception_design`。

失败信号：

- 输出精确点击路径、选择器、等待时间、重试次数或指令参数。
- 直接设计异常分支。
- 生成 HTML。

## 流转总览

1. 模块 1 完成答案记录后进入 `enter_next_module`。
2. 模块 2 边界足够清晰后进入 `rpa_boundary_check`。
3. 模块 3 判定 `suitable` 或 `conditionally_suitable` 后进入 `process_breakdown`。
4. 模块 4 生成业务流程卡片后进入 `exception_design`。

## 人工验收结论

若以上四段全部通过，可以认为模块 1-4 主链路通畅；若任一模块失败，应先修复该模块合同，再继续开发模块 5。
