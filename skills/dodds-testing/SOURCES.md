# Primary sources

Selected Kent C. Dodds articles behind this skill:

- [The Testing Trophy and Testing Classifications](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications) — confidence, cost, and test scope
- [Static vs Unit vs Integration vs E2E Testing for Frontend Apps](https://kentcdodds.com/blog/static-vs-unit-vs-integration-vs-e2e-tests) — frontend examples of each scope
- [Write tests. Not too many. Mostly integration.](https://kentcdodds.com/blog/write-tests) — integration-heavy strategy and coverage limits
- [How to know what to test](https://kentcdodds.com/blog/how-to-know-what-to-test) — prioritize use cases and critical paths
- [Testing Implementation Details](https://kentcdodds.com/blog/testing-implementation-details) — false positives, false negatives, and public behavior
- [Common mistakes with React Testing Library](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library) — semantic queries, interactions, async behavior, and `act`
- [Making your UI tests resilient to change](https://kentcdodds.com/blog/making-your-ui-tests-resilient-to-change) — selectors and accessibility
- [Stop mocking fetch](https://kentcdodds.com/blog/stop-mocking-fetch) — request-boundary interception
- [The Merits of Mocking](https://kentcdodds.com/blog/the-merits-of-mocking) — confidence surrendered at mocked boundaries
- [Test Isolation with React](https://kentcdodds.com/blog/test-isolation-with-react) — independent state and cleanup
- [Write fewer, longer tests](https://kentcdodds.com/blog/write-fewer-longer-tests) — coherent workflows over assertion quotas
- [Avoid Nesting when you're Testing](https://kentcdodds.com/blog/avoid-nesting-when-youre-testing) — explicit setup over hidden shared state
- [AHA Testing](https://kentcdodds.com/blog/aha-testing) — avoid premature test abstractions
- [How to test custom React hooks](https://kentcdodds.com/blog/how-to-test-custom-react-hooks) — component behavior versus reusable hook APIs
- [Effective Snapshot Testing](https://kentcdodds.com/blog/effective-snapshot-testing) — focused, reviewable snapshots
- [Fix the "not wrapped in act(...)" warning](https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning) — account for observable async updates
- [Make Your Test Fail](https://kentcdodds.com/blog/make-your-test-fail) — verify that a passing test is meaningful

## Reading older examples

The principles remain useful, but examples may predate the installed packages:

- Prefer Kent's later role-first guidance over early `getByText` examples.
- Derive `user-event`, MSW, matcher, and cleanup syntax from installed versions and their documentation.
- Treat Cypress, Jest, and React-specific snippets as examples, not requirements.
