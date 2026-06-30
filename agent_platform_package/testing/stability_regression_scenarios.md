# Memory-driven Stability Regression Scenarios

Use this document before deployment or after major prompt, RAG, or skill changes. The goal is not to force one fixed answer, but to verify stable behavior across modules, memory updates, gate transitions, and final report structure.

## ecommerce_daily_report

- question_behavior: Use `multiple_choice_with_text` for platforms, data fields, output fields, and validation method. Do not ask exact click paths.
- requirement_memory_updates: Confirm business goal, platforms, input metrics, Tencent Docs output, and daily trigger as `F` facts. Keep metric mapping, date definition, and validation method as `G` gaps if unanswered.
- gate_state: Module 2 can be `partial_ready` for Module 3 when core boundary facts are known. Module 3 can be `partial_ready` for Module 4 when field mapping is a carry-forward gap.
- rpa_boundary: Usually `conditionally_suitable`, with field mapping, result log, login stability, and platform-store scope as capability or prework notes.
- report_sections: Final report must use all fixed report sections and show process cards with candidate capabilities for platform collection, data normalization, Tencent Docs writing, and logging.
- source_label_expectations: Field mapping and exception policies not asked from the customer must be `agent_inferred_pending_confirmation` or `required_before_build`, not `customer_confirmed`.

## inventory_monitor

- question_behavior: Use `multiple_choice_with_text` for source systems, monitored product scope, notification methods, and human fallback.
- requirement_memory_updates: Confirm monitoring goal and output alert as `F` facts. Keep threshold table, source field mapping, and receiver list as `G` gaps if missing.
- gate_state: Module 2 can move forward with `partial_ready` when goal, source, and output are clear. Module 4 must not block on exact UI details.
- rpa_boundary: Usually `conditionally_suitable` when inventory source is readable and threshold rules can be written; block only if threshold rules are undefined and cannot be confirmed.
- report_sections: Final report must include scope, threshold decision flow, notification flow, exception handling, fact layering, and Chinese development JSON summary.
- source_label_expectations: Threshold rules require customer confirmation; manual review policy may be RAG or Agent suggestion until confirmed.

## email_sorting

- question_behavior: Use `multiple_choice_with_text` for classification signals, folder or label outputs, manual review policy, and notification method.
- requirement_memory_updates: Confirm mailbox platform, classification goal, trigger, and target result as `F` facts. Keep category examples and low-confidence threshold as `G` gaps if unanswered.
- gate_state: Module 2 can move to Module 3 with semantic risk as a candidate. Module 3 should keep semantic judgment visible instead of finalizing fully unattended execution.
- rpa_boundary: Usually `conditionally_suitable` with manual review queue for low-confidence or semantic cases.
- report_sections: Final report must preserve semantic risk, manual review path, low-confidence handling, and source labels.
- source_label_expectations: Category examples supplied by customer are `customer_confirmed`; category rules inferred by Agent remain `agent_inferred_pending_confirmation`.

## logistics_interception

- question_behavior: Use choice-first questions for logistics platform, order source, interception trigger, result confirmation, and manual fallback.
- requirement_memory_updates: Confirm interception goal, operated system, input order identifiers, output result, and completion condition as `F` facts. Keep platform permissions and cutoff timing as `G` gaps if missing.
- gate_state: Module 2 should not ask exact selectors. Module 3 can proceed only when platform operability and result verification are analyzable.
- rpa_boundary: Usually `conditionally_suitable` if order state is queryable, interception action is repeatable, and result can be verified.
- report_sections: Final report must show main process cards, exception cards for missed cutoff and platform failure, and prework gaps.
- source_label_expectations: Cutoff timing and interception success criteria must be confirmed before development.

## material_synonym_judgment

- question_behavior: Ask whether naming rules, mapping table, standard master data, and manual review policy exist. Do not infer sameness rules from one sentence.
- requirement_memory_updates: Confirm material matching goal as an `F` fact, but record missing standard naming rules or mapping table as `G` gaps.
- gate_state: Module 2 may stop with blocker when rule clarity is absent. Module 3 should not force process breakdown for an open-ended semantic judgment task.
- rpa_boundary: Usually `not_suitable_for_direct_rpa` or `not_ready` until naming governance and mapping rules are established.
- report_sections: Final report should be a governance or gap report, not a build plan. It must include prework, reevaluation criteria, and fact layering.
- source_label_expectations: Suggested governance steps can be RAG or Agent suggestions; they are not customer-confirmed implementation facts.

## captcha_heavy_platform_collection

- question_behavior: Use `multiple_choice_with_text` for captcha type, appearance frequency, paid service acceptance, human fallback, and authorization or compliance constraints.
- requirement_memory_updates: Confirm platform, collection goal, captcha type, frequency, and fallback acceptance as `F` facts when answered. Keep unsupported captcha details as `G` gaps.
- gate_state: Module 3 must retrieve captcha boundary material before marking captcha as a blocker. `partial_ready` is allowed when captcha is occasional and fallback exists.
- rpa_boundary: Captcha is a conditional capability, not an automatic blocker. Block only when high-frequency unattended execution is required and no supported instruction, paid service, or human fallback is accepted.
- report_sections: Final report must show captcha handling as a capability boundary, exception policy, cost or accuracy confirmation gap, and source-labeled recommendation.
- source_label_expectations: Captcha service suggestions are `rag_suggested`; customer authorization and fallback decisions must be `customer_confirmed`.
