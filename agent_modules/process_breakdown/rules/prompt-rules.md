# Process Breakdown Prompt Rules

## Do

- Start from module 3's decision and prework.
- Preserve module 2 boundary facts instead of asking them again.
- Generate 4-8 business-readable process cards for typical automation needs.
- Attach candidate Yingdao capability families where useful.
- Ask module 4 process questions when the implementation path, repeated object, loop scope, field mapping, branch condition, write target, or candidate capability family cannot be inferred from upstream facts.
- Mark exception topics for module 5 without designing them.
- Summarize cross-step dependencies such as account permissions, field mapping, template readiness, date scope, and result logging.
- Auto-transition to module 5 when business process cards are coherent and exception topics can be handed off.

## Do Not

- Do not ask for exact button names.
- Do not generate selectors or wait times.
- Do not design exception branches.
- Do not generate retry counts or detailed error handling.
- Do not generate instruction parameter values.
- Do not override module 3's suitability decision.
- Do not produce a final build guide.
- Do not produce HTML.
