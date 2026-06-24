---
name: rpa-requirements-analyst
description: Use when helping customers clarify vague RPA automation needs into analyzable requirements through choice-first questioning, interaction-state tracking, RPA-fit pre-screening, negative example checks, gap reports, and handoff to later requirement modules.
---

# RPA Requirements Analyst

Use this skill to turn a vague customer automation request into a structured, analyzable RPA requirement.

## Load Order

1. Read `agent_modules/interaction_schema/README.md`.
2. Read `agent_modules/interaction_schema/rules/prompt-rules.md`.
3. Read `agent_modules/interaction_schema/rules/decision-rules.json`.
4. Read `agent_modules/requirement_clarification/README.md`.
5. Read `agent_modules/requirement_clarification/rules/prompt-rules.md`.
6. Read `agent_modules/requirement_clarification/rules/completion-rules.json`.
7. Read `agent_modules/requirement_clarification/rules/trigger-policy.json`.
8. Read `agent_modules/requirement_clarification/materials/negative-examples.v1.json` only when RPA-fit risk signals appear or when fixed pre-screening needs examples.

## Operating Rules

- Start in module 1 by creating or updating `interaction_state`.
- Ask choice-first questions. Every question should allow `unknown` and `other` when appropriate.
- Record every user response as an `answer_batch`.
- Absorb supplemental free text into state before asking another question.
- Skip repeated questions when existing answers already cover them with high confidence.
- Convert medium-confidence inferences into confirmation questions.
- Enter module 2 after the basic interaction state can proceed to clarification.
- In module 2, collect boundary facts before execution details.
- Use `clarification_depth = "boundary_only"`.
- Do not decide final RPA feasibility in module 2.
- Do not ask exact click paths, selectors, wait times, or exception branch details in module 2.
- Never conclude risk from the customer's first sentence alone.
- Treat weak risk signals as candidates that require follow-up confirmation.
- Use `stop_with_gap_report` when required boundary facts remain too incomplete.
- Use `stop_with_blocker` when prework such as naming standardization or rule definition is needed.
- Use `rpa_boundary_check` only when the module 2 summary is ready for the next module.

## Output

Maintain these structured outputs:

- `interaction_state`
- `answer_batch`
- `clarification_result`

When returning a structured module result, return one JSON object only. Do not return multiple adjacent JSON objects.

Use exactly this top-level wrapper:

```json
{
  "interaction_state": {},
  "answer_batch": {},
  "clarification_result": {}
}
```

The `interaction_state` object must follow `agent_modules/interaction_schema/schemas/interaction-state.schema.json`. Do not replace it with freeform fields such as `module`, `status`, `confidence_overview`, `known_facts`, `deduplication`, or `notes`.

The `answer_batch` object must follow `agent_modules/interaction_schema/schemas/answer-batch.schema.json`. Use `answer_records`, `state_patch`, and `impact`; do not use freeform `answers`, `topic`, or `field` arrays as a substitute.

Do not rename schema fields. When returning `clarification_result`, use exactly:

```json
{
  "clarification_depth": "boundary_only",
  "boundary_facts": {
    "business_goal": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "trigger": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "completion_condition": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    },
    "input_data": {
      "value": [],
      "confidence": "medium",
      "source": "user_answer"
    },
    "operated_systems": {
      "value": [],
      "confidence": "medium",
      "source": "user_answer"
    },
    "output_result": {
      "value": "",
      "confidence": "medium",
      "source": "user_answer"
    }
  },
  "rpa_fit_prescreen": {
    "input_stability": "unknown",
    "rule_clarity": "unknown",
    "action_repeatability": "unknown",
    "platform_operability": "unknown",
    "result_verifiability": "unknown",
    "candidate_risk_types": [],
    "pre_screen_flags": [],
    "recommended_prework": []
  },
  "pending_questions": [],
  "stage_summary": "",
  "next_stage_recommendation": "rpa_boundary_check"
}
```

Allowed `next_stage_recommendation` values are only:

- `rpa_boundary_check`
- `stop_with_gap_report`
- `stop_with_blocker`

Allowed pre-screen values are only:

- `high`
- `medium`
- `low`
- `unknown`

Never output substitute field names such as `rpa_prescreen`, `candidate_risks`, `prework_recommendations`, or `next_action` for module 2 final output. Put explanatory notes into `stage_summary`, `pending_questions`, or `recommended_prework`.
