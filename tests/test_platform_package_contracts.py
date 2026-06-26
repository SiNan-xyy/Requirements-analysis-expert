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


if __name__ == "__main__":
    unittest.main()
