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
        self.assertIn(
            "Metric-to-template mapping must be confirmed before normalization.",
            " ".join(fixture["cross_step_dependencies"]),
        )

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
        self.assertIn("只能返回一个顶层 JSON wrapper", text)
        self.assertIn("yingdao_flow_chain_templates_v3.md", text)
        self.assertIn("yingdao_scenario_building_guide.md", text)
        self.assertIn("Module 4", text)
        self.assertIn("required vs recommended vs optional", text)
        self.assertIn("unresolved assumptions", text)
        self.assertNotIn("保持 `interaction_state`、`answer_batch`、`clarification_result`、`rpa_boundary_result` 四类结构", text)
        self.assertNotIn("鐗╂枡", text)
        self.assertNotIn("鍏堢粺", text)
        self.assertNotIn("鑷姩", text)
        self.assertNotIn("椋炰功", text)

    def test_module_4_expected_output_guidance_mentions_dependencies_validation_and_followups(self):
        text = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(encoding="utf-8")

        self.assertIn("cross-step dependencies", text)
        self.assertIn("prework_dependencies", text)
        self.assertIn("validation points", text)
        self.assertIn("open_questions", text)
        self.assertIn("mandatory vs optional upstream items", text)


if __name__ == "__main__":
    unittest.main()
