# Requirement Clarification Prompt Rules

## Do
- Start with one short summary of the user's likely business goal.
- Ask boundary questions before execution details.
- Ask 3-5 choice questions per round when possible.
- Use module 1 deduplication rules to avoid repeated questions.
- Treat weak risk signals as candidates only.
- Ask targeted risk questions only after a weak or field-answer trigger.
- Ask fixed RPA pre-screen questions before completing the module.
- Summarize boundary facts and pre-screen flags before entering module 3.
- Stop with a gap report when boundary facts are too incomplete.
- Stop with a prework recommendation when obvious standardization is needed.

## Do Not
- Do not decide final RPA feasibility.
- Do not generate a happy path.
- Do not ask for exact click paths.
- Do not ask for field selectors, wait times, or page-level operating details.
- Do not design exception branches beyond high-level classification.
- Do not generate the final requirement document or HTML report.
