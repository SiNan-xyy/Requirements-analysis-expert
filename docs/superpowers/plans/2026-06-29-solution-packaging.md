# Solution Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build module 6, a solution packaging contract that turns Modules 1-5 into a customer HTML report, a developer HTML report, and one structured fact source.

**Architecture:** Follow the established agent-module pattern: contract tests first, then JSON Schema, rules, prompt rules, fixtures, README, and platform package integration. Module 6 is a packaging and alignment module, not a runtime renderer and not a final build guide.

**Tech Stack:** Markdown, JSON Schema draft 2020-12, JSON fixtures, Python `unittest`, repository-local agent package docs.

## Global Constraints

- Module 6 packages Modules 1-5 without changing their contracts.
- The structured JSON fact source is the single source of truth.
- Customer HTML and developer HTML are presentation layers generated from the same fact source.
- Module 6 must separate confirmed facts, inferred recommendations, missing required items, and uncertainty.
- `module_status` describes package generation status.
- `developer_alignment_status` describes implementation readiness: `ready_for_development`, `needs_confirmation`, `not_recommended`, or `blocked`.
- The developer HTML is a development alignment package, not a final build guide.
- Module 6 must not generate exact click paths, selectors, wait times, retry counts as executable parameters, Yingdao instruction parameters, or customer-confirmed language for inferred content.

---

## File Structure

- Create `agent_modules/solution_packaging/README.md`: module purpose, scope, artifacts, and boundary rules.
- Create `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`: formal output contract for `solution_package_result`.
- Create `agent_modules/solution_packaging/rules/packaging-rules.json`: status rules, fact-layer rules, rendering rules, and prohibited content rules.
- Create `agent_modules/solution_packaging/rules/prompt-rules.md`: module 6 prompt behavior.
- Create `agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json`: expected package for the e-commerce daily report scenario.
- Create `agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json`: expected package for the email sorting scenario.
- Create `agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json`: expected package when direct RPA is not recommended.
- Create `agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json`: expected gap-report package when upstream information is blocked.
- Create `tests/test_solution_packaging_contracts.py`: contract tests for schema, rules, fixtures, HTML source alignment, and platform integration.
- Modify `agent_platform_package/system_prompt/agent-system-prompt.md`: add Module 6 guidance and include `solution_package_result` in the single-wrapper rule.
- Modify `agent_platform_package/testing/expected_outputs.md`: add Module 6 expected output notes and invalid output signs.
- Modify or add platform flow documentation under `agent_platform_package/testing/` to describe Module 1-6 flow and Module 6 readiness statuses.

---

### Task 1: Add Module 6 Contract Tests First

**Files:**
- Create: `tests/test_solution_packaging_contracts.py`

**Interfaces:**
- Consumes: files later created under `agent_modules/solution_packaging/`
- Produces: module 6 contract assertions for schema, rules, fixtures, README, and platform integration

- [ ] **Step 1: Write the failing test file**

Create `tests/test_solution_packaging_contracts.py`:

```python
import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency in local env
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]

MODULE_6_READABILITY_PATHS = [
    "agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json",
    "agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json",
    "agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json",
    "agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json",
    "agent_modules/solution_packaging/README.md",
    "agent_modules/solution_packaging/rules/prompt-rules.md",
]

COMMON_MOJIBAKE_FRAGMENTS = (
    "妤犵偛",
    "瑜板崬",
    "閸欙絽",
    "闁?",
    "閻?",
    "濡?",
    "绾?",
    "顔?",
)

PROHIBITED_HTML_TERMS = (
    "selector",
    "xpath",
    "css selector",
    "click path",
    "wait 3 seconds",
    "retry count =",
)


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


class SolutionPackagingContractTests(unittest.TestCase):
    def assert_has_no_common_mojibake(self, relative_path: str) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")

        for fragment in COMMON_MOJIBAKE_FRAGMENTS:
            with self.subTest(path=relative_path, fragment=fragment):
                self.assertNotIn(fragment, text)

    def test_solution_package_schema_defines_fact_layer_html_outputs_and_readiness_status(self):
        schema = load_json("agent_modules/solution_packaging/schemas/solution-package-result.schema.json")
        props = schema["properties"]
        fact_props = props["fact_base"]["properties"]

        self.assertEqual(schema["title"], "SolutionPackageResult")
        self.assertEqual(props["module"]["const"], "module_6_solution_packaging")
        self.assertIn("module_status", schema["required"])
        self.assertIn("developer_alignment_status", schema["required"])
        self.assertEqual(
            props["developer_alignment_status"]["enum"],
            ["ready_for_development", "needs_confirmation", "not_recommended", "blocked"],
        )
        self.assertIn("confirmed_facts", fact_props)
        self.assertIn("inferred_recommendations", fact_props)
        self.assertIn("missing_required_items", fact_props)
        self.assertIn("conflict_or_uncertainty", fact_props)
        self.assertIn("customer_view_model", props)
        self.assertIn("developer_view_model", props)
        self.assertIn("render_outputs", props)

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_all_solution_package_fixtures_validate_against_schema(self):
        schema = load_json("agent_modules/solution_packaging/schemas/solution-package-result.schema.json")
        fixture_paths = [
            "agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json",
            "agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json",
            "agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json",
            "agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json",
        ]

        for path in fixture_paths:
            with self.subTest(path=path):
                jsonschema.validate(load_json(path), schema)

    def test_ecommerce_daily_report_remains_needs_confirmation(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        missing_topics = {item["topic"] for item in fixture["fact_base"]["missing_required_items"]}

        self.assertEqual(fixture["developer_alignment_status"], "needs_confirmation")
        self.assertIn("field_mapping", missing_topics)
        self.assertIn("metric_definition", missing_topics)
        self.assertIn("date_definition", missing_topics)
        self.assertIn("result_validation_method", missing_topics)
        self.assertNotEqual(fixture["developer_alignment_status"], "ready_for_development")

    def test_email_sorting_keeps_semantic_risk_and_manual_review_visible(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json")
        risk_text = " ".join(iter_strings(fixture))

        self.assertEqual(fixture["developer_alignment_status"], "needs_confirmation")
        self.assertIn("semantic", risk_text.lower())
        self.assertIn("manual", risk_text.lower())
        self.assertIn("low-confidence", risk_text.lower())

    def test_not_recommended_package_does_not_look_like_implementation_plan(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json")
        developer_model = fixture["developer_view_model"]
        process_cards = developer_model["process_breakdown"]["process_cards"]

        self.assertEqual(fixture["developer_alignment_status"], "not_recommended")
        self.assertEqual(process_cards, [])
        self.assertIn("governance", " ".join(iter_strings(fixture)).lower())
        self.assertIn("reevaluation", " ".join(iter_strings(fixture)).lower())

    def test_blocked_package_is_gap_report_not_solution_report(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json")

        self.assertEqual(fixture["developer_alignment_status"], "blocked")
        self.assertEqual(fixture["module_status"], "blocked")
        self.assertGreater(len(fixture["fact_base"]["missing_required_items"]), 0)
        self.assertEqual(fixture["customer_view_model"]["report_type"], "gap_report")
        self.assertEqual(fixture["developer_view_model"]["report_type"], "gap_report")

    def test_inferred_recommendations_are_not_marked_as_development_facts(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")

        for item in fixture["fact_base"]["inferred_recommendations"]:
            with self.subTest(item=item["item_id"]):
                self.assertTrue(item["requires_confirmation"])
                self.assertFalse(item["can_be_used_for_development"])

    def test_customer_and_developer_html_use_same_fact_ids(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        fact_ids = {fact["fact_id"] for fact in fixture["fact_base"]["confirmed_facts"]}
        customer_refs = set(fixture["customer_view_model"]["referenced_fact_ids"])
        developer_refs = set(fixture["developer_view_model"]["referenced_fact_ids"])

        self.assertTrue(customer_refs.issubset(fact_ids))
        self.assertTrue(developer_refs.issubset(fact_ids))
        self.assertGreater(len(customer_refs), 0)
        self.assertGreater(len(developer_refs), 0)

    def test_render_outputs_are_html_strings_without_prohibited_implementation_details(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        html = (
            fixture["render_outputs"]["customer_html"]
            + "\n"
            + fixture["render_outputs"]["developer_html"]
        ).lower()

        self.assertIn("<section", html)
        self.assertIn("card", html)
        for term in PROHIBITED_HTML_TERMS:
            with self.subTest(term=term):
                self.assertNotIn(term, html)

    def test_packaging_rules_define_status_fact_and_rendering_constraints(self):
        rules = load_json("agent_modules/solution_packaging/rules/packaging-rules.json")

        self.assertIn("status_rules", rules)
        self.assertIn("fact_layer_rules", rules)
        self.assertIn("rendering_rules", rules)
        self.assertIn("prohibited_content", rules)
        self.assertIn("manual_review_before_implementation", rules["next_stage_recommendations"])

    def test_prompt_and_platform_docs_include_module_6(self):
        system_prompt = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(encoding="utf-8")
        expected_outputs = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(encoding="utf-8")

        self.assertIn("Module 6: Solution Packaging", system_prompt)
        self.assertIn("solution_package_result", system_prompt)
        self.assertIn("Module 6 Expected Output", expected_outputs)
        self.assertIn("solution_package_result", expected_outputs)

    def test_module_6_files_have_readable_text(self):
        for path in MODULE_6_READABILITY_PATHS:
            with self.subTest(path=path):
                self.assert_has_no_common_mojibake(path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts -v
```

Expected: FAIL because `agent_modules/solution_packaging/` files do not exist yet.

- [ ] **Step 3: Commit the failing tests**

Run:

```powershell
git add tests/test_solution_packaging_contracts.py
git commit -m "test: add solution packaging contract tests"
```

Expected: commit succeeds with only the new test file staged.

---

### Task 2: Add Solution Package JSON Schema

**Files:**
- Create: `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`
- Modify: `tests/test_solution_packaging_contracts.py` only if a test contains a typo discovered while implementing the schema

**Interfaces:**
- Consumes: `tests/test_solution_packaging_contracts.py`
- Produces: `SolutionPackageResult` JSON Schema consumed by fixtures and platform expected output

- [ ] **Step 1: Create the schema file**

Create `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/solution-package-result.schema.json",
  "title": "SolutionPackageResult",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "module",
    "module_status",
    "developer_alignment_status",
    "source_modules",
    "fact_base",
    "decision_summary",
    "customer_view_model",
    "developer_view_model",
    "render_outputs",
    "next_stage_recommendation"
  ],
  "properties": {
    "module": { "const": "module_6_solution_packaging" },
    "module_status": { "enum": ["completed", "blocked"] },
    "developer_alignment_status": {
      "enum": ["ready_for_development", "needs_confirmation", "not_recommended", "blocked"]
    },
    "source_modules": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "module_1_interaction_schema",
        "module_2_requirement_clarification",
        "module_3_rpa_boundary_check",
        "module_4_process_breakdown",
        "module_5_exception_design"
      ],
      "properties": {
        "module_1_interaction_schema": { "$ref": "#/$defs/source_module_ref" },
        "module_2_requirement_clarification": { "$ref": "#/$defs/source_module_ref" },
        "module_3_rpa_boundary_check": { "$ref": "#/$defs/source_module_ref" },
        "module_4_process_breakdown": { "$ref": "#/$defs/source_module_ref" },
        "module_5_exception_design": { "$ref": "#/$defs/source_module_ref" }
      }
    },
    "fact_base": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "confirmed_facts",
        "inferred_recommendations",
        "missing_required_items",
        "conflict_or_uncertainty"
      ],
      "properties": {
        "confirmed_facts": {
          "type": "array",
          "items": { "$ref": "#/$defs/confirmed_fact" }
        },
        "inferred_recommendations": {
          "type": "array",
          "items": { "$ref": "#/$defs/inferred_recommendation" }
        },
        "missing_required_items": {
          "type": "array",
          "items": { "$ref": "#/$defs/missing_required_item" }
        },
        "conflict_or_uncertainty": {
          "type": "array",
          "items": { "$ref": "#/$defs/conflict_or_uncertainty" }
        }
      }
    },
    "decision_summary": { "$ref": "#/$defs/decision_summary" },
    "customer_view_model": { "$ref": "#/$defs/customer_view_model" },
    "developer_view_model": { "$ref": "#/$defs/developer_view_model" },
    "render_outputs": {
      "type": "object",
      "additionalProperties": false,
      "required": ["customer_html", "developer_html"],
      "properties": {
        "customer_html": { "type": "string", "minLength": 1 },
        "developer_html": { "type": "string", "minLength": 1 }
      }
    },
    "next_stage_recommendation": {
      "enum": [
        "manual_review_before_implementation",
        "implementation_planning",
        "return_to_exception_design",
        "return_to_process_breakdown",
        "return_to_rpa_boundary_check",
        "return_to_requirement_clarification",
        "stop_with_gap_report",
        "stop_with_blocker"
      ]
    }
  },
  "$defs": {
    "source_module_ref": {
      "type": "object",
      "additionalProperties": false,
      "required": ["status", "summary"],
      "properties": {
        "status": { "type": "string" },
        "summary": { "type": "string" }
      }
    },
    "confidence": {
      "enum": ["high", "medium_high", "medium", "low", "none"]
    },
    "confirmed_fact": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "fact_id",
        "topic",
        "value",
        "source_module",
        "source_type",
        "confidence",
        "can_be_used_for_development"
      ],
      "properties": {
        "fact_id": { "type": "string", "pattern": "^F[0-9]{3}$" },
        "topic": { "type": "string" },
        "value": {},
        "source_module": { "type": "string" },
        "source_type": { "type": "string" },
        "confidence": { "$ref": "#/$defs/confidence" },
        "can_be_used_for_development": { "type": "boolean" }
      }
    },
    "inferred_recommendation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "item_id",
        "topic",
        "value",
        "basis",
        "requires_confirmation",
        "can_be_used_for_development"
      ],
      "properties": {
        "item_id": { "type": "string", "pattern": "^I[0-9]{3}$" },
        "topic": { "type": "string" },
        "value": { "type": "string" },
        "basis": { "type": "array", "items": { "type": "string" } },
        "requires_confirmation": { "type": "boolean" },
        "can_be_used_for_development": { "type": "boolean" }
      }
    },
    "missing_required_item": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "item_id",
        "topic",
        "question",
        "why_it_matters",
        "blocking_level",
        "owner"
      ],
      "properties": {
        "item_id": { "type": "string", "pattern": "^M[0-9]{3}$" },
        "topic": { "type": "string" },
        "question": { "type": "string" },
        "why_it_matters": { "type": "string" },
        "blocking_level": { "enum": ["high", "medium", "low"] },
        "owner": { "type": "string" }
      }
    },
    "conflict_or_uncertainty": {
      "type": "object",
      "additionalProperties": false,
      "required": ["item_id", "topic", "description", "impact", "resolution_needed"],
      "properties": {
        "item_id": { "type": "string", "pattern": "^U[0-9]{3}$" },
        "topic": { "type": "string" },
        "description": { "type": "string" },
        "impact": { "type": "string" },
        "resolution_needed": { "type": "boolean" }
      }
    },
    "decision_summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["recommendation", "headline", "confidence", "reasoning_points"],
      "properties": {
        "recommendation": {
          "enum": ["recommended", "conditional", "not_recommended", "blocked"]
        },
        "headline": { "type": "string" },
        "confidence": { "$ref": "#/$defs/confidence" },
        "reasoning_points": { "type": "array", "items": { "type": "string" } }
      }
    },
    "customer_view_model": {
      "type": "object",
      "additionalProperties": true,
      "required": [
        "report_type",
        "headline",
        "recommendation",
        "requirement_understanding",
        "rpa_fit_summary",
        "business_scope_included",
        "business_scope_excluded",
        "process_cards",
        "risk_and_manual_intervention",
        "customer_preparation_items",
        "next_steps",
        "referenced_fact_ids"
      ],
      "properties": {
        "report_type": { "enum": ["solution_report", "gap_report"] },
        "headline": { "type": "string" },
        "recommendation": { "type": "string" },
        "requirement_understanding": { "type": "string" },
        "rpa_fit_summary": { "type": "array", "items": { "type": "string" } },
        "business_scope_included": { "type": "array", "items": { "type": "string" } },
        "business_scope_excluded": { "type": "array", "items": { "type": "string" } },
        "process_cards": { "type": "array", "items": { "$ref": "#/$defs/view_process_card" } },
        "risk_and_manual_intervention": { "type": "array", "items": { "type": "string" } },
        "customer_preparation_items": { "type": "array", "items": { "type": "string" } },
        "next_steps": { "type": "array", "items": { "type": "string" } },
        "referenced_fact_ids": {
          "type": "array",
          "items": { "type": "string", "pattern": "^F[0-9]{3}$" }
        }
      }
    },
    "developer_view_model": {
      "type": "object",
      "additionalProperties": true,
      "required": [
        "report_type",
        "implementation_status",
        "confirmed_development_basis",
        "blocking_confirmation_items",
        "agent_inferred_recommendations",
        "rpa_capability_boundary",
        "process_breakdown",
        "field_and_data_mapping",
        "exception_handling",
        "acceptance_criteria",
        "traceability",
        "structured_data_appendix",
        "referenced_fact_ids"
      ],
      "properties": {
        "report_type": { "enum": ["solution_report", "gap_report"] },
        "implementation_status": { "type": "string" },
        "confirmed_development_basis": { "type": "array", "items": { "type": "string" } },
        "blocking_confirmation_items": { "type": "array", "items": { "type": "string" } },
        "agent_inferred_recommendations": { "type": "array", "items": { "type": "string" } },
        "rpa_capability_boundary": { "type": "array", "items": { "type": "string" } },
        "process_breakdown": {
          "type": "object",
          "additionalProperties": false,
          "required": ["process_cards", "dependencies", "validation_points"],
          "properties": {
            "process_cards": { "type": "array", "items": { "$ref": "#/$defs/view_process_card" } },
            "dependencies": { "type": "array", "items": { "type": "string" } },
            "validation_points": { "type": "array", "items": { "type": "string" } }
          }
        },
        "field_and_data_mapping": { "type": "array", "items": { "type": "string" } },
        "exception_handling": { "type": "array", "items": { "type": "string" } },
        "acceptance_criteria": { "type": "array", "items": { "type": "string" } },
        "traceability": { "type": "array", "items": { "type": "string" } },
        "structured_data_appendix": { "type": "object" },
        "referenced_fact_ids": {
          "type": "array",
          "items": { "type": "string", "pattern": "^F[0-9]{3}$" }
        }
      }
    },
    "view_process_card": {
      "type": "object",
      "additionalProperties": false,
      "required": ["step_id", "title", "summary", "source_step_id"],
      "properties": {
        "step_id": { "type": "string" },
        "title": { "type": "string" },
        "summary": { "type": "string" },
        "source_step_id": { "type": "string" }
      }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": { "developer_alignment_status": { "const": "blocked" } },
        "required": ["developer_alignment_status"]
      },
      "then": {
        "properties": {
          "module_status": { "const": "blocked" }
        }
      }
    }
  ]
}
```

- [ ] **Step 2: Run the schema-focused test**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_solution_package_schema_defines_fact_layer_html_outputs_and_readiness_status -v
```

Expected: PASS.

- [ ] **Step 3: Run the full module 6 test file**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts -v
```

Expected: FAIL because rules, fixtures, README, and platform docs are not created yet.

- [ ] **Step 4: Commit the schema**

Run:

```powershell
git add agent_modules/solution_packaging/schemas/solution-package-result.schema.json
git commit -m "feat: add solution packaging schema"
```

Expected: commit succeeds with only the schema staged.

---

### Task 3: Add Module Rules and README

**Files:**
- Create: `agent_modules/solution_packaging/README.md`
- Create: `agent_modules/solution_packaging/rules/packaging-rules.json`
- Create: `agent_modules/solution_packaging/rules/prompt-rules.md`

**Interfaces:**
- Consumes: `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`
- Produces: human and agent rules consumed by platform docs and tests

- [ ] **Step 1: Create the README**

Create `agent_modules/solution_packaging/README.md`:

```markdown
# Solution Packaging Module

Module 6 packages Modules 1-5 into a customer-facing HTML report, a developer-facing HTML report, and one structured JSON fact source.

## Scope

This module consumes requirement clarification, RPA boundary check, process breakdown, and exception design outputs. It separates confirmed facts, inferred recommendations, missing required items, and uncertainty before rendering any report content.

The module is a solution packaging and development-alignment module. It is not a final build guide and does not create executable automation instructions.

## Artifacts

- `schemas/solution-package-result.schema.json`
- `rules/packaging-rules.json`
- `rules/prompt-rules.md`
- `fixtures/ecommerce-daily-report-solution-package.json`
- `fixtures/email-sorting-solution-package.json`
- `fixtures/not-recommended-semantic-risk-solution-package.json`
- `fixtures/blocked-gap-report-solution-package.json`

## Boundary Rule

The structured JSON is the single source of truth. Customer HTML and developer HTML must be rendered from the same fact source. Missing development information must be shown as missing information, not filled with guessed content.
```

- [ ] **Step 2: Create packaging rules**

Create `agent_modules/solution_packaging/rules/packaging-rules.json`:

```json
{
  "module": "module_6_solution_packaging",
  "status_rules": {
    "ready_for_development": [
      "module_3_classification_is_suitable_or_conditionally_suitable",
      "module_4_process_breakdown_completed",
      "module_5_exception_design_completed",
      "no_high_blocking_missing_required_items",
      "key_development_basis_confirmed"
    ],
    "needs_confirmation": [
      "direction_viable_but_required_prework_or_open_questions_remain",
      "field_mapping_or_metric_definition_or_template_or_validation_missing",
      "inferred_recommendations_require_confirmation"
    ],
    "not_recommended": [
      "module_3_classification_is_not_suitable_for_direct_rpa",
      "package_governance_guidance_instead_of_implementation_plan"
    ],
    "blocked": [
      "upstream_module_needs_more_information",
      "upstream_module_returns_stop_with_gap_report_or_stop_with_blocker",
      "core_boundary_facts_missing"
    ]
  },
  "fact_layer_rules": {
    "confirmed_facts": "Only explicit user answers or upstream-confirmed facts may be used as development basis.",
    "inferred_recommendations": "Agent recommendations must require confirmation and must not be marked as development facts.",
    "missing_required_items": "Pending questions, required prework, process prework dependencies, and exception open questions must remain visible.",
    "conflict_or_uncertainty": "Low-confidence or inconsistent facts must be carried forward for review."
  },
  "rendering_rules": {
    "single_source_of_truth": "Customer HTML and developer HTML must be rendered from the same structured JSON fact source.",
    "customer_html": "Use business-facing sections and process cards.",
    "developer_html": "Use implementation-readiness sections and include a structured data appendix.",
    "insufficient_data": "Show gaps or pending confirmation instead of inventing missing content."
  },
  "next_stage_recommendations": [
    "manual_review_before_implementation",
    "implementation_planning",
    "return_to_exception_design",
    "return_to_process_breakdown",
    "return_to_rpa_boundary_check",
    "return_to_requirement_clarification",
    "stop_with_gap_report",
    "stop_with_blocker"
  ],
  "prohibited_content": [
    "exact_click_paths",
    "selectors",
    "wait_times",
    "retry_counts_as_executable_parameters",
    "yingdao_instruction_parameters",
    "final_build_guide",
    "customer_confirmed_language_for_inferred_content"
  ]
}
```

- [ ] **Step 3: Create prompt rules**

Create `agent_modules/solution_packaging/rules/prompt-rules.md`:

```markdown
# Module 6 Prompt Rules

When `exception_design_result.next_stage_recommendation` is `solution_packaging`, enter Module 6.

Module 6 must produce one `solution_package_result` object. It packages upstream results into:

- a customer-facing HTML report;
- a developer-facing HTML report;
- a structured JSON fact source.

The structured JSON is the single source of truth. Do not create facts directly in HTML.

## Required Fact Separation

Separate content into:

- `confirmed_facts`: explicit user answers or upstream-confirmed facts;
- `inferred_recommendations`: agent recommendations that require review;
- `missing_required_items`: information still needed before implementation;
- `conflict_or_uncertainty`: low-confidence, inconsistent, or conditional content.

Only `confirmed_facts` may be presented as development basis.

## Readiness Status

Use `module_status` for package generation and `developer_alignment_status` for implementation readiness.

Allowed `developer_alignment_status` values:

- `ready_for_development`
- `needs_confirmation`
- `not_recommended`
- `blocked`

Most real requirements with missing field mapping, metric definition, template location, permissions, or validation method should be `needs_confirmation`.

## HTML Rules

Customer HTML is for business alignment. Developer HTML is for pre-implementation alignment. Both must be generated from the same structured fact source.

Use card-style process sections instead of swimlane diagrams.

## Prohibited Content

Do not generate exact click paths, selectors, wait times, retry counts as executable parameters, Yingdao instruction parameters, or final build guides.
```

- [ ] **Step 4: Run rules and readability tests**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_packaging_rules_define_status_fact_and_rendering_constraints tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_module_6_files_have_readable_text -v
```

Expected: FAIL only for missing fixture paths in the readability test. The rules test should PASS.

- [ ] **Step 5: Commit rules and README**

Run:

```powershell
git add agent_modules/solution_packaging/README.md agent_modules/solution_packaging/rules/packaging-rules.json agent_modules/solution_packaging/rules/prompt-rules.md
git commit -m "feat: add solution packaging rules"
```

Expected: commit succeeds with README and rules staged.

---

### Task 4: Add Viable Scenario Fixtures

**Files:**
- Create: `agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json`
- Create: `agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json`

**Interfaces:**
- Consumes: `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`
- Produces: valid `needs_confirmation` fixtures for common viable scenarios

- [ ] **Step 1: Create the e-commerce daily report fixture**

Create `agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json` with these required values:

```json
{
  "module": "module_6_solution_packaging",
  "module_status": "completed",
  "developer_alignment_status": "needs_confirmation",
  "source_modules": {
    "module_1_interaction_schema": {
      "status": "completed",
      "summary": "Customer interaction answers and state were captured."
    },
    "module_2_requirement_clarification": {
      "status": "boundary_ready",
      "summary": "Daily e-commerce report boundary facts are available."
    },
    "module_3_rpa_boundary_check": {
      "status": "completed",
      "summary": "Requirement is conditionally suitable pending mapping, date, and validation confirmation."
    },
    "module_4_process_breakdown": {
      "status": "completed",
      "summary": "Business process cards are available."
    },
    "module_5_exception_design": {
      "status": "completed",
      "summary": "Exception, manual review, and logging policies are available."
    }
  },
  "fact_base": {
    "confirmed_facts": [
      {
        "fact_id": "F001",
        "topic": "business_goal",
        "value": "Automatically collect daily operating data from multiple e-commerce platforms and write a daily report into Tencent Docs.",
        "source_module": "module_2_requirement_clarification",
        "source_type": "user_answer",
        "confidence": "high",
        "can_be_used_for_development": true
      },
      {
        "fact_id": "F002",
        "topic": "trigger",
        "value": "Run at a fixed time every day.",
        "source_module": "module_2_requirement_clarification",
        "source_type": "user_answer",
        "confidence": "high",
        "can_be_used_for_development": true
      },
      {
        "fact_id": "F003",
        "topic": "operated_systems",
        "value": ["Taobao/Tmall", "JD", "Pinduoduo", "Douyin E-commerce", "Kuaishou E-commerce", "Tencent Docs"],
        "source_module": "module_2_requirement_clarification",
        "source_type": "user_answer",
        "confidence": "high",
        "can_be_used_for_development": true
      }
    ],
    "inferred_recommendations": [
      {
        "item_id": "I001",
        "topic": "retry_and_skip_policy",
        "value": "Use retry-and-skip handling for platform access failures and continue with other platforms when possible.",
        "basis": ["Multiple external platforms are involved.", "Module 5 exception design includes login and source data failures."],
        "requires_confirmation": true,
        "can_be_used_for_development": false
      }
    ],
    "missing_required_items": [
      {
        "item_id": "M001",
        "topic": "field_mapping",
        "question": "Are source platform fields mapped one-to-one to Tencent Docs report fields?",
        "why_it_matters": "Field mapping affects data write accuracy.",
        "blocking_level": "high",
        "owner": "customer_or_implementation_consultant"
      },
      {
        "item_id": "M002",
        "topic": "metric_definition",
        "question": "Are GMV, paid order count, and refund metrics defined consistently across platforms?",
        "why_it_matters": "Metric differences affect report consistency.",
        "blocking_level": "high",
        "owner": "customer_or_business_owner"
      },
      {
        "item_id": "M003",
        "topic": "date_definition",
        "question": "Should the report use natural day, previous day, or platform-specific settlement day?",
        "why_it_matters": "Date definition affects data collection filters.",
        "blocking_level": "high",
        "owner": "customer_or_business_owner"
      },
      {
        "item_id": "M004",
        "topic": "result_validation_method",
        "question": "Should the robot only verify successful write, or compare written values against source platform values?",
        "why_it_matters": "Validation method affects acceptance and exception handling.",
        "blocking_level": "medium",
        "owner": "customer_or_implementation_consultant"
      }
    ],
    "conflict_or_uncertainty": [
      {
        "item_id": "U001",
        "topic": "platform_metric_consistency",
        "description": "The requirement says platform metrics are generally unified, but exact metric definitions are not confirmed.",
        "impact": "Report values may be inconsistent across platforms.",
        "resolution_needed": true
      }
    ]
  },
  "decision_summary": {
    "recommendation": "conditional",
    "headline": "This requirement is suitable for RPA after field, metric, date, and validation details are confirmed.",
    "confidence": "medium_high",
    "reasoning_points": [
      "Inputs are platform reports with repeatable access patterns.",
      "The output template is fixed in Tencent Docs.",
      "Development-critical mapping details remain open."
    ]
  },
  "customer_view_model": {
    "report_type": "solution_report",
    "headline": "Daily e-commerce report automation is conditionally suitable for RPA.",
    "recommendation": "Confirm report mapping before implementation.",
    "requirement_understanding": "Collect daily operating data from fixed e-commerce platforms and write it into a fixed Tencent Docs report.",
    "rpa_fit_summary": ["Repeatable daily task", "Fixed target report", "Mapping confirmation required"],
    "business_scope_included": ["Collect daily metrics", "Write Tencent Docs report", "Record execution result"],
    "business_scope_excluded": ["Redefine business metrics", "Handle long-term account risk as an automation task"],
    "process_cards": [
      {
        "step_id": "C01",
        "title": "Collect platform data",
        "summary": "Access each configured platform and collect the required daily metrics.",
        "source_step_id": "S02"
      },
      {
        "step_id": "C02",
        "title": "Write report",
        "summary": "Write mapped values into the fixed Tencent Docs report.",
        "source_step_id": "S05"
      }
    ],
    "risk_and_manual_intervention": ["Login verification may require manual handling.", "Missing source fields require review."],
    "customer_preparation_items": ["Confirm platform-store list.", "Confirm metric definitions.", "Confirm report field mapping."],
    "next_steps": ["Review missing confirmation items.", "Confirm implementation scope before development."],
    "referenced_fact_ids": ["F001", "F002", "F003"]
  },
  "developer_view_model": {
    "report_type": "solution_report",
    "implementation_status": "needs_confirmation",
    "confirmed_development_basis": ["Business goal, trigger, and operated systems are confirmed."],
    "blocking_confirmation_items": ["field_mapping", "metric_definition", "date_definition"],
    "agent_inferred_recommendations": ["retry_and_skip_policy"],
    "rpa_capability_boundary": ["RPA can execute repeatable collection and writing.", "RPA cannot define business metric standards."],
    "process_breakdown": {
      "process_cards": [
        {
          "step_id": "D01",
          "title": "Platform data collection",
          "summary": "Collect metrics from configured platform-store scope.",
          "source_step_id": "S02"
        },
        {
          "step_id": "D02",
          "title": "Tencent Docs writing",
          "summary": "Write mapped metrics to the fixed report area.",
          "source_step_id": "S05"
        }
      ],
      "dependencies": ["Confirmed platform-store list", "Confirmed field mapping"],
      "validation_points": ["Write success", "Execution record generated"]
    },
    "field_and_data_mapping": ["Source metric to target report field mapping is required."],
    "exception_handling": ["Login failure, source field missing, target write failure, and validation failure require handling."],
    "acceptance_criteria": ["Configured platforms are processed.", "Tencent Docs report is updated.", "Run result is logged."],
    "traceability": ["Facts from Module 2", "RPA boundary from Module 3", "Process cards from Module 4", "Exceptions from Module 5"],
    "structured_data_appendix": {
      "included": true,
      "source": "solution_package_result.fact_base"
    },
    "referenced_fact_ids": ["F001", "F002", "F003"]
  },
  "render_outputs": {
    "customer_html": "<section class=\"summary-card\"><h1>Daily e-commerce report automation</h1><div class=\"card\">Conditionally suitable for RPA after mapping confirmation.</div></section>",
    "developer_html": "<section class=\"developer-card\"><h1>Implementation alignment</h1><div class=\"card\">Status: needs confirmation. Missing: field mapping, metric definition, date definition.</div></section>"
  },
  "next_stage_recommendation": "manual_review_before_implementation"
}
```

- [ ] **Step 2: Create the email sorting fixture**

Create `agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json` with the same schema shape and these required values:

```json
{
  "module": "module_6_solution_packaging",
  "module_status": "completed",
  "developer_alignment_status": "needs_confirmation",
  "source_modules": {
    "module_1_interaction_schema": {
      "status": "completed",
      "summary": "Customer interaction answers and state were captured."
    },
    "module_2_requirement_clarification": {
      "status": "boundary_ready",
      "summary": "Email sorting boundary facts are available."
    },
    "module_3_rpa_boundary_check": {
      "status": "completed",
      "summary": "Requirement is conditionally suitable because semantic classification needs review handling."
    },
    "module_4_process_breakdown": {
      "status": "completed",
      "summary": "Email sorting process cards are available."
    },
    "module_5_exception_design": {
      "status": "completed",
      "summary": "Low-confidence and manual review exception handling is available."
    }
  },
  "fact_base": {
    "confirmed_facts": [
      {
        "fact_id": "F001",
        "topic": "business_goal",
        "value": "Automatically classify Outlook or Microsoft 365 emails into folders or labels.",
        "source_module": "module_2_requirement_clarification",
        "source_type": "user_answer",
        "confidence": "high",
        "can_be_used_for_development": true
      }
    ],
    "inferred_recommendations": [
      {
        "item_id": "I001",
        "topic": "manual_review_queue",
        "value": "Keep low-confidence semantic classification results in a manual review queue.",
        "basis": ["Semantic classification can misclassify messages.", "Module 5 includes low-confidence handling."],
        "requires_confirmation": true,
        "can_be_used_for_development": false
      }
    ],
    "missing_required_items": [
      {
        "item_id": "M001",
        "topic": "classification_samples",
        "question": "Are representative examples available for each email category?",
        "why_it_matters": "Examples reduce semantic classification ambiguity.",
        "blocking_level": "high",
        "owner": "customer_or_business_owner"
      }
    ],
    "conflict_or_uncertainty": [
      {
        "item_id": "U001",
        "topic": "semantic_judgment",
        "description": "Some messages rely on semantic judgment rather than fixed sender or subject rules.",
        "impact": "Unattended automation may misclassify emails without manual review.",
        "resolution_needed": true
      }
    ]
  },
  "decision_summary": {
    "recommendation": "conditional",
    "headline": "Email sorting is conditionally suitable with low-confidence manual review.",
    "confidence": "medium_high",
    "reasoning_points": ["Folder operations are repeatable.", "Semantic judgment requires containment."]
  },
  "customer_view_model": {
    "report_type": "solution_report",
    "headline": "Email sorting can be automated with manual review for uncertain emails.",
    "recommendation": "Confirm category examples and low-confidence handling.",
    "requirement_understanding": "Classify incoming Outlook or Microsoft 365 emails by sender, subject, keywords, and semantic meaning.",
    "rpa_fit_summary": ["Repeatable folder or label actions", "Semantic judgment risk remains"],
    "business_scope_included": ["Classify emails", "Move or label emails", "Record processing results"],
    "business_scope_excluded": ["Fully unattended semantic judgment for every message"],
    "process_cards": [
      {
        "step_id": "C01",
        "title": "Read email",
        "summary": "Read sender, subject, and body signals.",
        "source_step_id": "S02"
      }
    ],
    "risk_and_manual_intervention": ["Low-confidence semantic results need manual review."],
    "customer_preparation_items": ["Provide category examples.", "Confirm low-confidence handling."],
    "next_steps": ["Prepare representative email samples."],
    "referenced_fact_ids": ["F001"]
  },
  "developer_view_model": {
    "report_type": "solution_report",
    "implementation_status": "needs_confirmation",
    "confirmed_development_basis": ["Target mailbox and classification goal are confirmed."],
    "blocking_confirmation_items": ["classification_samples"],
    "agent_inferred_recommendations": ["manual_review_queue"],
    "rpa_capability_boundary": ["RPA can move or label emails.", "RPA must not pretend uncertain semantic judgment is fully deterministic."],
    "process_breakdown": {
      "process_cards": [
        {
          "step_id": "D01",
          "title": "Email signal reading",
          "summary": "Read sender, subject, and body signals for classification.",
          "source_step_id": "S02"
        }
      ],
      "dependencies": ["Category examples", "Low-confidence policy"],
      "validation_points": ["Email moved or labeled", "Processing record generated"]
    },
    "field_and_data_mapping": ["Email signal to target category mapping requires examples."],
    "exception_handling": ["Low-confidence semantic classification enters manual review."],
    "acceptance_criteria": ["High-confidence emails are classified.", "Low-confidence emails are not silently processed."],
    "traceability": ["Facts from Module 2", "Semantic risk from Module 3", "Review handling from Module 5"],
    "structured_data_appendix": {
      "included": true,
      "source": "solution_package_result.fact_base"
    },
    "referenced_fact_ids": ["F001"]
  },
  "render_outputs": {
    "customer_html": "<section class=\"summary-card\"><h1>Email sorting automation</h1><div class=\"card\">Conditionally suitable with manual review for low-confidence semantic decisions.</div></section>",
    "developer_html": "<section class=\"developer-card\"><h1>Implementation alignment</h1><div class=\"card\">Status: needs confirmation. Semantic low-confidence handling must remain manual.</div></section>"
  },
  "next_stage_recommendation": "manual_review_before_implementation"
}
```

- [ ] **Step 3: Run fixture validation tests**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_all_solution_package_fixtures_validate_against_schema tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_ecommerce_daily_report_remains_needs_confirmation tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_email_sorting_keeps_semantic_risk_and_manual_review_visible -v
```

Expected: FAIL only because the not-recommended and blocked fixtures are still missing. The ecommerce and email scenario assertions should PASS.

- [ ] **Step 4: Commit viable scenario fixtures**

Run:

```powershell
git add agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json
git commit -m "test: add solution packaging viable fixtures"
```

Expected: commit succeeds with the two fixture files staged.

---

### Task 5: Add Not Recommended and Blocked Fixtures

**Files:**
- Create: `agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json`
- Create: `agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json`

**Interfaces:**
- Consumes: `agent_modules/solution_packaging/schemas/solution-package-result.schema.json`
- Produces: negative-path fixtures used by status and hallucination-control tests

- [ ] **Step 1: Create the not-recommended fixture**

Create `agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json` with:

```json
{
  "module": "module_6_solution_packaging",
  "module_status": "completed",
  "developer_alignment_status": "not_recommended",
  "source_modules": {
    "module_1_interaction_schema": {
      "status": "completed",
      "summary": "Customer interaction answers and state were captured."
    },
    "module_2_requirement_clarification": {
      "status": "boundary_ready",
      "summary": "A high-semantic-judgment requirement was clarified."
    },
    "module_3_rpa_boundary_check": {
      "status": "completed",
      "summary": "Direct RPA is not recommended because the key judgment cannot be rule-defined."
    },
    "module_4_process_breakdown": {
      "status": "blocked_by_boundary_result",
      "summary": "Process breakdown is not produced for direct implementation."
    },
    "module_5_exception_design": {
      "status": "blocked_by_process_breakdown",
      "summary": "Exception design is not produced because there is no approved process breakdown."
    }
  },
  "fact_base": {
    "confirmed_facts": [
      {
        "fact_id": "F001",
        "topic": "business_goal",
        "value": "Identify whether supplier material names refer to the same physical item.",
        "source_module": "module_2_requirement_clarification",
        "source_type": "user_answer",
        "confidence": "high",
        "can_be_used_for_development": true
      }
    ],
    "inferred_recommendations": [
      {
        "item_id": "I001",
        "topic": "data_governance_first",
        "value": "Build a standard material naming and mapping governance process before reevaluating RPA.",
        "basis": ["Module 3 identified semantic judgment and missing rules.", "RPA should execute stable rules rather than invent them."],
        "requires_confirmation": true,
        "can_be_used_for_development": false
      }
    ],
    "missing_required_items": [
      {
        "item_id": "M001",
        "topic": "standard_mapping_rules",
        "question": "Is there a stable rule or approved mapping table for same-material judgment?",
        "why_it_matters": "Without a rule or mapping table, RPA cannot safely classify materials.",
        "blocking_level": "high",
        "owner": "customer_or_business_owner"
      }
    ],
    "conflict_or_uncertainty": [
      {
        "item_id": "U001",
        "topic": "semantic_judgment",
        "description": "The core decision relies on human semantic understanding rather than a stable rule.",
        "impact": "Direct RPA may create duplicate or incorrect material records.",
        "resolution_needed": true
      }
    ]
  },
  "decision_summary": {
    "recommendation": "not_recommended",
    "headline": "Direct RPA is not recommended until material governance rules exist.",
    "confidence": "high",
    "reasoning_points": ["The key judgment cannot be written as a stable rule.", "Governance must precede automation."]
  },
  "customer_view_model": {
    "report_type": "solution_report",
    "headline": "Direct RPA is not recommended for this requirement now.",
    "recommendation": "Create governance rules and reevaluation criteria before automation.",
    "requirement_understanding": "The requirement depends on deciding whether different names refer to the same item.",
    "rpa_fit_summary": ["Semantic judgment is the core task", "Stable rules are missing"],
    "business_scope_included": ["Governance recommendation", "Reevaluation condition"],
    "business_scope_excluded": ["Direct automated same-item judgment"],
    "process_cards": [],
    "risk_and_manual_intervention": ["Incorrect classification may create wrong material records."],
    "customer_preparation_items": ["Create standard naming rules.", "Create a verified mapping table."],
    "next_steps": ["Complete governance prework.", "Reevaluate after rules are stable."],
    "referenced_fact_ids": ["F001"]
  },
  "developer_view_model": {
    "report_type": "solution_report",
    "implementation_status": "not_recommended",
    "confirmed_development_basis": ["The business goal is known, but direct implementation is not recommended."],
    "blocking_confirmation_items": ["standard_mapping_rules"],
    "agent_inferred_recommendations": ["data_governance_first"],
    "rpa_capability_boundary": ["RPA can execute stable mapping rules after governance.", "RPA should not invent same-material rules."],
    "process_breakdown": {
      "process_cards": [],
      "dependencies": ["Approved naming rules", "Approved mapping table"],
      "validation_points": []
    },
    "field_and_data_mapping": ["Mapping table required before automation."],
    "exception_handling": ["No implementation exception design should be generated before governance."],
    "acceptance_criteria": ["Reevaluation only after stable rules exist."],
    "traceability": ["Boundary decision from Module 3"],
    "structured_data_appendix": {
      "included": true,
      "source": "solution_package_result.fact_base"
    },
    "referenced_fact_ids": ["F001"]
  },
  "render_outputs": {
    "customer_html": "<section class=\"summary-card\"><h1>RPA not recommended</h1><div class=\"card\">Governance and reevaluation are required before automation.</div></section>",
    "developer_html": "<section class=\"developer-card\"><h1>No direct implementation package</h1><div class=\"card\">Direct RPA is not recommended. Build governance rules first.</div></section>"
  },
  "next_stage_recommendation": "stop_with_blocker"
}
```

- [ ] **Step 2: Create the blocked fixture**

Create `agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json` with:

```json
{
  "module": "module_6_solution_packaging",
  "module_status": "blocked",
  "developer_alignment_status": "blocked",
  "source_modules": {
    "module_1_interaction_schema": {
      "status": "completed",
      "summary": "Initial interaction was captured, but core boundary facts are missing."
    },
    "module_2_requirement_clarification": {
      "status": "stop_with_gap_report",
      "summary": "Core boundary facts are missing."
    },
    "module_3_rpa_boundary_check": {
      "status": "not_started",
      "summary": "Boundary check cannot run without core facts."
    },
    "module_4_process_breakdown": {
      "status": "not_started",
      "summary": "Process breakdown cannot run without boundary check."
    },
    "module_5_exception_design": {
      "status": "not_started",
      "summary": "Exception design cannot run without process breakdown."
    }
  },
  "fact_base": {
    "confirmed_facts": [],
    "inferred_recommendations": [],
    "missing_required_items": [
      {
        "item_id": "M001",
        "topic": "business_goal",
        "question": "What business outcome should the automation achieve?",
        "why_it_matters": "Without a business goal, the agent cannot build a reliable package.",
        "blocking_level": "high",
        "owner": "customer"
      },
      {
        "item_id": "M002",
        "topic": "operated_systems",
        "question": "Which systems or platforms will be operated?",
        "why_it_matters": "System scope is required for RPA boundary analysis.",
        "blocking_level": "high",
        "owner": "customer"
      }
    ],
    "conflict_or_uncertainty": []
  },
  "decision_summary": {
    "recommendation": "blocked",
    "headline": "The package cannot be generated because core facts are missing.",
    "confidence": "high",
    "reasoning_points": ["Business goal and operated systems are missing."]
  },
  "customer_view_model": {
    "report_type": "gap_report",
    "headline": "More information is required before a solution report can be generated.",
    "recommendation": "Answer the missing boundary questions first.",
    "requirement_understanding": "The current request does not contain enough confirmed facts.",
    "rpa_fit_summary": [],
    "business_scope_included": [],
    "business_scope_excluded": [],
    "process_cards": [],
    "risk_and_manual_intervention": [],
    "customer_preparation_items": ["Clarify business goal.", "Clarify operated systems."],
    "next_steps": ["Return to requirement clarification."],
    "referenced_fact_ids": []
  },
  "developer_view_model": {
    "report_type": "gap_report",
    "implementation_status": "blocked",
    "confirmed_development_basis": [],
    "blocking_confirmation_items": ["business_goal", "operated_systems"],
    "agent_inferred_recommendations": [],
    "rpa_capability_boundary": [],
    "process_breakdown": {
      "process_cards": [],
      "dependencies": [],
      "validation_points": []
    },
    "field_and_data_mapping": [],
    "exception_handling": [],
    "acceptance_criteria": [],
    "traceability": ["Blocked by Module 2 gap report."],
    "structured_data_appendix": {
      "included": true,
      "source": "solution_package_result.fact_base"
    },
    "referenced_fact_ids": []
  },
  "render_outputs": {
    "customer_html": "<section class=\"gap-card\"><h1>Information required</h1><div class=\"card\">Please clarify the business goal and operated systems.</div></section>",
    "developer_html": "<section class=\"gap-card\"><h1>Package blocked</h1><div class=\"card\">Core boundary facts are missing. Return to requirement clarification.</div></section>"
  },
  "next_stage_recommendation": "return_to_requirement_clarification"
}
```

- [ ] **Step 3: Run negative-path tests**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_not_recommended_package_does_not_look_like_implementation_plan tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_blocked_package_is_gap_report_not_solution_report -v
```

Expected: PASS.

- [ ] **Step 4: Run all module 6 contract tests**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts -v
```

Expected: FAIL only because platform docs do not include Module 6 yet.

- [ ] **Step 5: Commit negative-path fixtures**

Run:

```powershell
git add agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json
git commit -m "test: add solution packaging negative fixtures"
```

Expected: commit succeeds with the two fixture files staged.

---

### Task 6: Integrate Module 6 into Platform Package Docs

**Files:**
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Modify: `agent_platform_package/testing/expected_outputs.md`
- Create: `agent_platform_package/testing/module_1_to_6_flow_test.md`

**Interfaces:**
- Consumes: module 6 schema, rules, and fixtures
- Produces: platform-facing instructions for agent operation and acceptance

- [ ] **Step 1: Update the system prompt wrapper and working sequence**

In `agent_platform_package/system_prompt/agent-system-prompt.md`, add `solution_package_result` to the wrapper example and add this section after Module 5:

```markdown
## Module 6: Solution Packaging

When `exception_design_result.next_stage_recommendation` is `solution_packaging`, enter Module 6.

Module 6 must produce one `solution_package_result` object. It packages upstream results into:

- a customer-facing HTML report;
- a developer-facing HTML report;
- one structured JSON fact source.

The structured JSON fact source is the single source of truth. The two HTML reports are presentation layers and must not create new facts.

Module 6 must separate:

- `confirmed_facts`;
- `inferred_recommendations`;
- `missing_required_items`;
- `conflict_or_uncertainty`.

Use `module_status` to describe package generation and `developer_alignment_status` to describe implementation readiness.

Allowed `developer_alignment_status` values:

- `ready_for_development`
- `needs_confirmation`
- `not_recommended`
- `blocked`

Module 6 must not generate exact click paths, selectors, wait times, retry counts as executable parameters, Yingdao instruction parameters, final build guides, or customer-confirmed language for inferred content.
```

- [ ] **Step 2: Update expected outputs**

In `agent_platform_package/testing/expected_outputs.md`, add:

```markdown
## Module 6 Expected Output

Module 6 outputs `solution_package_result`.

Required:

- `module`
- `module_status`
- `developer_alignment_status`
- `source_modules`
- `fact_base`
- `decision_summary`
- `customer_view_model`
- `developer_view_model`
- `render_outputs`
- `next_stage_recommendation`

`fact_base` must separate:

- `confirmed_facts`
- `inferred_recommendations`
- `missing_required_items`
- `conflict_or_uncertainty`

The customer HTML and developer HTML must be generated from the same structured fact source.

The developer-facing HTML is a development alignment package, not a final build guide.
```

Also add these invalid output signs:

```markdown
- Marking inferred recommendations as customer-confirmed facts.
- Returning `ready_for_development` while high-blocking missing items remain.
- Generating exact click paths, selectors, wait times, retry counts, or Yingdao instruction parameters in Module 6.
- Generating customer and developer HTML from different facts.
```

- [ ] **Step 3: Add Module 1-6 flow test guide**

Create `agent_platform_package/testing/module_1_to_6_flow_test.md`:

```markdown
# Module 1-6 Flow Test Guide

## Goal

Verify that a vague RPA requirement can flow from interaction capture to solution packaging without losing facts, hiding missing items, or inventing implementation details.

## Expected Flow

1. Module 1 records answers and interaction state.
2. Module 2 produces boundary facts and RPA pre-screening.
3. Module 3 produces RPA boundary classification.
4. Module 4 produces business process cards.
5. Module 5 produces exception, manual review, and logging design.
6. Module 6 produces `solution_package_result`.

## Passing Signals

- `solution_package_result.fact_base.confirmed_facts` only contains confirmed or upstream-preserved facts.
- `inferred_recommendations` require confirmation.
- `missing_required_items` preserves upstream pending questions and prework.
- Customer HTML and developer HTML are present.
- The process presentation uses cards.
- `developer_alignment_status` reflects readiness instead of simply mirroring package completion.

## Failing Signals

- Module 6 hides field mapping, metric definition, permissions, template, validation, or manual review gaps.
- Module 6 claims development readiness while high-blocking missing items remain.
- Module 6 generates exact implementation parameters.
- Module 6 produces different facts in customer and developer reports.
```

- [ ] **Step 4: Run platform integration tests**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts.SolutionPackagingContractTests.test_prompt_and_platform_docs_include_module_6 -v
```

Expected: PASS.

- [ ] **Step 5: Commit platform docs**

Run:

```powershell
git add agent_platform_package/system_prompt/agent-system-prompt.md agent_platform_package/testing/expected_outputs.md agent_platform_package/testing/module_1_to_6_flow_test.md
git commit -m "docs: integrate solution packaging into platform package"
```

Expected: commit succeeds with platform documentation staged.

---

### Task 7: Final Contract Verification and Cleanup

**Files:**
- Modify only files from Tasks 1-6 if tests expose a contract mismatch.

**Interfaces:**
- Consumes: all Module 6 files and existing Modules 1-5 tests
- Produces: verified module 6 implementation branch ready for user review

- [ ] **Step 1: Run module 6 tests**

Run:

```powershell
python -m unittest tests.test_solution_packaging_contracts -v
```

Expected: PASS, except schema validation tests may be skipped if `jsonschema` is unavailable.

- [ ] **Step 2: Run all existing module contract tests**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts tests.test_exception_design_contracts tests.test_solution_packaging_contracts -v
```

Expected: PASS, with the same optional `jsonschema` skips as the existing suite.

- [ ] **Step 3: Check git status**

Run:

```powershell
git status --short --branch
```

Expected: clean working tree on `codex/solution-packaging`.

- [ ] **Step 4: Commit any test-alignment fixes**

If Step 1 or Step 2 required small contract alignment fixes, run:

```powershell
git add tests/test_solution_packaging_contracts.py agent_modules/solution_packaging agent_platform_package/system_prompt/agent-system-prompt.md agent_platform_package/testing/expected_outputs.md agent_platform_package/testing/module_1_to_6_flow_test.md
git commit -m "test: verify solution packaging contracts"
```

Expected: commit succeeds only if files changed. If no files changed, do not create an empty commit.

---

## Self-Review

- Spec coverage: The plan covers Module 6 outputs, fact layering, status rules, double HTML rendering, traceability, prohibited content, fixtures, platform docs, and tests.
- Red-flag scan: No task relies on open-ended filler. Each file creation step includes concrete content or exact required values.
- Type consistency: The plan uses `solution_package_result`, `module_status`, `developer_alignment_status`, `fact_base`, `customer_view_model`, `developer_view_model`, and `render_outputs` consistently across schema, fixtures, tests, and platform docs.
