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
    "楠炲啿",
    "濞村",
    "閼?",
    "閻?",
    "閸忓牏",
    "妞嬬偘鍔?",
    "闁?",
    "闁?",
    "闁?",
    "濡?",
    "鐎?",
    "閸欙絽绶?",
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
        fixture = load_json(
            "agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json"
        )

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
