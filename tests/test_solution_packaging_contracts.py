import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency in local env
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]

MODULE_6_READABILITY_PATHS = [
    "agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json",
    "agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json",
    "agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json",
    "agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json",
    "agent_modules/solution_packaging/README.md",
    "agent_modules/solution_packaging/rules/prompt-rules.md",
]

COMMON_MOJIBAKE_FRAGMENTS = (
    "濡ょ姷鍋?",
    "鐟滄澘宕?",
    "闁告瑱绲?",
    "闂?",
    "闁?",
    "婵?",
    "缁?",
    "椤?",
)

PROHIBITED_HTML_TERMS = (
    "selector",
    "xpath",
    "css selector",
    "click path",
    "wait 3 seconds",
    "retry count =",
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


class SolutionPackagingContractTests(unittest.TestCase):
    def assert_has_no_common_mojibake(self, relative_path: str) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")

        for fragment in COMMON_MOJIBAKE_FRAGMENTS:
            with self.subTest(path=relative_path, fragment=fragment):
                self.assertNotIn(fragment, text)

    def test_solution_package_schema_defines_fact_layer_html_outputs_and_readiness_status(self):
        schema = load_json("agent_modules/solution_packaging/schemas/solution-package-result.schema.json")
        props = schema["properties"]
        fact_props = props["fact_base"]["properties"]

        self.assertEqual(schema["title"], "SolutionPackageResult")
        self.assertEqual(props["module"]["const"], "module_6_solution_packaging")
        self.assertIn("module_status", schema["required"])
        self.assertIn("developer_alignment_status", schema["required"])
        self.assertEqual(
            props["developer_alignment_status"]["enum"],
            ["ready_for_development", "needs_confirmation", "not_recommended", "blocked"],
        )
        self.assertIn("confirmed_facts", fact_props)
        self.assertIn("inferred_recommendations", fact_props)
        self.assertIn("missing_required_items", fact_props)
        self.assertIn("conflict_or_uncertainty", fact_props)
        self.assertIn("customer_view_model", props)
        self.assertIn("developer_view_model", props)
        self.assertIn("render_outputs", props)

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_all_solution_package_fixtures_validate_against_schema(self):
        schema = load_json("agent_modules/solution_packaging/schemas/solution-package-result.schema.json")
        fixture_paths = [
            "agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json",
            "agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json",
            "agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json",
            "agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json",
        ]

        for path in fixture_paths:
            with self.subTest(path=path):
                jsonschema.validate(load_json(path), schema)

    def test_ecommerce_daily_report_remains_needs_confirmation(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        missing_topics = {item["topic"] for item in fixture["fact_base"]["missing_required_items"]}

        self.assertEqual(fixture["developer_alignment_status"], "needs_confirmation")
        self.assertIn("field_mapping", missing_topics)
        self.assertIn("metric_definition", missing_topics)
        self.assertIn("date_definition", missing_topics)
        self.assertIn("result_validation_method", missing_topics)
        self.assertNotEqual(fixture["developer_alignment_status"], "ready_for_development")

    def test_email_sorting_keeps_semantic_risk_and_manual_review_visible(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json")
        risk_text = " ".join(iter_strings(fixture))

        self.assertEqual(fixture["developer_alignment_status"], "needs_confirmation")
        self.assertIn("semantic", risk_text.lower())
        self.assertIn("manual", risk_text.lower())
        self.assertIn("low-confidence", risk_text.lower())

    def test_not_recommended_package_does_not_look_like_implementation_plan(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json")
        developer_model = fixture["developer_view_model"]
        process_cards = developer_model["process_breakdown"]["process_cards"]

        self.assertEqual(fixture["developer_alignment_status"], "not_recommended")
        self.assertEqual(process_cards, [])
        self.assertIn("governance", " ".join(iter_strings(fixture)).lower())
        self.assertIn("reevaluation", " ".join(iter_strings(fixture)).lower())

    def test_blocked_package_is_gap_report_not_solution_report(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json")

        self.assertEqual(fixture["developer_alignment_status"], "blocked")
        self.assertEqual(fixture["module_status"], "blocked")
        self.assertGreater(len(fixture["fact_base"]["missing_required_items"]), 0)
        self.assertEqual(fixture["customer_view_model"]["report_type"], "gap_report")
        self.assertEqual(fixture["developer_view_model"]["report_type"], "gap_report")

    def test_inferred_recommendations_are_not_marked_as_development_facts(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")

        for item in fixture["fact_base"]["inferred_recommendations"]:
            with self.subTest(item=item["item_id"]):
                self.assertTrue(item["requires_confirmation"])
                self.assertFalse(item["can_be_used_for_development"])

    def test_customer_and_developer_html_use_same_fact_ids(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        fact_ids = {fact["fact_id"] for fact in fixture["fact_base"]["confirmed_facts"]}
        customer_refs = set(fixture["customer_view_model"]["referenced_fact_ids"])
        developer_refs = set(fixture["developer_view_model"]["referenced_fact_ids"])

        self.assertTrue(customer_refs.issubset(fact_ids))
        self.assertTrue(developer_refs.issubset(fact_ids))
        self.assertGreater(len(customer_refs), 0)
        self.assertGreater(len(developer_refs), 0)

    def test_render_outputs_are_html_strings_without_prohibited_implementation_details(self):
        fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        html = (
            fixture["render_outputs"]["customer_html"]
            + "\n"
            + fixture["render_outputs"]["developer_html"]
        ).lower()

        self.assertIn("<section", html)
        self.assertIn("card", html)
        for term in PROHIBITED_HTML_TERMS:
            with self.subTest(term=term):
                self.assertNotIn(term, html)

    def test_packaging_rules_define_status_fact_and_rendering_constraints(self):
        rules = load_json("agent_modules/solution_packaging/rules/packaging-rules.json")

        self.assertIn("status_rules", rules)
        self.assertIn("fact_layer_rules", rules)
        self.assertIn("rendering_rules", rules)
        self.assertIn("prohibited_content", rules)
        self.assertIn("manual_review_before_implementation", rules["next_stage_recommendations"])

    def test_prompt_and_platform_docs_include_module_6(self):
        system_prompt = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(encoding="utf-8")
        expected_outputs = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(encoding="utf-8")

        self.assertIn("Module 6: Solution Packaging", system_prompt)
        self.assertIn("solution_package_result", system_prompt)
        self.assertIn("Module 6 Expected Output", expected_outputs)
        self.assertIn("solution_package_result", expected_outputs)

    def test_module_6_files_have_readable_text(self):
        for path in MODULE_6_READABILITY_PATHS:
            with self.subTest(path=path):
                self.assert_has_no_common_mojibake(path)


if __name__ == "__main__":
    unittest.main()
