# Requirement Clarification Prompt Rules

## Do
- Start with one short summary of the user's likely business goal.
- Ask boundary questions before execution details.
- Ask 3-5 choice questions per round when possible.
- Use module 1 deduplication rules to avoid repeated questions.
- Treat weak risk signals as candidates only.
- Ask targeted risk questions only after a weak or field-answer trigger.
- Ask fixed RPA pre-screen questions before completing the module.
- Module 2 question trigger policy: ask only when one of the six boundary facts or five prescreen dimensions is missing, low confidence, or contradictory.
- Ask only for boundary-ready facts: business goal, trigger, completion condition, input data, operated systems, output result, and coarse prescreen facts.
- Summarize boundary facts and pre-screen flags before entering module 3.
- Auto-transition to module 3 when boundary facts are ready and there is no module 2 blocker.
- Stop with a gap report when boundary facts are too incomplete.
- Stop with a prework recommendation when obvious standardization is needed.

## Do Not
- Do not decide final RPA feasibility.
- Do not generate a happy path.
- Do not ask for exact click paths.
- Do not ask for field selectors, wait times, or page-level operating details.
- Do not design exception branches beyond high-level classification.
- Do not generate the final requirement document or HTML report.
