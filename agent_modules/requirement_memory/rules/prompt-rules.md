# 需求记忆体提示词规则

## 每轮固定动作

1. 先读取当前需求记忆体。
2. 判断客户最新回答是在新增事实、修正事实、确认推断，还是回答缺口。
3. 更新 `F/I/G/C/R/D` 编号记录。
4. 根据 gate 规则判断当前模块是 `ready`、`partial_ready` 还是 `blocked`。
5. 只围绕仍然有效的缺口继续提问。

## 分层表达

- 客户明确说过的内容：写入 `confirmed_facts`。
- 上游模块基于已确认事实形成的稳定结论：写入 `confirmed_facts`，来源为 `upstream_confirmed`。
- Agent 根据经验、RAG 或上下文推测的内容：写入 `inferred_items`。
- 开发或判断前仍缺少的信息：写入 `gaps`。
- 客户更正前文、推翻旧信息：写入 `conflicts`，并退休旧问题或旧事实。

## 禁止事项

- 不要把 RAG 建议写成客户已确认事实。
- 不要把未回答的异常处理策略写成确定方案。
- 不要因为上游 JSON 字段缺失就丢失已经记录在记忆体里的事实。
- 不要重复询问已经由事实覆盖的问题。

## 输出口径

当需要展示给客户时，用中文说明：

- 已确认：可以作为后续分析依据。
- 待确认：需要客户补充或确认。
- 建议项：来自经验或材料库，不能直接当作客户已确认。
- 可继续：说明可以携带哪些缺口进入下一模块。

## Unknown And Other

- unknown means the customer cannot confirm now.
- other means the options do not cover a known answer.
- unknown must not require supplement text.
- other without supplement text must ask for supplement.
- unknown creates or updates a gap when the field is required.
- other with supplement can become a candidate fact or confirmed fact depending on confidence and wording.
