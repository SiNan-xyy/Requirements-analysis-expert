import json
import re
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


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


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
        self.assertEqual(props["process_breakdown_blocker"]["type"], "string")
        self.assertEqual(props["process_breakdown_blocker"]["minLength"], 1)
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
            props["source_process_steps"]["items"]["pattern"],
            "^S[0-9]{2}$",
        )
        self.assertEqual(
            list(flow_props.keys()),
            ["step_id", "step_name", "source_exception_notes", "exception_cards"],
        )
        self.assertEqual(flow_props["step_id"]["pattern"], "^S[0-9]{2}$")
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
        self.assertEqual(card_props["detection_basis"]["minItems"], 1)
        self.assertEqual(card_props["candidate_yingdao_capabilities"]["minItems"], 1)
        self.assertEqual(card_props["related_upstream_risks"]["minItems"], 1)
        related_risk_def = schema["$defs"]["related_upstream_risk"]["oneOf"]
        self.assertEqual(len(related_risk_def), 2)
        self.assertEqual(related_risk_def[0]["$ref"], "#/$defs/module_3_risk_type")
        self.assertEqual(related_risk_def[1]["$ref"], "#/$defs/module_3_capability_note")
        self.assertEqual(
            schema["$defs"]["module_3_capability_note"]["pattern"],
            "^requires_[a-z0-9_]+$",
        )
        completed_rule = next(
            rule
            for rule in schema["allOf"]
            if rule["if"]["properties"]["status"]["const"] == "completed"
        )
        blocked_rule = next(
            rule
            for rule in schema["allOf"]
            if rule["if"]["properties"]["status"]["const"] == "blocked_by_process_breakdown"
        )
        self.assertEqual(
            completed_rule["then"]["properties"]["next_stage_recommendation"]["const"],
            "solution_packaging",
        )
        self.assertEqual(completed_rule["then"]["properties"]["exception_flows"]["minItems"], 1)
        self.assertIn("process_breakdown_blocker", blocked_rule["then"]["required"])
        self.assertEqual(blocked_rule["then"]["properties"]["exception_flows"]["maxItems"], 0)
        self.assertEqual(
            blocked_rule["then"]["properties"]["next_stage_recommendation"]["enum"],
            [
                "return_to_process_breakdown",
                "return_to_rpa_boundary_check",
                "return_to_requirement_clarification",
                "stop_with_blocker",
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
        self.assertIn(
            "include candidate Yingdao capability families for each exception card",
            rules["generation_requirements"],
        )
        self.assertIn(
            "when status is completed route to solution_packaging",
            rules["generation_requirements"],
        )
        self.assertIn(
            "when status is blocked_by_process_breakdown require process_breakdown_blocker, keep exception_flows empty, and route to an upstream action",
            rules["generation_requirements"],
        )
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
        self.assertIn("candidate Yingdao capability families", text)
        self.assertIn("solution_packaging", text)
        self.assertIn("process_breakdown_blocker", text)
        self.assertIn("upstream completion or clarification action", text)
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

    def test_email_fixture_covers_module_4_focus_steps(self):
        process_breakdown = load_json(
            "agent_modules/process_breakdown/fixtures/email-sorting-process-breakdown.json"
        )
        fixture = load_json("agent_modules/exception_design/fixtures/email-sorting-exception-design.json")

        expected_focus_steps = process_breakdown["handoff_to_exception_design"]["focus_steps"]

        self.assertEqual(fixture["source_process_steps"], expected_focus_steps)
        self.assertEqual(
            [flow["step_id"] for flow in fixture["exception_flows"]],
            expected_focus_steps,
        )

    def test_email_fixture_expands_signal_extraction_and_low_confidence_exceptions(self):
        fixture = load_json("agent_modules/exception_design/fixtures/email-sorting-exception-design.json")

        self.assertEqual(fixture["module"], "module_5_exception_design")
        self.assertEqual(fixture["next_stage_recommendation"], "solution_packaging")
        self.assertIn("S03", fixture["source_process_steps"])
        self.assertIn("S04", fixture["source_process_steps"])

        signal_flow = next(flow for flow in fixture["exception_flows"] if flow["step_id"] == "S03")
        self.assertEqual(
            signal_flow["source_exception_notes"],
            ["empty body", "unsupported format", "missing subject"],
        )
        self.assertEqual(len(signal_flow["exception_cards"]), 3)
        empty_body_card = next(
            card for card in signal_flow["exception_cards"] if card["exception_id"] == "E-S03-01"
        )
        self.assertEqual(empty_body_card["exception_type"], "source_field_missing")
        self.assertEqual(empty_body_card["severity"], "needs_manual_review")
        self.assertIn("manual review queue", empty_body_card["candidate_yingdao_capabilities"])
        self.assertIn("semantic_judgment", empty_body_card["related_upstream_risks"])
        unsupported_format_card = next(
            card for card in signal_flow["exception_cards"] if card["exception_id"] == "E-S03-02"
        )
        self.assertEqual(unsupported_format_card["exception_type"], "file_format_unreadable")
        self.assertIn("data extraction", unsupported_format_card["candidate_yingdao_capabilities"])
        self.assertIn("unstable_input", unsupported_format_card["related_upstream_risks"])
        missing_subject_card = next(
            card for card in signal_flow["exception_cards"] if card["exception_id"] == "E-S03-03"
        )
        self.assertEqual(missing_subject_card["exception_type"], "source_field_missing")
        self.assertEqual(missing_subject_card["continue_policy"], "continue_other_items")
        self.assertIn("requires_manual_review_queue", missing_subject_card["related_upstream_risks"])

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

    def test_email_fixture_related_upstream_risks_match_module_3_email_context(self):
        boundary_result = load_json(
            "agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json"
        )
        fixture = load_json("agent_modules/exception_design/fixtures/email-sorting-exception-design.json")

        allowed_risk_types = {risk["risk_type"] for risk in boundary_result["risks"]}
        allowed_capability_notes = set(boundary_result["capability_notes"])
        allowed_related_values = allowed_risk_types | allowed_capability_notes
        used_related_values = set()

        for flow in fixture["exception_flows"]:
            for card in flow["exception_cards"]:
                for related_value in card["related_upstream_risks"]:
                    used_related_values.add(related_value)
                    with self.subTest(
                        exception_id=card["exception_id"],
                        related_value=related_value,
                    ):
                        self.assertIn(related_value, allowed_related_values)

        self.assertTrue(used_related_values & allowed_risk_types)
        self.assertTrue(used_related_values & allowed_capability_notes)

    def test_blocked_result_requires_process_breakdown_blocker_and_upstream_routing(self):
        schema = load_json("agent_modules/exception_design/schemas/exception-design-result.schema.json")

        blocked_result = {
            "module": "module_5_exception_design",
            "status": "blocked_by_process_breakdown",
            "process_breakdown_blocker": "Module 4 returned incomplete email classification dependencies and directed follow-up before exception design can start.",
            "source_process_steps": ["S03"],
            "exception_depth": "semi_implementation_exception_flows",
            "exception_flows": [],
            "global_exception_policies": [],
            "manual_review_policy": {
                "required": False,
                "review_queue_name": "",
                "review_record_fields": [],
            },
            "logging_policy": {
                "required": False,
                "minimum_record_fields": [],
            },
            "open_questions": [],
            "next_stage_recommendation": "return_to_process_breakdown",
        }

        if jsonschema is None:
            blocked_rule = next(
                rule
                for rule in schema["allOf"]
                if rule["if"]["properties"]["status"]["const"] == "blocked_by_process_breakdown"
            )
            self.assertIn("process_breakdown_blocker", blocked_rule["then"]["required"])
            self.assertNotIn(
                "solution_packaging",
                blocked_rule["then"]["properties"]["next_stage_recommendation"]["enum"],
            )
            return

        jsonschema.validate(instance=blocked_result, schema=schema)

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                instance={
                    **blocked_result,
                    "process_breakdown_blocker": "",
                },
                schema=schema,
            )

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                instance={
                    key: value
                    for key, value in blocked_result.items()
                    if key != "process_breakdown_blocker"
                },
                schema=schema,
            )

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                instance={
                    **blocked_result,
                    "exception_flows": [
                        {
                            "step_id": "S03",
                            "step_name": "Extract classification signals",
                            "source_exception_notes": ["missing subject"],
                            "exception_cards": [
                                {
                                    "exception_id": "E-S03-01",
                                    "exception_type": "source_field_missing",
                                    "severity": "needs_manual_review",
                                    "trigger_signal": "Missing subject blocks safe classification.",
                                    "detection_basis": ["email subject presence"],
                                    "handling_strategy": "Hold the item for review.",
                                    "continue_policy": "wait_for_manual_review",
                                    "candidate_yingdao_capabilities": ["condition judgment"],
                                    "human_intervention": "required",
                                    "record_fields": ["message_id"],
                                    "related_upstream_risks": ["requires_manual_review_queue"],
                                }
                            ],
                        }
                    ],
                },
                schema=schema,
            )

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                instance={
                    **blocked_result,
                    "next_stage_recommendation": "solution_packaging",
                },
                schema=schema,
            )

    def test_completed_result_requires_exception_flows_and_solution_packaging(self):
        schema = load_json("agent_modules/exception_design/schemas/exception-design-result.schema.json")

        completed_result = {
            "module": "module_5_exception_design",
            "status": "completed",
            "source_process_steps": ["S03"],
            "exception_depth": "semi_implementation_exception_flows",
            "exception_flows": [
                {
                    "step_id": "S03",
                    "step_name": "Extract classification signals",
                    "source_exception_notes": ["missing subject"],
                    "exception_cards": [
                        {
                            "exception_id": "E-S03-01",
                            "exception_type": "source_field_missing",
                            "severity": "needs_manual_review",
                            "trigger_signal": "Missing subject blocks safe classification.",
                            "detection_basis": ["email subject presence"],
                            "handling_strategy": "Hold the item for review.",
                            "continue_policy": "wait_for_manual_review",
                            "candidate_yingdao_capabilities": ["condition judgment"],
                            "human_intervention": "required",
                            "record_fields": ["message_id"],
                            "related_upstream_risks": ["requires_manual_review_queue"],
                        }
                    ],
                }
            ],
            "global_exception_policies": [],
            "manual_review_policy": {
                "required": True,
                "review_queue_name": "email_pending_manual_confirmation",
                "review_record_fields": ["message_id"],
            },
            "logging_policy": {
                "required": True,
                "minimum_record_fields": ["run_id"],
            },
            "open_questions": [],
            "next_stage_recommendation": "solution_packaging",
        }

        if jsonschema is None:
            completed_rule = next(
                rule
                for rule in schema["allOf"]
                if rule["if"]["properties"]["status"]["const"] == "completed"
            )
            self.assertEqual(
                completed_rule["then"]["properties"]["next_stage_recommendation"]["const"],
                "solution_packaging",
            )
            self.assertEqual(completed_rule["then"]["properties"]["exception_flows"]["minItems"], 1)
            return

        jsonschema.validate(instance=completed_result, schema=schema)

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                instance={
                    **completed_result,
                    "exception_flows": [],
                },
                schema=schema,
            )

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                instance={
                    **completed_result,
                    "status": "completed",
                    "next_stage_recommendation": "return_to_process_breakdown",
                },
                schema=schema,
            )

    def test_platform_package_guidance_mentions_module_5_wrapper_and_output_contract(self):
        prompt_text = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(
            encoding="utf-8"
        )
        expected_output_text = (
            ROOT / "agent_platform_package/testing/expected_outputs.md"
        ).read_text(encoding="utf-8")

        self.assertIn("exception_design_result", prompt_text)
        self.assertIn(
            "Module 5 must produce one `exception_design_result` object.",
            prompt_text,
        )
        self.assertIn(
            "Module 5 must produce semi-implementation-level exception flows by process step.",
            prompt_text,
        )
        self.assertIn(
            "Module 5 must start from module 4 focus steps and exception notes, and reference module 3 risks and capability notes as supporting evidence.",
            prompt_text,
        )
        self.assertIn("single top-level JSON wrapper", expected_output_text)
        self.assertIn("## Module 5 Expected Output", expected_output_text)
        self.assertIn("semi_implementation_exception_flows", expected_output_text)
        self.assertIn("global_exception_policies", expected_output_text)
        self.assertIn("manual_review_policy", expected_output_text)
        self.assertIn("logging_policy", expected_output_text)
        self.assertIn("solution_packaging", expected_output_text)

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

    def test_exception_design_fixtures_remain_semi_implementation_level(self):
        fixtures = [
            load_json("agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json"),
            load_json("agent_modules/exception_design/fixtures/email-sorting-exception-design.json"),
        ]
        forbidden_terms = (
            "selector",
            "xpath",
            "click path",
            "instruction parameter",
            "solution blueprint",
            "html",
        )
        forbidden_patterns = (
            re.compile(r"\bwait(?:\s+\d+)?\b", re.IGNORECASE),
            re.compile(r"\b\d+\s+(?:second|seconds|minute|minutes)\b", re.IGNORECASE),
            re.compile(r"\bretry\s+\d+\b", re.IGNORECASE),
            re.compile(r"\b\d+\s+times\b", re.IGNORECASE),
        )

        for fixture in fixtures:
            for text in iter_strings(fixture):
                lowered = text.lower()
                for term in forbidden_terms:
                    with self.subTest(term=term, text=text):
                        self.assertNotIn(term, lowered)
                for pattern in forbidden_patterns:
                    with self.subTest(pattern=pattern.pattern, text=text):
                        self.assertIsNone(pattern.search(text))

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

    def test_module_5_assets_do_not_contain_common_mojibake_fragments(self):
        for relative_path in MODULE_5_READABILITY_PATHS:
            self.assert_has_no_common_mojibake(relative_path)


if __name__ == "__main__":
    unittest.main()
