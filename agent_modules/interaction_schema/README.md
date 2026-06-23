# Interaction Schema Module

This module defines the first layer of the RPA requirements analyst agent: the choice-first interaction state, question format, answer recording format, next-step decision rules, and deduplication rules.

It does not evaluate RPA feasibility, break down process steps, design exceptions, or generate HTML reports.

## Files

- `schemas/interaction-state.schema.json`: interaction state contract.
- `schemas/question.schema.json`: choice-question contract.
- `schemas/answer-batch.schema.json`: answer record and state patch contract.
- `rules/decision-rules.json`: ordered next-action rules.
- `rules/prompt-rules.md`: agent prompt behavior rules.
- `fixtures/`: valid examples used by tests and platform integration.
