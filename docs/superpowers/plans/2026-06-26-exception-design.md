# Exception Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build module 5, an exception design contract that expands module 4 process-card exception handoffs into semi-implementation-level exception flows.

**Architecture:** Follow the established module pattern: contract tests first, then JSON Schema, rules, prompt rules, fixtures, README, and platform package integration. Module 5 remains agent-contract material, not a runtime executor and not a final solution/HTML generator.

**Tech Stack:** Markdown, JSON Schema draft 2020-12, JSON fixtures, Python `unittest`, repository-local agent package docs.

## Global Constraints

- Module 5 consumes module 4 process cards and module 3 risks without repeating module 2 clarification.
- Module 5 only runs when module 4 recommends `exception_design`.
- Module 5 defines a structured `exception_design_result`.
- Module 5 expands exceptions by process step.
- Exception cards must include severity, trigger signal, detection basis, handling strategy, continuation policy, candidate capability families, human intervention, record fields, and upstream risk links.
- Module 5 preserves global manual review and logging policies.
- Module 5 remains semi-implementation-level and does not generate exact automation parameters.
- Module 5 routes downstream to `solution_packaging` when complete.

---

## File Structure

- Create `agent_modules/exception_design/README.md`: module purpose, scope, artifact list, and boundary rules.
- Create `agent_modules/exception_design/schemas/exception-design-result.schema.json`: formal output contract for `exception_design_result`.
- Create `agent_modules/exception_design/rules/exception-rules.json`: gating rules, severity values, continue policies, and required fields.
- Create `agent_modules/exception_design/rules/prompt-rules.md`: module 5 prompt behavior.
- Create `agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json`: expected module 5 output for e-commerce daily report.
- Create `agent_modules/exception_design/fixtures/email-sorting-exception-design.json`: expected module 5 output for email sorting.
- Create `tests/test_exception_design_contracts.py`: contract tests for module 5.
- Modify `agent_platform_package/system_prompt/agent-system-prompt.md`: add module 5 guidance and include `exception_design_result` in the single-wrapper rule/example.
- Modify `agent_platform_package/testing/expected_outputs.md`: add module 5 expected output notes.
- Modify `agent_platform_package/testing/module_1_to_4_flow_test.md` or create follow-up notes only if needed to point from module 4 to module 5. Do not rename the existing flow guide.

---

### Task 1: Add Module 5 Contract Tests First

**Files:**
- Create: `tests/test_exception_design_contracts.py`

**Interfaces:**
- Consumes: files later created under `agent_modules/exception_design/`
- Produces: module 5 contract assertions for schema, rules, fixtures, README, and platform integration

- [ ] **Step 1: Write the failing test file**

Create `tests/test_exception_design_contracts.py`:

```python
import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency in local env
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]

MODULE_5_READABILITY_PATHS = [
    "agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json",
    "agent_modules/exception_design/fixtures/email-sorting-exception-design.json",
    "agent_modules/exception_design/README.md",
    "agent_modules/exception_design/rules/prompt-rules.md",
]

COMMON_MOJIBAKE_FRAGMENTS = (
    "骞冲",
    "娴嬭",
    "鑷",
    "鐗",
    "鍏堢",
    "椋炰功",
    "閭",
    "閼",
    "閻",
    "妞",
    "瀹",
    "鍙ｅ緞",
)


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class ExceptionDesignContractTests(unittest.TestCase):
    def assert_has_no_common_mojibake(self, relative_path: str) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")

        for fragment in COMMON_MOJIBAKE_FRAGMENTS:
            with self.subTest(path=relative_path, fragment=fragment):
                self.assertNotIn(fragment, text)

    def test_exception_design_schema_defines_step_flows_and_policies(self):
        schema = load_json("agent_modules/exception_design/schemas/exception-design-result.schema.json")
        props = schema["properties"]
        flow_props = schema["$defs"]["exception_flow"]["properties"]
        card_props = schema["$defs"]["exception_card"]["properties"]

        self.assertEqual(schema["title"], "ExceptionDesignResult")
        self.assertEqual(props["module"]["const"], "module_5_exception_design")
        self.assertEqual(props["exception_depth"]["const"], "semi_implementation_exception_flows")
        self.assertEqual(
            props["status"]["enum"],
            ["completed", "blocked_by_process_breakdown", "needs_more_information"],
        )
        self.assertEqual(
            props["next_stage_recommendation"]["enum"],
            [
                "solution_packaging",
                "return_to_process_breakdown",
                "return_to_rpa_boundary_check",
                "return_to_requirement_clarification",
                "stop_with_blocker",
            ],
        )
        self.assertEqual(
            props["source_process_steps"]["items"]["type"],
            "string",
        )
        self.assertEqual(
            list(flow_props.keys()),
            ["step_id", "step_name", "source_exception_notes", "exception_cards"],
        )
        self.assertEqual(
            list(card_props.keys()),
            [
                "exception_id",
                "exception_type",
                "severity",
                "trigger_signal",
                "detection_basis",
                "handling_strategy",
                "continue_policy",
                "candidate_yingdao_capabilities",
                "human_intervention",
                "record_fields",
                "related_upstream_risks",
            ],
        )
        self.assertIn("manual_review_policy", schema["required"])
        self.assertIn("logging_policy", schema["required"])

    def test_exception_rules_gate_on_module_4_and_forbid_exact_parameters(self):
        rules = load_json("agent_modules/exception_design/rules/exception-rules.json")

        self.assertEqual(rules["module"], "module_5_exception_design")
        self.assertEqual(rules["exception_depth"], "semi_implementation_exception_flows")
        self.assertEqual(rules["required_source_recommendation"], "exception_design")
        self.assertIn("module_4_focus_steps_are_primary", rules["source_priority"])
        self.assertIn("module_3_risks_are_supporting_evidence", rules["source_priority"])
        self.assertEqual(
            rules["severity_levels"],
            ["blocking", "needs_manual_review", "recoverable", "log_only"],
        )
        self.assertIn("continue_other_items", rules["continue_policies"])
        self.assertIn("retry_then_escalate", rules["continue_policies"])
        self.assertIn("do_not_generate_selectors", rules["forbidden_behaviors"])
        self.assertIn("do_not_generate_wait_times", rules["forbidden_behaviors"])
        self.assertIn("do_not_generate_instruction_parameters", rules["forbidden_behaviors"])
        self.assertIn("do_not_generate_html", rules["forbidden_behaviors"])

    def test_prompt_rules_keep_module_5_semi_implementation_level(self):
        text = (ROOT / "agent_modules/exception_design/rules/prompt-rules.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Start from module 4 focus steps", text)
        self.assertIn("Reference module 3 risks", text)
        self.assertIn("Do not generate exact selectors", text)
        self.assertIn("Do not generate wait times", text)
        self.assertIn("Do not generate Yingdao instruction parameters", text)
        self.assertIn("Use module 1 choice-first format", text)

    def test_ecommerce_fixture_expands_platform_collection_exceptions(self):
        fixture = load_json("agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json")

        self.assertEqual(fixture["module"], "module_5_exception_design")
        self.assertEqual(fixture["status"], "completed")
        self.assertEqual(fixture["exception_depth"], "semi_implementation_exception_flows")
        self.assertEqual(fixture["next_stage_recommendation"], "solution_packaging")
        self.assertIn("S03", fixture["source_process_steps"])
        self.assertTrue(fixture["manual_review_policy"]["required"])
        self.assertTrue(fixture["logging_policy"]["required"])

        all_cards = [
            card
            for flow in fixture["exception_flows"]
            for card in flow["exception_cards"]
        ]
        types = {card["exception_type"] for card in all_cards}
        self.assertIn("login_failure", types)
        self.assertIn("source_data_missing", types)
        self.assertIn("target_write_failure", types)
        login_card = next(card for card in all_cards if card["exception_type"] == "login_failure")
        self.assertEqual(login_card["severity"], "blocking")
        self.assertEqual(login_card["human_intervention"], "required")
        self.assertIn("unstable_platform", login_card["related_upstream_risks"])
        self.assertIn("platform", login_card["record_fields"])

    def test_email_fixture_expands_low_confidence_exception(self):
        fixture = load_json("agent_modules/exception_design/fixtures/email-sorting-exception-design.json")

        self.assertEqual(fixture["module"], "module_5_exception_design")
        self.assertEqual(fixture["next_stage_recommendation"], "solution_packaging")
        self.assertIn("S04", fixture["source_process_steps"])

        all_cards = [
            card
            for flow in fixture["exception_flows"]
            for card in flow["exception_cards"]
        ]
        low_confidence_cards = [
            card for card in all_cards if card["exception_type"] == "low_confidence"
        ]
        self.assertEqual(len(low_confidence_cards), 1)
        card = low_confidence_cards[0]
        self.assertEqual(card["severity"], "needs_manual_review")
        self.assertEqual(card["continue_policy"], "continue_other_items")
        self.assertIn("manual review queue", card["candidate_yingdao_capabilities"])
        self.assertIn("semantic_judgment", card["related_upstream_risks"])
        self.assertIn("message_id", card["record_fields"])

    def test_exception_design_fixtures_validate_against_schema_when_validator_available(self):
        if jsonschema is None:
            self.skipTest("jsonschema is not installed in this environment")

        schema = load_json("agent_modules/exception_design/schemas/exception-design-result.schema.json")
        fixtures = [
            "agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json",
            "agent_modules/exception_design/fixtures/email-sorting-exception-design.json",
        ]

        for relative_path in fixtures:
            with self.subTest(path=relative_path):
                jsonschema.validate(instance=load_json(relative_path), schema=schema)

    def test_readme_lists_module_5_artifacts(self):
        text = (ROOT / "agent_modules/exception_design/README.md").read_text(encoding="utf-8")
        expected_paths = [
            "schemas/exception-design-result.schema.json",
            "rules/exception-rules.json",
            "rules/prompt-rules.md",
            "fixtures/ecommerce-daily-report-exception-design.json",
            "fixtures/email-sorting-exception-design.json",
        ]

        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)

    def test_platform_prompt_allows_exception_design_result_in_single_wrapper(self):
        text = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("exception_design_result", text)
        self.assertIn("Module 5", text)
        self.assertIn("semi-implementation-level exception flows", text)
        self.assertIn("do not generate exact selectors", text)

    def test_module_5_expected_output_guidance_mentions_exception_contract(self):
        text = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("exception_design_result", text)
        self.assertIn("semi_implementation_exception_flows", text)
        self.assertIn("manual_review_policy", text)
        self.assertIn("logging_policy", text)
        self.assertIn("solution_packaging", text)

    def test_module_5_assets_do_not_contain_common_mojibake_fragments(self):
        for relative_path in MODULE_5_READABILITY_PATHS:
            self.assert_has_no_common_mojibake(relative_path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```powershell
python -m unittest tests.test_exception_design_contracts -v
```

Expected: FAIL with `FileNotFoundError` for missing `agent_modules/exception_design` files.

- [ ] **Step 3: Commit failing tests**

Run:

```powershell
git add tests/test_exception_design_contracts.py
git commit -m "test: add exception design contracts"
```

---

### Task 2: Add Module 5 Schema and Rules

**Files:**
- Create: `agent_modules/exception_design/schemas/exception-design-result.schema.json`
- Create: `agent_modules/exception_design/rules/exception-rules.json`
- Create: `agent_modules/exception_design/rules/prompt-rules.md`

**Interfaces:**
- Consumes: test expectations from Task 1.
- Produces: formal module 5 output contract and prompt rules for fixtures and platform integration.

- [ ] **Step 1: Create `exception-design-result.schema.json`**

Create `agent_modules/exception_design/schemas/exception-design-result.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ExceptionDesignResult",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "module",
    "status",
    "source_process_steps",
    "exception_depth",
    "exception_flows",
    "global_exception_policies",
    "manual_review_policy",
    "logging_policy",
    "open_questions",
    "next_stage_recommendation"
  ],
  "properties": {
    "module": { "const": "module_5_exception_design" },
    "status": {
      "enum": ["completed", "blocked_by_process_breakdown", "needs_more_information"]
    },
    "source_process_steps": {
      "type": "array",
      "items": { "type": "string" }
    },
    "exception_depth": { "const": "semi_implementation_exception_flows" },
    "exception_flows": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/exception_flow" }
    },
    "global_exception_policies": {
      "type": "array",
      "items": { "type": "string" }
    },
    "manual_review_policy": { "$ref": "#/$defs/manual_review_policy" },
    "logging_policy": { "$ref": "#/$defs/logging_policy" },
    "open_questions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "next_stage_recommendation": {
      "enum": [
        "solution_packaging",
        "return_to_process_breakdown",
        "return_to_rpa_boundary_check",
        "return_to_requirement_clarification",
        "stop_with_blocker"
      ]
    }
  },
  "$defs": {
    "exception_flow": {
      "type": "object",
      "additionalProperties": false,
      "required": ["step_id", "step_name", "source_exception_notes", "exception_cards"],
      "properties": {
        "step_id": { "type": "string" },
        "step_name": { "type": "string" },
        "source_exception_notes": {
          "type": "array",
          "items": { "type": "string" }
        },
        "exception_cards": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/exception_card" }
        }
      }
    },
    "exception_card": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "exception_id",
        "exception_type",
        "severity",
        "trigger_signal",
        "detection_basis",
        "handling_strategy",
        "continue_policy",
        "candidate_yingdao_capabilities",
        "human_intervention",
        "record_fields",
        "related_upstream_risks"
      ],
      "properties": {
        "exception_id": { "type": "string", "pattern": "^E-S[0-9]{2}-[0-9]{2}$" },
        "exception_type": { "$ref": "#/$defs/exception_type" },
        "severity": { "$ref": "#/$defs/severity" },
        "trigger_signal": { "type": "string", "minLength": 1 },
        "detection_basis": {
          "type": "array",
          "items": { "type": "string" }
        },
        "handling_strategy": { "type": "string", "minLength": 1 },
        "continue_policy": { "$ref": "#/$defs/continue_policy" },
        "candidate_yingdao_capabilities": {
          "type": "array",
          "items": { "type": "string" }
        },
        "human_intervention": { "enum": ["none", "optional", "required"] },
        "record_fields": {
          "type": "array",
          "minItems": 1,
          "items": { "type": "string" }
        },
        "related_upstream_risks": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "exception_type": {
      "enum": [
        "login_failure",
        "permission_missing",
        "captcha_or_device_verification",
        "source_data_missing",
        "source_field_missing",
        "download_failure",
        "file_format_unreadable",
        "field_mapping_mismatch",
        "rule_not_matched",
        "low_confidence",
        "target_template_changed",
        "target_write_failure",
        "result_verification_failed",
        "notification_failure",
        "manual_review_timeout",
        "unknown_exception"
      ]
    },
    "severity": {
      "enum": ["blocking", "needs_manual_review", "recoverable", "log_only"]
    },
    "continue_policy": {
      "enum": [
        "stop_entire_run",
        "stop_current_step",
        "continue_other_items",
        "skip_current_item",
        "retry_then_escalate",
        "wait_for_manual_review",
        "log_and_continue"
      ]
    },
    "manual_review_policy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["required", "review_queue_name", "review_record_fields"],
      "properties": {
        "required": { "type": "boolean" },
        "review_queue_name": { "type": "string" },
        "review_record_fields": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "logging_policy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["required", "minimum_record_fields"],
      "properties": {
        "required": { "type": "boolean" },
        "minimum_record_fields": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Create `exception-rules.json`**

Create `agent_modules/exception_design/rules/exception-rules.json`:

```json
{
  "module": "module_5_exception_design",
  "exception_depth": "semi_implementation_exception_flows",
  "required_source_recommendation": "exception_design",
  "source_priority": [
    "module_4_focus_steps_are_primary",
    "module_4_exception_notes_are_primary_topics",
    "module_4_assumptions_validation_points_and_dependencies_are_context",
    "module_3_risks_are_supporting_evidence",
    "module_2_boundary_facts_are_wording_context_only"
  ],
  "severity_levels": [
    "blocking",
    "needs_manual_review",
    "recoverable",
    "log_only"
  ],
  "continue_policies": [
    "stop_entire_run",
    "stop_current_step",
    "continue_other_items",
    "skip_current_item",
    "retry_then_escalate",
    "wait_for_manual_review",
    "log_and_continue"
  ],
  "human_intervention_values": [
    "none",
    "optional",
    "required"
  ],
  "required_exception_card_fields": [
    "exception_id",
    "exception_type",
    "severity",
    "trigger_signal",
    "detection_basis",
    "handling_strategy",
    "continue_policy",
    "candidate_yingdao_capabilities",
    "human_intervention",
    "record_fields",
    "related_upstream_risks"
  ],
  "generation_requirements": [
    "expand exceptions by module 4 process step",
    "link exception cards to module 3 risks or capability notes when relevant",
    "preserve manual review policy",
    "preserve logging policy",
    "prefer scoped continuation when business-safe",
    "ask only when exception handling would be unsafe without confirmation"
  ],
  "forbidden_behaviors": [
    "do_not_override_module_3_decision",
    "do_not_rebuild_module_4_happy_path",
    "do_not_repeat_module_2_boundary_questions",
    "do_not_generate_exact_click_paths",
    "do_not_generate_selectors",
    "do_not_generate_wait_times",
    "do_not_generate_retry_counts_as_parameters",
    "do_not_generate_instruction_parameters",
    "do_not_generate_solution_blueprint",
    "do_not_generate_html"
  ]
}
```

- [ ] **Step 3: Create `prompt-rules.md`**

Create `agent_modules/exception_design/rules/prompt-rules.md`:

```markdown
# Exception Design Prompt Rules

## Do

- Start from module 4 focus steps and exception notes.
- Reference module 3 risks and capability notes as exception evidence.
- Keep exception handling semi-implementation-level.
- Produce step-level exception flows.
- Define severity, trigger signal, detection basis, handling strategy, continuation policy, human intervention, record fields, and related upstream risks.
- Preserve manual review and logging requirements.
- Use module 1 choice-first format when exception handling cannot be safely designed from upstream facts.

## Do Not

- Do not override module 3's suitability decision.
- Do not rebuild module 4's happy path.
- Do not repeat module 2 boundary questions.
- Do not generate exact selectors.
- Do not generate exact click paths.
- Do not generate wait times.
- Do not generate retry counts as implementation parameters.
- Do not generate Yingdao instruction parameters.
- Do not generate the final solution blueprint.
- Do not generate HTML.
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m unittest tests.test_exception_design_contracts -v
```

Expected: schema/rules/prompt tests pass; fixture, README, and platform integration tests still fail.

- [ ] **Step 5: Commit schema and rules**

Run:

```powershell
git add agent_modules/exception_design/schemas/exception-design-result.schema.json agent_modules/exception_design/rules/exception-rules.json agent_modules/exception_design/rules/prompt-rules.md
git commit -m "feat: add exception design schema and rules"
```

---

### Task 3: Add Module 5 Fixtures and README

**Files:**
- Create: `agent_modules/exception_design/README.md`
- Create: `agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json`
- Create: `agent_modules/exception_design/fixtures/email-sorting-exception-design.json`

**Interfaces:**
- Consumes: schema/rules from Task 2.
- Produces: readable expected outputs for common e-commerce and email scenarios.

- [ ] **Step 1: Create README**

Create `agent_modules/exception_design/README.md`:

```markdown
# Exception Design Module

Module 5 expands module 4 exception handoff points into semi-implementation-level exception flows.

## Scope

This module consumes module 4 `process_breakdown_result` and references module 3 `rpa_boundary_result` risks. It does not repeat requirement clarification, override RPA boundary decisions, rebuild the happy path, generate exact selectors, generate wait times, produce Yingdao instruction parameters, or create HTML.

## Artifacts

- `schemas/exception-design-result.schema.json`
- `rules/exception-rules.json`
- `rules/prompt-rules.md`
- `fixtures/ecommerce-daily-report-exception-design.json`
- `fixtures/email-sorting-exception-design.json`

## Boundary Rule

Exception flows describe detection, containment, continuation policy, human intervention, and logging. They are not build scripts.
```

- [ ] **Step 2: Create e-commerce fixture**

Create `agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json`:

```json
{
  "module": "module_5_exception_design",
  "status": "completed",
  "source_process_steps": ["S02", "S03", "S04", "S05", "S06"],
  "exception_depth": "semi_implementation_exception_flows",
  "exception_flows": [
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
          "handling_strategy": "Do not write an inferred value into the report. Add the item to the manual review list and keep source evidence.",
          "continue_policy": "continue_other_items",
          "candidate_yingdao_capabilities": ["condition judgment", "table processing", "logging"],
          "human_intervention": "required",
          "record_fields": ["platform", "store", "date", "missing_metric", "source_snapshot"],
          "related_upstream_risks": ["unstable_input", "requires_field_mapping"]
        }
      ]
    },
    {
      "step_id": "S05",
      "step_name": "Write Tencent Docs report",
      "source_exception_notes": ["write failure", "template changed", "permission missing"],
      "exception_cards": [
        {
          "exception_id": "E-S05-01",
          "exception_type": "target_write_failure",
          "severity": "blocking",
          "trigger_signal": "The Tencent Docs template cannot be opened, edited, or saved to the configured position.",
          "detection_basis": ["target document state", "write result", "permission status"],
          "handling_strategy": "Stop report delivery, notify a human operator, and preserve normalized data so it can be written manually or retried later.",
          "continue_policy": "stop_current_step",
          "candidate_yingdao_capabilities": ["condition judgment", "online document editing", "logging", "notification"],
          "human_intervention": "required",
          "record_fields": ["document", "target_position", "write_status", "failure_reason", "detected_at"],
          "related_upstream_risks": ["unverifiable_result", "requires_result_log"]
        }
      ]
    }
  ],
  "global_exception_policies": [
    "Do not overwrite report values when source data is missing or mapping is uncertain.",
    "Continue unaffected platforms only when each platform can be isolated in the report.",
    "Preserve source value and written value evidence for every abnormal item."
  ],
  "manual_review_policy": {
    "required": true,
    "review_queue_name": "daily_report_manual_review",
    "review_record_fields": ["platform", "store", "date", "metric", "exception_type", "source_evidence"]
  },
  "logging_policy": {
    "required": true,
    "minimum_record_fields": ["run_id", "step_id", "exception_id", "severity", "detected_at", "handling_result"]
  },
  "open_questions": [],
  "next_stage_recommendation": "solution_packaging"
}
```

- [ ] **Step 3: Create email fixture**

Create `agent_modules/exception_design/fixtures/email-sorting-exception-design.json`:

```json
{
  "module": "module_5_exception_design",
  "status": "completed",
  "source_process_steps": ["S02", "S04", "S05", "S06"],
  "exception_depth": "semi_implementation_exception_flows",
  "exception_flows": [
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
        },
        {
          "exception_id": "E-S04-02",
          "exception_type": "rule_not_matched",
          "severity": "needs_manual_review",
          "trigger_signal": "No folder or label rule matches the email after sender, subject, and body checks.",
          "detection_basis": ["classification taxonomy", "sender rules", "subject rules", "body keyword rules"],
          "handling_strategy": "Place the email into the pending category and record why no rule matched.",
          "continue_policy": "continue_other_items",
          "candidate_yingdao_capabilities": ["condition judgment", "email processing", "logging"],
          "human_intervention": "required",
          "record_fields": ["message_id", "sender", "subject", "rule_check_result", "detected_at"],
          "related_upstream_risks": ["missing_rules", "semantic_judgment"]
        }
      ]
    }
  ],
  "global_exception_policies": [
    "Do not permanently classify low-confidence emails without a manual review route.",
    "Keep the original email available for review.",
    "Log classification evidence for every manually reviewed message."
  ],
  "manual_review_policy": {
    "required": true,
    "review_queue_name": "email_pending_manual_confirmation",
    "review_record_fields": ["message_id", "sender", "subject", "matched_signals", "exception_type"]
  },
  "logging_policy": {
    "required": true,
    "minimum_record_fields": ["run_id", "step_id", "exception_id", "message_id", "detected_at", "handling_result"]
  },
  "open_questions": [],
  "next_stage_recommendation": "solution_packaging"
}
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m unittest tests.test_exception_design_contracts -v
```

Expected: schema/rules/prompt/fixtures/README tests pass; platform prompt and expected-output tests still fail.

- [ ] **Step 5: Commit fixtures and README**

Run:

```powershell
git add agent_modules/exception_design/README.md agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json agent_modules/exception_design/fixtures/email-sorting-exception-design.json
git commit -m "feat: add exception design fixtures"
```

---

### Task 4: Add Platform Package Integration

**Files:**
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Modify: `agent_platform_package/testing/expected_outputs.md`

**Interfaces:**
- Consumes: module 5 contract from Tasks 2-3.
- Produces: platform prompt and testing guidance that expose module 5 through the single JSON wrapper.

- [ ] **Step 1: Update system prompt wrapper guidance**

Modify `agent_platform_package/system_prompt/agent-system-prompt.md` so the single-wrapper rule and example include `exception_design_result`.

Required readable phrase:

```markdown
Module 5 must produce one `exception_design_result` object. It turns module 4 exception handoff steps into semi-implementation-level exception flows.
```

Add guidance:

```markdown
Module 5 must produce semi-implementation-level exception flows by process step. It may define severity, trigger signal, detection basis, handling strategy, continuation policy, candidate Yingdao capability families, human intervention, record fields, manual review policy, and logging policy.

Module 5 must start from module 4 focus steps and exception notes, and reference module 3 risks and capability notes as supporting evidence.

Module 5 must not generate exact selectors, exact click paths, wait times, retry counts as implementation parameters, Yingdao instruction parameters, final solution blueprint, or HTML.
```

- [ ] **Step 2: Update expected outputs**

Add a Module 5 section to `agent_platform_package/testing/expected_outputs.md`:

```markdown
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
```

- [ ] **Step 3: Run focused tests**

Run:

```powershell
python -m unittest tests.test_exception_design_contracts tests.test_process_breakdown_contracts tests.test_platform_package_contracts -v
```

Expected: PASS, with only optional `jsonschema` skips allowed.

- [ ] **Step 4: Commit platform integration**

Run:

```powershell
git add agent_platform_package/system_prompt/agent-system-prompt.md agent_platform_package/testing/expected_outputs.md
git commit -m "docs: add exception design platform guidance"
```

---

### Task 5: Full Verification

**Files:**
- Modify: none unless verification exposes a defect.

**Interfaces:**
- Consumes: all module 1-5 contracts.
- Produces: final evidence that module 5 integrates with existing modules.

- [ ] **Step 1: Run complete contract tests**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts tests.test_platform_package_contracts tests.test_exception_design_contracts -v
```

Expected: PASS, with only optional `jsonschema` skips allowed if dependency is unavailable.

- [ ] **Step 2: Run module 5 readability scan**

Run:

```powershell
rg -n "骞冲|娴嬭|鑷|鐗|鍏堢|椋炰功|閭|閼|閻|妞|瀹|鍙ｅ緞" agent_modules/exception_design agent_platform_package/testing tests/test_exception_design_contracts.py
```

Expected: matches only in `tests/test_exception_design_contracts.py` because it contains the deliberate pattern literals.

- [ ] **Step 3: Verify git state**

Run:

```powershell
git status --short
git log --oneline -8
```

Expected: clean working tree and latest module 5 commits visible.

- [ ] **Step 4: Commit verification fix only if files changed**

If verification exposed a defect, fix it and commit:

```powershell
git add <changed-files>
git commit -m "test: verify exception design module"
```

If no files changed, do not create an empty commit.

---

## Self-Review

- Spec coverage: Tasks cover tests, schema/rules, prompt rules, fixtures, README, platform prompt integration, expected outputs, and full verification.
- Placeholder scan: no deferred implementation markers are present.
- Type consistency: `exception_design_result`, `module_5_exception_design`, `semi_implementation_exception_flows`, and `solution_packaging` match the written spec.
- Scope check: the plan is focused on module 5 only and leaves solution packaging, HTML generation, and quality audit to later modules.
