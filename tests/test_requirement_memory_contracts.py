import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class RequirementMemoryContractTests(unittest.TestCase):
    def test_requirement_memory_schema_defines_fact_ledger_sections(self):
        schema = load_json("agent_modules/requirement_memory/schemas/requirement-memory.schema.json")
        props = schema["properties"]

        self.assertEqual(schema["title"], "RequirementMemory")
        self.assertEqual(props["module"]["const"], "global_requirement_memory")
        self.assertIn("current_stage", schema["required"])
        self.assertIn("confirmed_facts", schema["required"])
        self.assertIn("inferred_items", schema["required"])
        self.assertIn("gaps", schema["required"])
        self.assertIn("conflicts", schema["required"])
        self.assertIn("retired_questions", schema["required"])
        self.assertIn("decisions", schema["required"])
        self.assertIn("gate_states", schema["required"])

    def test_requirement_memory_schema_uses_controlled_ids_sources_and_gate_states(self):
        schema = load_json("agent_modules/requirement_memory/schemas/requirement-memory.schema.json")

        self.assertEqual(schema["$defs"]["fact_id"]["pattern"], "^F[0-9]{3}$")
        self.assertEqual(schema["$defs"]["inference_id"]["pattern"], "^I[0-9]{3}$")
        self.assertEqual(schema["$defs"]["gap_id"]["pattern"], "^G[0-9]{3}$")
        self.assertEqual(schema["$defs"]["conflict_id"]["pattern"], "^C[0-9]{3}$")
        self.assertEqual(schema["$defs"]["retired_id"]["pattern"], "^R[0-9]{3}$")
        self.assertEqual(schema["$defs"]["decision_id"]["pattern"], "^D[0-9]{3}$")
        self.assertEqual(
            schema["$defs"]["source_label"]["enum"],
            [
                "customer_confirmed",
                "upstream_confirmed",
                "rag_suggested",
                "agent_inferred_pending_confirmation",
                "required_before_build",
            ],
        )
        self.assertEqual(schema["$defs"]["gate_state"]["enum"], ["ready", "partial_ready", "blocked"])

    def test_requirement_memory_schema_limits_next_question_plan_question_types(self):
        schema = load_json("agent_modules/requirement_memory/schemas/requirement-memory.schema.json")
        question_type_enum = schema["properties"]["next_question_plan"]["items"]["properties"]["question_type"]["enum"]

        self.assertEqual(question_type_enum, ["single_choice", "multiple_choice"])

    def test_update_rules_protect_confirmed_facts_and_require_read_before_write(self):
        rules = load_json("agent_modules/requirement_memory/rules/update-rules.json")

        self.assertEqual(rules["module"], "global_requirement_memory")
        self.assertIn("read_memory_before_every_turn", rules["global_rules"])
        self.assertIn("confirmed_facts_require_customer_or_upstream_source", rules["global_rules"])
        self.assertIn("inferred_items_cannot_be_used_for_development", rules["global_rules"])
        self.assertIn("gaps_must_track_blocking_stage", rules["global_rules"])
        self.assertIn("conflicts_must_supersede_or_retire_old_facts", rules["global_rules"])

    def test_memory_update_rules_separate_unknown_from_other(self):
        rules = load_json("agent_modules/requirement_memory/rules/update-rules.json")
        semantics = rules["unknown_other_semantics"]

        self.assertEqual(semantics["unknown"]["memory_target"], "gaps")
        self.assertFalse(semantics["unknown"]["requires_supplement_text"])
        self.assertEqual(
            semantics["other_with_supplement"]["memory_target"], "confirmed_facts_or_inferred_items"
        )
        self.assertEqual(
            semantics["other_without_supplement"]["memory_target"], "retired_questions_or_next_question_plan"
        )
        self.assertTrue(semantics["other_without_supplement"]["requires_supplement_text"])

    def test_memory_prompt_rules_explain_unknown_and_other_separately(self):
        text = (ROOT / "agent_modules/requirement_memory/rules/prompt-rules.md").read_text(encoding="utf-8")

        self.assertIn("unknown means the customer cannot confirm now", text)
        self.assertIn("other means the options do not cover a known answer", text)
        self.assertIn("unknown must not require supplement text", text)
        self.assertIn("other without supplement text must ask for supplement", text)

    def test_memory_template_contains_required_markdown_sections(self):
        text = (ROOT / "agent_modules/requirement_memory/templates/requirement_memory_template.md").read_text(
            encoding="utf-8"
        )

        expected_sections = [
            "# 需求记忆体",
            "## 当前阶段",
            "## 已确认事实 F",
            "## 推断建议 I",
            "## 待确认缺口 G",
            "## 冲突或更正 C",
            "## 已废弃问题 R",
            "## 模块判断 D",
            "## 模块就绪度 Gate",
        ]
        for section in expected_sections:
            with self.subTest(section=section):
                self.assertIn(section, text)

    def test_ecommerce_memory_fixture_demonstrates_confirmed_inferred_gap_and_gate(self):
        text = (ROOT / "agent_modules/requirement_memory/fixtures/ecommerce-memory.md").read_text(
            encoding="utf-8"
        )

        for term in ["F001", "I001", "G001", "D001", "partial_ready", "客户回答"]:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_gate_rules_define_transitions_with_minimum_facts(self):
        rules = load_json("agent_modules/requirement_memory/rules/gate-rules.json")

        self.assertEqual(rules["module"], "global_requirement_memory")
        expected_transitions = [
            "module_2_to_module_3",
            "module_3_to_module_4",
            "module_4_to_module_5",
            "module_5_to_module_6",
        ]
        self.assertEqual(list(rules["transitions"].keys()), expected_transitions)
        for transition in expected_transitions:
            with self.subTest(transition=transition):
                transition_rules = rules["transitions"][transition]
                self.assertIn("minimum_facts", transition_rules)
                self.assertIn("allowed_carry_forward_gaps", transition_rules)
                self.assertIn("hard_blockers", transition_rules)
                self.assertIn("ready_states", transition_rules)
                self.assertIn("partial_ready", transition_rules["ready_states"])


if __name__ == "__main__":
    unittest.main()
