# Yingdao RPA Boundary Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build module 3, a Yingdao RPA capability-boundary checker that consumes module 2 facts and returns a structured decision before process breakdown.

**Architecture:** Follow the existing module pattern: static schemas, rules, materials, fixtures, README, and unittest contract tests. Module 3 will not implement a runtime evaluator yet; it will define the agent-facing contract, controlled vocabulary, prompt constraints, and testable sample outputs.

**Tech Stack:** Markdown, JSON Schema draft 2020-12, JSON fixtures, Python `unittest`, repository-local documentation and packaging files.

## Global Constraints

- Module 3 consumes module 2 facts instead of repeating module 2 clarification.
- Use conditional admissibility: `suitable`, `conditionally_suitable`, `not_ready`, `not_suitable_for_direct_rpa`.
- Do not decide suitability from instruction existence alone.
- Preserve module 2 controlled risk identifiers: `semantic_judgment`, `missing_rules`, `unstable_input`, `unverifiable_result`, `unstable_platform`, `human_verification`, `open_ended_exceptions`, `low_roi`.
- Module 3 may ask only capability-critical confirmation questions, not exact click paths, selectors, step sequence, exception branch design, or instruction parameter values.
- Keep `agent_modules.zip` untracked and untouched.
- Source material with duplicate alias `yingdao_flow_chain_templates_v3_duplicate.md` must not be packaged unless proven different from `yingdao_flow_chain_templates_v3.md`.

---

## File Structure

- Create `agent_modules/rpa_boundary_check/README.md`: module purpose, artifacts, and boundary notes.
- Create `agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json`: formal output contract.
- Create `agent_modules/rpa_boundary_check/rules/decision-rules.json`: classification rules and dimension requirements.
- Create `agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json`: ordered use of Yingdao materials.
- Create `agent_modules/rpa_boundary_check/rules/prompt-rules.md`: agent behavior constraints.
- Create `agent_modules/rpa_boundary_check/materials/source-material-manifest.json`: normalized manifest for the seven approved source files.
- Create `agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json`: expected output for the Outlook sorting case.
- Create `agent_modules/rpa_boundary_check/fixtures/ecommerce-daily-report-boundary-result.json`: expected output for the e-commerce daily report case.
- Create `tests/test_rpa_boundary_check_contracts.py`: contract tests for schema, rules, materials, fixtures, and prompt boundaries.
- Modify `agent_platform_package/system_prompt/agent-system-prompt.md`: add module 3 summary and output discipline.
- Modify `agent_platform_package/testing/expected_outputs.md`: add module 3 expected output notes.

---

### Task 1: Add Module 3 Contract Tests First

**Files:**
- Create: `tests/test_rpa_boundary_check_contracts.py`

**Interfaces:**
- Consumes: files that later tasks create under `agent_modules/rpa_boundary_check/`
- Produces: test names and assertions that define the module 3 contract

- [ ] **Step 1: Write the failing test file**

Create `tests/test_rpa_boundary_check_contracts.py` with this content:

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class RpaBoundaryCheckContractTests(unittest.TestCase):
    def test_boundary_result_schema_defines_decision_dimensions(self):
        schema = load_json("agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json")
        props = schema["properties"]
        decision_props = props["decision"]["properties"]
        dimension_props = props["dimension_results"]["properties"]

        self.assertEqual(schema["title"], "RpaBoundaryResult")
        self.assertEqual(props["module"]["const"], "module_3_rpa_boundary_check")
        self.assertEqual(
            decision_props["classification"]["enum"],
            ["suitable", "conditionally_suitable", "not_ready", "not_suitable_for_direct_rpa"],
        )
        self.assertEqual(decision_props["confidence"]["enum"], ["high", "medium_high", "medium", "low"])
        self.assertEqual(
            list(dimension_props.keys()),
            [
                "scenario_match",
                "instruction_support",
                "input_readiness",
                "rule_readiness",
                "platform_operability",
                "result_verifiability",
                "exception_containment",
            ],
        )

    def test_schema_preserves_controlled_risk_types_and_capability_notes(self):
        schema = load_json("agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json")

        self.assertEqual(
            schema["$defs"]["risk_type"]["enum"],
            [
                "semantic_judgment",
                "missing_rules",
                "unstable_input",
                "unverifiable_result",
                "unstable_platform",
                "human_verification",
                "open_ended_exceptions",
                "low_roi",
            ],
        )
        self.assertEqual(
            schema["$defs"]["capability_note"]["enum"],
            [
                "requires_api_or_data_export",
                "requires_stable_login",
                "requires_field_mapping",
                "requires_template_standardization",
                "requires_manual_review_queue",
                "requires_result_log",
            ],
        )

    def test_decision_rules_encode_conditional_admissibility(self):
        rules = load_json("agent_modules/rpa_boundary_check/rules/decision-rules.json")

        self.assertEqual(rules["module"], "module_3_rpa_boundary_check")
        self.assertEqual(rules["design_choice"], "conditional_admissibility")
        self.assertEqual(
            rules["dimension_order"],
            [
                "scenario_match",
                "instruction_support",
                "input_readiness",
                "rule_readiness",
                "platform_operability",
                "result_verifiability",
                "exception_containment",
            ],
        )
        self.assertIn("instruction_match_is_evidence_not_decision", rules["global_rules"])
        self.assertIn("missing_required_module_2_facts_returns_not_ready", rules["global_rules"])
        self.assertEqual(rules["classification_rules"]["conditionally_suitable"]["default_for_real_customer_requirements"], True)

    def test_material_retrieval_policy_orders_yingdao_sources(self):
        policy = load_json("agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json")
        steps = policy["retrieval_order"]
        names = [step["source"] for step in steps]

        self.assertEqual(names[0], "yingdao_instruction_search_keywords.xlsx")
        self.assertEqual(names[1], "yingdao_scenario_building_guide.md")
        self.assertEqual(names[2], "yingdao_flow_chain_templates_v3.md")
        self.assertEqual(names[-1], "agent_answer_templates.md")
        self.assertEqual(steps[-1]["use"], "answer_shape_only")

    def test_source_material_manifest_classifies_seven_approved_files(self):
        manifest = load_json("agent_modules/rpa_boundary_check/materials/source-material-manifest.json")
        sources = manifest["sources"]
        source_names = {source["source"] for source in sources}

        self.assertEqual(manifest["version"], "v1")
        self.assertEqual(len(sources), 7)
        self.assertIn("yingdao_instruction_capability_library_cleaned.xlsx", source_names)
        self.assertIn("yingdao_core_instruction_library.xlsx", source_names)
        self.assertIn("yingdao_instruction_search_keywords.xlsx", source_names)
        self.assertIn("requirement_to_instruction_mapping.xlsx", source_names)
        self.assertIn("yingdao_flow_chain_templates_v3.md", source_names)
        self.assertIn("yingdao_scenario_building_guide.md", source_names)
        self.assertIn("agent_answer_templates.md", source_names)
        self.assertNotIn("影刀常见流程指令链模板V3_逻辑结构版 (1).md", source_names)

    def test_prompt_rules_keep_module_3_out_of_process_breakdown(self):
        text = (ROOT / "agent_modules/rpa_boundary_check/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Do not ask for exact click paths", text)
        self.assertIn("Do not produce the happy-path process breakdown", text)
        self.assertIn("Instruction existence is evidence, not a decision", text)
        self.assertIn("Ask capability-critical confirmation questions only", text)

    def test_email_sorting_fixture_is_conditionally_suitable(self):
        fixture = load_json("agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json")

        self.assertEqual(fixture["module"], "module_3_rpa_boundary_check")
        self.assertEqual(fixture["decision"]["classification"], "conditionally_suitable")
        self.assertIn("semantic_judgment", [risk["risk_type"] for risk in fixture["risks"]])
        self.assertIn("requires_manual_review_queue", fixture["capability_notes"])
        self.assertEqual(fixture["next_stage_recommendation"], "process_breakdown")

    def test_ecommerce_fixture_requires_mapping_and_verification_prework(self):
        fixture = load_json("agent_modules/rpa_boundary_check/fixtures/ecommerce-daily-report-boundary-result.json")

        self.assertEqual(fixture["decision"]["classification"], "conditionally_suitable")
        self.assertIn("requires_field_mapping", fixture["capability_notes"])
        self.assertIn("requires_result_log", fixture["capability_notes"])
        self.assertEqual(fixture["dimension_results"]["result_verifiability"]["status"], "conditional")
        self.assertIn("平台-店铺清单", " ".join(fixture["required_prework"]))

    def test_readme_lists_module_3_artifacts(self):
        text = (ROOT / "agent_modules/rpa_boundary_check/README.md").read_text(encoding="utf-8")

        expected_paths = [
            "schemas/rpa-boundary-result.schema.json",
            "rules/decision-rules.json",
            "rules/material-retrieval-policy.json",
            "rules/prompt-rules.md",
            "materials/source-material-manifest.json",
            "fixtures/email-sorting-boundary-result.json",
            "fixtures/ecommerce-daily-report-boundary-result.json",
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```powershell
python -m unittest tests.test_rpa_boundary_check_contracts -v
```

Expected: FAIL because `agent_modules/rpa_boundary_check/` files do not exist yet.

- [ ] **Step 3: Commit the failing tests**

Run:

```powershell
git add tests/test_rpa_boundary_check_contracts.py
git commit -m "test: add RPA boundary check contracts"
```

Expected: commit succeeds with one new test file.

---

### Task 2: Add Module 3 Schema And Rules

**Files:**
- Create: `agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json`
- Create: `agent_modules/rpa_boundary_check/rules/decision-rules.json`
- Create: `agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json`
- Create: `agent_modules/rpa_boundary_check/rules/prompt-rules.md`

**Interfaces:**
- Consumes: test assertions from Task 1
- Produces: schema/rules consumed by fixtures, README, platform prompt, and later module implementation

- [ ] **Step 1: Create the schema file**

Create `agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/rpa-boundary-result.schema.json",
  "title": "RpaBoundaryResult",
  "type": "object",
  "required": [
    "module",
    "status",
    "decision",
    "dimension_results",
    "matched_yingdao_capabilities",
    "risks",
    "capability_notes",
    "required_prework",
    "not_to_do_in_rpa",
    "next_stage_recommendation",
    "pending_questions"
  ],
  "additionalProperties": false,
  "properties": {
    "module": {
      "const": "module_3_rpa_boundary_check"
    },
    "status": {
      "type": "string",
      "enum": ["completed", "needs_more_information"]
    },
    "decision": {
      "type": "object",
      "required": ["classification", "summary", "confidence"],
      "additionalProperties": false,
      "properties": {
        "classification": {
          "type": "string",
          "enum": ["suitable", "conditionally_suitable", "not_ready", "not_suitable_for_direct_rpa"]
        },
        "summary": {
          "type": "string"
        },
        "confidence": {
          "type": "string",
          "enum": ["high", "medium_high", "medium", "low"]
        }
      }
    },
    "dimension_results": {
      "type": "object",
      "required": [
        "scenario_match",
        "instruction_support",
        "input_readiness",
        "rule_readiness",
        "platform_operability",
        "result_verifiability",
        "exception_containment"
      ],
      "additionalProperties": false,
      "properties": {
        "scenario_match": {
          "$ref": "#/$defs/dimension_result"
        },
        "instruction_support": {
          "$ref": "#/$defs/dimension_result"
        },
        "input_readiness": {
          "$ref": "#/$defs/dimension_result"
        },
        "rule_readiness": {
          "$ref": "#/$defs/dimension_result"
        },
        "platform_operability": {
          "$ref": "#/$defs/dimension_result"
        },
        "result_verifiability": {
          "$ref": "#/$defs/dimension_result"
        },
        "exception_containment": {
          "$ref": "#/$defs/dimension_result"
        }
      }
    },
    "matched_yingdao_capabilities": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/matched_capability"
      }
    },
    "risks": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/risk"
      }
    },
    "capability_notes": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/capability_note"
      },
      "uniqueItems": true
    },
    "required_prework": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "not_to_do_in_rpa": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "next_stage_recommendation": {
      "type": "string",
      "enum": ["process_breakdown", "return_to_requirement_clarification", "stop_with_gap_report", "stop_with_blocker"]
    },
    "pending_questions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "$defs": {
    "dimension_status": {
      "type": "string",
      "enum": ["pass", "conditional", "fail", "unknown"]
    },
    "dimension_result": {
      "type": "object",
      "required": ["status", "evidence", "notes", "required_prework"],
      "additionalProperties": false,
      "properties": {
        "status": {
          "$ref": "#/$defs/dimension_status"
        },
        "evidence": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "notes": {
          "type": "string"
        },
        "required_prework": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    },
    "matched_capability": {
      "type": "object",
      "required": ["scenario_family", "candidate_instruction_categories", "candidate_instruction_names", "source_material"],
      "additionalProperties": false,
      "properties": {
        "scenario_family": {
          "type": "string"
        },
        "candidate_instruction_categories": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "candidate_instruction_names": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "source_material": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    },
    "risk_type": {
      "type": "string",
      "enum": [
        "semantic_judgment",
        "missing_rules",
        "unstable_input",
        "unverifiable_result",
        "unstable_platform",
        "human_verification",
        "open_ended_exceptions",
        "low_roi"
      ]
    },
    "risk": {
      "type": "object",
      "required": ["risk_type", "severity", "evidence", "mitigation"],
      "additionalProperties": false,
      "properties": {
        "risk_type": {
          "$ref": "#/$defs/risk_type"
        },
        "severity": {
          "type": "string",
          "enum": ["high", "medium", "low"]
        },
        "evidence": {
          "type": "string"
        },
        "mitigation": {
          "type": "string"
        }
      }
    },
    "capability_note": {
      "type": "string",
      "enum": [
        "requires_api_or_data_export",
        "requires_stable_login",
        "requires_field_mapping",
        "requires_template_standardization",
        "requires_manual_review_queue",
        "requires_result_log"
      ]
    }
  }
}
```

- [ ] **Step 2: Create decision rules**

Create `agent_modules/rpa_boundary_check/rules/decision-rules.json`:

```json
{
  "module": "module_3_rpa_boundary_check",
  "design_choice": "conditional_admissibility",
  "dimension_order": [
    "scenario_match",
    "instruction_support",
    "input_readiness",
    "rule_readiness",
    "platform_operability",
    "result_verifiability",
    "exception_containment"
  ],
  "required_module_2_facts": [
    "business_goal",
    "input_data",
    "operated_systems",
    "output_result",
    "completion_condition"
  ],
  "recommended_module_2_facts": [
    "trigger",
    "rule_clarity",
    "input_stability",
    "platform_operability",
    "result_verifiability"
  ],
  "global_rules": [
    "instruction_match_is_evidence_not_decision",
    "missing_required_module_2_facts_returns_not_ready",
    "module_3_must_not_repeat_module_2_boundary_clarification",
    "module_3_must_not_generate_process_breakdown",
    "module_3_questions_must_be_capability_critical"
  ],
  "classification_rules": {
    "suitable": {
      "required_dimension_statuses": {
        "scenario_match": ["pass"],
        "instruction_support": ["pass"],
        "rule_readiness": ["pass"],
        "platform_operability": ["pass"],
        "result_verifiability": ["pass"]
      },
      "allows_minor_conditionals": ["input_readiness", "exception_containment"]
    },
    "conditionally_suitable": {
      "default_for_real_customer_requirements": true,
      "requires_supported_core": true,
      "allows_prework_when_concrete": true,
      "containment_strategies": [
        "standardization",
        "field_mapping",
        "manual_review_queue",
        "login_stabilization",
        "result_logging",
        "api_or_data_export"
      ]
    },
    "not_ready": {
      "use_when": [
        "required_information_missing",
        "boundary_facts_not_confirmed",
        "input_rules_output_or_platform_access_cannot_be_judged_yet"
      ]
    },
    "not_suitable_for_direct_rpa": {
      "use_when": [
        "core_task_depends_on_open_ended_semantic_judgment_without_rules_or_review",
        "input_highly_unstable_and_cannot_be_standardized",
        "target_platform_cannot_be_operated_or_accessed_reliably",
        "strong_human_verification_is_frequent_and_cannot_be_separated",
        "success_cannot_be_verified",
        "process_is_low_frequency_high_variability_and_heavy_manual_judgment"
      ]
    }
  }
}
```

- [ ] **Step 3: Create material retrieval policy**

Create `agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json`:

```json
{
  "module": "module_3_rpa_boundary_check",
  "retrieval_order": [
    {
      "source": "yingdao_instruction_search_keywords.xlsx",
      "use": "normalize_customer_language"
    },
    {
      "source": "yingdao_scenario_building_guide.md",
      "use": "match_scenario_family"
    },
    {
      "source": "yingdao_flow_chain_templates_v3.md",
      "use": "check_mature_flow_chain_pattern"
    },
    {
      "source": "yingdao_core_instruction_library.xlsx",
      "use": "verify_high_priority_instruction_support"
    },
    {
      "source": "yingdao_instruction_capability_library_cleaned.xlsx",
      "use": "verify_broader_capability_and_constraints"
    },
    {
      "source": "requirement_to_instruction_mapping.xlsx",
      "use": "few_shot_examples_and_regression_cases"
    },
    {
      "source": "agent_answer_templates.md",
      "use": "answer_shape_only"
    }
  ],
  "rules": [
    "prefer_core_instruction_library_before_extended_capability_library",
    "do_not_use_answer_template_as_capability_evidence",
    "do_not_package_duplicate_flow_chain_template_copy",
    "treat_instruction_match_as_evidence_not_decision"
  ]
}
```

- [ ] **Step 4: Create prompt rules**

Create `agent_modules/rpa_boundary_check/rules/prompt-rules.md`:

```markdown
# RPA Boundary Check Prompt Rules

## Do

- Consume module 2 `clarification_result` facts before asking any new question.
- Judge capability through conditions: scenario match, instruction support, input readiness, rule readiness, platform operability, result verifiability, and exception containment.
- Treat Instruction existence is evidence, not a decision.
- Ask capability-critical confirmation questions only when a dimension cannot be judged.
- Return one structured `rpa_boundary_result` object.
- Use controlled risk identifiers from module 2.
- Explain required prework as concrete customer actions.

## Do Not

- Do not ask for exact click paths.
- Do not ask for selectors, UI element names, or instruction parameter values.
- Do not produce the happy-path process breakdown.
- Do not design detailed exception branches.
- Do not generate the final HTML report.
- Do not classify a requirement as suitable only because a similar instruction exists.
- Do not repeat module 2 boundary questions when the facts are already present.
```

- [ ] **Step 5: Run tests to verify partial progress**

Run:

```powershell
python -m unittest tests.test_rpa_boundary_check_contracts -v
```

Expected: schema and rules tests pass; manifest, fixtures, and README tests still fail.

- [ ] **Step 6: Commit schema and rules**

Run:

```powershell
git add agent_modules/rpa_boundary_check/schemas agent_modules/rpa_boundary_check/rules
git commit -m "feat: add RPA boundary schema and rules"
```

Expected: commit succeeds with four new module 3 contract files.

---

### Task 3: Add Source Manifest, Fixtures, And README

**Files:**
- Create: `agent_modules/rpa_boundary_check/materials/source-material-manifest.json`
- Create: `agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json`
- Create: `agent_modules/rpa_boundary_check/fixtures/ecommerce-daily-report-boundary-result.json`
- Create: `agent_modules/rpa_boundary_check/README.md`

**Interfaces:**
- Consumes: schema and rules from Task 2
- Produces: testable examples and material role definitions for later Agent package updates

- [ ] **Step 1: Create source material manifest**

Create `agent_modules/rpa_boundary_check/materials/source-material-manifest.json`:

```json
{
  "version": "v1",
  "module": "module_3_rpa_boundary_check",
  "sources": [
    {
      "source": "yingdao_instruction_capability_library_cleaned.xlsx",
      "role": "skill_material_and_rag_source",
      "purpose": "Main capability library for instruction capabilities, prerequisites, unsuitable scenarios, common errors, and handling suggestions."
    },
    {
      "source": "yingdao_core_instruction_library.xlsx",
      "role": "skill_material",
      "purpose": "High-priority core instruction subset used before broader extended instruction matching."
    },
    {
      "source": "yingdao_instruction_search_keywords.xlsx",
      "role": "retrieval_normalization",
      "purpose": "Maps customer wording to standard requirement types and candidate instruction keys."
    },
    {
      "source": "requirement_to_instruction_mapping.xlsx",
      "role": "few_shot_examples_and_tests",
      "purpose": "Small demand-to-instruction examples for scenario mapping, risks, clarification questions, and regression tests."
    },
    {
      "source": "yingdao_flow_chain_templates_v3.md",
      "original_filename": "影刀常见流程指令链模板V3_逻辑结构版.md",
      "role": "module_4_primary_module_3_supporting",
      "purpose": "Checks whether a mature flow-chain pattern exists without generating detailed process breakdown in module 3."
    },
    {
      "source": "yingdao_scenario_building_guide.md",
      "role": "scenario_level_rag_source",
      "purpose": "Maps needs to broad scenario families such as web automation, Excel processing, file handling, login, collection, and notification."
    },
    {
      "source": "agent_answer_templates.md",
      "role": "answer_shape_only",
      "purpose": "Constrains response shape after a decision; not used as capability evidence."
    }
  ]
}
```

- [ ] **Step 2: Create email sorting fixture**

Create `agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json`:

```json
{
  "module": "module_3_rpa_boundary_check",
  "status": "completed",
  "decision": {
    "classification": "conditionally_suitable",
    "summary": "邮件自动整理需求具备明确系统、输入、输出和处理记录，但正文语义分类存在误分风险，适合在规则分类基础上加入低置信度人工确认。",
    "confidence": "medium_high"
  },
  "dimension_results": {
    "scenario_match": {
      "status": "pass",
      "evidence": ["邮件系统处理", "规则分类", "结果清单或日报"],
      "notes": "需求可映射到邮件读取、条件判断、分类写入和日志记录场景。",
      "required_prework": []
    },
    "instruction_support": {
      "status": "pass",
      "evidence": ["系统集成/邮件", "数据清洗与转换", "条件判断"],
      "notes": "发件人、发件域名和主题关键词可按规则处理。",
      "required_prework": []
    },
    "input_readiness": {
      "status": "conditional",
      "evidence": ["大部分邮件来源和格式固定，偶尔有新类型邮件"],
      "notes": "新类型邮件需要进入待人工确认，避免直接误分。",
      "required_prework": ["准备典型样例邮件和新类型邮件处理策略。"]
    },
    "rule_readiness": {
      "status": "conditional",
      "evidence": ["已有固定分类目录，部分需要邮件语义判断"],
      "notes": "关键词和发件人规则适合自动化；语义判断需要规则样例和置信度控制。",
      "required_prework": ["为每个分类补充发件人、主题关键词、正文关键词和样例邮件。"]
    },
    "platform_operability": {
      "status": "pass",
      "evidence": ["Outlook / Microsoft 365 账号和邮箱权限稳定"],
      "notes": "系统和权限边界清楚。",
      "required_prework": []
    },
    "result_verifiability": {
      "status": "pass",
      "evidence": ["每封邮件记录目标文件夹/标签、判断依据、处理时间"],
      "notes": "处理日志可以验证输出。",
      "required_prework": []
    },
    "exception_containment": {
      "status": "conditional",
      "evidence": ["低置信度邮件进入待人工确认"],
      "notes": "语义不确定性通过人工确认队列收敛。",
      "required_prework": ["明确低置信度阈值或人工确认规则。"]
    }
  },
  "matched_yingdao_capabilities": [
    {
      "scenario_family": "系统集成/邮件",
      "candidate_instruction_categories": ["邮件", "条件判断", "数据处理"],
      "candidate_instruction_names": ["邮件读取", "IF 条件", "写入Excel"],
      "source_material": ["yingdao_instruction_search_keywords.xlsx", "yingdao_core_instruction_library.xlsx"]
    }
  ],
  "risks": [
    {
      "risk_type": "semantic_judgment",
      "severity": "medium",
      "evidence": "部分分类依赖正文语义判断。",
      "mitigation": "低置信度邮件进入待人工确认，并记录判断依据。"
    },
    {
      "risk_type": "unstable_input",
      "severity": "low",
      "evidence": "偶尔出现新类型邮件。",
      "mitigation": "在日报中标记未命中规则或低置信度邮件。"
    }
  ],
  "capability_notes": ["requires_manual_review_queue", "requires_result_log"],
  "required_prework": [
    "准备固定分类目录或标签清单。",
    "为每个分类补充典型发件人、主题关键词、正文关键词或样例邮件。",
    "明确低置信度邮件进入待人工确认的规则。",
    "确定处理日志字段：主题、发件人、分类结果、判断依据、处理时间、是否需人工确认。"
  ],
  "not_to_do_in_rpa": ["不要让机器人在没有规则或人工确认队列的情况下直接判断开放式语义分类。"],
  "next_stage_recommendation": "process_breakdown",
  "pending_questions": []
}
```

- [ ] **Step 3: Create e-commerce daily report fixture**

Create `agent_modules/rpa_boundary_check/fixtures/ecommerce-daily-report-boundary-result.json`:

```json
{
  "module": "module_3_rpa_boundary_check",
  "status": "completed",
  "decision": {
    "classification": "conditionally_suitable",
    "summary": "多平台电商日报需求具备固定频率、固定店铺范围和明确写入目标，适合优先进入RPA方案设计；进入流程拆解前需要确认平台-店铺清单、指标口径、日期范围和结果核对方式。",
    "confidence": "medium_high"
  },
  "dimension_results": {
    "scenario_match": {
      "status": "pass",
      "evidence": ["网页自动化/数据采集", "网页自动化/文件下载", "Excel/表格处理", "腾讯文档写入"],
      "notes": "该需求符合多平台后台采集、表格处理和在线文档写入的组合场景。",
      "required_prework": []
    },
    "instruction_support": {
      "status": "pass",
      "evidence": ["行业平台报表下载", "数据清洗与转换", "文件与办公文档处理"],
      "notes": "候选能力覆盖登录、查询、下载或读取、汇总、写入。",
      "required_prework": []
    },
    "input_readiness": {
      "status": "conditional",
      "evidence": ["多个电商平台和固定店铺", "指标包括GMV、支付订单数、退款金额、退款单数"],
      "notes": "店铺数量固定有利于自动化，但多平台字段和口径需要映射。",
      "required_prework": ["确认平台-店铺清单。", "确认各平台指标与腾讯文档字段的一一对应关系。"]
    },
    "rule_readiness": {
      "status": "conditional",
      "evidence": ["各平台数据口径大体统一，只需要按同一口径汇总"],
      "notes": "汇总规则可自动化，但必须明确日期口径和指标口径。",
      "required_prework": ["明确日报日期范围，例如自然日或前一日。", "明确退款金额和退款单数的统计口径。"]
    },
    "platform_operability": {
      "status": "conditional",
      "evidence": ["登录态相对稳定，基本不会频繁遇到验证码或设备确认"],
      "notes": "平台可操作性较好，但多平台登录稳定性仍需作为前置条件。",
      "required_prework": ["确认每个平台是否有稳定账号、权限和登录策略。"]
    },
    "result_verifiability": {
      "status": "conditional",
      "evidence": ["当前只要求成功写入，不要求与源平台逐项自动核对"],
      "notes": "写入成功只能证明动作完成，不能证明数据正确。",
      "required_prework": ["至少记录源平台取数值、写入值、处理时间和异常状态。"]
    },
    "exception_containment": {
      "status": "conditional",
      "evidence": ["多平台多店铺可能存在口径差异和登录异常"],
      "notes": "常见异常可以通过平台级失败记录和人工复核收敛。",
      "required_prework": ["定义平台登录失败、数据缺失、模板写入失败时的处理方式。"]
    }
  },
  "matched_yingdao_capabilities": [
    {
      "scenario_family": "电商平台日报采集",
      "candidate_instruction_categories": ["网页自动化", "文件下载", "Excel/表格处理", "在线文档写入"],
      "candidate_instruction_names": ["打开网页", "下载文件", "读取Excel", "写入Excel", "条件判断"],
      "source_material": ["yingdao_instruction_search_keywords.xlsx", "yingdao_scenario_building_guide.md", "yingdao_flow_chain_templates_v3.md"]
    }
  ],
  "risks": [
    {
      "risk_type": "unstable_platform",
      "severity": "medium",
      "evidence": "涉及多个电商平台后台，登录态和页面结构可能变化。",
      "mitigation": "优先确认账号权限、登录策略和是否可通过报表导出/API降低页面依赖。"
    },
    {
      "risk_type": "unverifiable_result",
      "severity": "medium",
      "evidence": "当前只要求写入成功，不自动核对源数据。",
      "mitigation": "增加源值、写入值和异常状态记录。"
    }
  ],
  "capability_notes": ["requires_stable_login", "requires_field_mapping", "requires_result_log"],
  "required_prework": [
    "确认平台-店铺清单是否固定且完整。",
    "确认各平台指标与腾讯文档字段的一一对应关系。",
    "确认日报日期口径是自然日、前一日还是平台统计日。",
    "确认每个平台的账号权限和登录稳定性。",
    "确认最小结果校验方式，至少保留源平台取数值和写入值。"
  ],
  "not_to_do_in_rpa": ["不要只以腾讯文档写入成功作为数据正确性的唯一证明。"],
  "next_stage_recommendation": "process_breakdown",
  "pending_questions": []
}
```

- [ ] **Step 4: Create README**

Create `agent_modules/rpa_boundary_check/README.md`:

```markdown
# RPA Boundary Check Module

Module 3 decides whether a clarified requirement is suitable for Yingdao RPA, conditionally suitable after prework, not ready, or not suitable for direct unattended RPA.

## Scope

This module consumes module 2 `clarification_result` facts. It does not repeat boundary clarification, generate happy-path process steps, design exception branches, or produce the final HTML report.

## Artifacts

- `schemas/rpa-boundary-result.schema.json`
- `rules/decision-rules.json`
- `rules/material-retrieval-policy.json`
- `rules/prompt-rules.md`
- `materials/source-material-manifest.json`
- `fixtures/email-sorting-boundary-result.json`
- `fixtures/ecommerce-daily-report-boundary-result.json`

## Decision Dimensions

- `scenario_match`
- `instruction_support`
- `input_readiness`
- `rule_readiness`
- `platform_operability`
- `result_verifiability`
- `exception_containment`

## Boundary Rule

Instruction existence is evidence, not a decision. The module must check whether inputs, rules, platform access, output verification, and exception containment are concrete enough before recommending process breakdown.
```

- [ ] **Step 5: Run module 3 tests**

Run:

```powershell
python -m unittest tests.test_rpa_boundary_check_contracts -v
```

Expected: all module 3 contract tests pass.

- [ ] **Step 6: Commit module 3 materials**

Run:

```powershell
git add agent_modules/rpa_boundary_check
git commit -m "feat: add RPA boundary materials and fixtures"
```

Expected: commit succeeds with module 3 schema, rules, materials, fixtures, and README.

---

### Task 4: Update Agent Platform Package For Module 3

**Files:**
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Modify: `agent_platform_package/testing/expected_outputs.md`

**Interfaces:**
- Consumes: `agent_modules/rpa_boundary_check/` artifacts
- Produces: platform-facing prompt and testing guidance for module 3

- [ ] **Step 1: Update system prompt**

Add this section after the module 2 guidance in `agent_platform_package/system_prompt/agent-system-prompt.md`:

```markdown
## Module 3: Yingdao RPA Boundary Check

When `clarification_result.next_stage_recommendation` is `rpa_boundary_check`, enter module 3.

Module 3 must produce one `rpa_boundary_result` object. Use the classification values:

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

Evaluate seven dimensions:

- `scenario_match`
- `instruction_support`
- `input_readiness`
- `rule_readiness`
- `platform_operability`
- `result_verifiability`
- `exception_containment`

Instruction existence is evidence, not a decision. Do not conclude that a requirement can be automated only because a related Yingdao instruction exists.

Do not generate happy-path steps, exception branches, exact click paths, selectors, or instruction parameters in module 3. If information is missing, ask capability-critical confirmation questions only.
```

- [ ] **Step 2: Update expected outputs**

Add this section to `agent_platform_package/testing/expected_outputs.md`:

```markdown
## Module 3 Expected Output

The platform should return a single top-level wrapper containing:

- `interaction_state`
- `answer_batch` when user answers were recorded in the same turn
- `clarification_result` when module 2 facts are still relevant
- `rpa_boundary_result` when module 3 has completed

For module 3, `rpa_boundary_result.decision.classification` must be one of:

- `suitable`
- `conditionally_suitable`
- `not_ready`
- `not_suitable_for_direct_rpa`

`candidate_instruction_names` may appear as evidence, but the final decision must also cite input readiness, rule readiness, platform operability, result verifiability, and exception containment.

The e-commerce daily report scenario should normally be `conditionally_suitable`, not automatically `suitable`, until platform-store mapping, metric mapping, date scope, login stability, and result verification are confirmed.
```

- [ ] **Step 3: Run existing contract tests**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit platform package updates**

Run:

```powershell
git add agent_platform_package/system_prompt/agent-system-prompt.md agent_platform_package/testing/expected_outputs.md
git commit -m "docs: add RPA boundary platform guidance"
```

Expected: commit succeeds with two updated platform package docs.

---

### Task 5: Final Verification And Push

**Files:**
- Verify only; no expected file changes unless a previous task failed.

**Interfaces:**
- Consumes: all module 3 artifacts and tests
- Produces: pushed branch ready for user review

- [ ] **Step 1: Run full contract suite**

Run:

```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts -v
```

Expected: all tests pass.

- [ ] **Step 2: Scan module 3 files for known mojibake markers**

Run:

```powershell
rg -n "褰卞|鍙ｅ緞|閼|閻|鐠|妞|\\?md" agent_modules/rpa_boundary_check docs/superpowers/specs/2026-06-25-yingdao-rpa-boundary-check-design.md agent_platform_package
```

Expected: no matches. If the approved spec still contains a corrupted Chinese filename, replace that display name with `yingdao_flow_chain_templates_v3.md` plus `original_filename` metadata in the manifest.

- [ ] **Step 3: Check git status**

Run:

```powershell
git status --short
```

Expected: only `?? agent_modules.zip` remains untracked.

- [ ] **Step 4: Push branch**

Run:

```powershell
git push
```

Expected: branch `codex/agent-platform-package` pushes successfully to GitHub.
