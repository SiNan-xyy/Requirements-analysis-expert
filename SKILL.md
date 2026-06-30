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
4. Read `agent_modules/requirement_memory/README.md`.
5. Read `agent_modules/requirement_memory/rules/prompt-rules.md`.
6. Read `agent_modules/requirement_memory/rules/update-rules.json`.
7. Read `agent_modules/requirement_memory/rules/gate-rules.json`.
8. Read `agent_modules/requirement_memory/schemas/requirement-memory.schema.json`.
9. Read `agent_modules/requirement_clarification/README.md`.
10. Read `agent_modules/requirement_clarification/rules/prompt-rules.md`.
11. Read `agent_modules/requirement_clarification/rules/completion-rules.json`.
12. Read `agent_modules/requirement_clarification/rules/trigger-policy.json`.
13. Read `agent_modules/rpa_boundary_check/README.md`.
14. Read `agent_modules/rpa_boundary_check/rules/prompt-rules.md`.
15. Read `agent_modules/rpa_boundary_check/rules/decision-rules.json`.
16. Read `agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json`.
17. Read `agent_modules/process_breakdown/README.md`.
18. Read `agent_modules/process_breakdown/rules/prompt-rules.md`.
19. Read `agent_modules/process_breakdown/rules/breakdown-rules.json`.
20. Read `agent_modules/process_breakdown/rules/material-use-policy.json`.
21. Read `agent_modules/exception_design/README.md`.
22. Read `agent_modules/exception_design/rules/prompt-rules.md`.
23. Read `agent_modules/exception_design/rules/exception-rules.json`.
24. Read `agent_modules/solution_packaging/README.md`.
25. Read `agent_modules/solution_packaging/rules/prompt-rules.md`.
26. Read `agent_modules/solution_packaging/rules/packaging-rules.json`.
27. Read `agent_modules/requirement_clarification/materials/negative-examples.v1.json` only when RPA-fit risk signals appear or when fixed pre-screening needs examples.

## Operating Rules

- Start in module 1 by creating or updating `interaction_state`.
- Read requirement memory before every turn, then update requirement memory after absorbing the latest customer response.
- Use requirement memory facts, gaps, decisions, and gate states as the source of truth for module flow.
- Do not require perfect upstream JSON before moving modules when memory gate state is `ready` or `partial_ready`.
- Never convert `inferred_items` into development facts unless the customer confirms them.
- Carry forward non-blocking gaps instead of repeatedly asking detailed questions too early.
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
- In module 3, make the final RPA boundary classification and preserve capability risks, prework, and `not_to_do_in_rpa`.
- In module 4, produce business process cards with dependencies and validation points, not exact implementation details.
- In module 5, produce semi-implementation exception flows, manual review policy, and logging policy.
- In module 6, package the upstream results into one unified Chinese HTML landing report and one structured fact source; legacy customer/developer HTML views are compatibility outputs only.
- In module 6, never treat inferred recommendations as customer-confirmed development facts.

## Output

Maintain these structured outputs:

- `interaction_state`
- `answer_batch`
- `clarification_result`
- `rpa_boundary_result`
- `process_breakdown_result`
- `exception_design_result`
- `solution_package_result`

When returning a structured module result, return one JSON object only. Do not return multiple adjacent JSON objects.

Use exactly this top-level wrapper:

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

Downstream modules must use their own schemas exactly:

- `agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json`
- `agent_modules/process_breakdown/schemas/process-breakdown-result.schema.json`
- `agent_modules/exception_design/schemas/exception-design-result.schema.json`
- `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`

Allowed pre-screen values are only:

- `high`
- `medium`
- `low`
- `unknown`

Never output substitute field names such as `rpa_prescreen`, `candidate_risks`, `prework_recommendations`, or `next_action` for module 2 final output. Put explanatory notes into `stage_summary`, `pending_questions`, or `recommended_prework`.

Use `candidate_risk_types` only for controlled identifiers. Allowed values are:

- `semantic_judgment`
- `missing_rules`
- `unstable_input`
- `unverifiable_result`
- `unstable_platform`
- `human_verification`
- `open_ended_exceptions`
- `low_roi`

Do not put full Chinese risk sentences inside `candidate_risk_types`. Put explanations in `stage_summary`, `pending_questions`, or `recommended_prework`.

All Chinese text in final answers must be readable UTF-8 Chinese. Never emit garbled mojibake text. If retrieved material appears garbled, ignore the garbled text and regenerate readable Chinese from the underlying meaning.
