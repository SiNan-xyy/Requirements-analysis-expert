status: completed
files_changed:
  - agent_modules/exception_design/README.md
  - agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json
  - agent_modules/exception_design/fixtures/email-sorting-exception-design.json
  - .superpowers/sdd/exception-task-3-report.md
commit_hash: c7c77c7
tests_run:
  - python -m unittest tests.test_exception_design_contracts -v
test_result: 8 tests ran, 7 passed, 0 failed, 1 skipped (`jsonschema` not installed locally)
self_review_notes:
  - Matched the README and both fixtures to the Task 3 brief while keeping values compatible with the tightened Task 2 schema constraints.
  - Kept related upstream risks to module 3 risk identifiers and requires_* capability notes only.
  - Limited codebase edits to the three Task 3 deliverables plus the requested report file.

---
status: completed
task: Module 5 / Exception Design / Task 3 fix pass
files_changed:
  - agent_modules/exception_design/README.md
  - agent_modules/exception_design/fixtures/ecommerce-daily-report-exception-design.json
  - agent_modules/exception_design/fixtures/email-sorting-exception-design.json
  - .superpowers/sdd/exception-task-3-report.md
fix_summary:
  - Added exception flows for every `source_process_steps` entry in both fixtures.
  - Added exception cards that materially cover the module 4 exception notes called out in review, including login, permission, template, mapping, verification, mailbox, apply-label, and logging branches.
  - Documented the module 4 gating rule in the Module 5 README.
validation:
  - `python -m unittest tests.test_exception_design_contracts -v` -> 8 ran, 1 skipped (`jsonschema` not installed), 0 failed.
commit_hash_note: The exact final commit hash is added after commit time and may not be knowable inside this report until the commit is created.
