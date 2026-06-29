import json
import copy
import re
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

SOLUTION_PACKAGE_FIXTURE_PATHS = [
    "agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json",
    "agent_modules/solution_packaging/fixtures/email-sorting-solution-package.json",
    "agent_modules/solution_packaging/fixtures/not-recommended-semantic-risk-solution-package.json",
    "agent_modules/solution_packaging/fixtures/blocked-gap-report-solution-package.json",
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

PROHIBITED_IMPLEMENTATION_DETAIL_PATTERNS = (
    re.compile(r"\bcss\s+selector\b", re.IGNORECASE),
    re.compile(r"\bselector\b", re.IGNORECASE),
    re.compile(r"\bxpath\b", re.IGNORECASE),
    re.compile(r"\bclick\s+path\b", re.IGNORECASE),
    re.compile(r"\bwait\s+\d+\s+seconds?\b", re.IGNORECASE),
    re.compile(r"\bretry\s+\d+\s+times?\b", re.IGNORECASE),
    re.compile(r"\bretry\s+count\s*=", re.IGNORECASE),
    re.compile(r"点击路径"),
    re.compile(r"选择器"),
    re.compile(r"等待\s*\d+\s*秒"),
    re.compile(r"重试\s*\d+\s*次"),
    re.compile(r"指令参数"),
)

INVENTED_FACT_MARKER = "UNSOURCED_FACT"


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
        source_modules = props["source_modules"]

        self.assertEqual(schema["title"], "SolutionPackageResult")
        self.assertEqual(props["module"]["const"], "module_6_solution_packaging")
        self.assertIn("module_status", schema["required"])
        self.assertIn("developer_alignment_status", schema["required"])
        self.assertIn("module_1_interaction_schema", source_modules["required"])
        self.assertIn("module_1_interaction_schema", source_modules["properties"])
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

        for path in SOLUTION_PACKAGE_FIXTURE_PATHS:
            with self.subTest(path=path):
                jsonschema.validate(load_json(path), schema)

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_schema_rejects_ready_for_development_with_high_blocking_missing_items(self):
        schema = load_json("agent_modules/solution_packaging/schemas/solution-package-result.schema.json")
        fixture = copy.deepcopy(load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json"))

        fixture["developer_alignment_status"] = "ready_for_development"
        fixture["next_stage_recommendation"] = "implementation_planning"

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(fixture, schema)

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_schema_rejects_inferred_recommendations_marked_as_development_ready(self):
        schema = load_json("agent_modules/solution_packaging/schemas/solution-package-result.schema.json")
        base_fixture = load_json("agent_modules/solution_packaging/fixtures/ecommerce-daily-report-solution-package.json")
        invalid_cases = [
            ("requires_confirmation_false", {"requires_confirmation": False}),
            ("can_be_used_for_development_true", {"can_be_used_for_development": True}),
        ]

        for case_name, override in invalid_cases:
            with self.subTest(case=case_name):
                fixture = copy.deepcopy(base_fixture)
                fixture["fact_base"]["inferred_recommendations"][0].update(override)

                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(fixture, schema)

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

    def test_customer_and_developer_outputs_use_same_source_facts(self):
        for path in SOLUTION_PACKAGE_FIXTURE_PATHS:
            with self.subTest(path=path):
                fixture = load_json(path)
                fact_ids = {fact["fact_id"] for fact in fixture["fact_base"]["confirmed_facts"]}
                customer_refs = set(fixture["customer_view_model"]["referenced_fact_ids"])
                developer_refs = set(fixture["developer_view_model"]["referenced_fact_ids"])

                self.assertTrue(customer_refs.issubset(fact_ids))
                self.assertTrue(developer_refs.issubset(fact_ids))
                self.assertNotIn(INVENTED_FACT_MARKER, fixture["render_outputs"]["customer_html"])
                self.assertNotIn(INVENTED_FACT_MARKER, fixture["render_outputs"]["developer_html"])
                self.assertIn(
                    fixture["customer_view_model"]["headline"],
                    fixture["render_outputs"]["customer_html"],
                )
                self.assertIn(
                    fixture["developer_view_model"]["implementation_status"],
                    fixture["render_outputs"]["developer_html"],
                )

                if fact_ids:
                    self.assertGreater(len(customer_refs), 0)
                    self.assertGreater(len(developer_refs), 0)

    def test_render_outputs_are_html_strings(self):
        for path in SOLUTION_PACKAGE_FIXTURE_PATHS:
            fixture = load_json(path)
            for html_key in ("customer_html", "developer_html"):
                with self.subTest(path=path, html_key=html_key):
                    html = fixture["render_outputs"][html_key].lower()

                    self.assertIn("<section", html)
                    self.assertIn("card", html)

    def test_solution_packages_do_not_expose_prohibited_implementation_details(self):
        for path in SOLUTION_PACKAGE_FIXTURE_PATHS:
            fixture = load_json(path)
            for value in iter_strings(fixture):
                for pattern in PROHIBITED_IMPLEMENTATION_DETAIL_PATTERNS:
                    with self.subTest(path=path, pattern=pattern.pattern, value=value):
                        self.assertIsNone(pattern.search(value))

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
