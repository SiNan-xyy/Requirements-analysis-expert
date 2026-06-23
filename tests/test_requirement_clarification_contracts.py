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
        self.assertEqual(fixture["boundary_facts"]["business_goal"]["value"], "自动完成物流拦截")
        self.assertEqual(fixture["boundary_facts"]["input_data"]["value"], ["物流单号"])
        self.assertEqual(fixture["rpa_fit_prescreen"]["rule_clarity"], "medium")
        self.assertIn("物流拦截", fixture["stage_summary"])
        self.assertIn("影刀商户后台", fixture["stage_summary"])
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


if __name__ == "__main__":
    unittest.main()
