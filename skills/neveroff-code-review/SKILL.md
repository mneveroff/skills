---
name: neveroff-code-review
description: Reviews GitHub pull requests end to end in NeverOff's style. Uses an isolated clean worktree pinned to the PR head, gathers current project and issue context, reviews code against both repository standards and the originating spec, writes a durable draft with concise first-person feedback, and posts only after approval with head-movement and thread-state checks. Use when reviewing or re-reviewing a PR, working through a PR review backlog, drafting GitHub review comments, or posting an approved review.
---

# NeverOff Code Review

Review through five stages:

**scope → context → review → draft → post**

The first four stages produce a durable draft. Do not post to GitHub until the user has read and approved that draft, unless they explicitly pre-approved posting during this session.

## Core rules

- Pin every review to a PR head SHA.
- Review from an isolated clean worktree. Do not switch, reset, clean, or modify the user's main checkout.
- Write the draft under `$TMPDIR` (else `/tmp`), unless local guidance names a different temp or review-record directory. Chat gets only that path and the verdict.
- Review only changes owned by this PR.
- Judge code on two separate axes: repository standards and the originating spec.
- Check current context, not only what existed when the PR opened.
- Verify material findings yourself before drafting. Do not paste sub-agent reports.
- Keep evidence and review logistics in the draft. Post only conclusions and actions.
- Decide the verdict from this PR's content. Stack order and upstream approval do not set the verdict.
- Treat the draft as review memory. Record findings considered and dropped.
- Re-check the PR head and state before every GitHub write.

## Stage 1: Scope the PR

### Read the current PR

Infer the owner and repository from the Git remote when possible. Fetch:

```bash
gh pr view <nr> -R <owner>/<repo> --json title,body,state,url,headRefName,headRefOid,baseRefName,reviews,reviewDecision,statusCheckRollup
```

Capture:

- PR URL, title, state, base, head branch, and head SHA.
- Current review decision and checks.
- Issue, PRD, ADR, or other spec references.
- Whether this is a first review or re-review.

### Find previous review memory

Look for a review-record location in repository guidance and existing review files. Search it for this repository and PR number. Identify:

- The latest reviewed head.
- The latest record confirmed as posted.
- Earlier `Not raised` decisions and cross-PR notes.
- Any existing unposted draft for the current head.

Do not create a duplicate draft for a head already reviewed unless the user asks. Prefer a review-record or temp path named in repository guidance. Otherwise write to `${TMPDIR:-/tmp}/<repo>-pr<nr>-<short-sha>-review.md`.

### Classify re-review movement

For a re-review, compare the prior reviewed head with the current head:

- **Content change:** the PR-owned patch changed. Review the new PR-owned content.
- **Patch-equivalent rebase or restack:** ancestry changed but the effective patch did not. Refresh context and line mappings, but do not treat unchanged content as new.
- **Retarget-only:** the base changed without a PR-owned patch change. Recompute ownership and review consequences without repeating unchanged content.

Use merge-base diffs, `git range-diff`, and patch IDs when SHAs alone are misleading. A finding belongs on the PR whose current diff owns the affected line.

Map any stacked PRs for scope and draft-only context.

## Stage 2: Prepare an isolated worktree

### Protect existing work

Inspect worktrees before creating one:

```bash
git worktree list --porcelain
```

Reuse a review worktree only when:

- Its `HEAD` equals the captured PR head SHA.
- `git status --short` is empty.
- It is clearly a review worktree for this PR.

If it is dirty, stale, or belongs to other work, leave it untouched and create a new worktree. Never repair it with reset, checkout, clean, stash, or deletion.

### Fetch and create

From the repository that owns the Git object database:

```bash
git fetch origin "<base-ref>"
git fetch origin "pull/<nr>/head"
git worktree add --detach "<review-path>" FETCH_HEAD
```

Use a distinct disposable path such as:

```text
${TMPDIR:-/tmp}/<repo>-pr<nr>-review-<short-sha>
```

Immediately verify:

```bash
git -C "<review-path>" rev-parse HEAD
git -C "<review-path>" status --short
```

The observed `HEAD` must equal the captured `headRefOid`, and the worktree must be clean. If the host does not expose GitHub pull refs, use another non-destructive fetch method, then verify the SHA in the same way.

Do not use `gh pr checkout` in the user's main checkout.

### Pin the review range

Fetch the current base and calculate the merge base. Record one stable range for the review:

```bash
git -C "<review-path>" merge-base "refs/remotes/origin/<base-ref>" HEAD
git -C "<review-path>" diff "<merge-base>...HEAD"
git -C "<review-path>" log "<merge-base>..HEAD" --oneline
```

Use fully qualified refs when a short ref is ambiguous.

## Stage 3: Gather current context

Read context in this order:

1. **Repository guidance:** `AGENTS.md`, `CLAUDE.md`, contributing guides, standards, decisions, and relevant skills.
2. **PR conversation:** all reviews, inline threads, author replies, and current checks. For re-reviews, fetch GraphQL `reviewThreads`.
3. **Previous review records:** preserve earlier scope and `Not raised` decisions unless current evidence changes them.
4. **Originating spec:** issue, PRD, ADR, design document, acceptance criteria, or user-provided brief.
5. **Shared project docs:** current architecture and domain decisions named by repository guidance.
6. **External knowledge sources:** issue trackers, meeting records, and team discussions only when a PR claim or rationale depends on them.
7. **Sibling PRs:** confirm whether claimed fixes are merged and which PR currently owns each change.

Do not trust an author reply such as “fixed” or “tracked in an issue” without checking the code or issue. A follow-up issue can close a thread only when the remaining work is intentionally outside this PR.

For strong claims, check the primary source. Distinguish:

- Current fact from target state.
- Confirmed decision from open action.
- Merged fix from open sibling PR.
- Production evidence from undeployed code or another service's telemetry.

For documentation and architecture PRs, audit claims directly against their cited sources. A merged PR must be self-contained and must not link to files that only exist in another open PR.

## Stage 4: Review

### Run the installed code-review skill

Run the installed [`/code-review`](../code-review/SKILL.md) skill for code PRs. It is expected to be present and owns the two-axis Standards and Spec process, smell baseline, sub-agent prompts, and axis reporting rules. Do not copy or redefine that guidance here.

Give `/code-review`:

- The absolute review-worktree path.
- The pinned merge base as its fixed point.
- The current head SHA and commit list.
- The spec and standards sources found during context gathering.
- The instruction to review only this PR's current owned change.

Use its two reports as review input. Do not paste them into the draft.

### Verify and synthesize

The parent reviewer must inspect every material candidate finding against:

- The current worktree and exact diff.
- Repository standards and current decisions.
- The spec or primary record.
- PR ownership and prior review history.

Drop false positives, duplicates, pre-existing issues, findings owned by another PR, and issues already enforced by tooling. Do not paste sub-agent prose into the draft.

Run relevant checks from repository guidance in the review worktree. Match effort to risk. At minimum, run `git diff --check` when appropriate.

Do not install dependencies, read ignored dependency trees, or generate broad output when repository rules prohibit it. If tests cannot run, use exact-head CI evidence and state the limit in the draft. After checks, inspect `git status --short`. Do not remove generated files or changes with destructive commands.

### Set severity and verdict

- `APPROVE`: this PR is acceptable. Remaining notes are non-blocking.
- `COMMENT`: this PR should wait for a substantive reason that does not justify a request for changes.
- `REQUEST_CHANGES`: there is a material correctness, safety, privacy, or contract problem in this PR.

Stack order, retargeting, rebase work, and upstream approval are not enough by themselves to lower the verdict. A clean reapproval may have no review body.

## Stage 5: Write the durable draft

Write this content to `${TMPDIR:-/tmp}/<repo>-pr<nr>-<short-sha>-review.md`, or to the temp/review-record directory named in local guidance. Then stop. In chat, give only the file path and verdict. Do not post during the same step.

Use this header:

```markdown
# Draft review - <owner>/<repo>#<nr> (<short title>)

**PR:** <url>
**Head reviewed:** `<sha>`
**Prior reviews:** <state and links, or "none">
**Movement:** <first review|content change|patch-equivalent rebase/restack|retarget-only>

Verdict to select in GitHub: **<Approve|Comment|Request changes>**

> **NOT POSTED** - preview for wording and substance check.
```

Use these sections:

1. `## Review body (top-level comment)`
2. `## Inline comments`
3. `## Stack context (draft only)`, when needed
4. `## Not raised (considered and dropped)`
5. `## Cross-PR consistency check (context, not for posting)`, when needed
6. `## Draft-only evidence and posting plan`

For re-reviews, split inline comments:

- `### A. Replies into existing threads`
- `### B. New inline comments`

Name replies as `A<n> - reply to <comment/thread id> (<topic>, <file:line>)`. State whether each thread will resolve.

Name new comments as `B<n> - <file:line> - <blocking status>`.

Record the worktree path, exact head, checks, limits, thread plan, and GitHub event in the draft-only evidence section.

## NeverOff voice and format

### Write like a reviewer, not an audit report

- Write as `I`: “I think”, “I can see”, “I'd”, “I'm happy with”.
- Prefer “can we...” and “could we...” for interpretation and design questions.
- Use direct wording for clear mechanical facts. Do not add fake uncertainty to a typo, broken link, or missing file.
- Keep blockers explicit even when phrased as questions.
- Give a specific positive reaction when it adds useful context. Do not build a praise sandwich.
- Vary openings and sentence shape. Do not reuse a visible template across nearby reviews.
- Prefer commas and full stops. Avoid repeated em dashes and polished, parallel sentence chains.
- Keep the top-level body short: useful reaction, remaining asks, and merge stance.
- Keep inline comments self-contained: identify the concept, explain why it matters, ask for the change, and state whether it blocks.
- State conclusions, not the checking process. Evidence belongs in draft-only sections.
- Do not summarize the author's own diff back to them.
- Acknowledge resolved prior asks in one line.
- Use mild judgement language such as “appears correct” or “holds up”, not audit marks such as “verified ✓”.

Useful starts:

- “I think this may overpromise...”
- “Can we phrase this as target state...”
- “I don't see where this contract is defined...”
- “Am I reading this right...?”
- “Tiny one:”
- “Not a blocker, but...”

### Link body and inline labels exactly

If the body references `(B1)` or `(B2)`, every matching inline must start with:

```markdown
> **B1 - blocking.** ...
```

Every body reference must have one matching inline, and every labelled inline must use the same severity in both places.

Avoid long tables in posted comments. Keep research, two-axis notes, and evidence in the draft.

### Keep thread replies short

When an old ask is satisfied, use one line or resolve without a reply:

```text
Looks correct, resolving, thanks.
```

Do not narrate the verification or explain the author's fix back to them. A longer reply is appropriate only when the thread remains open or the reply adds a new finding.

### Trim posted prose

Before approval, remove:

- Verification narration.
- Repeated conclusions and duplicate stance.
- Summaries of changes the author already knows.
- Stack and merge-order logistics.
- Any sentence that does not change the author's understanding or required action.

## Stage 6: Post only after approval

### Prevent stale writes

Immediately before each GitHub write action, fetch the PR state and `headRefOid` again. This applies to:

- Thread replies.
- Main review submission.
- Thread resolution.
- Review dismissal.
- Pending-review recovery.

If the head or PR state changed, stop. Reclassify movement, update the worktree, remap ownership and lines, and get fresh approval when the content to post would change.

### Map comments to current lines

Fetch current files:

```bash
gh api "repos/<owner>/<repo>/pulls/<nr>/files" --paginate
```

Attach each inline comment to the intended current `RIGHT`-side line. If that line is absent, unchanged, or deleted, reply to an existing thread or move the finding to the top-level body. Never attach it to a nearby unrelated line.

### Post

Post the approved review through the GitHub API with the approved event:

```bash
gh api "repos/<owner>/<repo>/pulls/<nr>/reviews" --method POST --input -
```

Use `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.

Reply to the latest relevant comment in an existing thread, not an older comment. Resolve only threads explicitly planned for resolution or clearly satisfied.

### Verify separately

After posting, verify:

- The intended main submitted review exists.
- Its event, body, and inline count match the approved draft.
- The current `reviewDecision`.
- No unsubmitted or `PENDING` review remains.
- Intended thread replies exist.
- Intended threads are resolved.
- Threads meant to remain open are still open.

GitHub records thread replies as empty `COMMENTED` reviews. Do not mistake them for the main review.

Submitted reviews cannot be deleted. Pending reviews can be deleted. If a submitted review used the wrong event, dismiss it and post the intended event.

GraphQL thread resolution requires review-thread node IDs, not REST comment IDs.

### Update the durable record

Only after verification, replace the draft marker with observed facts:

```markdown
> **POSTED YYYY-MM-DD** as `<EVENT>` review <review-url> (<body|no body>, <n> inline comments); thread replies <ids|none>; <n> threads resolved; intentional unresolved threads <ids|none>.
```

Keep the record for later review rounds.

## Final checklist

- Review worktree is clean and pinned to the recorded head.
- Main checkout was not changed.
- Review scope contains only this PR's current owned changes.
- Current repository standards and spec were both considered.
- Every material finding was checked by the parent reviewer.
- Verdict matches the actual merge stance.
- Body and inline labels match.
- Posted prose contains conclusions, not audit narration.
- Draft exists in the resolved temp path.
- Nothing was posted before approval.
- Every GitHub write used a fresh head/state check.
- Post state, pending reviews, and threads were verified.