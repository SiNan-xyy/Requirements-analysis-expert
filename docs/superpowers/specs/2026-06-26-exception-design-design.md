# Exception Design Design

## Goal

Build module 5 for the requirements analyst agent: a semi-implementation-level exception design module that expands the risk and exception handoff points from module 4 into structured exception flows.

Module 5 answers:

```text
When the main RPA process fails or becomes uncertain, how should the robot detect the exception, contain it, record it, and decide whether to continue, retry, stop, or ask for human review?
```

It must not answer:

```text
What exact selector should be captured?
How many seconds should the robot wait?
Which exact button path should be clicked?
What exact Yingdao instruction parameters should be configured?
What should the final HTML report look like?
```

Those belong to later implementation or packaging modules.

## Position In The Agent Workflow

Module 1 owns interaction structure.

Module 2 owns requirement clarification and RPA pre-screening.

Module 3 owns Yingdao RPA capability-boundary evaluation.

Module 4 owns happy-path process breakdown at business-process-card level.

Module 5 consumes module 4 and references module 3. It produces step-level exception handling design that can be reviewed before final blueprint packaging.

Downstream modules remain separate:

- Module 6: requirement blueprint generation
- Module 7: HTML report generation
- Module 8: quality audit

## Confirmed Design Choices

Use option B for granularity: semi-implementation-level exception flows.

Use option B for source scope: module 4 is primary, and module 3 risks are referenced.

Use option B for output shape: expand exceptions by module 4 process card.

This means module 5 is more concrete than a high-level risk list, but still less concrete than a developer SOP.

## Core Principle

Module 5 designs exception handling policies and branches, not exact automation instructions.

It can say:

```text
If a platform login fails because of captcha or device verification, mark the platform as blocked, notify a human operator, continue other platforms when safe, and record account, platform, detected time, and blocking reason.
```

It must not say:

```text
Click the verification button, wait 5 seconds, use selector #captcha, then retry exactly 3 times.
```

## Inputs

Module 5 starts only when module 4 recommends exception design:

```json
{
  "process_breakdown_result": {
    "module": "module_4_process_breakdown",
    "status": "completed",
    "next_stage_recommendation": "exception_design",
    "handoff_to_exception_design": {
      "required": true,
      "focus_steps": ["S02", "S03"]
    }
  }
}
```

Required upstream facts:

| Source | Required Facts |
| --- | --- |
| `process_breakdown_result.process_cards` | `step_id`, `step_name`, `input`, `output`, `depends_on`, `handoff_to_exception_design`, `exception_design_notes` |
| `process_breakdown_result.assumptions` | assumptions that may fail during execution |
| `process_breakdown_result.validation_points` | validation points that need exception handling or manual confirmation |
| `process_breakdown_result.cross_step_dependencies` | dependencies that may create cross-step failure propagation |
| `rpa_boundary_result.decision` | source classification and confidence |
| `rpa_boundary_result.risks` | capability-boundary risks that may become exception triggers |
| `rpa_boundary_result.required_prework` | prework that may remain a blocker or a runtime check |
| `rpa_boundary_result.capability_notes` | constraints such as login stability, field mapping, result logging, or manual review queue |

If module 4 is blocked, incomplete, or points back to module 2 or module 3, module 5 must not invent exception flows. It should return a blocked result that names the upstream blocker.

## Source Priority

Module 5 reads upstream context in this order:

1. Module 4 `process_cards` with `handoff_to_exception_design = true`.
2. Module 4 `exception_design_notes`.
3. Module 4 `assumptions`, `validation_points`, and `cross_step_dependencies`.
4. Module 3 `risks`, `required_prework`, and `capability_notes`.
5. Module 2 boundary facts only for wording and context, not for repeating clarification.

Module 5 must not re-ask module 2 boundary questions unless missing information makes an exception branch impossible to define.

## Exception Severity Levels

Module 5 uses four severity levels:

| Severity | Meaning | Typical Action |
| --- | --- | --- |
| `blocking` | The current step or whole run cannot safely continue. | Stop the affected scope, notify human operator, record blocking reason. |
| `needs_manual_review` | The robot can detect uncertainty but should not decide alone. | Route item to manual review queue, record reason, continue safe work. |
| `recoverable` | The robot can retry, skip affected item, or continue unaffected branches. | Retry or continue with controlled logging. |
| `log_only` | The issue does not affect execution correctness. | Record only. |

The severity is a design decision, not a runtime score.

## Exception Card Contract

Each exception card must contain:

```json
{
  "exception_id": "E-S03-01",
  "exception_type": "missing_data",
  "severity": "needs_manual_review",
  "trigger_signal": "",
  "detection_basis": [],
  "handling_strategy": "",
  "continue_policy": "continue_other_items",
  "candidate_yingdao_capabilities": [],
  "human_intervention": "required",
  "record_fields": [],
  "related_upstream_risks": []
}
```

### Field Meaning

| Field | Meaning |
| --- | --- |
| `exception_id` | Stable ID formed from process step and sequence, such as `E-S03-01`. |
| `exception_type` | Controlled identifier such as `login_failure`, `missing_data`, or `low_confidence`. |
| `severity` | One of `blocking`, `needs_manual_review`, `recoverable`, `log_only`. |
| `trigger_signal` | Human-readable signal that indicates this exception happened. |
| `detection_basis` | Data, page state, system result, file status, or rule used to detect the exception. |
| `handling_strategy` | Semi-implementation-level strategy for containment or recovery. |
| `continue_policy` | Whether the robot stops, continues other items, retries, skips the item, or waits for human review. |
| `candidate_yingdao_capabilities` | Candidate capability families such as condition judgment, logging, notification, file check, or manual review queue. |
| `human_intervention` | `none`, `optional`, or `required`. |
| `record_fields` | Fields that must be written to logs or review lists. |
| `related_upstream_risks` | Risk identifiers or capability notes inherited from module 3. |

## Output Contract

Module 5 writes an `exception_design_result` object:

```json
{
  "module": "module_5_exception_design",
  "status": "completed",
  "source_process_steps": ["S02", "S03"],
  "exception_depth": "semi_implementation_exception_flows",
  "exception_flows": [
    {
      "step_id": "S03",
      "step_name": "Collect platform daily data",
      "source_exception_notes": ["login failure", "missing data", "download failure"],
      "exception_cards": []
    }
  ],
  "global_exception_policies": [],
  "manual_review_policy": {
    "required": true,
    "review_queue_name": "",
    "review_record_fields": []
  },
  "logging_policy": {
    "required": true,
    "minimum_record_fields": []
  },
  "open_questions": [],
  "next_stage_recommendation": "solution_packaging"
}
```

Allowed `status` values:

- `completed`
- `blocked_by_process_breakdown`
- `needs_more_information`

Allowed `exception_depth` value:

- `semi_implementation_exception_flows`

Allowed `next_stage_recommendation` values:

- `solution_packaging`
- `return_to_process_breakdown`
- `return_to_rpa_boundary_check`
- `return_to_requirement_clarification`
- `stop_with_blocker`

## Default Exception Types

Module 5 may use these controlled exception types:

- `login_failure`
- `permission_missing`
- `captcha_or_device_verification`
- `source_data_missing`
- `source_field_missing`
- `download_failure`
- `file_format_unreadable`
- `field_mapping_mismatch`
- `rule_not_matched`
- `low_confidence`
- `target_template_changed`
- `target_write_failure`
- `result_verification_failed`
- `notification_failure`
- `manual_review_timeout`
- `unknown_exception`

The list is extensible only when a customer scenario clearly needs a new type.

## Continue Policy Values

Allowed `continue_policy` values:

- `stop_entire_run`
- `stop_current_step`
- `continue_other_items`
- `skip_current_item`
- `retry_then_escalate`
- `wait_for_manual_review`
- `log_and_continue`

Module 5 should prefer scoped continuation when the business process allows it. For example, if one e-commerce platform fails but other platforms can still be collected safely, the exception can stop the affected platform and continue other platforms.

## Question Behavior

Module 5 should ask questions only when exception handling would be unsafe without confirmation.

Allowed questions:

- Whether an exception should stop the whole run or only the affected item.
- Whether a low-confidence item should enter manual review, be skipped, or be processed with a warning.
- Which minimum fields must appear in an exception log.
- Whether a platform failure can be isolated while other platforms continue.
- Whether result verification failure blocks delivery or creates a review item.

Disallowed questions:

- Exact button names.
- Exact selectors.
- Exact wait times.
- Retry counts as fixed implementation parameters.
- Detailed Yingdao instruction parameter values.
- Final HTML layout.

If a question is needed, module 5 must use module 1's choice-first format, with `unknown` and `other` routes.

## Example: Multi-Platform E-Commerce Daily Report

For a module 4 card:

```json
{
  "step_id": "S03",
  "step_name": "Collect platform daily data",
  "exception_design_notes": ["login failure", "missing data", "download failure"]
}
```

Module 5 may produce:

```json
{
  "step_id": "S03",
  "step_name": "Collect platform daily data",
  "source_exception_notes": ["login failure", "missing data", "download failure"],
  "exception_cards": [
    {
      "exception_id": "E-S03-01",
      "exception_type": "login_failure",
      "severity": "blocking",
      "trigger_signal": "A platform account cannot reach the daily report page because login fails, captcha appears, or device verification is required.",
      "detection_basis": ["login result", "page state", "account permission status"],
      "handling_strategy": "Mark the affected platform as blocked, notify a human operator, and continue other platforms only when platform-level isolation is allowed.",
      "continue_policy": "continue_other_items",
      "candidate_yingdao_capabilities": ["condition judgment", "logging", "notification"],
      "human_intervention": "required",
      "record_fields": ["platform", "account", "date", "failure_reason", "detected_at"],
      "related_upstream_risks": ["unstable_platform", "requires_stable_login"]
    },
    {
      "exception_id": "E-S03-02",
      "exception_type": "source_data_missing",
      "severity": "needs_manual_review",
      "trigger_signal": "A configured platform-store-date combination returns no data or misses a required metric.",
      "detection_basis": ["platform-store list", "metric mapping", "raw data fields"],
      "handling_strategy": "Do not write an inferred value into the report. Add the item to the manual review list and keep the source evidence.",
      "continue_policy": "continue_other_items",
      "candidate_yingdao_capabilities": ["condition judgment", "table processing", "logging"],
      "human_intervention": "required",
      "record_fields": ["platform", "store", "date", "missing_metric", "source_snapshot"],
      "related_upstream_risks": ["unstable_input", "requires_field_mapping"]
    }
  ]
}
```

## Example: Email Sorting

For a module 4 card:

```json
{
  "step_id": "S04",
  "step_name": "Classify email",
  "exception_design_notes": ["low confidence", "unknown category", "mailbox permission failure"]
}
```

Module 5 may produce:

```json
{
  "step_id": "S04",
  "step_name": "Classify email",
  "source_exception_notes": ["low confidence", "unknown category", "mailbox permission failure"],
  "exception_cards": [
    {
      "exception_id": "E-S04-01",
      "exception_type": "low_confidence",
      "severity": "needs_manual_review",
      "trigger_signal": "The email does not match sender, subject, keyword, or sample-message rules with enough confidence.",
      "detection_basis": ["classification rules", "matched signals", "manual review threshold"],
      "handling_strategy": "Move or label the email as pending manual confirmation instead of assigning a final category.",
      "continue_policy": "continue_other_items",
      "candidate_yingdao_capabilities": ["condition judgment", "manual review queue", "logging"],
      "human_intervention": "required",
      "record_fields": ["message_id", "sender", "subject", "matched_signals", "detected_at"],
      "related_upstream_risks": ["semantic_judgment", "requires_manual_review_queue"]
    }
  ]
}
```

## Prompt Behavior

Module 5 should:

- Start from module 4 focus steps and exception notes.
- Reference module 3 risks and capability notes as exception evidence.
- Keep exception handling semi-implementation-level.
- Produce step-level exception flows.
- Define severity, trigger signal, detection basis, handling strategy, continuation policy, human intervention, and record fields.
- Preserve manual review and logging requirements.
- Ask only when exception handling cannot be safely designed from upstream facts.

Module 5 should not:

- Override module 3's suitability decision.
- Rebuild module 4's happy path.
- Ask module 2 boundary questions again.
- Generate exact selectors, click paths, wait times, retry counts, or instruction parameters.
- Produce final solution blueprint.
- Produce HTML.

## Acceptance Criteria

Module 5 design is accepted when:

- It consumes module 4 process cards and module 3 risks without repeating module 2 clarification.
- It only runs when module 4 recommends `exception_design`.
- It defines a structured `exception_design_result`.
- It expands exceptions by process step.
- It defines exception cards with severity, trigger signal, detection basis, handling strategy, continuation policy, candidate capability families, human intervention, record fields, and upstream risk links.
- It preserves global manual review and logging policies.
- It remains semi-implementation-level and does not generate exact automation parameters.
- It routes downstream to `solution_packaging` when complete.
