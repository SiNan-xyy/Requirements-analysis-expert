# Interaction Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build module 1 for the RPA requirements analyst agent: a validated interaction schema package for choice-first questioning, answer writing, progression decisions, and deduplication.

**Architecture:** Create a small, file-based module under `agent_modules/interaction_schema/`. JSON schema files define stable data contracts, Markdown prompt rules define agent behavior, fixtures demonstrate expected examples, and Python stdlib tests validate that the examples and schema contracts stay coherent.

**Tech Stack:** JSON, Markdown, Python 3 stdlib `unittest` and `json`, no third-party runtime dependencies.

## Global Constraints

- Implement only module 1: interaction state, choice-question schema, answer record/state patch model, next-step decision rules, and deduplication/answer absorption rules.
- Do not implement RPA capability boundary scoring.
- Do not implement process breakdown logic.
- Do not implement exception and branch design logic.
- Do not implement HTML report generation.
- Every required question must support `unknown` and `other` answer routes.
- Every question may support supplemental free text; free text is required when `other` is selected.
- Preserve answer provenance and confidence for inferred fields.
- Avoid repeated questions by recomputing pending questions after each answer batch.
- Use ASCII punctuation in repository files unless Chinese user-facing example text is required.

---

## File Structure

- Create `agent_modules/interaction_schema/README.md`: module overview and file index.
- Create `agent_modules/interaction_schema/schemas/interaction-state.schema.json`: contract for interaction state.
- Create `agent_modules/interaction_schema/schemas/question.schema.json`: contract for choice questions.
- Create `agent_modules/interaction_schema/schemas/answer-batch.schema.json`: contract for answer records, state patches, and impacts.
- Create `agent_modules/interaction_schema/rules/decision-rules.json`: ordered next-action rules and gap stop policy.
- Create `agent_modules/interaction_schema/rules/prompt-rules.md`: prompt behavior rules for module 1.
- Create `agent_modules/interaction_schema/fixtures/valid-interaction-state.json`: canonical valid state fixture.
- Create `agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json`: canonical valid question fixture.
- Create `agent_modules/interaction_schema/fixtures/valid-answer-batch.json`: canonical valid answer batch fixture.
- Create `agent_modules/interaction_schema/fixtures/deduplication-url-inference.json`: fixture showing URL-based system type inference.
- Create `tests/test_interaction_schema_contracts.py`: Python stdlib tests for schemas, fixtures, and required rules.

---

### Task 1: Scaffold Module Files And Baseline Tests

**Files:**
- Create: `agent_modules/interaction_schema/README.md`
- Create: `agent_modules/interaction_schema/schemas/interaction-state.schema.json`
- Create: `agent_modules/interaction_schema/fixtures/valid-interaction-state.json`
- Create: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Produces: `agent_modules/interaction_schema/schemas/interaction-state.schema.json`
- Produces: `agent_modules/interaction_schema/fixtures/valid-interaction-state.json`
- Produces test helper `load_json(relative_path: str) -> dict`

- [ ] **Step 1: Write the failing test**

Create `tests/test_interaction_schema_contracts.py` with:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: FAIL with `FileNotFoundError` for `valid-interaction-state.json` or `interaction-state.schema.json`.

- [ ] **Step 3: Create minimal module README**

Create `agent_modules/interaction_schema/README.md` with:

```markdown
# Interaction Schema Module

This module defines the first layer of the RPA requirements analyst agent: the choice-first interaction state, question format, answer recording format, next-step decision rules, and deduplication rules.

It does not evaluate RPA feasibility, break down process steps, design exceptions, or generate HTML reports.

## Files

- `schemas/interaction-state.schema.json`: interaction state contract.
- `schemas/question.schema.json`: choice-question contract.
- `schemas/answer-batch.schema.json`: answer record and state patch contract.
- `rules/decision-rules.json`: ordered next-action rules.
- `rules/prompt-rules.md`: agent prompt behavior rules.
- `fixtures/`: valid examples used by tests and platform integration.
```

- [ ] **Step 4: Create interaction state schema**

Create `agent_modules/interaction_schema/schemas/interaction-state.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/interaction-state.schema.json",
  "title": "InteractionState",
  "type": "object",
  "required": [
    "stage",
    "status",
    "completion_level",
    "answered_question_ids",
    "pending_question_ids",
    "last_summary",
    "next_action"
  ],
  "additionalProperties": false,
  "properties": {
    "stage": {
      "type": "string",
      "enum": [
        "intake",
        "clarification",
        "rpa_boundary_check",
        "process_breakdown",
        "exception_design",
        "blueprint_ready"
      ]
    },
    "status": {
      "type": "string",
      "enum": [
        "collecting",
        "summarizing",
        "waiting_user_confirm",
        "ready_for_next_module",
        "blocked"
      ]
    },
    "completion_level": {
      "type": "string",
      "enum": [
        "insufficient",
        "partial",
        "workable",
        "development_ready"
      ]
    },
    "answered_question_ids": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "uniqueItems": true
    },
    "pending_question_ids": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "uniqueItems": true
    },
    "last_summary": {
      "type": "string"
    },
    "next_action": {
      "type": "string",
      "enum": [
        "ask_questions",
        "ask_repair_question",
        "request_free_text",
        "summarize_and_confirm",
        "enter_next_module",
        "stop_with_gap_report",
        "stop_with_blocker"
      ]
    }
  }
}
```

- [ ] **Step 5: Create valid interaction state fixture**

Create `agent_modules/interaction_schema/fixtures/valid-interaction-state.json` with:

```json
{
  "stage": "intake",
  "status": "collecting",
  "completion_level": "insufficient",
  "answered_question_ids": [],
  "pending_question_ids": ["trigger_type"],
  "last_summary": "",
  "next_action": "ask_questions"
}
```

- [ ] **Step 6: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: PASS for both tests.

- [ ] **Step 7: Commit**

Run:

```powershell
git add agent_modules/interaction_schema/README.md agent_modules/interaction_schema/schemas/interaction-state.schema.json agent_modules/interaction_schema/fixtures/valid-interaction-state.json tests/test_interaction_schema_contracts.py
git commit -m "feat: add interaction state schema"
```

---

### Task 2: Add Choice Question Schema And Fixture

**Files:**
- Create: `agent_modules/interaction_schema/schemas/question.schema.json`
- Create: `agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json`
- Modify: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: `load_json(relative_path: str) -> dict`
- Produces: question schema with `type`, `importance`, `free_text`, and `retry_policy`

- [ ] **Step 1: Write the failing tests**

Append these methods inside `InteractionSchemaContractTests`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: FAIL with `FileNotFoundError` for `question.schema.json` or `valid-question-trigger-type.json`.

- [ ] **Step 3: Create choice question schema**

Create `agent_modules/interaction_schema/schemas/question.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/question.schema.json",
  "title": "ChoiceQuestion",
  "type": "object",
  "required": [
    "question_id",
    "stage",
    "question",
    "type",
    "importance",
    "blocks_stage_progression",
    "allow_unknown",
    "target_field",
    "options",
    "free_text",
    "retry_policy"
  ],
  "additionalProperties": false,
  "properties": {
    "question_id": {
      "type": "string",
      "minLength": 1
    },
    "stage": {
      "type": "string"
    },
    "question": {
      "type": "string",
      "minLength": 1
    },
    "type": {
      "type": "string",
      "enum": ["single_choice", "multiple_choice"]
    },
    "importance": {
      "type": "string",
      "enum": ["required", "recommended", "optional"]
    },
    "blocks_stage_progression": {
      "type": "boolean"
    },
    "allow_unknown": {
      "type": "boolean"
    },
    "target_field": {
      "type": "string",
      "minLength": 1
    },
    "options": {
      "type": "array",
      "minItems": 2,
      "items": {
        "type": "object",
        "required": ["label", "value"],
        "additionalProperties": false,
        "properties": {
          "label": {
            "type": "string",
            "minLength": 1
          },
          "value": {
            "type": "string",
            "minLength": 1
          },
          "description": {
            "type": "string"
          }
        }
      }
    },
    "free_text": {
      "type": "object",
      "required": ["enabled", "field", "required_when"],
      "additionalProperties": false,
      "properties": {
        "enabled": {
          "type": "boolean"
        },
        "field": {
          "type": "string"
        },
        "required_when": {
          "type": "object",
          "required": ["selected_values_include"],
          "additionalProperties": false,
          "properties": {
            "selected_values_include": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
      }
    },
    "retry_policy": {
      "type": "object",
      "required": ["max_retries", "fallback_to_single_question"],
      "additionalProperties": false,
      "properties": {
        "max_retries": {
          "type": "integer",
          "minimum": 0
        },
        "fallback_to_single_question": {
          "type": "boolean"
        }
      }
    },
    "depends_on_fields": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "skip_if": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  }
}
```

- [ ] **Step 4: Create valid trigger question fixture**

Create `agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json` with:

```json
{
  "question_id": "trigger_type",
  "stage": "clarification",
  "question": "这个流程通常从什么事件开始？",
  "type": "single_choice",
  "importance": "required",
  "blocks_stage_progression": true,
  "allow_unknown": true,
  "target_field": "requirement.trigger.type",
  "options": [
    {
      "label": "固定时间自动开始",
      "value": "scheduled",
      "description": "例如每天 9 点、每小时一次。"
    },
    {
      "label": "收到飞书/钉钉消息后开始",
      "value": "message_received",
      "description": "例如收到订单号、物流单号、审批消息。"
    },
    {
      "label": "收到文件或表格后开始",
      "value": "file_received",
      "description": "例如收到 Excel、CSV、下载文件。"
    },
    {
      "label": "人工点击按钮后开始",
      "value": "manual_start",
      "description": "适合人工确认后再执行的流程。"
    },
    {
      "label": "暂不确定",
      "value": "unknown"
    },
    {
      "label": "其他，请补充",
      "value": "other"
    }
  ],
  "free_text": {
    "enabled": true,
    "field": "requirement.trigger.note",
    "required_when": {
      "selected_values_include": ["other"]
    }
  },
  "retry_policy": {
    "max_retries": 2,
    "fallback_to_single_question": true
  }
}
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: PASS for all tests.

- [ ] **Step 6: Commit**

Run:

```powershell
git add agent_modules/interaction_schema/schemas/question.schema.json agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json tests/test_interaction_schema_contracts.py
git commit -m "feat: add choice question schema"
```

---

### Task 3: Add Answer Batch Schema And Fixture

**Files:**
- Create: `agent_modules/interaction_schema/schemas/answer-batch.schema.json`
- Create: `agent_modules/interaction_schema/fixtures/valid-answer-batch.json`
- Modify: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: `load_json(relative_path: str) -> dict`
- Produces: answer status enum `answered`, `unknown`, `skipped`, `invalid`, `needs_free_text`
- Produces: confidence enum `high`, `medium`, `low`, `none`

- [ ] **Step 1: Write the failing tests**

Append these methods inside `InteractionSchemaContractTests`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: FAIL with `FileNotFoundError` for `answer-batch.schema.json` or `valid-answer-batch.json`.

- [ ] **Step 3: Create answer batch schema**

Create `agent_modules/interaction_schema/schemas/answer-batch.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://yingdao.local/rpa-requirements/answer-batch.schema.json",
  "title": "AnswerBatch",
  "type": "object",
  "required": ["answer_records", "state_patch", "impact"],
  "additionalProperties": false,
  "properties": {
    "answer_records": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "question_id",
          "selected_values",
          "free_text",
          "answer_status",
          "confidence"
        ],
        "additionalProperties": false,
        "properties": {
          "question_id": {
            "type": "string",
            "minLength": 1
          },
          "selected_values": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "free_text": {
            "type": "string"
          },
          "answer_status": {
            "type": "string",
            "enum": ["answered", "unknown", "skipped", "invalid", "needs_free_text"]
          },
          "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low", "none"]
          }
        }
      }
    },
    "state_patch": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["value", "source", "confidence"],
        "additionalProperties": false,
        "properties": {
          "value": {},
          "source": {
            "type": "string"
          },
          "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low", "none"]
          }
        }
      }
    },
    "impact": {
      "type": "object",
      "required": [
        "blocks_stage_progression",
        "adds_pending_question"
      ],
      "additionalProperties": false,
      "properties": {
        "blocks_stage_progression": {
          "type": "boolean"
        },
        "adds_pending_question": {
          "type": "boolean"
        },
        "pending_question_ids": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "review_notes": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Create valid answer batch fixture**

Create `agent_modules/interaction_schema/fixtures/valid-answer-batch.json` with:

```json
{
  "answer_records": [
    {
      "question_id": "trigger_type",
      "selected_values": ["message_received"],
      "free_text": "客户把物流单号发给飞书机器人后触发",
      "answer_status": "answered",
      "confidence": "high"
    }
  ],
  "state_patch": {
    "requirement.trigger.type": {
      "value": "message_received",
      "source": "explicit_user_choice",
      "confidence": "high"
    },
    "requirement.trigger.description": {
      "value": "客户把物流单号发给飞书机器人后触发",
      "source": "user_free_text",
      "confidence": "high"
    }
  },
  "impact": {
    "blocks_stage_progression": false,
    "adds_pending_question": false,
    "pending_question_ids": [],
    "review_notes": []
  }
}
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: PASS for all tests.

- [ ] **Step 6: Commit**

Run:

```powershell
git add agent_modules/interaction_schema/schemas/answer-batch.schema.json agent_modules/interaction_schema/fixtures/valid-answer-batch.json tests/test_interaction_schema_contracts.py
git commit -m "feat: add answer batch schema"
```

---

### Task 4: Add Decision Rules And Prompt Rules

**Files:**
- Create: `agent_modules/interaction_schema/rules/decision-rules.json`
- Create: `agent_modules/interaction_schema/rules/prompt-rules.md`
- Modify: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: `load_json(relative_path: str) -> dict`
- Produces ordered decision rules with `condition` and `next_action`
- Produces gap stop policy with `max_required_unknown_count`, `max_retries_per_question`, and `fallback_to_single_question`

- [ ] **Step 1: Write the failing tests**

Append these methods inside `InteractionSchemaContractTests`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: FAIL with `FileNotFoundError` for `decision-rules.json` or `prompt-rules.md`.

- [ ] **Step 3: Create decision rules**

Create `agent_modules/interaction_schema/rules/decision-rules.json` with:

```json
{
  "decision_rules": [
    {
      "condition": "has_invalid_required_answer",
      "next_action": "ask_repair_question"
    },
    {
      "condition": "has_other_without_free_text",
      "next_action": "request_free_text"
    },
    {
      "condition": "has_unanswered_required_questions",
      "next_action": "ask_questions"
    },
    {
      "condition": "stage_required_questions_complete",
      "next_action": "summarize_and_confirm"
    },
    {
      "condition": "user_confirmed_summary",
      "next_action": "enter_next_module"
    },
    {
      "condition": "too_many_unknown_required_fields",
      "next_action": "stop_with_gap_report"
    }
  ],
  "gap_stop_policy": {
    "max_required_unknown_count": 3,
    "max_retries_per_question": 2,
    "fallback_to_single_question": true
  }
}
```

- [ ] **Step 4: Create prompt rules**

Create `agent_modules/interaction_schema/rules/prompt-rules.md` with:

```markdown
# Interaction Prompt Rules

Use these rules only for module 1 interaction control.

- Ask 3-5 questions per batch when the user is engaged and the context is clear.
- Ask only one simplified question if the prior batch was skipped or unclear.
- Prefer business language over technical language.
- Always include `other` and `unknown` routes for required questions.
- Summarize what was learned before entering the next module.
- Do not ask a question if the answer was already supplied or can be inferred with high confidence.
- Do not generate downstream artifacts until the current stage summary is confirmed.
- If too many required fields are unknown, stop with a gap report instead of forcing progress.
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: PASS for all tests.

- [ ] **Step 6: Commit**

Run:

```powershell
git add agent_modules/interaction_schema/rules/decision-rules.json agent_modules/interaction_schema/rules/prompt-rules.md tests/test_interaction_schema_contracts.py
git commit -m "feat: add interaction decision rules"
```

---

### Task 5: Add Deduplication Fixture And Contract Tests

**Files:**
- Create: `agent_modules/interaction_schema/fixtures/deduplication-url-inference.json`
- Modify: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: `load_json(relative_path: str) -> dict`
- Produces fixture showing URL inference of `systems[].type` as `browser_web`

- [ ] **Step 1: Write the failing tests**

Append these methods inside `InteractionSchemaContractTests`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: FAIL with `FileNotFoundError` for `deduplication-url-inference.json`.

- [ ] **Step 3: Create deduplication fixture**

Create `agent_modules/interaction_schema/fixtures/deduplication-url-inference.json` with:

```json
{
  "user_answer": "平台是影刀商城后台，网址是 https://shop.yingdao.com/worktop/logistics-list，用 admin 登录。",
  "state_patch": {
    "systems[0].name": {
      "value": "影刀商城后台",
      "source": "user_free_text",
      "confidence": "high"
    },
    "systems[0].entry_url": {
      "value": "https://shop.yingdao.com/worktop/logistics-list",
      "source": "user_free_text",
      "confidence": "high"
    },
    "systems[0].type": {
      "value": "browser_web",
      "source": "inferred_from_url",
      "confidence": "high"
    },
    "systems[0].login_required": {
      "value": true,
      "source": "inferred_from_login_phrase",
      "confidence": "medium"
    },
    "systems[0].account_hint": {
      "value": "admin",
      "source": "user_free_text",
      "confidence": "high"
    }
  },
  "deduplication": {
    "skipped_question_ids": [
      "system_name",
      "system_entry_url",
      "system_type"
    ],
    "confirmation_question_ids": [
      "login_required"
    ],
    "medium_confidence_strategy": "ask_confirmation_question"
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: PASS for all tests.

- [ ] **Step 5: Commit**

Run:

```powershell
git add agent_modules/interaction_schema/fixtures/deduplication-url-inference.json tests/test_interaction_schema_contracts.py
git commit -m "feat: add answer deduplication fixture"
```

---

### Task 6: Final Module Documentation And Verification

**Files:**
- Modify: `agent_modules/interaction_schema/README.md`
- Modify: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes all module files from Tasks 1-5
- Produces a README with acceptance criteria and usage notes

- [ ] **Step 1: Write the failing documentation coverage test**

Append this method inside `InteractionSchemaContractTests`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails if README is incomplete**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
```

Expected: FAIL if the README does not mention every module artifact.

- [ ] **Step 3: Update README with final artifact index and usage notes**

Replace `agent_modules/interaction_schema/README.md` with:

```markdown
# Interaction Schema Module

This module defines the first layer of the RPA requirements analyst agent: the choice-first interaction state, question format, answer recording format, next-step decision rules, and deduplication rules.

It does not evaluate RPA feasibility, break down process steps, design exceptions, or generate HTML reports.

## Artifact Index

- `schemas/interaction-state.schema.json`: interaction state contract.
- `schemas/question.schema.json`: choice-question contract.
- `schemas/answer-batch.schema.json`: answer record and state patch contract.
- `rules/decision-rules.json`: ordered next-action rules and gap stop policy.
- `rules/prompt-rules.md`: agent prompt behavior rules.
- `fixtures/valid-interaction-state.json`: baseline interaction state example.
- `fixtures/valid-question-trigger-type.json`: required trigger question example.
- `fixtures/valid-answer-batch.json`: answer record and state patch example.
- `fixtures/deduplication-url-inference.json`: answer absorption example that infers a web system from a URL and skips repeated system questions.

## Usage

Use these files as the module 1 contract for agent platform integration.

1. Render questions from `schemas/question.schema.json` compatible objects.
2. Store every user response as an answer record.
3. Apply `state_patch` values into the shared requirement state.
4. Recompute pending questions after every answer batch.
5. Use `rules/decision-rules.json` to choose the next action.
6. Use `rules/prompt-rules.md` to keep the conversation concise and non-repetitive.

## Acceptance Criteria

- Questions support only `single_choice` and `multiple_choice`.
- Questions classify importance as `required`, `recommended`, or `optional`.
- Questions support free text and require it when `other` is selected.
- Answers distinguish `answered`, `unknown`, `skipped`, `invalid`, and `needs_free_text`.
- Inferred fields preserve source and confidence.
- High-confidence inferred answers skip repeated questions.
- Medium-confidence inferred answers become confirmation questions.
- Excessive unknown required fields stop the workflow with a gap report.
```

- [ ] **Step 4: Run full verification**

Run:

```powershell
& 'C:\Users\司南\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_interaction_schema_contracts -v
git status --short
```

Expected: all tests PASS. `git status --short` shows only files modified by Task 6.

- [ ] **Step 5: Commit**

Run:

```powershell
git add agent_modules/interaction_schema/README.md tests/test_interaction_schema_contracts.py
git commit -m "docs: finalize interaction schema module"
```

---

## Self-Review

Spec coverage:

- Interaction state model is implemented by Task 1.
- Choice-question model is implemented by Task 2.
- Answer record and state patch model is implemented by Task 3.
- Next-step decision rules are implemented by Task 4.
- Question deduplication and answer absorption are implemented by Task 5.
- Final module documentation and verification are implemented by Task 6.

Placeholder scan:

- No implementation step contains TBD, TODO, "fill in details", or unspecified error handling.

Type consistency:

- `answer_status`, `confidence`, `importance`, `type`, and `next_action` values match the design spec.
- Fixture paths referenced by tests match the file structure.
- Python test helper `load_json(relative_path: str) -> dict` is defined before all tests that use it.

