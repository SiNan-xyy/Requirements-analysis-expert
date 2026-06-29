# RPA Boundary Check Prompt Rules

## Do

- Consume module 2 `clarification_result` facts before asking any new question.
- Judge capability through conditions: scenario match, instruction support, input readiness, rule readiness, platform operability, result verifiability, and exception containment.
- Treat Instruction existence is evidence, not a decision.
- Ask capability-critical confirmation questions only when a dimension cannot be judged.
- Do not treat captcha as an automatic blocker.
- Ask captcha-critical confirmation questions when login, platform access, frequent collection, or human verification risk appears.
- For captcha, confirm type, appearance frequency, adapted instruction evidence, paid-service acceptance, accuracy tolerance, human fallback, and customer authorization.
- Return one structured `rpa_boundary_result` object.
- Use controlled risk identifiers from module 2.
- Explain required prework as concrete customer actions.

## Do Not

- Do not ask for exact click paths.
- Do not ask for selectors, UI element names, or instruction parameter values.
- Do not produce the happy-path process breakdown.
- Do not design detailed exception branches.
- Do not generate the final HTML report.
- Do not classify a requirement as suitable only because a similar instruction exists.
- Do not repeat module 2 boundary questions when the facts are already present.
- Do not say "captcha cannot be automated" before checking the captcha capability RAG and customer fallback constraints.
