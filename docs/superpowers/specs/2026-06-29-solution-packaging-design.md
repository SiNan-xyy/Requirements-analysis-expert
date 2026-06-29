# Module 6 Solution Packaging Design

## Purpose

Module 6, `solution_packaging`, packages the results from Modules 1-5 into two readable HTML deliverables and one structured fact source. It is a solution packaging and development-alignment module, not a final implementation specification generator.

The module must help customers and implementation teams align on what is known, what is recommended, what is missing, and what cannot be treated as confirmed. It must not invent implementation facts that were not confirmed by the customer or produced by upstream modules.

## Outputs

Module 6 produces:

1. A customer-facing HTML report.
2. A developer-facing HTML report.
3. A structured JSON fact source used to render both HTML reports.

The structured JSON is the single source of truth. The two HTML reports are presentation layers with different audiences and different levels of detail.

## Audience Split

### Customer HTML

The customer-facing HTML report is used for business alignment. It should explain:

- the requirement understanding;
- the RPA recommendation;
- the RPA fit reasoning;
- the business scope;
- the main process cards;
- risks and manual intervention points;
- customer preparation items;
- the recommended next step.

It should avoid implementation-heavy content such as field-level engineering detail, exact selectors, click paths, wait times, retry counts, or instruction parameters.

### Developer HTML

The developer-facing HTML report is used for pre-implementation alignment. It should explain:

- implementation readiness status;
- confirmed facts that may be used as development basis;
- missing or blocking confirmation items;
- agent-inferred recommendations that require review;
- RPA capability boundaries;
- process breakdown cards;
- field and data mapping requirements;
- exception handling design;
- acceptance criteria;
- traceability back to Modules 1-5;
- a collapsed or secondary structured data appendix.

The developer report is a development alignment package. It is not a final build guide.

## Source Modules

Module 6 consumes the following upstream outputs:

- Module 1: interaction state, answered questions, pending questions, answer records, and deduplication state.
- Module 2: boundary facts, RPA pre-screening, pending questions, and stage summary.
- Module 3: final RPA boundary decision, dimension results, matched Yingdao capabilities, risks, capability notes, required prework, and `not_to_do_in_rpa`.
- Module 4: business process cards, assumptions, validation points, cross-step dependencies, open questions, and exception-design handoff notes.
- Module 5: exception flows, manual review policy, logging policy, global exception policies, and open questions.

Module 6 may package incomplete upstream information, but it must clearly mark the resulting package as `needs_confirmation` or `blocked` when appropriate.

## Status Model

Module 6 uses two separate status fields:

```json
{
  "module_status": "completed",
  "developer_alignment_status": "needs_confirmation"
}
```

`module_status` describes whether Module 6 successfully generated the package.

`developer_alignment_status` describes whether the requirement is ready for implementation alignment:

- `ready_for_development`
- `needs_confirmation`
- `not_recommended`
- `blocked`

### ready_for_development

Use this status when:

- Module 3 classification is `suitable` or `conditionally_suitable`;
- Module 4 process breakdown is completed;
- Module 5 exception design is completed;
- no high-blocking missing required items remain;
- key development basis is confirmed: systems, input, output, completion condition, main process, exception handling, logging, and manual review policy.

Low-risk optional or recommended items may remain, but they must be marked as non-blocking.

### needs_confirmation

Use this status when the requirement direction is viable, but development cannot proceed cleanly before more confirmation.

This status is triggered by any of:

- Module 2 `pending_questions`;
- Module 3 `required_prework` or `pending_questions`;
- Module 4 `open_questions` or key `prework_dependencies`;
- Module 5 `open_questions`;
- missing field mapping, account permission, template location, metric definition, validation method, or other implementation-critical information.

This is expected to be the most common status for real customer requirements.

### not_recommended

Use this status when Module 3 classifies the requirement as `not_suitable_for_direct_rpa`.

The package should explain:

- why direct RPA is not recommended;
- what prerequisite governance or process changes are needed;
- what conditions would allow reevaluation later.

Module 6 must not generate a full implementation-looking process plan in this status.

### blocked

Use this status when upstream information is insufficient or blocked.

This status is triggered by any of:

- Module 2 recommends `stop_with_gap_report` or `stop_with_blocker`;
- Module 3 status is `needs_more_information`;
- Module 4 status is `blocked_by_boundary_result` or `needs_more_information`;
- Module 5 status is `blocked_by_process_breakdown` or `needs_more_information`;
- core facts such as business goal, input, output, operated systems, or completion condition are missing.

The HTML reports should become gap reports rather than solution reports.

## Fact Layer

The fact layer prevents hallucination and makes the reports traceable.

```json
{
  "fact_base": {
    "confirmed_facts": [],
    "inferred_recommendations": [],
    "missing_required_items": [],
    "conflict_or_uncertainty": []
  }
}
```

### confirmed_facts

Confirmed facts come from explicit user answers or upstream module outputs that preserve confirmed user information.

Each confirmed fact should include:

- `fact_id`;
- `topic`;
- `value`;
- `source_module`;
- `source_type`;
- `confidence`;
- `can_be_used_for_development`.

Only confirmed facts may be presented as development basis.

### inferred_recommendations

Inferred recommendations come from RPA experience, Module 3 risks, Module 4 process assumptions, or Module 5 exception design.

Each inferred recommendation should include:

- `item_id`;
- `topic`;
- `value`;
- `basis`;
- `requires_confirmation`;
- `can_be_used_for_development`.

Inferred recommendations must not be treated as customer-confirmed facts.

### missing_required_items

Missing required items come from upstream pending questions, required prework, process prework dependencies, and exception open questions.

Each item should include:

- `item_id`;
- `topic`;
- `question`;
- `why_it_matters`;
- `blocking_level`;
- `owner`.

Blocking levels are:

- `high`;
- `medium`;
- `low`.

### conflict_or_uncertainty

Conflicts and uncertainties come from low-confidence facts, conditionally suitable decisions, open questions, and inconsistencies between upstream modules.

Each item should include:

- `item_id`;
- `topic`;
- `description`;
- `impact`;
- `resolution_needed`.

## Structured JSON Shape

The Module 6 output should fit the existing platform pattern of a single top-level JSON wrapper. The new stage object is `solution_package_result`.

```json
{
  "interaction_state": {},
  "solution_package_result": {
    "module": "module_6_solution_packaging",
    "module_status": "completed",
    "developer_alignment_status": "needs_confirmation",
    "source_modules": {},
    "fact_base": {
      "confirmed_facts": [],
      "inferred_recommendations": [],
      "missing_required_items": [],
      "conflict_or_uncertainty": []
    },
    "decision_summary": {},
    "customer_view_model": {},
    "developer_view_model": {},
    "render_outputs": {
      "customer_html": "",
      "developer_html": ""
    },
    "next_stage_recommendation": "manual_review_before_implementation"
  }
}
```

## Customer View Model

The customer view model should contain:

- `headline`;
- `recommendation`;
- `requirement_understanding`;
- `rpa_fit_summary`;
- `business_scope_included`;
- `business_scope_excluded`;
- `process_cards`;
- `risk_and_manual_intervention`;
- `customer_preparation_items`;
- `next_steps`.

The customer report should use cards instead of swimlane diagrams for process presentation.

## Developer View Model

The developer view model should contain:

- `implementation_status`;
- `confirmed_development_basis`;
- `blocking_confirmation_items`;
- `agent_inferred_recommendations`;
- `rpa_capability_boundary`;
- `process_breakdown`;
- `field_and_data_mapping`;
- `exception_handling`;
- `acceptance_criteria`;
- `traceability`;
- `structured_data_appendix`.

The structured data appendix may be collapsed or placed after the readable report content.

## Rendering Rules

Both HTML reports must be generated from the same structured JSON fact source.

The rendering layer must not create new facts. If a section has insufficient source data, it should show a gap, a pending confirmation item, or a non-blocking note instead of filling the section with guessed content.

The process section should use cards. It must not use a swimlane diagram as the primary representation.

## Traceability Rules

Every material conclusion should trace back to one or more upstream modules:

- requirement facts trace to Module 1 or Module 2;
- RPA fit, risk, and capability boundary trace to Module 3;
- process cards and validation points trace to Module 4;
- exception, manual review, and logging design trace to Module 5.

If a value cannot be traced, it must be marked as an inferred recommendation or missing item.

## Prohibited Content

Module 6 must not generate:

- exact click paths;
- selectors;
- wait times;
- retry counts as executable parameters;
- Yingdao instruction parameters;
- a final build guide;
- a claim that development is ready when high-blocking missing items remain;
- customer-confirmed language for inferred content.

## Testing Expectations

The implementation should include contract tests for:

- successful `solution_package_result` schema validation;
- `needs_confirmation` for the ecommerce daily report fixture when field mapping, metric definition, date definition, or validation method is missing;
- semantic email sorting retaining manual review or low-confidence handling;
- `not_recommended` packages not producing implementation-looking process plans;
- `blocked` packages becoming gap reports;
- customer and developer HTML being generated from the same fact source;
- inferred recommendations never being marked as development facts;
- missing required items driving `developer_alignment_status`.

## Acceptance Criteria

Module 6 is acceptable when:

- it can package Modules 1-5 without changing their contracts;
- it keeps facts, inferences, missing items, and uncertainty separate;
- it renders two HTML reports from one structured JSON source;
- it correctly distinguishes module completion from development readiness;
- it preserves upstream open questions and prework instead of hiding them;
- it avoids prohibited implementation details;
- it routes the next step according to readiness status.
