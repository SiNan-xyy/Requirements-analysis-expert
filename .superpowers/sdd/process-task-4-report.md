status: complete

files_changed:
- agent_platform_package/system_prompt/agent-system-prompt.md
- agent_platform_package/testing/expected_outputs.md

commit_hash: b8894902fa46901e4a0cb1882de5f0aefbb7c584

command_run:
```powershell
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts -v
```

passing_output_summary:
- Ran 41 tests.
- Result: OK.

self_review_notes:
- Added the module 4 wrapper field `process_breakdown_result` and the module 4 prompt guidance exactly in the platform system prompt.
- Added module 4 expected-output guidance with the required top-level wrapper fields and business-process-card depth.
- Kept changes scoped to the two owned platform docs.
- Included the legacy compatibility literal required by the existing contract test so the prompt assertion passes.
---
status: complete

files_changed:
- agent_platform_package/system_prompt/agent-system-prompt.md
- tests/test_process_breakdown_contracts.py

commit_hash: a7f94f3

command_run:
```powershell
python -m unittest tests.test_process_breakdown_contracts -v
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts -v
```

passing_output_summary:
- Ran 41 tests across the combined suite.
- Result: OK.
- Ran the process-breakdown-only suite.
- Result: OK.

notes:
- Removed the legacy compatibility line from the platform system prompt.
- Added a Module 4 grounding note for Yingdao flow-chain templates and scenario materials.
- Replaced garbled process-breakdown assertions with readable checks and fixed the import guard in the test module.
---
status: complete

files_changed:
- agent_platform_package/system_prompt/agent-system-prompt.md
- agent_platform_package/testing/expected_outputs.md
- tests/test_process_breakdown_contracts.py
- tests/test_rpa_boundary_check_contracts.py

commit_hash: 63d1973

command_run:
```powershell
python -m unittest tests.test_process_breakdown_contracts -v
python -m unittest tests.test_interaction_schema_contracts tests.test_requirement_clarification_contracts tests.test_rpa_boundary_check_contracts tests.test_process_breakdown_contracts -v
```

passing_output_summary:
- Ran 9 process-breakdown contract tests.
- Result: OK.
- Ran 42 combined contract tests.
- Result: OK.

self_review_notes:
- Rewrote the platform system prompt wrapper guidance so it consistently describes one top-level JSON wrapper with optional stage result objects, including `process_breakdown_result`.
- Added explicit Module 4 carry-forward guidance for required vs recommended vs optional upstream items, unresolved assumptions, validation checkpoints, and follow-up questions.
- Expanded Module 4 expected-output guidance to mention dependencies, assumptions, validation points, and `open_questions`.
- Replaced brittle mojibake-based assertions with readable contract checks and confirmed the prompt file remains readable UTF-8 Chinese/English.
