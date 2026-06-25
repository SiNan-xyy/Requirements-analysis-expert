# Process Breakdown Module

Module 4 turns an approved or conditionally approved RPA requirement into business process cards with candidate Yingdao capability families.

## Scope

This module consumes module 2 `clarification_result` facts and module 3 `rpa_boundary_result` decisions. It does not repeat requirement clarification, override RPA boundary decisions, design exception branches, generate exact click paths, or produce final HTML.

## Artifacts

- `schemas/process-breakdown-result.schema.json`
- `rules/breakdown-rules.json`
- `rules/material-use-policy.json`
- `rules/prompt-rules.md`
- `fixtures/ecommerce-daily-report-process-breakdown.json`
- `fixtures/email-sorting-process-breakdown.json`

## Process Card Fields

- `step_id`
- `step_name`
- `business_purpose`
- `input`
- `operation_summary`
- `output`
- `candidate_yingdao_capabilities`
- `depends_on`
- `prework_dependencies`
- `handoff_to_exception_design`
- `exception_design_notes`

## Boundary Rule

Cards are business-process descriptions, not build scripts. Candidate Yingdao capabilities orient the later build, but module 4 must not generate selectors, click paths, wait times, retry counts, or instruction parameter values.
