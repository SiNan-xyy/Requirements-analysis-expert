# Yingdao RPA Boundary Check Design

## Goal

Build module 3 for the requirements analyst agent: a formal Yingdao RPA capability-boundary check that consumes the structured facts from module 2 and decides whether the requirement is suitable for Yingdao RPA, conditionally suitable after prework, or not suitable for direct unattended automation yet.

Module 3 must answer a narrower question than the later process-design modules:

```text
Can Yingdao RPA reasonably support this requirement, and what conditions must be true before process breakdown starts?
```

It must not produce the full build plan, exact instruction sequence, exception branches, implementation steps, or final HTML report.

## Position In The Agent Workflow

Module 1 owns the interaction contract:

- Choice-first questions
- Free-text supplements
- Answer absorption
- Deduplication
- Stage progression

Module 2 owns boundary-only clarification:

- Business goal
- Trigger
- Completion condition
- Input data
- Operated systems
- Output result
- Early RPA pre-screen signals

Module 3 consumes those outputs and produces a formal boundary decision.

Downstream modules remain separate:

- Module 4: happy-path process breakdown
- Module 5: branch and exception design
- Module 6: requirement blueprint generation
- Module 7: HTML report generation
- Module 8: quality audit

## Design Choice

Use the confirmed option B: conditional admissibility.

The module does not use a hard yes/no gate too early, and it does not hide the decision behind a vague numeric score. It classifies the requirement into one of four practical outcomes:

- `suitable`: ready to enter process breakdown.
- `conditionally_suitable`: likely suitable, but specific prework or constraints must be confirmed.
- `not_ready`: not ready for process breakdown because required rules, data, access, or verification are missing.
- `not_suitable_for_direct_rpa`: the core work depends on open-ended judgment, unstable inputs, or non-operable systems, so direct unattended RPA is not recommended.

This keeps the answer useful for customers while preserving the agent's boundary discipline.

## Source Material Classification

The new Yingdao materials should not all be used in the same way. They need different roles in the agent package.

| File | Recommended Role | Why |
| --- | --- | --- |
| `yingdao_instruction_capability_library_cleaned.xlsx` | Module 3 skill material and RAG source | Main capability library with instruction name, category, suitable scenarios, prerequisites, unsuitable scenarios, common errors, and handling suggestions. |
| `yingdao_core_instruction_library.xlsx` | Module 3 skill material | High-priority core instruction subset. Use it first to avoid over-matching obscure instructions. |
| `yingdao_instruction_search_keywords.xlsx` | Retrieval and normalization layer | Maps customer wording to standard requirement types and candidate instruction keys. |
| `requirement_to_instruction_mapping.xlsx` | Few-shot examples and test cases | Small, high-signal mapping from demand keywords to process modules, prerequisite questions, risks, and example answers. |
| `影刀常见流程指令链模板V3_逻辑结构版.md` | Module 4 primary material, Module 3 supporting material | Useful for checking whether a mature flow-chain pattern exists, but detailed flow chains belong mainly to process breakdown. |
| `yingdao_scenario_building_guide.md` | Scenario-level RAG source | Helps map needs to broad scenario families such as web automation, Excel processing, file handling, login, collection, and notification. |
| `agent_answer_templates.md` | Output style reference | Constrains response shape after the decision. It should not be used as evidence for capability. |

The duplicate `影刀常见流程指令链模板V3_逻辑结构版 (1).md` should not be uploaded or packaged unless it differs from the non-duplicate file. The inspected copies currently appear equivalent in size and purpose.

## Core Principle

Module 3 judges capability through conditions, not instruction existence.

Bad logic:

```text
There is an instruction that sounds related, so this requirement can be done.
```

Correct logic:

```text
The requirement maps to a supported scenario, has stable input, clear rules, operable systems, repeatable actions, verifiable output, and known exception handling. Therefore Yingdao RPA is suitable, or suitable after named prework.
```

An instruction match is evidence, not a decision.

## Module 3 Scope

Module 3 includes:

- Capability-boundary decision
- Yingdao scenario family matching
- Candidate instruction-category matching
- Precondition check against Yingdao instruction capability material
- Risk classification using module 2 pre-screen signals and Yingdao material
- Prework recommendations
- Decision explanation with evidence and uncertainty
- Next-stage recommendation

Module 3 excludes:

- Asking for exact buttons, selectors, page paths, or click order
- Designing the full happy path
- Designing exception branches in detail
- Producing final implementation steps
- Producing final requirement documents
- Producing HTML output

## Inputs

Module 3 starts only when module 2 has produced:

```json
{
  "interaction_state": {
    "stage": "rpa_boundary_check",
    "status": "ready_for_next_module"
  },
  "clarification_result": {
    "boundary_facts": {},
    "rpa_fit_prescreen": {},
    "pending_questions": [],
    "stage_summary": ""
  }
}
```

Required input facts:

| Field | Requirement |
| --- | --- |
| `business_goal` | Must be known at medium or high confidence. |
| `input_data` | Must identify source type and key data. |
| `operated_systems` | Must identify target systems or platforms. |
| `output_result` | Must identify the expected produced result. |
| `completion_condition` | Must describe when the automation is considered done. |

Recommended input facts:

| Field | Requirement |
| --- | --- |
| `trigger` | Needed for unattended and scheduled workflows. |
| `rule_clarity` | Needed to decide whether key judgment is automatable. |
| `input_stability` | Needed to decide whether the robot can read data reliably. |
| `platform_operability` | Needed to decide whether the robot can act on the target system. |
| `result_verifiability` | Needed to decide whether success and failure can be detected. |

If required facts are missing, module 3 must return a gap decision instead of guessing.

## Decision Dimensions

Module 3 evaluates seven dimensions.

| Dimension | Question |
| --- | --- |
| `scenario_match` | Does the need map to a known Yingdao scenario family? |
| `instruction_support` | Are there candidate Yingdao instruction categories or templates that can support the core actions? |
| `input_readiness` | Are source data, format, fields, and access stable enough? |
| `rule_readiness` | Can the key business judgment be written as explicit rules or controlled review logic? |
| `platform_operability` | Can Yingdao operate the involved platform through web, desktop, file, API, database, office, or message capabilities? |
| `result_verifiability` | Can the robot verify success, failure, and produced output? |
| `exception_containment` | Are common exceptions classifiable enough to handle or route to manual review? |

Each dimension uses:

- `status`: `pass`, `conditional`, `fail`, or `unknown`
- `evidence`: facts or retrieved material supporting the status
- `notes`: concise explanation
- `required_prework`: concrete prerequisite if status is `conditional` or `fail`

## Material Retrieval Logic

Module 3 should retrieve materials in this order:

1. Normalize customer language with `yingdao_instruction_search_keywords.xlsx`.
2. Match broad scenario families with `yingdao_scenario_building_guide.md`.
3. Check mature flow-chain patterns with `影刀常见流程指令链模板V3_逻辑结构版.md`.
4. Verify concrete capability and constraints with `yingdao_core_instruction_library.xlsx`.
5. Use `yingdao_instruction_capability_library_cleaned.xlsx` for broader supporting or limiting evidence.
6. Use `requirement_to_instruction_mapping.xlsx` as few-shot examples and regression cases.
7. Use `agent_answer_templates.md` only after the decision, for answer shape.

The agent should prefer high-priority core instructions before lower-priority extended instructions.

## Risk Types

Module 3 inherits the controlled risk identifiers from module 2 and may add Yingdao-specific evidence.

Allowed risk identifiers:

- `semantic_judgment`
- `missing_rules`
- `unstable_input`
- `unverifiable_result`
- `unstable_platform`
- `human_verification`
- `open_ended_exceptions`
- `low_roi`

Module 3 may also produce capability notes such as:

- `requires_api_or_data_export`
- `requires_stable_login`
- `requires_field_mapping`
- `requires_template_standardization`
- `requires_manual_review_queue`
- `requires_result_log`

These are not risk identifiers. They are prework or design constraints.

## Output Contract

Module 3 writes a `rpa_boundary_result` object.

```json
{
  "module": "module_3_rpa_boundary_check",
  "status": "completed",
  "decision": {
    "classification": "conditionally_suitable",
    "summary": "",
    "confidence": "medium_high"
  },
  "dimension_results": {
    "scenario_match": {
      "status": "pass",
      "evidence": [],
      "notes": "",
      "required_prework": []
    },
    "instruction_support": {
      "status": "pass",
      "evidence": [],
      "notes": "",
      "required_prework": []
    },
    "input_readiness": {
      "status": "conditional",
      "evidence": [],
      "notes": "",
      "required_prework": []
    },
    "rule_readiness": {
      "status": "conditional",
      "evidence": [],
      "notes": "",
      "required_prework": []
    },
    "platform_operability": {
      "status": "pass",
      "evidence": [],
      "notes": "",
      "required_prework": []
    },
    "result_verifiability": {
      "status": "conditional",
      "evidence": [],
      "notes": "",
      "required_prework": []
    },
    "exception_containment": {
      "status": "unknown",
      "evidence": [],
      "notes": "",
      "required_prework": []
    }
  },
  "matched_yingdao_capabilities": [
    {
      "scenario_family": "",
      "candidate_instruction_categories": [],
      "candidate_instruction_names": [],
      "source_material": []
    }
  ],
  "risks": [
    {
      "risk_type": "unstable_input",
      "severity": "medium",
      "evidence": "",
      "mitigation": ""
    }
  ],
  "required_prework": [],
  "not_to_do_in_rpa": [],
  "next_stage_recommendation": "process_breakdown",
  "pending_questions": []
}
```

Allowed `classification` values:

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

Allowed `confidence` values:

- `high`
- `medium_high`
- `medium`
- `low`

Allowed dimension status values:

- `pass`
- `conditional`
- `fail`
- `unknown`

## Classification Rules

### Suitable

Use `suitable` when:

- Scenario match is `pass`.
- Instruction support is `pass`.
- Input readiness is `pass` or minor `conditional`.
- Rule readiness is `pass`.
- Platform operability is `pass`.
- Result verifiability is `pass`.
- Exceptions are classifiable or safely routable.

### Conditionally Suitable

Use `conditionally_suitable` when:

- The core requirement is supported by Yingdao scenarios and instructions.
- One or more dimensions need prework, but the prework is concrete and achievable.
- Risks can be contained through standardization, field mapping, manual review queue, login stabilization, result logging, or API/data export.

This should be the default for many real customer requirements.

### Not Ready

Use `not_ready` when:

- Required information is missing.
- The user has not confirmed enough boundary facts.
- The input, rules, output, or platform access may be solvable, but cannot be judged yet.

This is a gap report, not a rejection.

### Not Suitable For Direct RPA

Use `not_suitable_for_direct_rpa` when:

- The core task depends on open-ended semantic judgment without rules or review.
- The input is highly unstable and cannot be standardized.
- The target platform cannot be operated or accessed reliably.
- Strong human verification is frequent and cannot be separated into a manual step.
- Success cannot be verified at all.
- Automation value is low because the process is rare, highly variable, and still requires heavy manual judgment.

## Question Behavior

Module 3 may ask questions only when a dimension cannot be judged from module 2 facts and retrieved material.

Allowed question types:

- Confirm missing capability-critical facts.
- Confirm whether a prework assumption is true.
- Choose among practical handling strategies, such as API export, file export, manual review queue, or direct page operation.

Disallowed question types:

- Exact click path
- Exact selector or UI element name
- Step-by-step build sequence
- Full exception branch design
- Detailed instruction parameter values

If module 3 asks questions, it must use module 1's choice-first question format and preserve `other` plus free-text supplement.

## Example: Email Sorting

Input summary:

```text
Automatically classify Outlook or Microsoft 365 emails by sender, subject keywords, and body semantics. Low-confidence messages go to manual review.
```

Expected module 3 classification:

```text
conditionally_suitable
```

Reason:

- Mail system and output are clear.
- Rule-based sender and keyword classification is suitable.
- Semantic classification introduces risk.
- Manual review queue can contain low-confidence cases.
- Result log can make the outcome verifiable.

Required prework:

- Classification list or label taxonomy.
- Sender, domain, subject keyword, and sample-email rules.
- Low-confidence threshold or review policy.
- Processing log fields.

## Example: Multi-Platform E-Commerce Daily Report

Input summary:

```text
Every day, collect GMV, paid order count, refund amount, and refund order count from multiple e-commerce platforms and fixed stores, then write the data into a Tencent Docs daily report template.
```

Expected module 3 classification:

```text
conditionally_suitable
```

Reason:

- Scenario maps to web automation, report download or data collection, Excel/table processing, and Tencent Docs writing.
- Repetition is high and store count is fixed.
- Main conditions are metric mapping, date scope, platform access stability, and result verification.
- If platform login frequently triggers strong verification, classification may drop to `not_ready` until login strategy is resolved.

Required prework:

- Platform-store list.
- Metric-to-template field mapping.
- Date scope, such as natural day or previous day.
- Login/session strategy.
- Minimum result verification, ideally source value record plus written value record.

## Acceptance Criteria

Module 3 design is accepted when:

- It consumes module 2 facts instead of repeating module 2 clarification.
- It uses conditional admissibility rather than a premature hard yes/no.
- It distinguishes instruction existence from actual automation suitability.
- It defines the seven decision dimensions.
- It classifies the seven provided Yingdao materials into skill, RAG, template, and testing roles.
- It preserves controlled risk identifiers.
- It defines a structured `rpa_boundary_result` output.
- It blocks process breakdown when required facts or prework are missing.
- It leaves exact flow steps, instruction parameters, and exception branches to later modules.
