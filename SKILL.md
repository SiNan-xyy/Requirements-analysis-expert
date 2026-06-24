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
