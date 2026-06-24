# Requirement Clarification Module

This module defines module 2 of the RPA requirements analyst agent: boundary-only clarification plus RPA-fit pre-screening.

It consumes the module 1 interaction schema. It does not decide final RPA feasibility, generate happy paths, design exception branches, or create HTML reports.

Module 2 never concludes risk from the initial request alone. It can only surface candidate risk signals, request clarification, and recommend prework when the semantic fit is not yet safe to finalize.

## Artifact Index

- `schemas/clarification-result.schema.json`: module 2 output contract.
- `schemas/negative-example.schema.json`: negative example material contract.
- `materials/negative-examples.v1.json`: approved RPA-fit negative examples.
- `rules/completion-rules.json`: analyzable and stop conditions.
- `rules/trigger-policy.json`: risk trigger levels and fixed pre-screen dimensions.
- `rules/prompt-rules.md`: prompt behavior rules for module 2.
- `fixtures/clarification-result-ready.json`: ready-for-module-3 example.
- `fixtures/semantic-risk-prescreen.json`: semantic matching pre-screen example.

## Scope

Module 2 stops at boundary-only clarification and RPA-fit pre-screening. It records the minimum business goal, trigger, completion condition, input data, operated systems, and output result needed to understand the request, then evaluates fixed pre-screen signals for risk.

## Boundary Facts

The boundary facts captured in this module are:

- `business_goal`
- `trigger`
- `completion_condition`
- `input_data`
- `operated_systems`
- `output_result`

## RPA Pre-Screen Dimensions

The fixed pre-screen dimensions are:

- `input_stability`
- `rule_clarity`
- `action_repeatability`
- `platform_operability`
- `result_verifiability`

## Risk Trigger Rule

Module 2 uses weak signals and boundary answers to surface candidate risks only. When the request depends on semantic judgment, naming alignment, or other prework that cannot be resolved from the initial request alone, the module maps that prework stop to the module 1 action `stop_with_blocker` instead of making a final feasibility decision.
