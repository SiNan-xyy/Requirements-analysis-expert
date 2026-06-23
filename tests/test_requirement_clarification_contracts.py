import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class RequirementClarificationContractTests(unittest.TestCase):
    def test_clarification_result_schema_defines_boundary_and_prescreen_fields(self):
        schema = load_json("agent_modules/requirement_clarification/schemas/clarification-result.schema.json")
        props = schema["properties"]
        boundary_required = props["boundary_facts"]["required"]
        prescreen_required = props["rpa_fit_prescreen"]["required"]

        self.assertEqual(props["clarification_depth"]["const"], "boundary_only")
        self.assertIn("business_goal", boundary_required)
        self.assertIn("trigger", boundary_required)
        self.assertIn("completion_condition", boundary_required)
        self.assertIn("input_data", boundary_required)
        self.assertIn("operated_systems", boundary_required)
        self.assertIn("output_result", boundary_required)
        self.assertIn("rule_clarity", prescreen_required)
        self.assertIn("result_verifiability", prescreen_required)

    def test_ready_fixture_points_to_rpa_boundary_check(self):
        fixture = load_json("agent_modules/requirement_clarification/fixtures/clarification-result-ready.json")

        self.assertEqual(fixture["clarification_depth"], "boundary_only")
        self.assertEqual(fixture["next_stage_recommendation"], "rpa_boundary_check")
        self.assertTrue(fixture["boundary_facts"]["business_goal"]["value"])
        self.assertIsInstance(fixture["boundary_facts"]["input_data"]["value"], list)
        self.assertGreaterEqual(len(fixture["boundary_facts"]["input_data"]["value"]), 1)
        self.assertEqual(fixture["rpa_fit_prescreen"]["rule_clarity"], "medium")
        self.assertTrue(fixture["stage_summary"])

    def test_semantic_risk_fixture_flags_prework_without_final_decision(self):
        fixture = load_json("agent_modules/requirement_clarification/fixtures/semantic-risk-prescreen.json")
        prescreen = fixture["rpa_fit_prescreen"]

        self.assertEqual(fixture["clarification_depth"], "boundary_only")
        self.assertIn("semantic_judgment", prescreen["candidate_risk_types"])
        self.assertIn("semantic_judgment", prescreen["pre_screen_flags"])
        self.assertIn("先统一物料主数据命名规则", prescreen["recommended_prework"])
        self.assertIn("建立供应商名称与标准物料名称的映射表", prescreen["recommended_prework"])
        self.assertEqual(fixture["next_stage_recommendation"], "stop_with_prework_recommendation")
        self.assertNotIn("final_feasibility", fixture)
        self.assertTrue(fixture["stage_summary"])

    def test_completion_rules_preserve_boundary_only_thresholds(self):
        rules = load_json("agent_modules/requirement_clarification/rules/completion-rules.json")

        self.assertEqual(rules["clarification_depth"], "boundary_only")
        self.assertEqual(
            rules["boundary_facts"],
            [
                "business_goal",
                "trigger",
                "completion_condition",
                "input_data",
                "operated_systems",
                "output_result",
            ],
        )
        self.assertEqual(
            rules["core_fields"],
            [
                "input_data",
                "operated_systems",
                "output_result",
            ],
        )
        self.assertEqual(rules["summarize_threshold"]["minimum_boundary_facts_medium_or_high"], 4)
        self.assertEqual(rules["summarize_threshold"]["minimum_prescreen_facts_answered_or_unknown"], 3)
        self.assertEqual(rules["summarize_threshold"]["forbidden_answer_statuses"], ["needs_free_text", "invalid"])
        self.assertIn("three_or_more_required_boundary_facts_unknown_after_retry", rules["stop_conditions"])
        self.assertIn("two_or_more_core_fields_unknown", rules["stop_conditions"])
        self.assertIn("business_goal_is_only_make_it_automatic", rules["stop_conditions"])
        self.assertIn("high_confidence_pre_screen_risk_requires_prework", rules["stop_conditions"])
        self.assertEqual(rules["next_actions"]["ready"], "summarize_and_confirm")
        self.assertEqual(rules["next_actions"]["confirmed"], "enter_next_module")
        self.assertEqual(rules["next_actions"]["insufficient"], "stop_with_gap_report")
        self.assertEqual(rules["next_actions"]["prework_required"], "stop_with_prework_recommendation")

    def test_trigger_policy_never_concludes_from_initial_request(self):
        rules = load_json("agent_modules/requirement_clarification/rules/trigger-policy.json")

        self.assertEqual(rules["trigger_levels"][0]["name"], "weak_keyword_trigger")
        self.assertTrue(rules["global_rules"]["never_conclude_from_initial_request_only"])
        self.assertIn("rule_clarity", rules["fixed_prescreen_dimensions"])
        self.assertIn("result_verifiability", rules["fixed_prescreen_dimensions"])
        self.assertTrue(rules["global_rules"]["weak_signals_create_candidate_risks_only"])
        self.assertTrue(rules["global_rules"]["field_answer_triggers_are_more_reliable_than_initial_keywords"])
        self.assertTrue(rules["global_rules"]["fixed_prescreen_questions_are_required_before_completion"])

    def test_prompt_rules_forbid_execution_step_drilling(self):
        rules = (ROOT / "agent_modules/requirement_clarification/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Do not ask for exact click paths", rules)
        self.assertIn("Do not decide final RPA feasibility", rules)
        self.assertIn("# Requirement Clarification Prompt Rules", rules)
        self.assertIn("## Do", rules)
        self.assertIn("## Do Not", rules)

    def test_negative_example_schema_requires_trigger_policy(self):
        schema = load_json("agent_modules/requirement_clarification/schemas/negative-example.schema.json")
        props = schema["properties"]
        trigger_policy = props["trigger_policy"]

        self.assertEqual(schema["title"], "NegativeExample")
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("trigger_policy", schema["required"])
        self.assertIn("case_id", schema["required"])
        self.assertIn("module_2_action", schema["required"])
        self.assertEqual(props["module_2_action"]["const"], "flag_rpa_fit_risk")
        self.assertGreaterEqual(props["options"]["minItems"], 5)
        self.assertIn("trigger_policy", props)
        self.assertIn("weak_signals", trigger_policy["required"])
        self.assertIn("trigger_from_fields", trigger_policy["required"])
        self.assertIn("confirmation_required", trigger_policy["required"])
        self.assertIn("never_conclude_from_initial_request_only", trigger_policy["required"])

    def test_negative_examples_v1_has_eight_approved_cases(self):
        library = load_json("agent_modules/requirement_clarification/materials/negative-examples.v1.json")
        examples = library["examples"]
        case_ids = {example["case_id"] for example in examples}

        self.assertEqual(library["version"], "v1")
        self.assertEqual(len(examples), 8)
        self.assertIn("semantic-material-matching", case_ids)
        self.assertIn("missing-stable-business-rules", case_ids)
        self.assertIn("frequent-strong-verification", case_ids)

        for example in examples:
            self.assertEqual(example["module_2_action"], "flag_rpa_fit_risk")
            self.assertIn("trigger_policy", example)
            self.assertTrue(example["trigger_policy"]["confirmation_required"])
            self.assertTrue(example["trigger_policy"]["never_conclude_from_initial_request_only"])

    def test_readme_lists_module_2_artifacts(self):
        text = (ROOT / "agent_modules/requirement_clarification/README.md").read_text(encoding="utf-8")

        expected_paths = [
            "schemas/clarification-result.schema.json",
            "schemas/negative-example.schema.json",
            "materials/negative-examples.v1.json",
            "rules/completion-rules.json",
            "rules/trigger-policy.json",
            "rules/prompt-rules.md",
            "fixtures/semantic-risk-prescreen.json",
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
