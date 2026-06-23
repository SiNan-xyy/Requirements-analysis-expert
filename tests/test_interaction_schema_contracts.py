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


if __name__ == "__main__":
    unittest.main()
