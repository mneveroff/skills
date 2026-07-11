---
name: dodds-testing
description: Applies Kent C. Dodds's confidence-first principles to frontend test strategy, implementation, and review. Use when choosing test scope, writing or reviewing UI tests, using Testing Library, mocking browser APIs or HTTP, or diagnosing brittle and low-value tests.
---

# Dodds Testing

Write the smallest test that gives strong confidence in a supported use case.

## Decide what to test

1. Ask what would be worst to break. Name that user or developer use case and its observable failure.
2. Choose the cheapest scope that faithfully proves it:
   - static analysis for type- and lint-shaped failures;
   - unit tests for pure functions and dense business-logic edge cases;
   - integration tests for most component, page, and collaborator behavior;
   - E2E tests for a small set of critical cross-system paths.
3. Treat coverage as a clue, not a target. Ask which important use case is uncovered.

Spend effort where confidence returned exceeds execution and maintenance cost. “Mostly integration” does not mean no unit or E2E tests.

## Work with the repository

Before writing a test, inspect installed package versions, test configuration, nearby tests, and package scripts. Match the repository's runner and conventions while applying the principles below.

## Write tests through public behavior

- Test what users see and do, or what developer consumers pass and receive.
- Prefer one coherent workflow with all assertions needed to prove it.
- Keep each test independent and able to run alone or in any order.
- Make setup explicit. Extract helpers only after repetition reveals a useful seam.
- When practical, temporarily break the behavior to prove the test fails for the intended reason; restore it, rerun the test, and confirm it passes.

By default, do not inspect component state, private methods, hook choice, component names, CSS structure, or other details that can change without changing behavior.

## Test frontend behavior

- Compose real components, routers, providers, and stores. Intercept external HTTP at the request boundary.
- Query as a user discovers the interface: accessible role and name first, then labels or visible content. Use test IDs only when a reliable user-facing query is impractical.
- Prefer semantic HTML; do not add incorrect ARIA merely to satisfy a query.
- Use realistic user interactions and await them.
- Wait for a specific observable result: appearance, disappearance, navigation, callback, request, or other public effect. Never wait an arbitrary duration.
- Treat `act` warnings as evidence of an unobserved update before adding manual `act`.
- Test ordinary extracted hooks through their component. Test a reusable hook directly only when its API is the supported contract.

Follow the installed versions of Testing Library, `user-event`, MSW, and the test runner rather than copying historical API syntax.

## Mock deliberately

Every mock removes confidence in a real integration.

- Keep production code real when it is safe, deterministic, and inexpensive.
- Intercept HTTP at the request boundary, typically with MSW; do not mock `fetch` or an API-client module when request behavior matters.
- Mock destructive, costly, nondeterministic, slow, or unavailable boundaries.
- Keep higher-level or contract coverage for important mocked boundaries.
- In E2E tests, create prerequisites through APIs when that flow is already covered; do not repeat login or registration through the UI in every test.

## Review a test

Reject or revise it when:

- it can pass while the supported behavior is broken;
- a behavior-preserving refactor would break it;
- mocks duplicate the implementation being tested;
- selectors encode styling or DOM structure;
- async work can outlive the assertion;
- shared mutable setup makes order matter;
- a large snapshot replaces an intentional assertion.

Keep snapshots only when the output is small, stable, and genuinely reviewable.

Run the narrowest relevant test, then the repository's applicable type and lint checks. Report what was and was not verified.

## Sources

This skill synthesizes Kent C. Dodds's primary-source writing. See [SOURCES.md](SOURCES.md) for the selected articles and how later guidance supersedes older API examples.
