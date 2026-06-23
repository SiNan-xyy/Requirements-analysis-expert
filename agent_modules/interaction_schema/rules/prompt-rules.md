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
