import json
import unittest
from pathlib import Path


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

    def test_question_schema_uses_only_single_or_multiple_choice(self):
        schema = load_json("agent_modules/interaction_schema/schemas/question.schema.json")

        self.assertEqual(schema["properties"]["type"]["enum"], ["single_choice", "multiple_choice"])
        self.assertEqual(
            schema["properties"]["importance"]["enum"],
            ["required", "recommended", "optional"],
        )

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
            ["answered", "unknown", "skipped", "invalid", "needs_free_text"],
        )
        self.assertEqual(
            answer_props["confidence"]["enum"],
            ["high", "medium", "low", "none"],
        )

    def test_answer_batch_fixture_updates_state_patch_and_impact(self):
        batch = load_json("agent_modules/interaction_schema/fixtures/valid-answer-batch.json")

        self.assertEqual(batch["answer_records"][0]["question_id"], "trigger_type")
        self.assertEqual(batch["answer_records"][0]["answer_status"], "answered")
        self.assertEqual(batch["state_patch"]["requirement.trigger.type"]["value"], "message_received")
        self.assertEqual(batch["impact"]["blocks_stage_progression"], False)
        self.assertEqual(batch["impact"]["adds_pending_question"], False)

    def test_decision_rules_have_required_order_and_gap_policy(self):
        rules = load_json("agent_modules/interaction_schema/rules/decision-rules.json")
        conditions = [rule["condition"] for rule in rules["decision_rules"]]

        self.assertEqual(conditions[0], "has_invalid_required_answer")
        self.assertEqual(conditions[1], "has_other_without_free_text")
        self.assertIn("has_unanswered_required_questions", conditions)
        self.assertEqual(rules["gap_stop_policy"]["max_required_unknown_count"], 3)
        self.assertEqual(rules["gap_stop_policy"]["max_retries_per_question"], 2)
        self.assertTrue(rules["gap_stop_policy"]["fallback_to_single_question"])

    def test_prompt_rules_document_mentions_no_repeated_questions(self):
        text = (ROOT / "agent_modules/interaction_schema/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("Do not ask a question if the answer was already supplied", text)
        self.assertIn("Summarize what was learned before entering the next module", text)

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
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
