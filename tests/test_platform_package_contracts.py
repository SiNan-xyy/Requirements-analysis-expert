import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PLATFORM_DOCS = [
    "agent_platform_package/testing/expected_outputs.md",
    "agent_platform_package/testing/platform_test_checklist.md",
]

COMMON_MOJIBAKE_FRAGMENTS = (
    "骞冲",
    "娴嬭",
    "鑷",
    "鐗",
    "鍏堢",
    "椋炰功",
    "閭",
    "閼",
    "閻",
    "妞",
    "瀹",
    "鍙ｅ緞",
)


class PlatformPackageContractTests(unittest.TestCase):
    def test_platform_docs_describe_supplement_text_mapping(self):
        checklist = (ROOT / "agent_platform_package/testing/platform_test_checklist.md").read_text(
            encoding="utf-8"
        )
        expected = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("supplement_text", checklist)
        self.assertIn("always_visible", checklist)
        self.assertIn("unknown is not other", checklist)
        self.assertIn("Question `type` must stay `single_choice` or `multiple_choice`", expected)
        self.assertIn("Do not output `multiple_choice_with_text`", expected)

    def test_platform_testing_docs_are_readable(self):
        for relative_path in PLATFORM_DOCS:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                self.assertIn("JSON", text)
                self.assertIn("interaction_state", text)
                self.assertIn("clarification_result", text)
                self.assertIn("rpa_boundary_result", text)
                self.assertIn("process_breakdown_result", text)
                for fragment in COMMON_MOJIBAKE_FRAGMENTS:
                    self.assertNotIn(fragment, text)

    def test_module_1_to_4_flow_guide_names_handoff_gates(self):
        text = (ROOT / "agent_platform_package/testing/module_1_to_4_flow_test.md").read_text(
            encoding="utf-8"
        )

        expected_terms = [
            "模块 1",
            "模块 2",
            "模块 3",
            "模块 4",
            "enter_next_module",
            "rpa_boundary_check",
            "process_breakdown",
            "exception_design",
            "suitable",
            "conditionally_suitable",
            "business_process_cards_with_candidate_capabilities",
        ]

        for term in expected_terms:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_captcha_capability_rag_is_registered(self):
        rag_path = ROOT / "agent_platform_package/rag_upload/12_captcha_capability_boundary.md"
        integration_guide = (ROOT / "agent_platform_package/integration_guide.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("12_captcha_capability_boundary.md", integration_guide)
        self.assertTrue(rag_path.exists())

        text = rag_path.read_text(encoding="utf-8")
        expected_terms = [
            "验证码不是天然不可做",
            "适配指令",
            "费用",
            "准确率",
            "人工兜底",
        ]
        for term in expected_terms:
            with self.subTest(term=term):
                self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
