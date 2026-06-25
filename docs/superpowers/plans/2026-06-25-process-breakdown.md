# Process Breakdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build module 4, a process breakdown contract that turns module 2 and module 3 outputs into business process cards with candidate Yingdao capability families.

**Architecture:** Follow the existing module pattern: JSON Schema, rules, material policy, prompt rules, fixtures, README, platform prompt guidance, expected-output guidance, and Python unittest contract tests. This module is still agent-contract material, not a runtime executor.

**Tech Stack:** Markdown, JSON Schema draft 2020-12, JSON fixtures, Python `unittest`, repository-local agent package docs.

## Global Constraints

- Module 4 consumes module 2 and module 3 outputs instead of repeating their questions.
- Module 4 only runs when module 3 allows process breakdown.
- Module 4 defines a structured `process_breakdown_result`.
- Process cards must include business purpose, input, operation summary, output, candidate capabilities, dependencies, and exception handoff markers.
- Module 4 uses Yingdao flow-chain templates and scenario materials without turning them into exact implementation steps.
- Module 4 blocks or returns upstream when module 3 says `not_ready` or `not_suitable_for_direct_rpa`.
- Module 4 leaves exception branches to module 5.
- Module 4 leaves final blueprint and HTML generation to later modules.

---

## File Structure

- Create `agent_modules/process_breakdown/README.md`: module purpose, artifacts, scope, and boundary rules.
- Create `agent_modules/process_breakdown/schemas/process-breakdown-result.schema.json`: formal output contract.
- Create `agent_modules/process_breakdown/rules/breakdown-rules.json`: process-card generation constraints and upstream gating.
- Create `agent_modules/process_breakdown/rules/material-use-policy.json`: ordered use of Yingdao flow-chain and scenario materials.
- Create `agent_modules/process_breakdown/rules/prompt-rules.md`: module 4 prompt behavior.
- Create `agent_modules/process_breakdown/fixtures/ecommerce-daily-report-process-breakdown.json`: expected card output for the e-commerce scenario.
- Create `agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json`: expected card output for the email sorting scenario.
- Create `tests/test_process_breakdown_contracts.py`: contract tests for module 4 schema, rules, fixtures, README, and platform prompt integration.
- Modify `agent_platform_package/system_prompt/agent-system-prompt.md`: add module 4 guidance and include `process_breakdown_result` in the single JSON wrapper rule.
- Modify `agent_platform_package/testing/expected_outputs.md`: add module 4 expected output notes.

---

### Task 1: Add Module 4 Contract Tests First

**Files:**
- Create: `tests/test_process_breakdown_contracts.py`

**Interfaces:**
- Consumes: files later created under `agent_modules/process_breakdown/`
- Produces: module 4 contract assertions for schema, rules, fixtures, README, and platform prompt integration

- [ ] **Step 1: Write the failing test file**

Create `tests/test_process_breakdown_contracts.py` with this content:

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class ProcessBreakdownContractTests(unittest.TestCase):
    def test_process_breakdown_schema_defines_cards_and_handoff(self):
        schema = load_json("agent_modules/process_breakdown/schemas/process-breakdown-result.schema.json")
        props = schema["properties"]
        card_props = schema["$defs"]["process_card"]["properties"]

        self.assertEqual(schema["title"], "ProcessBreakdownResult")
        self.assertEqual(props["module"]["const"], "module_4_process_breakdown")
        self.assertEqual(
            props["breakdown_depth"]["const"],
            "business_process_cards_with_candidate_capabilities",
        )
        self.assertEqual(
            props["status"]["enum"],
            ["completed", "blocked_by_boundary_result", "needs_more_information"],
        )
        self.assertEqual(
            props["next_stage_recommendation"]["enum"],
            [
                "exception_design",
                "return_to_rpa_boundary_check",
                "return_to_requirement_clarification",
                "stop_with_blocker",
            ],
        )
        self.assertEqual(
            list(card_props.keys()),
            [
                "step_id",
                "step_name",
                "business_purpose",
                "input",
                "operation_summary",
                "output",
                "candidate_yingdao_capabilities",
                "depends_on",
                "prework_dependencies",
                "handoff_to_exception_design",
                "exception_design_notes",
            ],
        )

    def test_breakdown_rules_gate_on_module_3_and_forbid_step_details(self):
        rules = load_json("agent_modules/process_breakdown/rules/breakdown-rules.json")

        self.assertEqual(rules["module"], "module_4_process_breakdown")
        self.assertEqual(rules["breakdown_depth"], "business_process_cards_with_candidate_capabilities")
        self.assertEqual(
            rules["allowed_source_classifications"],
            ["suitable", "conditionally_suitable"],
        )
        self.assertIn("not_ready", rules["blocked_source_classifications"])
        self.assertIn("not_suitable_for_direct_rpa", rules["blocked_source_classifications"])
        self.assertIn("do_not_generate_exact_click_paths", rules["forbidden_behaviors"])
        self.assertIn("do_not_design_exception_branches", rules["forbidden_behaviors"])
        self.assertIn("do_not_override_module_3_decision", rules["forbidden_behaviors"])
        self.assertEqual(rules["default_card_count"]["minimum"], 4)
        self.assertEqual(rules["default_card_count"]["maximum"], 8)

    def test_material_use_policy_prioritizes_flow_templates(self):
        policy = load_json("agent_modules/process_breakdown/rules/material-use-policy.json")
        sources = [item["source"] for item in policy["source_order"]]

        self.assertEqual(sources[0], "yingdao_flow_chain_templates_v3.md")
        self.assertEqual(sources[1], "yingdao_scenario_building_guide.md")
        self.assertIn("requirement_to_instruction_mapping.xlsx", sources)
        self.assertEqual(policy["excluded_as_process_evidence"], ["agent_answer_templates.md"])
        self.assertIn("use_templates_without_instruction_parameters", policy["rules"])

    def test_prompt_rules_keep_module_4_business_level(self):
        text = (ROOT / "agent_modules/process_breakdown/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Do not ask for exact button names", text)
        self.assertIn("Do not generate selectors or wait times", text)
        self.assertIn("Do not design exception branches", text)
        self.assertIn("Attach candidate Yingdao capability families", text)
        self.assertIn("Start from module 3's decision and prework", text)

    def test_ecommerce_fixture_has_business_cards_with_capabilities(self):
        fixture = load_json("agent_modules/process_breakdown/fixtures/ecommerce-daily-report-process-breakdown.json")

        self.assertEqual(fixture["module"], "module_4_process_breakdown")
        self.assertEqual(fixture["status"], "completed")
        self.assertEqual(fixture["next_stage_recommendation"], "exception_design")
        self.assertGreaterEqual(len(fixture["process_cards"]), 4)
        self.assertLessEqual(len(fixture["process_cards"]), 8)
        step_ids = [card["step_id"] for card in fixture["process_cards"]]
        self.assertEqual(step_ids[0], "S01")
        self.assertIn("S03", step_ids)
        collect_cards = [card for card in fixture["process_cards"] if card["step_id"] == "S03"]
        self.assertEqual(len(collect_cards), 1)
        collect_card = collect_cards[0]
        self.assertIn("web automation", collect_card["candidate_yingdao_capabilities"])
        self.assertTrue(collect_card["handoff_to_exception_design"])
        self.assertIn("login failure", collect_card["exception_design_notes"])
        self.assertIn("平台-店铺清单", " ".join(fixture["cross_step_dependencies"]))

    def test_email_fixture_routes_uncertain_classification_to_exception_design(self):
        fixture = load_json("agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json")

        self.assertEqual(fixture["module"], "module_4_process_breakdown")
        self.assertEqual(fixture["source_decision"]["classification"], "conditionally_suitable")
        classify_cards = [card for card in fixture["process_cards"] if card["step_name"] == "Classify email"]
        self.assertEqual(len(classify_cards), 1)
        classify_card = classify_cards[0]
        self.assertIn("condition judgment", classify_card["candidate_yingdao_capabilities"])
        self.assertIn("manual review queue", classify_card["candidate_yingdao_capabilities"])
        self.assertTrue(classify_card["handoff_to_exception_design"])
        self.assertIn("low confidence", classify_card["exception_design_notes"])

    def test_readme_lists_module_4_artifacts(self):
        text = (ROOT / "agent_modules/process_breakdown/README.md").read_text(encoding="utf-8")
        expected_paths = [
            "schemas/process-breakdown-result.schema.json",
            "rules/breakdown-rules.json",
            "rules/material-use-policy.json",
            "rules/prompt-rules.md",
            "fixtures/ecommerce-daily-report-process-breakdown.json",
            "fixtures/email-sorting-process-breakdown.json",
        ]

        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)

    def test_platform_prompt_allows_process_breakdown_result_in_single_wrapper(self):
        text = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(encoding="utf-8")

        self.assertIn("process_breakdown_result", text)
        self.assertIn("最终结构化输出只能返回一个 JSON 对象", text)
        self.assertIn("Module 4", text)
        self.assertNotIn("rpa_boundary_result` 四类结构", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```powershell
python -m unittest tests.test_process_breakdown_contracts -v
```

Expected: FAIL with `FileNotFoundError` for missing `agent_modules/process_breakdown` files.

- [ ] **Step 3: Commit failing tests**

Run:

```powershell
git add tests/test_process_breakdown_contracts.py
git commit -m "test: add process breakdown contracts"
```

Expected: commit succeeds with one new test file.

---

### Task 2: Add Module 4 Schema And Rules

**Files:**
- Create: `agent_modules/process_breakdown/schemas/process-breakdown-result.schema.json`
- Create: `agent_modules/process_breakdown/rules/breakdown-rules.json`
- Create: `agent_modules/process_breakdown/rules/material-use-policy.json`
- Create: `agent_modules/process_breakdown/rules/prompt-rules.md`

**Interfaces:**
- Consumes: test assertions from Task 1
- Produces: schema and rules used by module 4 fixtures and platform guidance

- [ ] **Step 1: Create schema**

Create `agent_modules/process_breakdown/schemas/process-breakdown-result.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/process-breakdown-result.schema.json",
  "title": "ProcessBreakdownResult",
  "type": "object",
  "required": [
    "module",
    "status",
    "source_decision",
    "breakdown_depth",
    "process_cards",
    "cross_step_dependencies",
    "open_questions",
    "handoff_to_exception_design",
    "next_stage_recommendation"
  ],
  "additionalProperties": false,
  "properties": {
    "module": {
      "const": "module_4_process_breakdown"
    },
    "status": {
      "type": "string",
      "enum": ["completed", "blocked_by_boundary_result", "needs_more_information"]
    },
    "source_decision": {
      "type": "object",
      "required": ["classification", "confidence"],
      "additionalProperties": false,
      "properties": {
        "classification": {
          "type": "string",
          "enum": ["suitable", "conditionally_suitable", "not_ready", "not_suitable_for_direct_rpa"]
        },
        "confidence": {
          "type": "string",
          "enum": ["high", "medium_high", "medium", "low"]
        }
      }
    },
    "breakdown_depth": {
      "const": "business_process_cards_with_candidate_capabilities"
    },
    "process_cards": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/process_card"
      }
    },
    "cross_step_dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "open_questions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "handoff_to_exception_design": {
      "type": "object",
      "required": ["required", "focus_steps", "notes"],
      "additionalProperties": false,
      "properties": {
        "required": {
          "type": "boolean"
        },
        "focus_steps": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "notes": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    },
    "next_stage_recommendation": {
      "type": "string",
      "enum": [
        "exception_design",
        "return_to_rpa_boundary_check",
        "return_to_requirement_clarification",
        "stop_with_blocker"
      ]
    }
  },
  "$defs": {
    "process_card": {
      "type": "object",
      "required": [
        "step_id",
        "step_name",
        "business_purpose",
        "input",
        "operation_summary",
        "output",
        "candidate_yingdao_capabilities",
        "depends_on",
        "prework_dependencies",
        "handoff_to_exception_design",
        "exception_design_notes"
      ],
      "additionalProperties": false,
      "properties": {
        "step_id": {
          "type": "string",
          "pattern": "^S[0-9]{2}$"
        },
        "step_name": {
          "type": "string"
        },
        "business_purpose": {
          "type": "string"
        },
        "input": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "operation_summary": {
          "type": "string"
        },
        "output": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "candidate_yingdao_capabilities": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "depends_on": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^S[0-9]{2}$"
          }
        },
        "prework_dependencies": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "handoff_to_exception_design": {
          "type": "boolean"
        },
        "exception_design_notes": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Create breakdown rules**

Create `agent_modules/process_breakdown/rules/breakdown-rules.json`:

```json
{
  "module": "module_4_process_breakdown",
  "breakdown_depth": "business_process_cards_with_candidate_capabilities",
  "allowed_source_classifications": ["suitable", "conditionally_suitable"],
  "blocked_source_classifications": ["not_ready", "not_suitable_for_direct_rpa"],
  "default_card_count": {
    "minimum": 4,
    "maximum": 8
  },
  "required_card_fields": [
    "step_id",
    "step_name",
    "business_purpose",
    "input",
    "operation_summary",
    "output",
    "candidate_yingdao_capabilities",
    "depends_on",
    "prework_dependencies",
    "handoff_to_exception_design",
    "exception_design_notes"
  ],
  "default_card_pattern": [
    "trigger_and_preparation",
    "load_configuration_scope_or_input",
    "enter_or_connect_to_source_system",
    "read_query_download_or_collect_source_data",
    "normalize_match_filter_or_calculate_data",
    "enter_or_connect_to_target_system",
    "write_upload_notify_or_generate_output",
    "record_execution_result_and_handoff_items"
  ],
  "forbidden_behaviors": [
    "do_not_generate_exact_click_paths",
    "do_not_generate_selectors_or_wait_times",
    "do_not_design_exception_branches",
    "do_not_generate_instruction_parameters",
    "do_not_override_module_3_decision",
    "do_not_generate_html"
  ],
  "question_policy": {
    "ask_only_when_main_flow_cannot_be_coherent": true,
    "must_use_module_1_choice_format": true,
    "must_include_unknown_and_other_routes": true
  }
}
```

- [ ] **Step 3: Create material use policy**

Create `agent_modules/process_breakdown/rules/material-use-policy.json`:

```json
{
  "module": "module_4_process_breakdown",
  "source_order": [
    {
      "source": "yingdao_flow_chain_templates_v3.md",
      "use": "primary_process_chain_patterns"
    },
    {
      "source": "yingdao_scenario_building_guide.md",
      "use": "scenario_family_decomposition"
    },
    {
      "source": "requirement_to_instruction_mapping.xlsx",
      "use": "common_need_to_process_module_examples"
    },
    {
      "source": "yingdao_instruction_search_keywords.xlsx",
      "use": "normalize_user_wording_to_scenario_family"
    },
    {
      "source": "yingdao_core_instruction_library.xlsx",
      "use": "high_priority_candidate_capability_names"
    },
    {
      "source": "yingdao_instruction_capability_library_cleaned.xlsx",
      "use": "broader_capability_notes_and_constraints"
    }
  ],
  "excluded_as_process_evidence": ["agent_answer_templates.md"],
  "rules": [
    "use_templates_without_instruction_parameters",
    "candidate_capabilities_are_orientation_not_final_build_steps",
    "flow_chain_templates_do_not_override_module_3_prework",
    "scenario_material_may_help_card_names_and_business_purpose"
  ]
}
```

- [ ] **Step 4: Create prompt rules**

Create `agent_modules/process_breakdown/rules/prompt-rules.md`:

```markdown
# Process Breakdown Prompt Rules

## Do

- Start from module 3's decision and prework.
- Preserve module 2 boundary facts instead of asking them again.
- Generate 4-8 business-readable process cards for typical automation needs.
- Attach candidate Yingdao capability families where useful.
- Mark exception topics for module 5 without designing them.
- Summarize cross-step dependencies such as account permissions, field mapping, template readiness, date scope, and result logging.

## Do Not

- Do not ask for exact button names.
- Do not generate selectors or wait times.
- Do not design exception branches.
- Do not generate retry counts or detailed error handling.
- Do not generate instruction parameter values.
- Do not override module 3's suitability decision.
- Do not produce a final build guide.
- Do not produce HTML.
```

- [ ] **Step 5: Run tests to verify partial progress**

Run:

```powershell
python -m unittest tests.test_process_breakdown_contracts -v
```

Expected: schema and rules tests pass; fixture, README, and platform prompt tests still fail because later-task files are missing or unchanged.

- [ ] **Step 6: Commit schema and rules**

Run:

```powershell
git add agent_modules/process_breakdown/schemas agent_modules/process_breakdown/rules
git commit -m "feat: add process breakdown schema and rules"
```

Expected: commit succeeds with four module 4 files.

---

### Task 3: Add Module 4 Fixtures And README

**Files:**
- Create: `agent_modules/process_breakdown/fixtures/ecommerce-daily-report-process-breakdown.json`
- Create: `agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json`
- Create: `agent_modules/process_breakdown/README.md`

**Interfaces:**
- Consumes: module 4 schema and rules from Task 2
- Produces: concrete examples for the two already-used platform test scenarios

- [ ] **Step 1: Create e-commerce process breakdown fixture**

Create `agent_modules/process_breakdown/fixtures/ecommerce-daily-report-process-breakdown.json`:

```json
{
  "module": "module_4_process_breakdown",
  "status": "completed",
  "source_decision": {
    "classification": "conditionally_suitable",
    "confidence": "medium_high"
  },
  "breakdown_depth": "business_process_cards_with_candidate_capabilities",
  "process_cards": [
    {
      "step_id": "S01",
      "step_name": "Prepare report scope",
      "business_purpose": "Confirm the date, platform-store scope, and target report template before data collection starts.",
      "input": ["日报日期口径", "平台-店铺清单", "腾讯文档日报模板"],
      "operation_summary": "Load the fixed platform-store list, date scope, and report template configuration.",
      "output": ["execution scope", "target template position"],
      "candidate_yingdao_capabilities": ["configuration reading", "Excel or table reading"],
      "depends_on": [],
      "prework_dependencies": ["确认平台-店铺清单是否固定且完整", "确认日报日期口径"],
      "handoff_to_exception_design": false,
      "exception_design_notes": []
    },
    {
      "step_id": "S02",
      "step_name": "Enter platform accounts",
      "business_purpose": "Prepare access to each e-commerce platform backend.",
      "input": ["platform account permissions", "login strategy"],
      "operation_summary": "Open or connect to each platform backend using the configured account access method.",
      "output": ["available platform sessions"],
      "candidate_yingdao_capabilities": ["web automation", "login", "browser control"],
      "depends_on": ["S01"],
      "prework_dependencies": ["确认每个平台的账号权限和登录稳定性"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["login failure", "captcha or device verification", "permission missing"]
    },
    {
      "step_id": "S03",
      "step_name": "Collect platform daily data",
      "business_purpose": "Get the daily operating metrics for each platform and fixed store.",
      "input": ["platform-store list", "date scope", "account permissions"],
      "operation_summary": "Enter each platform backend and query or download the daily data under fixed conditions.",
      "output": ["raw platform daily data"],
      "candidate_yingdao_capabilities": ["web automation", "report download", "file reading"],
      "depends_on": ["S01", "S02"],
      "prework_dependencies": ["确认平台-店铺清单", "确认稳定登录策略"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["login failure", "missing data", "download failure"]
    },
    {
      "step_id": "S04",
      "step_name": "Normalize metrics",
      "business_purpose": "Convert platform data into the same report field structure.",
      "input": ["raw platform daily data", "metric mapping rules"],
      "operation_summary": "Map platform fields to report fields and calculate the values needed for the daily report.",
      "output": ["normalized report data"],
      "candidate_yingdao_capabilities": ["data processing", "Excel processing", "condition judgment"],
      "depends_on": ["S03"],
      "prework_dependencies": ["确认各平台指标与腾讯文档字段的一一对应关系"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["missing field", "metric口径 mismatch", "empty value"]
    },
    {
      "step_id": "S05",
      "step_name": "Write Tencent Docs report",
      "business_purpose": "Write normalized daily data into the fixed Tencent Docs report template.",
      "input": ["normalized report data", "Tencent Docs template position"],
      "operation_summary": "Open the target Tencent Docs template and write each platform-store metric into the configured position.",
      "output": ["updated Tencent Docs daily report"],
      "candidate_yingdao_capabilities": ["web automation", "online document editing", "table writing"],
      "depends_on": ["S04"],
      "prework_dependencies": ["确认腾讯文档模板和写入位置固定"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["write failure", "template changed", "permission missing"]
    },
    {
      "step_id": "S06",
      "step_name": "Record execution result",
      "business_purpose": "Preserve evidence for whether the report was generated correctly.",
      "input": ["source values", "written values", "execution status"],
      "operation_summary": "Record source value, written value, processing time, and abnormal items for later review.",
      "output": ["execution log", "manual review list"],
      "candidate_yingdao_capabilities": ["logging", "Excel writing", "notification"],
      "depends_on": ["S05"],
      "prework_dependencies": ["确认最小结果校验方式"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["source-write mismatch", "manual review required"]
    }
  ],
  "cross_step_dependencies": [
    "平台-店铺清单 must be fixed and complete.",
    "Metric-to-template mapping must be confirmed before normalization.",
    "Date scope must be agreed before collection.",
    "Stable login strategy is required for platform collection.",
    "Result log must preserve source values and written values."
  ],
  "open_questions": [],
  "handoff_to_exception_design": {
    "required": true,
    "focus_steps": ["S02", "S03", "S04", "S05", "S06"],
    "notes": ["Design login, missing data, template change, write failure, and source-write mismatch branches."]
  },
  "next_stage_recommendation": "exception_design"
}
```

- [ ] **Step 2: Create email sorting fixture**

Create `agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json`:

```json
{
  "module": "module_4_process_breakdown",
  "status": "completed",
  "source_decision": {
    "classification": "conditionally_suitable",
    "confidence": "medium_high"
  },
  "breakdown_depth": "business_process_cards_with_candidate_capabilities",
  "process_cards": [
    {
      "step_id": "S01",
      "step_name": "Prepare classification scope",
      "business_purpose": "Confirm mailbox, folder or label taxonomy, and classification rules before processing starts.",
      "input": ["mailbox access", "classification taxonomy", "sender and keyword rules"],
      "operation_summary": "Load the mailbox scope, target folders or labels, and the available classification rules.",
      "output": ["classification scope", "rule set"],
      "candidate_yingdao_capabilities": ["configuration reading", "table reading"],
      "depends_on": [],
      "prework_dependencies": ["准备固定分类目录或标签清单", "准备分类规则"],
      "handoff_to_exception_design": false,
      "exception_design_notes": []
    },
    {
      "step_id": "S02",
      "step_name": "Read new emails",
      "business_purpose": "Get the emails that need to be classified.",
      "input": ["Outlook or Microsoft 365 mailbox", "trigger condition"],
      "operation_summary": "Read newly arrived emails or the selected email batch from the mailbox.",
      "output": ["email list", "email metadata and content"],
      "candidate_yingdao_capabilities": ["email processing", "system integration"],
      "depends_on": ["S01"],
      "prework_dependencies": ["确认邮箱访问权限稳定"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["mailbox permission failure", "email read failure"]
    },
    {
      "step_id": "S03",
      "step_name": "Extract classification signals",
      "business_purpose": "Prepare the fields used for classification.",
      "input": ["email sender", "email subject", "email body"],
      "operation_summary": "Extract sender domain, subject keywords, body keywords, and available semantic examples.",
      "output": ["classification signals"],
      "candidate_yingdao_capabilities": ["text processing", "data extraction"],
      "depends_on": ["S02"],
      "prework_dependencies": ["准备典型发件人、主题关键词、正文关键词或样例邮件"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["empty body", "unsupported format", "missing subject"]
    },
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
    },
    {
      "step_id": "S05",
      "step_name": "Apply folder or label",
      "business_purpose": "Move or tag each email according to the classification result.",
      "input": ["email classification result", "target folder or label"],
      "operation_summary": "Move the email to the target folder or apply the target label; keep uncertain emails in the manual review queue.",
      "output": ["updated mailbox organization"],
      "candidate_yingdao_capabilities": ["email processing", "folder operation", "condition judgment"],
      "depends_on": ["S04"],
      "prework_dependencies": ["确认目标文件夹或标签已经存在"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["target folder missing", "move failure", "manual review routing"]
    },
    {
      "step_id": "S06",
      "step_name": "Record sorting result",
      "business_purpose": "Make the classification result auditable.",
      "input": ["email subject", "sender", "classification result", "judgment basis", "processing time"],
      "operation_summary": "Write the processing result and judgment basis into the sorting list or daily report.",
      "output": ["sorting log", "daily summary"],
      "candidate_yingdao_capabilities": ["Excel writing", "report generation", "notification"],
      "depends_on": ["S05"],
      "prework_dependencies": ["确定处理日志字段"],
      "handoff_to_exception_design": true,
      "exception_design_notes": ["log write failure", "summary generation failure"]
    }
  ],
  "cross_step_dependencies": [
    "Classification taxonomy must be fixed.",
    "Low-confidence review policy must be defined.",
    "Mailbox access must be stable.",
    "Processing log fields must be confirmed."
  ],
  "open_questions": [],
  "handoff_to_exception_design": {
    "required": true,
    "focus_steps": ["S02", "S03", "S04", "S05", "S06"],
    "notes": ["Design mailbox access, unknown category, low-confidence, move failure, and log failure branches."]
  },
  "next_stage_recommendation": "exception_design"
}
```

- [ ] **Step 3: Create README**

Create `agent_modules/process_breakdown/README.md`:

```markdown
# Process Breakdown Module

Module 4 turns an approved or conditionally approved RPA requirement into business process cards with candidate Yingdao capability families.

## Scope

This module consumes module 2 `clarification_result` facts and module 3 `rpa_boundary_result` decisions. It does not repeat requirement clarification, override RPA boundary decisions, design exception branches, generate exact click paths, or produce final HTML.

## Artifacts

- `schemas/process-breakdown-result.schema.json`
- `rules/breakdown-rules.json`
- `rules/material-use-policy.json`
- `rules/prompt-rules.md`
- `fixtures/ecommerce-daily-report-process-breakdown.json`
- `fixtures/email-sorting-process-breakdown.json`

## Process Card Fields

- `step_id`
- `step_name`
- `business_purpose`
- `input`
- `operation_summary`
- `output`
- `candidate_yingdao_capabilities`
- `depends_on`
- `prework_dependencies`
- `handoff_to_exception_design`
- `exception_design_notes`

## Boundary Rule

Cards are business-process descriptions, not build scripts. Candidate Yingdao capabilities orient the later build, but module 4 must not generate selectors, click paths, wait times, retry counts, or instruction parameter values.
```

- [ ] **Step 4: Run module 4 tests**

Run:

```powershell
python -m unittest tests.test_process_breakdown_contracts -v
```

Expected: fixture and README tests pass; platform prompt test may still fail until Task 4.

- [ ] **Step 5: Commit module 4 fixtures and README**

Run:

```powershell
git add agent_modules/process_breakdown/fixtures agent_modules/process_breakdown/README.md
git commit -m "feat: add process breakdown fixtures"
```

Expected: commit succeeds with three new files.

---

### Task 4: Update Agent Platform Package For Module 4

**Files:**
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Modify: `agent_platform_package/testing/expected_outputs.md`

**Interfaces:**
- Consumes: module 4 schema, rules, and fixtures from earlier tasks
- Produces: platform-facing prompt and expected output guidance for `process_breakdown_result`

- [ ] **Step 1: Update system prompt wrapper and module guidance**

Modify `agent_platform_package/system_prompt/agent-system-prompt.md`:

1. In the single JSON wrapper skeleton, add:

```json
  "process_breakdown_result": {}
```

2. Add this section after module 3 guidance:

```markdown
## Module 4: Process Breakdown

When `rpa_boundary_result.next_stage_recommendation` is `process_breakdown`, enter module 4.

Module 4 must produce one `process_breakdown_result` object. It turns the approved or conditionally approved requirement into business process cards with candidate Yingdao capability families.

Each process card must include:

- `step_id`
- `step_name`
- `business_purpose`
- `input`
- `operation_summary`
- `output`
- `candidate_yingdao_capabilities`
- `depends_on`
- `prework_dependencies`
- `handoff_to_exception_design`
- `exception_design_notes`

Module 4 must not generate exact click paths, selectors, wait times, retry counts, detailed exception branches, instruction parameters, final build guides, or HTML.

Exception topics may be named in `exception_design_notes`, but module 5 owns the actual branch design.
```

- [ ] **Step 2: Update expected outputs**

Add this section to `agent_platform_package/testing/expected_outputs.md`:

```markdown
## Module 4 Expected Output

When module 4 completes, the platform should return a single top-level wrapper containing:

- `interaction_state`
- `clarification_result`
- `rpa_boundary_result`
- `process_breakdown_result`

`process_breakdown_result.breakdown_depth` must be:

- `business_process_cards_with_candidate_capabilities`

Each process card should describe a business stage and candidate Yingdao capability families. It should not include selectors, exact click paths, wait times, retry counts, or instruction parameter values.

The e-commerce daily report scenario should produce cards for report scope preparation, platform access, platform data collection, metric normalization, Tencent Docs writing, and result logging.

The email sorting scenario should produce cards for classification scope preparation, email reading, signal extraction, classification, folder or label application, and result logging.
```

- [ ] **Step 3: Run full contract tests**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit platform updates**

Run:

```powershell
git add agent_platform_package/system_prompt/agent-system-prompt.md agent_platform_package/testing/expected_outputs.md
git commit -m "docs: add process breakdown platform guidance"
```

Expected: commit succeeds with two updated platform package docs.

---

### Task 5: Final Verification And Push

**Files:**
- Verify only; no expected file changes unless a previous task failed.

**Interfaces:**
- Consumes: all module 4 artifacts and tests
- Produces: pushed branch ready for user review

- [ ] **Step 1: Run full contract suite**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts -v
```

Expected: all tests pass.

- [ ] **Step 2: Scan module 4 files for known mojibake markers**

Run:

```powershell
rg -n "褰卞|鍙ｅ緞|閼|閻|鐠|妞|\\?md" agent_modules/process_breakdown docs/superpowers/specs/2026-06-25-process-breakdown-design.md agent_platform_package
```

Expected: no matches.

- [ ] **Step 3: Check git status**

Run:

```powershell
git status --short
```

Expected: clean working tree.

- [ ] **Step 4: Push branch**

Run:

```powershell
git push
```

Expected: branch `codex/agent-platform-package` pushes successfully to GitHub.

