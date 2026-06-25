# Process Breakdown Design

## Goal

Build module 4 for the requirements analyst agent: a main-process breakdown module that turns an approved or conditionally approved RPA requirement into business process cards with candidate Yingdao capability categories.

Module 4 answers:

```text
What are the main business stages of this automation, and what Yingdao capability families may support each stage?
```

It must not answer:

```text
What exact button should be clicked?
What selector should be captured?
How should every exception branch behave?
What is the final implementation plan?
```

Those belong to later modules.

## Position In The Agent Workflow

Module 1 owns interaction structure.

Module 2 owns requirement clarification and RPA pre-screening.

Module 3 owns Yingdao RPA capability-boundary evaluation.

Module 4 consumes module 2 and module 3 outputs. It produces a process breakdown that can be reviewed by the customer before exception design starts.

Downstream modules remain separate:

- Module 5: branch and exception design
- Module 6: requirement blueprint generation
- Module 7: HTML report generation
- Module 8: quality audit

## Design Choice

Use option B: business process cards plus candidate Yingdao capabilities.

Each card should describe a stable business segment:

- What the segment is for
- What input it needs
- What the robot roughly does
- What output it produces
- Which Yingdao capability families may support it
- Which prior steps or prework it depends on
- Whether module 5 needs to design exceptions for it

The card is not a build script. Candidate capabilities are evidence and orientation, not final instruction parameters.

## Core Principle

Module 4 breaks down the happy path at business-process level.

It can say:

```text
Enter each e-commerce platform, query or download the daily data, and normalize it into the reporting structure.
```

It must not say:

```text
Click the login button, wait 3 seconds, click the GMV field, use selector X, then click export.
```

## Inputs

Module 4 starts only when module 3 recommends process breakdown:

```json
{
  "rpa_boundary_result": {
    "decision": {
      "classification": "suitable"
    },
    "next_stage_recommendation": "process_breakdown"
  }
}
```

or:

```json
{
  "rpa_boundary_result": {
    "decision": {
      "classification": "conditionally_suitable"
    },
    "required_prework": []
  }
}
```

If module 3 returns `not_ready` or `not_suitable_for_direct_rpa`, module 4 must not generate process cards. It should return a blocked result that points back to module 3's gaps or blockers.

Required upstream facts:

| Source | Required Facts |
| --- | --- |
| `clarification_result.boundary_facts` | `business_goal`, `trigger`, `input_data`, `operated_systems`, `output_result`, `completion_condition` |
| `rpa_boundary_result.decision` | `classification`, `summary`, `confidence` |
| `rpa_boundary_result.dimension_results` | at least scenario, instruction, input, rule, platform, and result dimensions |
| `rpa_boundary_result.required_prework` | known prework that must appear as card dependencies |
| `rpa_boundary_result.matched_yingdao_capabilities` | candidate capability families and source material |

## Material Use

Module 4 uses the Yingdao flow-chain and scenario materials more heavily than module 3.

Recommended source order:

1. `yingdao_flow_chain_templates_v3.md`: primary source for common process-chain patterns.
2. `yingdao_scenario_building_guide.md`: scenario-family source for business-stage decomposition.
3. `requirement_to_instruction_mapping.xlsx`: examples for common user needs and process modules.
4. `yingdao_instruction_search_keywords.xlsx`: normalization of user wording into scenario families.
5. `yingdao_core_instruction_library.xlsx`: high-priority candidate capability names.
6. `yingdao_instruction_capability_library_cleaned.xlsx`: broader capability notes and constraints.

Module 4 should not use `agent_answer_templates.md` as process evidence. That file is only for final answer shape.

## Process Card Contract

Each process card must contain:

```json
{
  "step_id": "S01",
  "step_name": "",
  "business_purpose": "",
  "input": [],
  "operation_summary": "",
  "output": [],
  "candidate_yingdao_capabilities": [],
  "depends_on": [],
  "prework_dependencies": [],
  "handoff_to_exception_design": false,
  "exception_design_notes": []
}
```

### Field Meaning

| Field | Meaning |
| --- | --- |
| `step_id` | Stable ID such as `S01`, `S02`, `S03`. |
| `step_name` | Short business-stage name. |
| `business_purpose` | Why this step exists in the business process. |
| `input` | Data, system state, account, file, or rule needed by the step. |
| `operation_summary` | Business-level description of what the robot does. |
| `output` | Result produced by the step and consumed by later steps. |
| `candidate_yingdao_capabilities` | Candidate capability families or instruction categories, not final build parameters. |
| `depends_on` | Earlier process card IDs. |
| `prework_dependencies` | Module 3 prework needed before this step can be built reliably. |
| `handoff_to_exception_design` | Whether module 5 should design exceptions for this step. |
| `exception_design_notes` | Short notes naming exception topics, without designing the branches. |

## Output Contract

Module 4 writes a `process_breakdown_result` object:

```json
{
  "module": "module_4_process_breakdown",
  "status": "completed",
  "source_decision": {
    "classification": "conditionally_suitable",
    "confidence": "medium_high"
  },
  "breakdown_depth": "business_process_cards_with_candidate_capabilities",
  "process_cards": [],
  "cross_step_dependencies": [],
  "open_questions": [],
  "handoff_to_exception_design": {
    "required": true,
    "focus_steps": [],
    "notes": []
  },
  "next_stage_recommendation": "exception_design"
}
```

Allowed `status` values:

- `completed`
- `blocked_by_boundary_result`
- `needs_more_information`

Allowed `breakdown_depth` value:

- `business_process_cards_with_candidate_capabilities`

Allowed `next_stage_recommendation` values:

- `exception_design`
- `return_to_rpa_boundary_check`
- `return_to_requirement_clarification`
- `stop_with_blocker`

## Default Card Pattern

Module 4 should not force every process into the same steps, but many RPA requirements can start from this pattern:

1. Trigger and preparation
2. Load configuration, account, scope, or input list
3. Enter or connect to source system
4. Read, query, download, or collect source data
5. Normalize, match, filter, or calculate data
6. Enter or connect to target system
7. Write, upload, notify, or generate output
8. Record execution result and handoff items

Cards can be merged when a process is simple, or split when a stage has a distinct output and capability family.

## Question Behavior

Module 4 should ask questions only when it cannot produce a coherent main flow from module 2 and module 3 outputs.

Allowed questions:

- Confirm whether source data comes from query, download, file, API, or message.
- Confirm whether the target output is written to a system, file, online document, notification, or report.
- Confirm whether a prework dependency should be treated as a blocker or as a card dependency.
- Confirm the preferred main flow when there are two plausible happy paths.

Disallowed questions:

- Exact button names.
- Exact page selectors.
- Exact wait times.
- Retry counts.
- Detailed exception branch behavior.
- Full instruction parameter values.

If a question is needed, module 4 must use module 1's choice-first format, with `unknown` and `other` routes.

## Example: Multi-Platform E-Commerce Daily Report

Module 4 should produce cards like:

```json
{
  "step_id": "S03",
  "step_name": "Collect platform daily data",
  "business_purpose": "Get the daily operating metrics for each platform and fixed store.",
  "input": ["platform-store list", "date scope", "account permissions"],
  "operation_summary": "Enter each platform backend and query or download the daily data under fixed conditions.",
  "output": ["raw platform daily data"],
  "candidate_yingdao_capabilities": ["web automation", "report download", "file reading"],
  "depends_on": ["S01", "S02"],
  "prework_dependencies": ["confirm platform-store list", "confirm stable login strategy"],
  "handoff_to_exception_design": true,
  "exception_design_notes": ["login failure", "missing data", "download failure"]
}
```

The card names the exception topics, but module 5 designs the actual branches.

## Example: Email Sorting

Module 4 should produce cards like:

```json
{
  "step_id": "S04",
  "step_name": "Classify email",
  "business_purpose": "Decide which folder or label each email should enter.",
  "input": ["sender rules", "subject keywords", "body keyword or semantic examples", "classification taxonomy"],
  "operation_summary": "Apply sender, subject, and body rules to determine the target folder or label; route uncertain emails to manual review.",
  "output": ["email classification result", "manual review flag"],
  "candidate_yingdao_capabilities": ["email processing", "condition judgment", "text processing", "manual review queue"],
  "depends_on": ["S01", "S02", "S03"],
  "prework_dependencies": ["prepare classification rules", "define low-confidence review policy"],
  "handoff_to_exception_design": true,
  "exception_design_notes": ["low confidence", "unknown category", "mailbox permission failure"]
}
```

## Prompt Behavior

Module 4 should:

- Start from module 3's decision and prework.
- Preserve module 2 facts rather than asking them again.
- Generate 4-8 process cards for typical business automation needs.
- Keep each card business-readable.
- Attach candidate Yingdao capability families where useful.
- Mark exception topics for module 5 without designing them.
- Summarize cross-step dependencies such as account permissions, field mapping, template readiness, date scope, and result logging.

Module 4 should not:

- Override module 3's suitability decision.
- Remove module 3 prework dependencies.
- Invent final instruction parameters.
- Produce a final build guide.
- Produce HTML.

## Acceptance Criteria

Module 4 design is accepted when:

- It consumes module 2 and module 3 outputs instead of repeating their questions.
- It only runs when module 3 allows process breakdown.
- It defines a structured `process_breakdown_result`.
- It defines process cards with business purpose, input, operation summary, output, candidate capabilities, dependencies, and exception handoff markers.
- It uses Yingdao flow-chain templates and scenario materials without turning them into exact implementation steps.
- It blocks or returns upstream when module 3 says `not_ready` or `not_suitable_for_direct_rpa`.
- It leaves exception branches to module 5.
- It leaves final blueprint and HTML generation to later modules.

