# Exception Design Prompt Rules

## Do

- Start from module 4 focus steps and exception notes.
- Reference module 3 risks and capability notes as exception evidence.
- Keep exception handling semi-implementation-level.
- Produce step-level exception flows.
- Define severity, trigger signal, detection basis, handling strategy, continuation policy, human intervention, record fields, and related upstream risks.
- Preserve manual review and logging requirements.
- Use module 1 choice-first format when exception handling cannot be safely designed from upstream facts.

## Do Not

- Do not override module 3's suitability decision.
- Do not rebuild module 4's happy path.
- Do not repeat module 2 boundary questions.
- Do not generate exact selectors.
- Do not generate exact click paths.
- Do not generate wait times.
- Do not generate retry counts as implementation parameters.
- Do not generate Yingdao instruction parameters.
- Do not generate the final solution blueprint.
- Do not generate HTML.
