import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DOC = ROOT / "agent_platform_package/testing/stability_regression_scenarios.md"
CHECKLIST = ROOT / "agent_platform_package/testing/platform_test_checklist.md"

SCENARIOS = [
    "ecommerce_daily_report",
    "inventory_monitor",
    "email_sorting",
    "logistics_interception",
    "material_synonym_judgment",
    "captcha_heavy_platform_collection",
]

REQUIRED_CHECKPOINTS = [
    "question_behavior",
    "requirement_memory_updates",
    "gate_state",
    "rpa_boundary",
    "report_sections",
    "source_label_expectations",
]


class StabilityRegressionContractTests(unittest.TestCase):
    def test_stability_regression_scenarios_document_exists(self):
        self.assertTrue(SCENARIO_DOC.exists())

    def test_stability_regression_document_covers_core_scenarios(self):
        text = SCENARIO_DOC.read_text(encoding="utf-8")

        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                self.assertIn(scenario, text)

    def test_each_scenario_defines_required_stability_checkpoints(self):
        text = SCENARIO_DOC.read_text(encoding="utf-8")

        for scenario in SCENARIOS:
            scenario_start = text.index(f"## {scenario}")
            next_start = text.find("\n## ", scenario_start + 1)
            block = text[scenario_start:] if next_start == -1 else text[scenario_start:next_start]

            for checkpoint in REQUIRED_CHECKPOINTS:
                with self.subTest(scenario=scenario, checkpoint=checkpoint):
                    self.assertIn(checkpoint, block)

    def test_platform_checklist_mentions_memory_driven_stability_regression(self):
        text = CHECKLIST.read_text(encoding="utf-8")

        self.assertIn("Memory-driven stability regression", text)
        self.assertIn("stability_regression_scenarios.md", text)
        self.assertIn("requirement memory", text)
        self.assertIn("fixed report sections", text)


if __name__ == "__main__":
    unittest.main()
