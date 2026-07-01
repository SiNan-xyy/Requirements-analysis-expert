# Platform Test Checklist

Use this checklist to verify that the Agent platform loads Git Skill, RAG materials, and system prompts correctly, and that modules 1-6 remain contract-stable.

## Basic Loading

- Git Skill can be loaded from the current repository branch `master`.
- The Agent can read the root `SKILL.md`.
- The Agent can reference rules, schemas, and fixtures under `agent_modules/`.
- RAG can inspect materials under `agent_platform_package/rag_upload/`.
- RAG can inspect the 12 uploaded materials, including the Yingdao capability Chinese guide, Tencent Docs online spreadsheet capability, report collection scenarios, branch exception rules, HTML Chinese dictionary, report quality rules, and captcha capability boundary.
- The system prompt comes from `agent_platform_package/system_prompt/agent-system-prompt.md`.
- Before each module output, the Agent should first follow the Git Skill for the current module, then retrieve the mapped RAG materials.
- If no usable RAG evidence is retrieved, the Agent must say "未检索到可用 RAG 依据" instead of pretending to cite material.
- Module flow, JSON fields, question controls, and output contracts come from Git Skill and system prompt; RAG provides evidence and examples only.

## Skill And RAG Invocation

- Module 2 should retrieve requirement analysis, negative examples, logistics interception case, and requirement-template RAG before producing `clarification_result`.
- Module 3 should retrieve RPA boundary, negative examples, Yingdao capability cards, online spreadsheet capability, and captcha boundary RAG before producing `rpa_boundary_result`.
- Module 4 should retrieve Yingdao capability cards, online spreadsheet capability, and report collection scenario RAG before producing `process_breakdown_result`.
- Module 5 should retrieve branch/exception rules and captcha boundary RAG before producing `exception_design_result`.
- Module 6 should retrieve HTML display dictionary, report quality rules, and requirement-template fields before producing `solution_package_result`.
- Every recommendation or risk must be source-labeled as customer confirmed, RAG suggestion, Agent inference pending confirmation, or required prework before development.

## Interaction Behavior

- When the customer input is ambiguous, the Agent should ask boundary questions first instead of directly giving a development plan.
- Each round must prefer choice-question components.
- The Agent must switch between `single_choice` and `multiple_choice` based on the question meaning.
- Use `single_choice` only when exactly one answer should be selected.
- Use `multiple_choice` for platforms, systems, data sources, fields, object scope, exception handling, notification method, human fallback, and captcha handling.
- Each question must include both "unknown" and "other" paths, and must also show both "不确定" and "其他".
- Every supplement path must render an input box through `supplement_text`.
- Supplemented user information should be absorbed, not duplicated as the same follow-up question.
- Medium-confidence inference should become a confirmation question.
- Do not judge whether RPA is possible from the first customer sentence.

## Output Contract

- Structured output must always be a single top-level JSON object.
- Depending on the current stage, include the following objects as needed: `interaction_state`, `answer_batch`, `clarification_result`, `rpa_boundary_result`, `process_breakdown_result`, `exception_design_result`, `solution_package_result`.
- `interaction_state` must use standard fields only, and must not use alternative free-form fields such as `module`, `known_facts`, or `deduplication`.
- `answer_batch` must use `answer_records`, `state_patch`, and `impact`.
- Module 2 must use `rpa_fit_prescreen` rather than `rpa_prescreen`.
- Module 3 `decision.classification` must use a controlled enumeration.
- Module 4 must output business process cards, not exact click paths or instruction parameters.
- Module 5 must output semi-implementation exception cards, human review policy, and logging policy.
- Module 6 must output `solution_package_result`, and separate module status from development readiness status.

## Module Boundaries

- Module 2 must not ask for exact click paths, selectors, wait times, or exception-branch implementation details.
- Module 3 must not repeat Module 2 boundary clarification, and must not generate process breakdowns.
- Module 4 must not cover Module 3 boundary judgment, must not design exception branches, and must not generate HTML.
- Module 5 must not generate the final solution package, and must not generate exact instruction parameters.
- Module 6 must not turn inference into customer-confirmed facts, and must not generate the final development guide.

## Module 6 Checks

- `solution_package_result.fact_base.confirmed_facts` may contain only confirmed facts.
- `inferred_recommendations` must use `requires_confirmation = true` and `can_be_used_for_development = false`.
- When high-blocking missing items exist, do not output `developer_alignment_status = ready_for_development`.
- The unified HTML report must come from the same structured fact source as the customer and developer HTML.
- The unified HTML report is a requirements analysis and alignment package, not a final build guide.
- The unified HTML report should prefer Chinese and should not expose a large amount of English enumeration, machine fields, or IT jargon directly.
- Each key workflow step in the unified HTML report should show a reference Yingdao capability or explain when the capability basis is still unclear.
- Branches and exceptions must be source-labeled: customer confirmed, RAG suggestion, or Agent inference pending confirmation.
- Do not show exact click paths, selectors, wait times, retry counts, or instruction parameter details as implementation specifics.

## Readability

- Chinese output must be readable.
- Historical encoding corruption must not appear.
- If RAG materials or test materials contain corruption, ignore the corrupted text and restate the meaning in readable Chinese.

## Recommended Test Scenarios

- Logistics interception: verify that Module 2 asks boundary questions first.
- E-commerce multi-platform daily report: verify that Module 3 output is appropriate and preserves field mapping, KPI paths, date paths, and verification method gaps.
- Email auto-classification: verify that semantic judgment risk enters a low-confidence or human review path.
- Material synonym judgment: verify that direct RPA is not recommended when the text suggests a governance task rather than automation.

## Memory-driven stability regression

- Before deployment, run the scenarios in `agent_platform_package/testing/stability_regression_scenarios.md`.
- Confirm every scenario updates requirement memory before module transition.
- Confirm each transition uses requirement memory gate state: `ready`, `partial_ready`, or `blocked`.
- Confirm non-blocking gaps can be carried forward instead of forcing excessive questions.
- Confirm final reports keep fixed report sections across scenarios.
- Confirm inferred recommendations and RAG suggestions are source-labeled and not written as customer-confirmed facts.

## Platform-compatible question controls

- Question `type` must stay `single_choice` or `multiple_choice`.
- Do not output `single_choice_with_text` or `multiple_choice_with_text`.
- The platform should render `supplement_text.enabled = true` and `supplement_text.always_visible = true` as a default visible input box.
- Every question must show both `unknown` and `other`, and must also show both "不确定" and "其他".
- unknown is not other: `unknown` means the customer cannot confirm now and does not require supplement text.
- `other` means the customer knows an answer not covered by options and should provide supplement text.
- Supplement behavior must be represented by always-visible `supplement_text`; do not turn the `other` label into a supplement instruction.
