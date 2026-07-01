import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PLATFORM_DOCS = [
    "agent_platform_package/testing/expected_outputs.md",
    "agent_platform_package/testing/platform_test_checklist.md",
]
LIVE_CONTRACT_DOCS = [
    "agent_platform_package/system_prompt/agent-system-prompt.md",
    "agent_platform_package/testing/platform_test_checklist.md",
    "agent_platform_package/integration_guide.md",
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
        platform_controls_section = checklist.split("## Platform-compatible question controls\n", 1)[1]
        platform_controls_section = platform_controls_section.split("\n## ", 1)[0]

        checklist_fragments = [
            "supplement_text.enabled = true",
            "supplement_text.always_visible = true",
            "Question `type` must stay `single_choice` or `multiple_choice`",
            "Do not output `single_choice_with_text` or `multiple_choice_with_text`",
            "unknown is not other",
            'Every question must show both `unknown` and `other`, and must also show both "不确定" and "其他".',
            "不确定",
            "其他",
            "Supplement behavior must be represented by always-visible `supplement_text`",
        ]
        expected_fragments = [
            "Question `type` must stay `single_choice` or `multiple_choice`",
            "Do not output `single_choice_with_text`.",
            "Do not output `multiple_choice_with_text`.",
            "supplement_text.enabled = true",
            "supplement_text.always_visible = true",
            "unknown is not other.",
            "`unknown`",
            "`other`",
        ]

        for fragment in checklist_fragments:
            with self.subTest(doc="checklist", fragment=fragment):
                self.assertIn(fragment, checklist)

        self.assertNotIn("where appropriate", checklist)
        self.assertNotIn("where appropriate", platform_controls_section)

        for fragment in expected_fragments:
            with self.subTest(doc="expected_outputs", fragment=fragment):
                self.assertIn(fragment, expected)

    def test_live_contract_docs_use_unknown_other_plus_supplement_split(self):
        required_fragments = ["不确定", "其他", "supplement_text"]
        forbidden_fragments = ["other, please " + "supplement", "其他" + "，请补充"]

        for relative_path in LIVE_CONTRACT_DOCS:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for fragment in required_fragments:
                with self.subTest(path=relative_path, fragment=fragment):
                    self.assertIn(fragment, text)
            for fragment in forbidden_fragments:
                with self.subTest(path=relative_path, forbidden=fragment):
                    self.assertNotIn(fragment, text)

    def test_system_prompt_requires_skill_and_mapped_rag_before_output(self):
        prompt = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(
            encoding="utf-8"
        )
        checklist = (ROOT / "agent_platform_package/testing/platform_test_checklist.md").read_text(
            encoding="utf-8"
        )
        guide = (ROOT / "agent_platform_package/integration_guide.md").read_text(
            encoding="utf-8"
        )

        prompt_fragments = [
            "Skill 与 RAG 强制使用规则",
            "每一轮回复前，必须先读取并遵循 Git Skill",
            "每个模块输出前，必须检索并使用当前模块对应的 RAG 材料",
            "未检索到可用 RAG 依据",
            "RAG 只负责知识解释、能力依据、案例参考和风险提示",
            "客户已确认、RAG 建议、Agent 推断待确认、开发前必须补充确认",
            "模块 2 需求澄清",
            "模块 3 RPA 能力边界",
            "模块 4 流程拆解",
            "模块 5 异常设计",
            "模块 6 方案打包",
            "12_captcha_capability_boundary.md",
            "11_report_quality_rules.md",
        ]
        checklist_fragments = [
            "Skill And RAG Invocation",
            "Before each module output, the Agent should first follow the Git Skill",
            "If no usable RAG evidence is retrieved",
            "Module 3 should retrieve RPA boundary",
            "Every recommendation or risk must be source-labeled",
        ]
        guide_fragments = [
            "运行要求",
            "每一轮都应先按 Git Skill 判断当前模块",
            "模块与 RAG 对应关系",
            "每轮先遵循 Git Skill，再检索对应 RAG",
        ]

        for fragment in prompt_fragments:
            with self.subTest(doc="system_prompt", fragment=fragment):
                self.assertIn(fragment, prompt)
        for fragment in checklist_fragments:
            with self.subTest(doc="platform_test_checklist", fragment=fragment):
                self.assertIn(fragment, checklist)
        for fragment in guide_fragments:
            with self.subTest(doc="integration_guide", fragment=fragment):
                self.assertIn(fragment, guide)

    def test_system_prompt_emphasizes_core_priority_and_choice_controls(self):
        prompt = (ROOT / "agent_platform_package/system_prompt/agent-system-prompt.md").read_text(
            encoding="utf-8"
        )
        checklist = (ROOT / "agent_platform_package/testing/platform_test_checklist.md").read_text(
            encoding="utf-8"
        )
        guide = (ROOT / "agent_platform_package/integration_guide.md").read_text(
            encoding="utf-8"
        )

        prompt_fragments = [
            "最高优先级核心规则",
            "Git Skill 规则 > 本系统提示词 > RAG 材料 > Agent 自行推断",
            "必须优先使用选择题组件进行澄清",
            "必须根据题目含义切换单选和多选",
            "唯一答案、判断类、阶段类问题使用 `single_choice`",
            "可能存在多个答案的问题使用 `multiple_choice`",
            "所有补充选项必须加入输入框",
            "补充内容只能通过始终可见的 `supplement_text` 输入框承载",
            "Use `single_choice` only when the customer should select exactly one answer.",
            "Any option that allows supplementing information must use `supplement_text` as an input box",
        ]
        checklist_fragments = [
            "Each round must prefer choice-question components.",
            "The Agent must switch between `single_choice` and `multiple_choice` based on the question meaning.",
            "Use `single_choice` only when exactly one answer should be selected.",
            "Every supplement path must render an input box through `supplement_text`.",
        ]
        guide_fragments = [
            "最高优先级规则：Git Skill 规则 > 本系统提示词 > RAG 材料 > Agent 自行推断。",
            "根据题目含义切换 `single_choice` 和 `multiple_choice`",
            "所有补充选项必须加入输入框，由 `supplement_text` 承载。",
        ]

        for fragment in prompt_fragments:
            with self.subTest(doc="system_prompt", fragment=fragment):
                self.assertIn(fragment, prompt)
        for fragment in checklist_fragments:
            with self.subTest(doc="platform_test_checklist", fragment=fragment):
                self.assertIn(fragment, checklist)
        for fragment in guide_fragments:
            with self.subTest(doc="integration_guide", fragment=fragment):
                self.assertIn(fragment, guide)

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
