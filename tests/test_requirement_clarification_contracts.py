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
        self.assertEqual(fixture["rpa_fit_prescreen"]["rule_clarity"], "medium")
        self.assertIn("物流拦截", fixture["stage_summary"])


if __name__ == "__main__":
    unittest.main()
