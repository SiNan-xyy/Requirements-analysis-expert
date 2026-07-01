import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency in some environments
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class InteractionSchemaContractTests(unittest.TestCase):
    def test_interaction_state_fixture_has_required_fields(self):
        state = load_json("agent_modules/interaction_schema/fixtures/valid-interaction-state.json")

        self.assertEqual(state["stage"], "intake")
        self.assertEqual(state["status"], "collecting")
        self.assertEqual(state["completion_level"], "insufficient")
        self.assertEqual(state["next_action"], "ask_questions")
        self.assertIsInstance(state["answered_question_ids"], list)
        self.assertIsInstance(state["pending_question_ids"], list)

    def test_interaction_state_schema_defines_allowed_enums(self):
        schema = load_json("agent_modules/interaction_schema/schemas/interaction-state.schema.json")
        props = schema["properties"]

        self.assertIn("rpa_boundary_check", props["stage"]["enum"])
        self.assertIn("ready_for_next_module", props["status"]["enum"])
        self.assertIn("development_ready", props["completion_level"]["enum"])
        self.assertIn("stop_with_gap_report", props["next_action"]["enum"])

    def test_question_schema_uses_platform_compatible_choice_types(self):
        schema = load_json("agent_modules/interaction_schema/schemas/question.schema.json")
        options = schema["properties"]["options"]

        self.assertEqual(schema["properties"]["type"]["enum"], ["single_choice", "multiple_choice"])
        self.assertIn("supplement_text", schema["required"])
        supplement = schema["properties"]["supplement_text"]
        self.assertEqual(options["minItems"], 2)
        self.assertEqual(len(options["allOf"]), 2)
        required_values = set()
        for clause in options["allOf"]:
            self.assertEqual(clause["minContains"], 1)
            self.assertEqual(clause["contains"]["type"], "object")
            self.assertEqual(clause["contains"]["required"], ["value"])
            required_values.add(clause["contains"]["properties"]["value"]["const"])
        self.assertEqual(required_values, {"unknown", "other"})
        self.assertEqual(
            supplement["required"],
            ["enabled", "always_visible", "label", "placeholder"],
        )
        self.assertEqual(supplement["properties"]["enabled"]["const"], True)
        self.assertEqual(supplement["properties"]["always_visible"]["const"], True)
        self.assertEqual(
            schema["properties"]["importance"]["enum"],
            ["required", "recommended", "optional"],
        )

    @unittest.skipIf(jsonschema is None, "jsonschema is not installed in this environment")
    def test_question_schema_rejects_choice_options_missing_unknown_or_other(self):
        schema = load_json("agent_modules/interaction_schema/schemas/question.schema.json")
        question = load_json("agent_modules/interaction_schema/fixtures/multiple-choice-with-supplement-required.json")

        missing_unknown = json.loads(json.dumps(question))
        missing_unknown["options"] = [option for option in missing_unknown["options"] if option["value"] != "unknown"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=missing_unknown, schema=schema)

        missing_other = json.loads(json.dumps(question))
        missing_other["options"] = [option for option in missing_other["options"] if option["value"] != "other"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=missing_other, schema=schema)

    def test_required_question_fixture_supports_unknown_other_and_free_text(self):
        question = load_json("agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json")
        option_values = {option["value"] for option in question["options"]}

        self.assertEqual(question["type"], "single_choice")
        self.assertEqual(question["importance"], "required")
        self.assertTrue(question["blocks_stage_progression"])
        self.assertTrue(question["allow_unknown"])
        self.assertIn("unknown", option_values)
        self.assertIn("other", option_values)
        self.assertTrue(question["free_text"]["enabled"])
        self.assertEqual(
            question["free_text"]["required_when"]["selected_values_include"],
            ["other"],
        )

    def test_answer_batch_schema_defines_status_and_confidence_enums(self):
        schema = load_json("agent_modules/interaction_schema/schemas/answer-batch.schema.json")
        answer_props = schema["properties"]["answer_records"]["items"]["properties"]

        self.assertEqual(
            answer_props["answer_status"]["enum"],
            [
                "answered",
                "answered_with_supplement",
                "unknown",
                "unknown_with_note",
                "skipped",
                "invalid",
                "needs_free_text",
            ],
        )
        self.assertEqual(
            answer_props["confidence"]["enum"],
            ["high", "medium", "low", "none"],
        )

    def test_answer_batch_schema_distinguishes_unknown_other_and_supplement(self):
        schema = load_json("agent_modules/interaction_schema/schemas/answer-batch.schema.json")
        answer_props = schema["properties"]["answer_records"]["items"]["properties"]

        self.assertEqual(
            answer_props["answer_status"]["enum"],
            [
                "answered",
                "answered_with_supplement",
                "unknown",
                "unknown_with_note",
                "skipped",
                "invalid",
                "needs_free_text",
            ],
        )

    def test_answer_batch_fixture_updates_state_patch_and_impact(self):
        batch = load_json("agent_modules/interaction_schema/fixtures/valid-answer-batch.json")

        self.assertEqual(batch["answer_records"][0]["question_id"], "trigger_type")
        self.assertEqual(batch["answer_records"][0]["answer_status"], "answered")
        self.assertEqual(batch["answer_records"][0]["semantic_route"], "confirmed_answer")
        self.assertEqual(batch["state_patch"]["requirement.trigger.type"]["value"], "message_received")
        self.assertEqual(batch["impact"]["blocks_stage_progression"], False)
        self.assertEqual(batch["impact"]["adds_pending_question"], False)

    def test_unknown_and_other_fixture_have_different_semantics(self):
        fixture = load_json("agent_modules/interaction_schema/fixtures/answer-batch-unknown-vs-other.json")
        records = {record["question_id"]: record for record in fixture["answer_records"]}

        self.assertEqual(records["platform_access"]["answer_status"], "unknown")
        self.assertEqual(records["platform_access"]["semantic_route"], "gap_candidate")
        self.assertEqual(records["other_system"]["answer_status"], "answered_with_supplement")
        self.assertEqual(records["other_system"]["semantic_route"], "candidate_fact")
        self.assertEqual(records["other_without_text"]["answer_status"], "needs_free_text")
        self.assertEqual(records["other_without_text"]["semantic_route"], "supplement_required")

    def test_decision_rules_have_required_order_and_gap_policy(self):
        rules = load_json("agent_modules/interaction_schema/rules/decision-rules.json")
        conditions = [rule["condition"] for rule in rules["decision_rules"]]

        self.assertEqual(conditions[0], "has_invalid_required_answer")
        self.assertEqual(conditions[1], "has_other_without_free_text")
        self.assertIn("has_unanswered_required_questions", conditions)
        self.assertEqual(rules["gap_stop_policy"]["max_required_unknown_count"], 3)
        self.assertEqual(rules["gap_stop_policy"]["max_retries_per_question"], 2)
        self.assertTrue(rules["gap_stop_policy"]["fallback_to_single_question"])

    def test_question_type_policy_routes_coexisting_facts_to_multiple_choice(self):
        rules = load_json("agent_modules/interaction_schema/rules/decision-rules.json")
        policy = rules["question_type_policy"]

        self.assertEqual(policy["mutually_exclusive"], "single_choice")
        self.assertEqual(policy["coexisting_facts"], "multiple_choice")
        self.assertTrue(policy["must_include_unknown_option"])
        self.assertTrue(policy["must_include_other_option"])
        self.assertTrue(policy["must_include_always_visible_supplement_text"])
        self.assertIn("platform", policy["must_use_multiple_choice_for"])
        self.assertIn("data_source", policy["must_use_multiple_choice_for"])
        self.assertIn("input_field", policy["must_use_multiple_choice_for"])
        self.assertIn("output_field", policy["must_use_multiple_choice_for"])
        self.assertIn("object_scope", policy["must_use_multiple_choice_for"])
        self.assertIn("exception_handling", policy["must_use_multiple_choice_for"])
        self.assertIn("notification_method", policy["must_use_multiple_choice_for"])
        self.assertIn("human_fallback", policy["must_use_multiple_choice_for"])
        self.assertIn("captcha_handling", policy["must_use_multiple_choice_for"])
        self.assertIn("capability", policy["must_use_multiple_choice_for"])
        self.assertIn("risk", policy["must_use_multiple_choice_for"])
        self.assertIn("prework", policy["must_use_multiple_choice_for"])

    def test_decision_rules_distinguish_unknown_from_other(self):
        rules = load_json("agent_modules/interaction_schema/rules/decision-rules.json")
        semantics = rules["unknown_other_semantics"]

        self.assertEqual(semantics["unknown"]["meaning"], "customer cannot confirm now")
        self.assertFalse(semantics["unknown"]["requires_supplement_text"])
        self.assertEqual(semantics["unknown"]["semantic_route"], "gap_candidate")
        self.assertEqual(semantics["other"]["meaning"], "customer knows an answer not covered by options")
        self.assertTrue(semantics["other"]["requires_supplement_text"])
        self.assertEqual(semantics["other"]["semantic_route_when_text_present"], "candidate_fact")
        self.assertEqual(semantics["other"]["semantic_route_when_text_missing"], "supplement_required")

    def test_multiple_choice_fixture_uses_platform_type_and_supplement_text(self):
        question = load_json("agent_modules/interaction_schema/fixtures/multiple-choice-with-supplement-required.json")
        option_values = {option["value"] for option in question["options"]}

        self.assertEqual(question["type"], "multiple_choice")
        self.assertEqual(question["target_field"], "operated_systems")
        self.assertIn("other", option_values)
        self.assertIn("unknown", option_values)
        self.assertTrue(question["supplement_text"]["enabled"])
        self.assertTrue(question["supplement_text"]["always_visible"])
        self.assertEqual(question["supplement_text"]["label"], "请补充")

    def test_prompt_rules_document_mentions_platform_choice_guidance(self):
        text = (ROOT / "agent_modules/interaction_schema/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Use `multiple_choice` when multiple facts can coexist", text)
        self.assertIn("Do not use `multiple_choice_with_text`", text)
        self.assertIn("Always include `other` and `unknown` routes for required questions.", text)
        self.assertIn("Every question must include `unknown`, `other`, and always-visible `supplement_text`.", text)

    def test_deduplication_fixture_infers_web_system_from_url(self):
        fixture = load_json("agent_modules/interaction_schema/fixtures/deduplication-url-inference.json")
        patch = fixture["state_patch"]
        skipped = fixture["deduplication"]["skipped_question_ids"]

        self.assertEqual(
            patch["systems[0].entry_url"]["value"],
            "https://shop.yingdao.com/worktop/logistics-list",
        )
        self.assertEqual(patch["systems[0].type"]["value"], "browser_web")
        self.assertEqual(patch["systems[0].type"]["source"], "inferred_from_url")
        self.assertEqual(patch["systems[0].type"]["confidence"], "high")
        self.assertIn("system_type", skipped)

    def test_deduplication_fixture_records_confirmation_for_medium_confidence(self):
        fixture = load_json("agent_modules/interaction_schema/fixtures/deduplication-url-inference.json")

        self.assertEqual(
            fixture["deduplication"]["medium_confidence_strategy"],
            "ask_confirmation_question",
        )

    def test_readme_lists_all_module_artifacts(self):
        text = (ROOT / "agent_modules/interaction_schema/README.md").read_text(encoding="utf-8")

        expected_paths = [
            "schemas/interaction-state.schema.json",
            "schemas/question.schema.json",
            "schemas/answer-batch.schema.json",
            "rules/decision-rules.json",
            "rules/prompt-rules.md",
            "fixtures/deduplication-url-inference.json",
            "fixtures/multiple-choice-with-supplement-required.json",
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
