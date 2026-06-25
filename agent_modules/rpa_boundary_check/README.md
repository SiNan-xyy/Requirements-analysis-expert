# RPA Boundary Check Module

Module 3 decides whether a clarified requirement is suitable for Yingdao RPA, conditionally suitable after prework, not ready, or not suitable for direct unattended RPA.

## Scope

This module consumes module 2 `clarification_result` facts. It does not repeat boundary clarification, generate happy-path process steps, design exception branches, or produce the final HTML report.

## Artifacts

- `schemas/rpa-boundary-result.schema.json`
- `rules/decision-rules.json`
- `rules/material-retrieval-policy.json`
- `rules/prompt-rules.md`
- `materials/source-material-manifest.json`
- `fixtures/email-sorting-boundary-result.json`
- `fixtures/ecommerce-daily-report-boundary-result.json`

## Decision Dimensions

- `scenario_match`
- `instruction_support`
- `input_readiness`
- `rule_readiness`
- `platform_operability`
- `result_verifiability`
- `exception_containment`

## Boundary Rule

Instruction existence is evidence, not a decision. The module must check whether inputs, rules, platform access, output verification, and exception containment are concrete enough before recommending process breakdown.
