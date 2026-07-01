# Platform Compatible Question Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace unsupported `*_with_text` question types with platform-compatible choice questions plus always-visible supplement text, while separating `unknown` and `other` answer semantics.

**Architecture:** Keep the interaction schema as the source of truth for rendered question controls. Use `single_choice` and `multiple_choice` for platform rendering, and add `supplement_text` as an independent always-visible input contract. Update answer-batch and requirement-memory rules so `unknown` creates gaps while `other` requires supplement text before it can become an answer.

**Tech Stack:** JSON Schema draft 2020-12, Markdown rule docs, Python `unittest`, existing `agent_modules` contracts.

## Global Constraints

- `question.type` allows only `single_choice` and `multiple_choice`.
- Every question must include both `unknown` and `other` options.
- Every question must include `supplement_text.enabled = true` and `supplement_text.always_visible = true`.
- `unknown` means the customer cannot confirm the answer now; it must not require supplement text.
- `other` means the customer knows an answer not covered by options; it requires supplement text.
- Multi-fact questions must use `multiple_choice`, not `multiple_choice_with_text`.
- Do not redesign modules 2-6 business logic in this change.

---

### Task 1: Platform-Compatible Question Schema

**Files:**
- Modify: `agent_modules/interaction_schema/schemas/question.schema.json`
- Modify: `agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json`
- Delete: `agent_modules/interaction_schema/fixtures/multiple-choice-with-text-required.json`
- Create: `agent_modules/interaction_schema/fixtures/multiple-choice-with-supplement-required.json`
- Modify: `agent_modules/interaction_schema/README.md`
- Test: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: existing question contract with `options`, `free_text`, and `retry_policy`.
- Produces: question contract with stable `type` plus `supplement_text`.

- [ ] **Step 1: Update failing schema tests**

Change `tests/test_interaction_schema_contracts.py` so:

```python
def test_question_schema_uses_platform_compatible_choice_types(self):
    schema = load_json("agent_modules/interaction_schema/schemas/question.schema.json")

    self.assertEqual(schema["properties"]["type"]["enum"], ["single_choice", "multiple_choice"])
    self.assertIn("supplement_text", schema["required"])
    supplement = schema["properties"]["supplement_text"]
    self.assertEqual(
        supplement["required"],
        ["enabled", "always_visible", "label", "placeholder"],
    )
    self.assertEqual(supplement["properties"]["enabled"]["const"], True)
    self.assertEqual(supplement["properties"]["always_visible"]["const"], True)
```

Replace the old `test_multiple_choice_with_text_fixture_supports_supplement` with:

```python
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
```

Update README artifact assertions from `fixtures/multiple-choice-with-text-required.json` to `fixtures/multiple-choice-with-supplement-required.json`.

- [ ] **Step 2: Run interaction tests and verify failure**

Run: `python -m unittest tests.test_interaction_schema_contracts -v`

Expected: FAIL because schema still allows `*_with_text`, `supplement_text` is missing, and the new fixture does not exist.

- [ ] **Step 3: Update question schema**

Modify `agent_modules/interaction_schema/schemas/question.schema.json`:

```json
"type": {
  "type": "string",
  "enum": ["single_choice", "multiple_choice"]
},
"supplement_text": {
  "type": "object",
  "required": ["enabled", "always_visible", "label", "placeholder"],
  "additionalProperties": false,
  "properties": {
    "enabled": { "const": true },
    "always_visible": { "const": true },
    "label": { "type": "string", "minLength": 1 },
    "placeholder": { "type": "string", "minLength": 1 }
  }
}
```

Add `"supplement_text"` to the schema `required` list. Keep `free_text` for backward compatibility in this task.

- [ ] **Step 4: Update fixtures**

Add `supplement_text` to `agent_modules/interaction_schema/fixtures/valid-question-trigger-type.json`:

```json
"supplement_text": {
  "enabled": true,
  "always_visible": true,
  "label": "请补充",
  "placeholder": "如选项不完整，或需要说明特殊情况，请在这里补充"
}
```

Create `agent_modules/interaction_schema/fixtures/multiple-choice-with-supplement-required.json` with:

```json
{
  "question_id": "operated_systems",
  "stage": "intake",
  "question": "这个自动化需要操作哪些平台或系统？可以多选。",
  "type": "multiple_choice",
  "importance": "required",
  "blocks_stage_progression": true,
  "allow_unknown": true,
  "target_field": "operated_systems",
  "options": [
    {
      "label": "电商平台后台",
      "value": "ecommerce_platform_backend",
      "description": "例如淘宝、京东、拼多多、抖音电商等后台。"
    },
    {
      "label": "在线表格",
      "value": "online_spreadsheet",
      "description": "例如腾讯文档、飞书表格或金山文档。"
    },
    {
      "label": "本地文件",
      "value": "local_file",
      "description": "例如 Excel、CSV 或下载文件。"
    },
    {
      "label": "不确定",
      "value": "unknown",
      "description": "目前还不清楚具体操作系统。"
    },
    {
      "label": "其他",
      "value": "other",
      "description": "系统不在上述选项中，请在补充框说明。"
    }
  ],
  "free_text": {
    "enabled": true,
    "field": "operated_systems_supplement",
    "required_when": {
      "selected_values_include": ["other"]
    }
  },
  "supplement_text": {
    "enabled": true,
    "always_visible": true,
    "label": "请补充",
    "placeholder": "如选项不完整，或需要说明特殊情况，请在这里补充"
  },
  "retry_policy": {
    "max_retries": 2,
    "fallback_to_single_question": true
  },
  "depends_on_fields": [],
  "skip_if": []
}
```

Delete `agent_modules/interaction_schema/fixtures/multiple-choice-with-text-required.json`.

- [ ] **Step 5: Update README**

In `agent_modules/interaction_schema/README.md`, replace references to `multiple-choice-with-text-required.json` with `multiple-choice-with-supplement-required.json`, and state:

```markdown
- Questions support only `single_choice` and `multiple_choice` for platform rendering.
- Every question includes `unknown`, `other`, and an always-visible `supplement_text` field.
```

- [ ] **Step 6: Run interaction tests**

Run: `python -m unittest tests.test_interaction_schema_contracts -v`

Expected: PASS for schema and fixture tests after Task 1.

### Task 2: Question Type Policy And Prompt Rules

**Files:**
- Modify: `agent_modules/interaction_schema/rules/decision-rules.json`
- Modify: `agent_modules/interaction_schema/rules/prompt-rules.md`
- Modify: `agent_platform_package/system_prompt/agent-system-prompt.md`
- Modify: `agent_platform_package/testing/stability_regression_scenarios.md`
- Test: `tests/test_interaction_schema_contracts.py`
- Test: `tests/test_stability_regression_contracts.py`

**Interfaces:**
- Consumes: Task 1 schema with `type` and `supplement_text`.
- Produces: deterministic routing policy for multi-fact questions.

- [ ] **Step 1: Update failing policy tests**

Change `test_question_type_policy_routes_coexisting_facts_to_multi_choice_with_text` to:

```python
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
    self.assertIn("output_field", policy["must_use_multiple_choice_for"])
    self.assertIn("exception_handling", policy["must_use_multiple_choice_for"])
    self.assertIn("notification_method", policy["must_use_multiple_choice_for"])
    self.assertIn("human_fallback", policy["must_use_multiple_choice_for"])
    self.assertIn("captcha_handling", policy["must_use_multiple_choice_for"])
```

Update prompt-rule assertion:

```python
self.assertIn("Use `multiple_choice`", text)
self.assertIn("Do not use `multiple_choice_with_text`", text)
```

- [ ] **Step 2: Run interaction tests and verify failure**

Run: `python -m unittest tests.test_interaction_schema_contracts -v`

Expected: FAIL because decision rules and prompt rules still reference `*_with_text`.

- [ ] **Step 3: Update decision rules**

Modify `agent_modules/interaction_schema/rules/decision-rules.json`:

```json
"question_type_policy": {
  "mutually_exclusive": "single_choice",
  "coexisting_facts": "multiple_choice",
  "must_include_unknown_option": true,
  "must_include_other_option": true,
  "must_include_always_visible_supplement_text": true,
  "must_use_multiple_choice_for": [
    "platform",
    "data_source",
    "input_field",
    "output_field",
    "object_scope",
    "exception_handling",
    "notification_method",
    "human_fallback",
    "captcha_handling",
    "capability",
    "risk",
    "prework"
  ],
  "type_selection_rules": [
    "Use single_choice only when options are mutually exclusive.",
    "Use multiple_choice when several options can be true at the same time.",
    "Use multiple_choice for platforms, systems, data sources, input fields, output fields, object scope, exception handling, notification methods, human fallback, captcha handling, capabilities, risks, and prework.",
    "Every question must include unknown, other, and always-visible supplement_text.",
    "Do not output single_choice_with_text or multiple_choice_with_text."
  ]
}
```

- [ ] **Step 4: Update prompt rules and system prompt**

In `agent_modules/interaction_schema/rules/prompt-rules.md`, replace `*_with_text` guidance with:

```markdown
- Use `single_choice` only when options are mutually exclusive.
- Use `multiple_choice` when multiple facts can coexist, such as platform, data source, input field, output field, object scope, exception handling, notification method, human fallback, and captcha handling.
- Do not use `single_choice_with_text` or `multiple_choice_with_text`.
- Every question must include `unknown`, `other`, and always-visible `supplement_text`.
```

In `agent_platform_package/system_prompt/agent-system-prompt.md`, add a plain English preserved block under the overall rules:

```markdown
## Platform-compatible question controls

- Question `type` must be only `single_choice` or `multiple_choice`.
- Do not output `single_choice_with_text` or `multiple_choice_with_text`.
- Every question must include `unknown`, `other`, and always-visible `supplement_text`.
- Use `multiple_choice` for platforms, systems, data sources, fields, object scope, exception handling, notification method, human fallback, and captcha handling.
```

- [ ] **Step 5: Update stability scenario wording**

In `agent_platform_package/testing/stability_regression_scenarios.md`, replace every `multiple_choice_with_text` with `multiple_choice with always-visible supplement_text`.

- [ ] **Step 6: Run targeted tests**

Run: `python -m unittest tests.test_interaction_schema_contracts tests.test_stability_regression_contracts -v`

Expected: PASS.

### Task 3: Answer Status Semantics

**Files:**
- Modify: `agent_modules/interaction_schema/schemas/answer-batch.schema.json`
- Modify: `agent_modules/interaction_schema/fixtures/valid-answer-batch.json`
- Create: `agent_modules/interaction_schema/fixtures/answer-batch-unknown-vs-other.json`
- Modify: `agent_modules/interaction_schema/rules/decision-rules.json`
- Test: `tests/test_interaction_schema_contracts.py`

**Interfaces:**
- Consumes: selected option values and supplement text.
- Produces: answer statuses that distinguish unknown from other.

- [ ] **Step 1: Add failing answer status tests**

Add:

```python
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

def test_unknown_and_other_fixture_have_different_semantics(self):
    fixture = load_json("agent_modules/interaction_schema/fixtures/answer-batch-unknown-vs-other.json")
    records = {record["question_id"]: record for record in fixture["answer_records"]}

    self.assertEqual(records["platform_access"]["answer_status"], "unknown")
    self.assertEqual(records["platform_access"]["semantic_route"], "gap_candidate")
    self.assertEqual(records["other_system"]["answer_status"], "answered_with_supplement")
    self.assertEqual(records["other_system"]["semantic_route"], "candidate_fact")
    self.assertEqual(records["other_without_text"]["answer_status"], "needs_free_text")
    self.assertEqual(records["other_without_text"]["semantic_route"], "supplement_required")
```

- [ ] **Step 2: Run interaction tests and verify failure**

Run: `python -m unittest tests.test_interaction_schema_contracts -v`

Expected: FAIL because new statuses and fixture do not exist.

- [ ] **Step 3: Update answer batch schema**

In `agent_modules/interaction_schema/schemas/answer-batch.schema.json`, update `answer_status.enum` to:

```json
[
  "answered",
  "answered_with_supplement",
  "unknown",
  "unknown_with_note",
  "skipped",
  "invalid",
  "needs_free_text"
]
```

Add optional `semantic_route` to each answer record:

```json
"semantic_route": {
  "enum": [
    "confirmed_answer",
    "candidate_fact",
    "gap_candidate",
    "supplement_required",
    "ignored_or_skipped"
  ]
}
```

- [ ] **Step 4: Add unknown-vs-other fixture**

Create `agent_modules/interaction_schema/fixtures/answer-batch-unknown-vs-other.json`:

```json
{
  "answer_records": [
    {
      "question_id": "platform_access",
      "selected_values": ["unknown"],
      "free_text": "",
      "answer_status": "unknown",
      "semantic_route": "gap_candidate",
      "confidence": "none"
    },
    {
      "question_id": "other_system",
      "selected_values": ["other"],
      "free_text": "还需要操作一个供应商门户网页后台",
      "answer_status": "answered_with_supplement",
      "semantic_route": "candidate_fact",
      "confidence": "medium"
    },
    {
      "question_id": "other_without_text",
      "selected_values": ["other"],
      "free_text": "",
      "answer_status": "needs_free_text",
      "semantic_route": "supplement_required",
      "confidence": "none"
    }
  ],
  "state_patch": {},
  "impact": {
    "blocks_stage_progression": true,
    "adds_pending_question": true,
    "pending_question_ids": ["other_without_text"],
    "review_notes": [
      "unknown creates a gap candidate, while other without text requires supplement."
    ]
  }
}
```

- [ ] **Step 5: Update decision rules**

Add to `agent_modules/interaction_schema/rules/decision-rules.json`:

```json
"unknown_other_semantics": {
  "unknown": {
    "meaning": "customer cannot confirm now",
    "requires_supplement_text": false,
    "semantic_route": "gap_candidate"
  },
  "other": {
    "meaning": "customer knows an answer not covered by options",
    "requires_supplement_text": true,
    "semantic_route_when_text_present": "candidate_fact",
    "semantic_route_when_text_missing": "supplement_required"
  }
}
```

- [ ] **Step 6: Run interaction tests**

Run: `python -m unittest tests.test_interaction_schema_contracts -v`

Expected: PASS.

### Task 4: Requirement Memory Handling For Unknown And Other

**Files:**
- Modify: `agent_modules/requirement_memory/rules/update-rules.json`
- Modify: `agent_modules/requirement_memory/rules/prompt-rules.md`
- Modify: `agent_modules/requirement_memory/fixtures/ecommerce-memory.md`
- Test: `tests/test_requirement_memory_contracts.py`

**Interfaces:**
- Consumes: Task 3 `semantic_route` values.
- Produces: memory rules that route unknown to gaps and other supplements to candidate facts.

- [ ] **Step 1: Add failing memory tests**

Add to `tests/test_requirement_memory_contracts.py`:

```python
def test_memory_update_rules_separate_unknown_from_other(self):
    rules = load_json("agent_modules/requirement_memory/rules/update-rules.json")
    semantics = rules["unknown_other_semantics"]

    self.assertEqual(semantics["unknown"]["memory_target"], "gaps")
    self.assertFalse(semantics["unknown"]["requires_supplement_text"])
    self.assertEqual(semantics["other_with_supplement"]["memory_target"], "confirmed_facts_or_inferred_items")
    self.assertEqual(semantics["other_without_supplement"]["memory_target"], "retired_questions_or_next_question_plan")
    self.assertTrue(semantics["other_without_supplement"]["requires_supplement_text"])

def test_memory_prompt_rules_explain_unknown_and_other_separately(self):
    text = (ROOT / "agent_modules/requirement_memory/rules/prompt-rules.md").read_text(encoding="utf-8")

    self.assertIn("unknown means the customer cannot confirm now", text)
    self.assertIn("other means the options do not cover a known answer", text)
    self.assertIn("unknown must not require supplement text", text)
    self.assertIn("other without supplement text must ask for supplement", text)
```

- [ ] **Step 2: Run memory tests and verify failure**

Run: `python -m unittest tests.test_requirement_memory_contracts -v`

Expected: FAIL because memory rules do not define unknown/other semantics.

- [ ] **Step 3: Update memory update rules**

Add to `agent_modules/requirement_memory/rules/update-rules.json`:

```json
"unknown_other_semantics": {
  "unknown": {
    "meaning": "customer cannot confirm now",
    "memory_target": "gaps",
    "requires_supplement_text": false,
    "development_use": "not_confirmed"
  },
  "unknown_with_note": {
    "meaning": "customer is uncertain but added context",
    "memory_target": "inferred_items",
    "requires_confirmation": true,
    "development_use": "not_confirmed"
  },
  "other_with_supplement": {
    "meaning": "options do not cover a known answer",
    "memory_target": "confirmed_facts_or_inferred_items",
    "requires_confirmation_when_ambiguous": true
  },
  "other_without_supplement": {
    "meaning": "other was selected but the known answer was not provided",
    "memory_target": "retired_questions_or_next_question_plan",
    "requires_supplement_text": true
  }
}
```

- [ ] **Step 4: Update memory prompt rules**

Append to `agent_modules/requirement_memory/rules/prompt-rules.md`:

```markdown
## Unknown And Other

- unknown means the customer cannot confirm now.
- other means the options do not cover a known answer.
- unknown must not require supplement text.
- other without supplement text must ask for supplement.
- unknown creates or updates a gap when the field is required.
- other with supplement can become a candidate fact or confirmed fact depending on confidence and wording.
```

- [ ] **Step 5: Run memory tests**

Run: `python -m unittest tests.test_requirement_memory_contracts -v`

Expected: PASS.

### Task 5: Deployment Guidance And Regression

**Files:**
- Modify: `agent_platform_package/testing/platform_test_checklist.md`
- Modify: `agent_platform_package/testing/expected_outputs.md`
- Test: `tests/test_platform_package_contracts.py`
- Test: `tests/test_stability_regression_contracts.py`

**Interfaces:**
- Consumes: question schema, answer semantics, and memory behavior from Tasks 1-4.
- Produces: deployment checklist for platform mapping of `supplement_text`.

- [ ] **Step 1: Add failing platform tests**

In `tests/test_platform_package_contracts.py`, add:

```python
def test_platform_docs_describe_supplement_text_mapping(self):
    checklist = (ROOT / "agent_platform_package/testing/platform_test_checklist.md").read_text(encoding="utf-8")
    expected = (ROOT / "agent_platform_package/testing/expected_outputs.md").read_text(encoding="utf-8")

    self.assertIn("supplement_text", checklist)
    self.assertIn("always_visible", checklist)
    self.assertIn("unknown is not other", checklist)
    self.assertIn("Question `type` must stay `single_choice` or `multiple_choice`", expected)
    self.assertIn("Do not output `multiple_choice_with_text`", expected)
```

- [ ] **Step 2: Run platform tests and verify failure**

Run: `python -m unittest tests.test_platform_package_contracts tests.test_stability_regression_contracts -v`

Expected: FAIL because platform docs do not yet describe `supplement_text`.

- [ ] **Step 3: Update platform checklist**

Append to `agent_platform_package/testing/platform_test_checklist.md`:

```markdown
## Platform-compatible question controls

- Question `type` must stay `single_choice` or `multiple_choice`.
- The platform should render `supplement_text.enabled = true` and `supplement_text.always_visible = true` as a default visible input box.
- Every question must show both `不确定` and `其他`.
- unknown is not other: `不确定` means the customer cannot confirm now and does not require supplement text.
- `其他` means the customer knows an answer not covered by options and should provide supplement text.
- If the platform cannot render `supplement_text`, keep the choice question stable and use the `其他` option wording as fallback.
```

- [ ] **Step 4: Update expected outputs**

Add to `agent_platform_package/testing/expected_outputs.md`:

```markdown
## Platform-Compatible Question Output

Question `type` must stay `single_choice` or `multiple_choice`.

Do not output `single_choice_with_text` or `multiple_choice_with_text`.

Every question must include:

- `unknown`
- `other`
- `supplement_text.enabled = true`
- `supplement_text.always_visible = true`

unknown is not other. unknown creates a gap candidate when required; other requires supplement text when selected.
```

- [ ] **Step 5: Run platform tests**

Run: `python -m unittest tests.test_platform_package_contracts tests.test_stability_regression_contracts -v`

Expected: PASS.

### Task 6: Full Verification, Commit, And Push

**Files:**
- Test: `tests/*.py`

**Interfaces:**
- Consumes: all prior task changes.
- Produces: committed and pushed implementation branch.

- [ ] **Step 1: Run full tests**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 2: Run text quality scan**

Run: `rg -n "TODO|TBD|UNSOURCED_FACT" agent_modules agent_platform_package tests SKILL.md`

Expected: no matches.

- [ ] **Step 3: Run diff checks**

Run: `git diff --check`

Expected: no whitespace errors. Windows line-ending warnings are acceptable if no error lines are reported.

- [ ] **Step 4: Inspect status**

Run: `git status --short`

Expected: only intended files changed, with `agent_modules.zip` remaining untracked and unstaged if it is still present.

- [ ] **Step 5: Commit implementation**

Run:

```powershell
git add SKILL.md agent_modules agent_platform_package tests docs/superpowers/plans/2026-07-01-platform-compatible-question-controls.md
git commit -m "fix: use platform compatible question controls"
```

Expected: commit succeeds.

- [ ] **Step 6: Push branch**

Run:

```powershell
git push origin codex/continuous-rpa-agent-upgrade
```

Expected: branch pushed.

## Self-Review

- Spec coverage: Tasks cover platform-compatible types, always-visible supplement text, unknown/other semantic split, memory handling, deployment docs, tests, commit, and push.
- Placeholder scan: no task contains placeholder implementation language; every change has exact file targets and expected test commands.
- Type consistency: `supplement_text`, `unknown`, `other`, `answered_with_supplement`, and `unknown_with_note` are used consistently across schema, fixtures, rules, and tests.
