import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency in local env
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]
COMMON_MOJIBAKE_FRAGMENTS = (
    "褰卞",
    "鍙ｅ緞",
    "閼",
    "閻",
    "鐠",
    "妞",
    "鏈",
    "閺",
    "纭",
    "",
    "",
    "",
    "鏃ユ",
    "骞冲",
    "鑵捐",
)
MODULE_4_READABILITY_PATHS = [
    "agent_modules/process_breakdown/fixtures/ecommerce-daily-report-process-breakdown.json",
    "agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json",
    "agent_modules/process_breakdown/README.md",
    "agent_modules/process_breakdown/rules/prompt-rules.md",
]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class ProcessBreakdownContractTests(unittest.TestCase):
    def assert_has_no_common_mojibake(self, relative_path: str) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")

        for fragment in COMMON_MOJIBAKE_FRAGMENTS:
            with self.subTest(path=relative_path, fragment=fragment):
                self.assertNotIn(fragment, text)

    def test_process_breakdown_schema_defines_cards_handoff_and_context_fields(self):
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
        self.assertEqual(props["assumptions"]["type"], "array")
        self.assertEqual(props["assumptions"]["items"]["type"], "string")
        self.assertEqual(props["validation_points"]["type"], "array")
        self.assertEqual(props["validation_points"]["items"]["type"], "string")
        self.assertIn("assumptions", schema["required"])
        self.assertIn("validation_points", schema["required"])
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
        self.assertIn("assumptions", rules["required_result_fields"])
        self.assertIn("validation_points", rules["required_result_fields"])
        self.assertTrue(
            any("assumptions" in item for item in rules["generation_requirements"])
        )
        self.assertTrue(
            any("validation points" in item for item in rules["generation_requirements"])
        )
        self.assertTrue(
            any("required recommended and optional" in item for item in rules["generation_requirements"])
        )

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
        prepare_card = fixture["process_cards"][0]
        self.assertIn("web automation", collect_card["candidate_yingdao_capabilities"])
        self.assertTrue(collect_card["handoff_to_exception_design"])
        self.assertIn("login failure", collect_card["exception_design_notes"])
        self.assertIn("report date definition", prepare_card["input"])
        self.assertIn(
            "Confirm the platform-store list is fixed and complete.",
            prepare_card["prework_dependencies"],
        )
        self.assertIn(
            "Metric-to-template mapping must be confirmed before normalization.",
            " ".join(fixture["cross_step_dependencies"]),
        )
        self.assertGreaterEqual(len(fixture["assumptions"]), 2)
        self.assertIn("Tencent Docs template structure stays stable", " ".join(fixture["assumptions"]))
        self.assertGreaterEqual(len(fixture["validation_points"]), 2)
        self.assertIn("date scope matches the business definition", " ".join(fixture["validation_points"]))

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
        self.assertGreaterEqual(len(fixture["assumptions"]), 2)
        self.assertIn("Manual review staff can clear low-confidence items", " ".join(fixture["assumptions"]))
        self.assertGreaterEqual(len(fixture["validation_points"]), 2)
        self.assertIn("low-confidence routing threshold", " ".join(fixture["validation_points"]))

    def test_process_breakdown_fixtures_validate_against_schema_when_validator_available(self):
        if jsonschema is None:
            self.skipTest("jsonschema is not installed in this environment")

        schema = load_json("agent_modules/process_breakdown/schemas/process-breakdown-result.schema.json")
        fixtures = [
            "agent_modules/process_breakdown/fixtures/ecommerce-daily-report-process-breakdown.json",
            "agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json",
        ]

        for relative_path in fixtures:
            with self.subTest(path=relative_path):
                jsonschema.validate(
                    instance=load_json(relative_path),
                    schema=schema,
                )

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
        self.assertIn("yingdao_flow_chain_templates_v3.md", text)
        self.assertIn("yingdao_scenario_building_guide.md", text)
        self.assertIn("Module 4", text)
        self.assertIn("required vs recommended vs optional", text)
        self.assertIn("unresolved assumptions", text)

    def test_module_4_expected_output_guidance_mentions_dependencies_validation_and_followups(self):
        text = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(encoding="utf-8")

        self.assertIn("cross-step dependencies", text)
        self.assertIn("prework_dependencies", text)
        self.assertIn("validation points", text)
        self.assertIn("open_questions", text)
        self.assertIn("mandatory vs optional guidance", text)
        self.assertIn("required/recommended/optional", text)

    def test_module_4_assets_do_not_contain_common_mojibake_fragments(self):
        for relative_path in MODULE_4_READABILITY_PATHS:
            self.assert_has_no_common_mojibake(relative_path)


if __name__ == "__main__":
    unittest.main()
