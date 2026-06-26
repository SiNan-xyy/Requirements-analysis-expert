# Exception Design Module

Module 5 expands module 4 exception handoff points into semi-implementation-level exception flows.

## Scope

This module consumes module 4 `process_breakdown_result` and references module 3 `rpa_boundary_result` risks. It does not repeat requirement clarification, override RPA boundary decisions, rebuild the happy path, generate exact selectors, generate wait times, produce Yingdao instruction parameters, or create HTML.

## Artifacts

- `schemas/exception-design-result.schema.json`
- `rules/exception-rules.json`
- `rules/prompt-rules.md`
- `fixtures/ecommerce-daily-report-exception-design.json`
- `fixtures/email-sorting-exception-design.json`

## Boundary Rule

Exception flows describe detection, containment, continuation policy, human intervention, and logging. They are not build scripts.
