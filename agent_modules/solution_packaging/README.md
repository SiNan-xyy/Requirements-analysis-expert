# Solution Packaging Module

Module 6 packages Modules 1-5 into a customer-facing HTML report, a developer-facing HTML report, and one structured JSON fact source.

## Scope

This module consumes requirement clarification, RPA boundary check, process breakdown, and exception design outputs. It separates confirmed facts, inferred recommendations, missing required items, and uncertainty before rendering any report content.

The module is a solution packaging and development-alignment module. It is not a final build guide and does not create executable automation instructions.

## Artifacts

- `schemas/solution-package-result.schema.json`
- `rules/packaging-rules.json`
- `rules/prompt-rules.md`
- `fixtures/ecommerce-daily-report-solution-package.json`
- `fixtures/email-sorting-solution-package.json`
- `fixtures/not-recommended-semantic-risk-solution-package.json`
- `fixtures/blocked-gap-report-solution-package.json`

## Boundary Rule

The structured JSON is the single source of truth. Customer HTML and developer HTML must be rendered from the same fact source. Missing development information must be shown as missing information, not filled with guessed content.
