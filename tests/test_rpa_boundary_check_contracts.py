import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class RpaBoundaryCheckContractTests(unittest.TestCase):
    def test_boundary_result_schema_defines_decision_dimensions(self):
        schema = load_json("agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json")
        props = schema["properties"]
        decision_props = props["decision"]["properties"]
        dimension_props = props["dimension_results"]["properties"]

        self.assertEqual(schema["title"], "RpaBoundaryResult")
        self.assertEqual(props["module"]["const"], "module_3_rpa_boundary_check")
        self.assertEqual(
            decision_props["classification"]["enum"],
            ["suitable", "conditionally_suitable", "not_ready", "not_suitable_for_direct_rpa"],
        )
        self.assertEqual(decision_props["confidence"]["enum"], ["high", "medium_high", "medium", "low"])
        self.assertEqual(
            list(dimension_props.keys()),
            [
                "scenario_match",
                "instruction_support",
                "input_readiness",
                "rule_readiness",
                "platform_operability",
                "result_verifiability",
                "exception_containment",
            ],
        )

    def test_schema_preserves_controlled_risk_types_and_capability_notes(self):
        schema = load_json("agent_modules/rpa_boundary_check/schemas/rpa-boundary-result.schema.json")

        self.assertEqual(
            schema["$defs"]["risk_type"]["enum"],
            [
                "semantic_judgment",
                "missing_rules",
                "unstable_input",
                "unverifiable_result",
                "unstable_platform",
                "human_verification",
                "open_ended_exceptions",
                "low_roi",
            ],
        )
        self.assertEqual(
            schema["$defs"]["capability_note"]["enum"],
            [
                "requires_api_or_data_export",
                "requires_stable_login",
                "requires_field_mapping",
                "requires_template_standardization",
                "requires_manual_review_queue",
                "requires_result_log",
            ],
        )

    def test_decision_rules_encode_conditional_admissibility(self):
        rules = load_json("agent_modules/rpa_boundary_check/rules/decision-rules.json")

        self.assertEqual(rules["module"], "module_3_rpa_boundary_check")
        self.assertEqual(rules["design_choice"], "conditional_admissibility")
        self.assertEqual(
            rules["dimension_order"],
            [
                "scenario_match",
                "instruction_support",
                "input_readiness",
                "rule_readiness",
                "platform_operability",
                "result_verifiability",
                "exception_containment",
            ],
        )
        self.assertIn("instruction_match_is_evidence_not_decision", rules["global_rules"])
        self.assertIn("missing_required_module_2_facts_returns_not_ready", rules["global_rules"])
        self.assertEqual(rules["classification_rules"]["conditionally_suitable"]["default_for_real_customer_requirements"], True)

    def test_material_retrieval_policy_orders_yingdao_sources(self):
        policy = load_json("agent_modules/rpa_boundary_check/rules/material-retrieval-policy.json")
        steps = policy["retrieval_order"]
        names = [step["source"] for step in steps]

        self.assertEqual(names[0], "yingdao_instruction_search_keywords.xlsx")
        self.assertEqual(names[1], "yingdao_scenario_building_guide.md")
        self.assertEqual(names[2], "yingdao_flow_chain_templates_v3.md")
        self.assertEqual(names[-1], "agent_answer_templates.md")
        self.assertEqual(steps[-1]["use"], "answer_shape_only")

    def test_source_material_manifest_classifies_seven_approved_files(self):
        manifest = load_json("agent_modules/rpa_boundary_check/materials/source-material-manifest.json")
        sources = manifest["sources"]
        source_names = {source["source"] for source in sources}

        self.assertEqual(manifest["version"], "v1")
        self.assertEqual(len(sources), 7)
        self.assertIn("yingdao_instruction_capability_library_cleaned.xlsx", source_names)
        self.assertIn("yingdao_core_instruction_library.xlsx", source_names)
        self.assertIn("yingdao_instruction_search_keywords.xlsx", source_names)
        self.assertIn("requirement_to_instruction_mapping.xlsx", source_names)
        self.assertIn("yingdao_flow_chain_templates_v3.md", source_names)
        self.assertIn("yingdao_scenario_building_guide.md", source_names)
        self.assertIn("agent_answer_templates.md", source_names)
        self.assertNotIn("yingdao_flow_chain_templates_v3_duplicate.md", source_names)

    def test_prompt_rules_keep_module_3_out_of_process_breakdown(self):
        text = (ROOT / "agent_modules/rpa_boundary_check/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Do not ask for exact click paths", text)
        self.assertIn("Do not produce the happy-path process breakdown", text)
        self.assertIn("Instruction existence is evidence, not a decision", text)
        self.assertIn("Ask capability-critical confirmation questions only", text)

    def test_email_sorting_fixture_is_conditionally_suitable(self):
        fixture = load_json("agent_modules/rpa_boundary_check/fixtures/email-sorting-boundary-result.json")

        self.assertEqual(fixture["module"], "module_3_rpa_boundary_check")
        self.assertEqual(fixture["decision"]["classification"], "conditionally_suitable")
        self.assertIn("semantic_judgment", [risk["risk_type"] for risk in fixture["risks"]])
        self.assertIn("requires_manual_review_queue", fixture["capability_notes"])
        self.assertEqual(fixture["next_stage_recommendation"], "process_breakdown")

    def test_ecommerce_fixture_requires_mapping_and_verification_prework(self):
        fixture = load_json("agent_modules/rpa_boundary_check/fixtures/ecommerce-daily-report-boundary-result.json")

        self.assertEqual(fixture["decision"]["classification"], "conditionally_suitable")
        self.assertIn("requires_field_mapping", fixture["capability_notes"])
        self.assertIn("requires_result_log", fixture["capability_notes"])
        self.assertEqual(fixture["dimension_results"]["result_verifiability"]["status"], "conditional")
        self.assertIn("平台-店铺清单", " ".join(fixture["required_prework"]))

    def test_readme_lists_module_3_artifacts(self):
        text = (ROOT / "agent_modules/rpa_boundary_check/README.md").read_text(encoding="utf-8")

        expected_paths = [
            "schemas/rpa-boundary-result.schema.json",
            "rules/decision-rules.json",
            "rules/material-retrieval-policy.json",
            "rules/prompt-rules.md",
            "materials/source-material-manifest.json",
            "fixtures/email-sorting-boundary-result.json",
            "fixtures/ecommerce-daily-report-boundary-result.json",
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
