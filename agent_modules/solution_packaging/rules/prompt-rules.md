# Module 6 Prompt Rules

When `exception_design_result.next_stage_recommendation` is `solution_packaging`, enter Module 6.

Module 6 must produce one `solution_package_result` object. It packages upstream results into:

- a customer-facing HTML report;
- a developer-facing HTML report;
- a structured JSON fact source.

The structured JSON is the single source of truth. Do not create facts directly in HTML.

## Required Fact Separation

Separate content into:

- `confirmed_facts`: explicit user answers or upstream-confirmed facts;
- `inferred_recommendations`: agent recommendations that require review;
- `missing_required_items`: information still needed before implementation;
- `conflict_or_uncertainty`: low-confidence, inconsistent, or conditional content.

Only `confirmed_facts` may be presented as development basis.

## Readiness Status

Use `module_status` for package generation and `developer_alignment_status` for implementation readiness.

Allowed `developer_alignment_status` values:

- `ready_for_development`
- `needs_confirmation`
- `not_recommended`
- `blocked`

Most real requirements with missing field mapping, metric definition, template location, permissions, or validation method should be `needs_confirmation`.

## HTML Rules

Customer HTML is for business alignment. Developer HTML is for pre-implementation alignment. Both must be generated from the same structured fact source.

Use card-style process sections instead of swimlane diagrams.

## Prohibited Content

Do not generate exact click paths, selectors, wait times, retry counts as executable parameters, Yingdao instruction parameters, or final build guides.
