# Module 1-6 Flow Test Guide

## Goal

Verify that a vague RPA requirement can flow from interaction capture to solution packaging without losing facts, hiding missing items, or inventing implementation details.

## Expected Flow

1. Module 1 records answers and interaction state.
2. Module 2 produces boundary facts and RPA pre-screening.
3. Module 3 produces RPA boundary classification.
4. Module 4 produces business process cards.
5. Module 5 produces exception, manual review, and logging design.
6. Module 6 produces `solution_package_result`.

## Passing Signals

- `solution_package_result.fact_base.confirmed_facts` only contains confirmed or upstream-preserved facts.
- `inferred_recommendations` require confirmation.
- `missing_required_items` preserves upstream pending questions and prework.
- Unified HTML is present; customer and developer HTML may exist as compatibility views.
- The process presentation uses cards.
- `developer_alignment_status` reflects readiness instead of simply mirroring package completion.

## Failing Signals

- Module 6 hides field mapping, metric definition, permissions, template, validation, or manual review gaps.
- Module 6 claims development readiness while high-blocking missing items remain.
- Module 6 generates exact implementation parameters.
- Module 6 produces different facts across unified, customer, and developer report views.
