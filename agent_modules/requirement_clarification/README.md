# Requirement Clarification Module

This module defines module 2 of the RPA requirements analyst agent: boundary-only clarification plus RPA-fit pre-screening.

It consumes the module 1 interaction schema. It does not decide final RPA feasibility, generate happy paths, design exception branches, or create HTML reports.

## Artifact Index

- `schemas/clarification-result.schema.json`: module 2 output contract.
- `schemas/negative-example.schema.json`: negative example material contract.
- `materials/negative-examples.v1.json`: approved RPA-fit negative examples.
- `rules/completion-rules.json`: analyzable and stop conditions.
- `rules/trigger-policy.json`: risk trigger levels and fixed pre-screen dimensions.
- `rules/prompt-rules.md`: prompt behavior rules for module 2.
- `fixtures/clarification-result-ready.json`: ready-for-module-3 example.
- `fixtures/semantic-risk-prescreen.json`: semantic matching pre-screen example.

