# Agent Interaction Schema Design

## Goal

Build the first module of the RPA requirements analyst agent: a lightweight interaction state, choice-question schema, answer-writing model, and progression rules that let the agent guide users from a vague need toward structured requirements without prematurely implementing later modules.

This module does not evaluate RPA feasibility, break down processes, design exceptions, or generate the final HTML blueprint. It only defines the interaction foundation those later modules will use.

## Context

The agent will help customers turn vague automation ideas into RPA requirements that can eventually be handed to developers. The confirmed interaction style is choice-first: the agent asks multiple-choice questions, every question includes an "other / supplement" route, and the user can add free-text details.

The design must avoid becoming a rigid form. If a user answers one question and also supplies details that satisfy other questions, the agent should absorb that information, update the requirement state, and avoid asking repeated questions.

## Scope

Module 1 includes:

- Interaction state model
- Choice-question model
- Answer record and state patch model
- Next-step decision rules
- Question deduplication and answer absorption rules

Module 1 excludes:

- RPA capability boundary scoring
- Process breakdown logic
- Exception and branch design logic
- HTML report generation
- Platform-specific UI rendering
- Full production code implementation

## Design Choice

Use a balanced approach: lightweight schema plus prompt rules.

This avoids the two extremes:

- Pure schema would be stable but too rigid for early product iteration.
- Pure prompt logic would feel natural but would be harder to integrate into the existing agent platform.

The chosen design gives the platform stable structures while leaving enough freedom for the agent to ask natural follow-up questions and absorb extra information.

## Interaction State Model

The agent keeps an `interaction_state` object that tells it where the conversation is and what it should do next.

```json
{
  "stage": "intake",
  "status": "collecting",
  "completion_level": "insufficient",
  "answered_question_ids": [],
  "pending_question_ids": [],
  "last_summary": "",
  "next_action": "ask_questions"
}
```

### `stage`

Allowed values:

- `intake`: initial demand intake
- `clarification`: basic requirement clarification
- `rpa_boundary_check`: RPA capability boundary assessment
- `process_breakdown`: process step breakdown
- `exception_design`: branch and exception design
- `blueprint_ready`: ready for final blueprint generation

Module 1 only defines these values. Later modules own the detailed logic inside each stage.

### `status`

Allowed values:

- `collecting`: collecting answers
- `summarizing`: summarizing the current understanding
- `waiting_user_confirm`: waiting for the user to confirm the summary
- `ready_for_next_module`: ready to move to the next module
- `blocked`: blocked by missing or impossible information

### `completion_level`

Allowed values:

- `insufficient`: information is too incomplete to proceed
- `partial`: enough for an early summary, not enough for downstream work
- `workable`: enough to enter the next module
- `development_ready`: enough for final blueprint generation

### `next_action`

Allowed values:

- `ask_questions`
- `ask_repair_question`
- `request_free_text`
- `summarize_and_confirm`
- `enter_next_module`
- `stop_with_gap_report`
- `stop_with_blocker`

## Choice-Question Model

Each question is represented as a structured object. Question type only controls how many options can be selected. Free text is a general capability, not a separate question type.

```json
{
  "question_id": "trigger_type",
  "stage": "clarification",
  "question": "这个流程通常从什么事件开始？",
  "type": "single_choice",
  "importance": "required",
  "blocks_stage_progression": true,
  "allow_unknown": true,
  "target_field": "requirement.trigger.type",
  "options": [
    {
      "label": "固定时间自动开始",
      "value": "scheduled",
      "description": "例如每天 9 点、每小时一次。"
    },
    {
      "label": "收到飞书/钉钉消息后开始",
      "value": "message_received",
      "description": "例如收到订单号、物流单号、审批消息。"
    },
    {
      "label": "收到文件或表格后开始",
      "value": "file_received",
      "description": "例如收到 Excel、CSV、下载文件。"
    },
    {
      "label": "人工点击按钮后开始",
      "value": "manual_start",
      "description": "适合人工确认后再执行的流程。"
    },
    {
      "label": "暂不确定",
      "value": "unknown"
    },
    {
      "label": "其他，请补充",
      "value": "other"
    }
  ],
  "free_text": {
    "enabled": true,
    "field": "requirement.trigger.note",
    "required_when": {
      "selected_values_include": ["other"]
    }
  },
  "retry_policy": {
    "max_retries": 2,
    "fallback_to_single_question": true
  }
}
```

### Question Types

Allowed values:

- `single_choice`: user selects one option
- `multiple_choice`: user selects one or more options

### Importance

Allowed values:

- `required`: must be answered or explicitly marked unknown; can block stage progression
- `recommended`: improves requirement quality; unanswered values enter the pending list but do not necessarily block progression
- `optional`: background or metadata; unanswered values can remain blank

`importance` is the business-level classification. `blocks_stage_progression` is the workflow-level consequence.

### Free Text

Every question can support supplemental text. If the user chooses `other`, free text is required. If the user chooses a normal option, free text is optional and may still be used to enrich the requirement state.

## Answer Writing Model

Each user response produces two things:

1. An `answer_record` preserving what the user answered.
2. A `state_patch` updating structured requirement fields.

```json
{
  "answer_record": {
    "question_id": "trigger_type",
    "selected_values": ["message_received"],
    "free_text": "客户把物流单号发给飞书机器人后触发",
    "answer_status": "answered",
    "confidence": "high"
  },
  "state_patch": {
    "requirement.trigger.type": "message_received",
    "requirement.trigger.description": "客户把物流单号发给飞书机器人后触发"
  }
}
```

### Answer Status

Allowed values:

- `answered`: user gave a usable answer
- `unknown`: user explicitly chose or stated uncertainty
- `skipped`: user skipped the question
- `invalid`: answer cannot be mapped or understood
- `needs_free_text`: user chose `other` but did not provide required supplemental text

### Confidence

Allowed values:

- `high`: clear answer or high-confidence inference
- `medium`: usable but somewhat ambiguous
- `low`: explicitly uncertain or weakly inferred
- `none`: skipped or invalid

### Required Question Behavior

For a `required` question:

- `answered` may allow progression.
- `unknown` records the uncertainty but usually blocks progression if the field is stage-critical.
- `skipped` blocks progression.
- `invalid` triggers a repair question.
- `needs_free_text` triggers a supplemental text request.

For `recommended` and `optional` questions, missing information should be preserved in a pending list rather than blocking by default.

## Next-Step Decision Rules

After each answer batch, the agent must decide the next action by applying rules in order.

```json
{
  "decision_rules": [
    {
      "condition": "has_invalid_required_answer",
      "next_action": "ask_repair_question"
    },
    {
      "condition": "has_other_without_free_text",
      "next_action": "request_free_text"
    },
    {
      "condition": "has_unanswered_required_questions",
      "next_action": "ask_questions"
    },
    {
      "condition": "stage_required_questions_complete",
      "next_action": "summarize_and_confirm"
    },
    {
      "condition": "user_confirmed_summary",
      "next_action": "enter_next_module"
    },
    {
      "condition": "too_many_unknown_required_fields",
      "next_action": "stop_with_gap_report"
    }
  ]
}
```

### Gap Stop Policy

The agent should stop and produce a gap report when the user cannot answer enough stage-critical questions.

```json
{
  "gap_stop_policy": {
    "max_required_unknown_count": 3,
    "max_retries_per_question": 2,
    "fallback_to_single_question": true
  }
}
```

If an entire batch is skipped, the agent should downgrade to a single, simpler question instead of repeating the whole batch.

## Question Deduplication And Answer Absorption

The agent must avoid repeated questions. This is especially important because users often answer more than the current question asks.

Example:

If the agent asks where the logistics interception platform is and the user replies with `https://shop.yingdao.com/worktop/logistics-list`, the agent should infer that the system is likely a browser web system. It should not later ask the same user whether this system is web or desktop as a fresh question.

### Absorption Flow

```text
User answer
  -> Extract explicit answer to current question
  -> Extract additional useful fields from free text
  -> Apply all field updates
  -> Recompute pending questions
  -> Ask only questions that remain unresolved
```

### Question Metadata For Deduplication

Questions can define skip and inference rules.

```json
{
  "question_id": "system_type",
  "target_field": "systems[].type",
  "depends_on_fields": ["systems[].name", "systems[].entry_url"],
  "skip_if": [
    {
      "field": "systems[].entry_url",
      "matches": "^https?://",
      "infer": {
        "systems[].type": "browser_web"
      },
      "confidence": "high"
    }
  ]
}
```

### Field Provenance

Fields inferred from user answers should preserve their source and confidence.

```json
{
  "systems[].type": {
    "value": "browser_web",
    "source": "inferred_from_url",
    "confidence": "high"
  }
}
```

If the field is not certain, the agent should ask a confirmation question instead of repeating the original question:

```text
我根据你提供的网址判断：影刀商城后台是浏览器网页系统。这个判断对吗？
A. 对
B. 不对，它是客户端
C. 不确定
D. 其他，请补充
```

### Deduplication Rules

- Extract all useful fields from each answer, not only the current question's target field.
- Recompute `pending_question_ids` after every answer batch.
- Skip a question if its `target_field` already has a high-confidence answer.
- Convert medium-confidence inferences into confirmation questions.
- Mark related questions as answered if the user's supplemental text covers them.
- If a later explicit user answer conflicts with an inferred value, prefer the latest explicit user answer and preserve the conflict in a review note.

## Prompt Rules For Module 1

The agent should follow these prompt rules while using this module:

- Ask 3-5 questions per batch when the user is engaged and the context is clear.
- Ask only one simplified question if the prior batch was skipped or unclear.
- Prefer business language over technical language.
- Always include `other` and `unknown` routes for required questions.
- Summarize what was learned before entering the next module.
- Do not ask a question if the answer was already supplied or can be inferred with high confidence.
- Do not generate downstream artifacts until the current stage summary is confirmed.

## Acceptance Criteria

The module 1 design is accepted when:

- It defines a stable interaction state.
- It defines a question schema with single-choice and multiple-choice only.
- It supports required, recommended, and optional questions.
- It supports free text on every question and requires it when `other` is selected.
- It records skipped, unknown, invalid, and incomplete answers distinctly.
- It prevents repeated questions through answer absorption and field-level deduplication.
- It stops with a gap report instead of forcing progress when too many required fields are unknown.
- It leaves RPA feasibility, process breakdown, exception handling, and HTML generation to later modules.

