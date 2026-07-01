# Interaction Schema Module

This module defines the first layer of the RPA requirements analyst agent: the choice-first interaction state, question format, answer recording format, next-step decision rules, and deduplication rules.

It does not evaluate RPA feasibility, break down process steps, design exceptions, or generate HTML reports.

## Artifact Index

- `schemas/interaction-state.schema.json`: interaction state contract.
- `schemas/question.schema.json`: choice-question contract.
- `schemas/answer-batch.schema.json`: answer record and state patch contract.
- `rules/decision-rules.json`: ordered next-action rules and gap stop policy.
- `rules/prompt-rules.md`: agent prompt behavior rules.
- `fixtures/valid-interaction-state.json`: baseline interaction state example.
- `fixtures/valid-question-trigger-type.json`: required trigger question example.
- `fixtures/multiple-choice-with-supplement-required.json`: required multi-select question with supplement example.
- `fixtures/valid-answer-batch.json`: answer record and state patch example.
- `fixtures/deduplication-url-inference.json`: answer absorption example that infers a web system from a URL and skips repeated system questions.

## Usage

Use these files as the module 1 contract for agent platform integration.

1. Render questions from `schemas/question.schema.json` compatible objects.
2. Store every user response as an answer record.
3. Apply `state_patch` values into the shared requirement state.
4. Recompute pending questions after every answer batch.
5. Use `rules/decision-rules.json` to choose the next action.
6. Use `rules/prompt-rules.md` to keep the conversation concise and non-repetitive.

## Acceptance Criteria

- Questions support only `single_choice` and `multiple_choice` for platform rendering.
- Questions classify importance as `required`, `recommended`, or `optional`.
- Every question includes `unknown`, `other`, and an always-visible `supplement_text` field.
- Questions support free text and require it when `other` is selected.
- Answers distinguish `answered`, `unknown`, `skipped`, `invalid`, and `needs_free_text`.
- Inferred fields preserve source and confidence.
- High-confidence inferred answers skip repeated questions.
- Medium-confidence inferred answers become confirmation questions.
- Excessive unknown required fields stop the workflow with a gap report.
