# Platform Expected Outputs

## Generic Structured Output Wrapper

Valid output must always be a single top-level JSON object. The agent may include stage objects according to the current step, but it must not emit multiple adjacent JSON objects.

- `interaction_state`
- `answer_batch`
- `clarification_result`
- `rpa_boundary_result`
- `process_breakdown_result`
- `exception_design_result`
- `solution_package_result`

Example wrapper:

```json
{
  "interaction_state": {
    "stage": "clarification",
    "status": "ready_for_next_module",
    "completion_level": "workable",
    "answered_question_ids": [],
    "pending_question_ids": [],
    "last_summary": "",
    "next_action": "enter_next_module"
  },
  "answer_batch": {
    "answer_records": [],
    "state_patch": {},
    "impact": {
      "blocks_stage_progression": false,
      "adds_pending_question": false,
      "pending_question_ids": [],
      "review_notes": []
    }
  },
  "clarification_result": {},
  "rpa_boundary_result": {},
  "process_breakdown_result": {},
  "exception_design_result": {},
  "solution_package_result": {}
}
```

Real output may include only the objects needed for the current stage, but it must remain a single top-level JSON wrapper.

## Module 1 Expected Output

Module 1 records multiple-choice answers, free-form additions, state patches, and the next action.

Required:

- `answer_batch.answer_records`
- `answer_batch.state_patch`
- `answer_batch.impact`
- `interaction_state.next_action`

Do not replace these standard fields with free-form alternatives such as:

- `answers`
- `topic`
- `field`

## Module 2 Expected Output

Module 2 outputs `clarification_result`. It only performs boundary clarification and RPA pre-screening; it does not issue the final feasibility conclusion.

Required:

- `clarification_depth`
- `boundary_facts`
- `rpa_fit_prescreen`
- `pending_questions`
- `stage_summary`
- `next_stage_recommendation`

`boundary_facts` must cover:

- `business_goal`
- `trigger`
- `completion_condition`
- `input_data`
- `operated_systems`
- `output_result`

`rpa_fit_prescreen` must cover:

- `input_stability`
- `rule_clarity`
- `action_repeatability`
- `platform_operability`
- `result_verifiability`

## Module 3 Expected Output

Module 3 outputs `rpa_boundary_result` and decides whether the requirement is ready to enter process breakdown.

`rpa_boundary_result.decision.classification` must be one of:

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

The decision must consider:

- input readiness
- rule readiness
- platform operability
- result verifiability
- exception containment

Candidate Yingdao instructions may be used as evidence, but they must not be the sole basis for deciding that a requirement is suitable for RPA.

## Module 4 Expected Output

Module 4 outputs `process_breakdown_result`.

`process_breakdown_result.breakdown_depth` must be:

- `business_process_cards_with_candidate_capabilities`

Each process card should describe business-level stages and candidate Yingdao capability families. It must not include:

- selectors
- exact click paths
- wait times
- retry counts
- instruction parameters

Module 4 must preserve:

- `assumptions`
- `validation_points`
- `cross_step_dependencies`
- `open_questions`
- `prework_dependencies`
- required/recommended/optional upstream distinctions

English verification points:

- Preserve cross-step dependencies through `cross_step_dependencies`.
- Preserve validation points through `validation_points`.
- Preserve follow-up questions through `open_questions`.
- Preserve prior mandatory vs optional guidance, and do not erase the required/recommended/optional distinction.

## Module 5 Expected Output

Module 5 outputs `exception_design_result`.

`exception_design_result.exception_depth` must be:

- `semi_implementation_exception_flows`

Each exception card should describe severity, trigger signal, detection basis, handling strategy, continuation policy, candidate Yingdao capability families, human intervention, record fields, and related upstream risks.

Module 5 output must include:

- `exception_flows`
- `global_exception_policies`
- `manual_review_policy`
- `logging_policy`
- `open_questions`

Module 5 should route downstream to `solution_packaging` when complete.

Module 5 must not include exact selectors, exact click paths, wait times, retry counts as implementation parameters, or Yingdao instruction parameters.

## Module 6 Expected Output

Module 6 outputs `solution_package_result`.

Required:

- `module`
- `module_status`
- `developer_alignment_status`
- `source_modules`
- `fact_base`
- `decision_summary`
- `unified_view_model`
- `customer_view_model`
- `developer_view_model`
- `render_outputs`
- `next_stage_recommendation`

`fact_base` must separate:

- `confirmed_facts`
- `inferred_recommendations`
- `missing_required_items`
- `conflict_or_uncertainty`

`render_outputs` must include:

- `unified_html`
- optional compatibility `customer_html`
- optional compatibility `developer_html`

The unified HTML, customer HTML, and developer HTML must be generated from the same structured fact source.

The developer-facing HTML is a development alignment package, not a final build guide.

## Qualified Scenario Expectations

The ecommerce daily report scenario should usually remain `conditionally_suitable` until the platform-store list, metric mapping, date definition, login stability, and result verification method are confirmed.

The email sorting scenario should retain low-confidence human confirmation or a pending classification path when semantic judgment is involved, rather than being treated as a fully unattended workflow.

## Invalid Output Signs

- Emitting multiple adjacent JSON objects.
- Using `rpa_prescreen` instead of `rpa_fit_prescreen`.
- Using `candidate_risks` instead of `candidate_risk_types`.
- Using `prework_recommendations` instead of `recommended_prework`.
- Issuing the final "can do RPA" or "cannot do RPA" conclusion directly in Module 2.
- Asking for exact click paths, page selectors, wait times, or instruction parameters in Module 3, Module 4, or Module 5.
- Marking inferred recommendations as customer-confirmed facts.
- Returning `ready_for_development` while high-blocking missing items remain.
- Generating exact click paths, selectors, wait times, retry counts, or Yingdao instruction parameters in Module 6.
- Generating customer and developer HTML from different facts.
- Producing unreadable Chinese or mojibake.
