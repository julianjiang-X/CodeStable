# Execution Conventions

This file is copied by `cs-onboard` to
`.codestable/reference/execution-conventions.md`. It owns shared execution,
worktree, review, finish, and handoff rules.

## Main Coordination And Worktree Execution

CodeStable separates discussion / planning from code edits:

- **Main coordination checkout**: where the owner discusses requirements and
  writes design / analysis / roadmap / checklist, usually the `main` checkout.
- **Execution worktree**: where code changes happen. Each feature / issue /
  refactor uses its own git worktree and `codex/...` branch unless the owner
  explicitly approves direct edits in the current checkout.

Goal work may use `.codestable/goals/YYYY-MM-DD-{slug}` as the wrapper unit, but
code edits still obey the feature / issue / refactor worktree rules when those
flows apply.

## Short Correct Usage

1. Start: `cs {goal}`. The agent routes to feature / issue / refactor / explore
   / goal.
2. Implement: `开 worktree 实现`. The agent starts in an execution worktree and
   runs the start gate.
3. Review: `允许 subagent`. Completed code batches require independent review.
4. Commit: `提交这批实现`. Run validation, commit planner, and commit gate.
5. Finish: `finish worktree`. Run finish gate and record merge readiness.
6. Solidify finish artifacts: commit the generated finish report files.
7. Merge: only after explicit owner approval.

## Shared Planning Surface

Worktrees must not read sibling unmerged code diffs. Shared intent travels
through:

- `.codestable/goals/**`
- `.codestable/features/**`, `.codestable/issues/**`, `.codestable/refactors/**`
- `.codestable/roadmap/**`
- `.codestable/compound/**`
- owner-designated temporary coordination docs

If an execution worktree discovers the plan must change, sync the plan change
back through the shared planning surface or stop for owner judgment with an
`approval-report.md` when no stage report already carries the decision context.

## Before Creating An Execution Worktree

Confirm:

1. whether the current checkout is coordination or execution;
2. the spec / checklist / analysis / goal state is readable;
3. worktree path, branch, scope, and sibling-worktree boundaries are clear;
4. the worktree starts from the target baseline, not from another feature
   worktree unless stacked development is explicit.

Run start gate before implementation:

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/features/YYYY-MM-DD-{slug}
```

For goal-wrapped work, the gate unit should be the child feature / issue /
refactor unit when one exists. If the goal has no child unit yet, record the
reason in the goal iteration and follow the lightest applicable execution path.

## Worktree Rules

- Read only the shared planning surface and this worktree's code.
- Read sibling intent only after it is synchronized into shared docs.
- Stop for owner judgment when plan conflicts appear.
- Treat missing env / secrets as environment blockers, not code failures.

## Independent Code Review

Every execution worktree must trigger independent review before reporting a
completed implementation batch. Review is a completion gate, not a commit-time
afterthought.

If the current conversation has no subagent / delegation authorization, ask with
owner judgment context before implementation review. When this is not already
captured in a stage report, write `{unit}/approval-report.md` first:

```text
Context: CodeStable requires independent implementation review before completion.
Term: Subagent Review = a separate reviewer agent performs read-only review.
Why it matters: P0/P1 issues may otherwise surface after completion.
Options:
1. Subagent Review (recommended) - dispatch a reviewer before completion.
2. Inline Review - valid only if this platform has no subagent support.
Default: Subagent Review.
Non-automatic: This does not commit, merge, push, or accept findings.
Question: Which review authorization should CodeStable use?
```

Generate the smallest useful review packet:

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

Do not include `.env`, tokens, secrets, or local credentials.

Implementation review is the floor and always runs. Whether to add further
review stages (spec, security, verification) is decided by actual risk, not by
task shape — see `.codestable/reference/assurance.md`. Line count, file count,
and task kind are not risk proxies.

Review results land in `{slug}-implementation-review.md` with
`reviewer: subagent`. Use `reviewer: self` only when the platform truly lacks
subagents and `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1` is set.

### Freeze The Review Target

Freeze one explicit target before dispatching, and record its identifier in the
review packet:

- **diff review**: prefer the staged diff; an explicit git range or patch also
  works;
- **spec / design review**: freeze the document version — either a committed
  file version, or the full text plus its SHA-256 inside the packet;
- **audit**: freeze commit plus scope identifier.

When the target is carried as packet text, the reviewer reviews exactly that
text. Do not move the target or its worktree before the reviewer returns; if it
moves, the round is void — refreeze the complete target and then decide
follow-up or replacement by the lineage rules below.

### Reviewer Lineage

- A review **stage** is defined by a single review purpose. Spec review, change
  review, contract review, and final acceptance are **different stages**.
- The first round of every stage must use a **fresh reviewer** created by the
  main thread, independent from the implementer.
- Only re-review of fixes made for *this stage's* findings stays in the same
  stage. It must reuse **the same reviewer's same session** as a follow-up,
  carrying the new frozen target, both hashes, and a fix summary.
- Follow-up re-review must check the **complete current candidate plus this
  round's fix delta**, and report every prior finding as `resolved` /
  `unresolved` / `new findings`. Ticking off old findings without rechecking the
  whole candidate is not a valid re-review.
- Reviewer independence means independent *from the implementer*. It does not
  require the reviewer to forget its own previous round.
- A changed review purpose starts a new stage with a new fresh reviewer.

### Round Budget

- At most **3 rounds with a terminal report per stage**. Replacing the reviewer
  does not reset the count.
- Replace the reviewer only when: the original run failed or is unrecoverable;
  capability no longer fits; target, scope, design, or core path changed
  materially; the reviewer declares it cannot stay independent; or the owner
  asks for a second opinion. Replacement creates a fresh reviewer.
- If blocking findings or disagreement survive the budget, escalate to the owner.
  Do not keep trading rounds and do not declare completion.

### Reviewer Health

Bind the reviewer to its run and record the run identity. The run is **healthy**
when the target is still valid, capability still fits, and the reviewer is
`running` — or is `Awaiting` with a queryable run identity that still resolves
as active.

- While healthy, wait for the terminal report. Do not cancel, re-create, or
  dispatch a parallel reviewer just because a better dispatch method appeared.
- The round **fails without consuming budget** only when the run clearly failed
  or terminated with no report, is idle / `Awaiting` with no recoverable run
  identity, capability no longer fits, or the target became invalid.
- On failure, check the review packet and agent state first, then choose one
  bounded retry, a different dispatch method, or owner escalation. Do not blindly
  re-dispatch.

### Reviewer Is A Leaf

The reviewer is a leaf executor:

- it must not create, delegate to, or wake any sub-agent;
- it must not re-dispatch review to another flow;
- every invocation must return a terminal result. When context is insufficient
  it returns `NeedsContext` with the missing items and the scope already
  checked — never `idle`, `Awaiting`, or no result;
- blocking findings unresolved means it must not report "pass".

Fixing is the main thread's job, not the reviewer's.

### When The Reviewer Returns No Report

Reviewers ending on `Idle.` or a bare "report delivered" line while the analysis
itself completed is a **common** failure, not a theoretical one. Restating the
rule above in the dispatch prompt does not reliably prevent it. So the caller
recovers rather than re-runs:

1. **Read the agent's transcript before concluding anything.** The report is
   usually present in an earlier assistant message; the final message is what
   got lost. Extract the longest assistant text block from the run's `.jsonl`
   and check whether it is a complete report.
2. **A recovered report is a valid terminal report.** Consume it, and do not
   spend a round re-dispatching for something already produced.
3. Only when the transcript truly holds no report does the round count as
   failed-without-report — then apply the reviewer-health rules above (one
   bounded retry, a different dispatch method, or owner escalation).
4. Never substitute your own judgment for the missing report and never report
   review results the reviewer did not produce.

Token cost is the reason this matters: a completed analysis re-run from scratch
costs a full review for output that already exists.

## Context Packets

For multi-stage handoff:

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience handoff --output /tmp/codestable-handoff.md --decided "{已决定}" --remaining "{下一步}"
```

For human-facing reports:

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience human-reviewer --language {en-or-zh} --output /tmp/codestable-human-review.md --decided "{decided}" --remaining "{next step}" --evidence "{verification evidence}"
```

Choose `{en-or-zh}` by mapping `.codestable/attention.md` to a supported tool
language. If the project's report language policy is not covered by the tool's
`--language` choices, write or adapt the human-facing report in the project
language instead of passing the raw attention prose as a CLI value.

Run sufficiency gate before sending:

```bash
python3 .codestable/tools/check-context-sufficiency.py --file /tmp/codestable-human-review.md --strict --json
```

## Finish And Commit Gates

Before finish / merge:

```bash
python3 .codestable/tools/codestable-finish-worktree.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --json --validation "{验证命令} -> {结果}"
```

Finish gate writes learning, context-check, merge-readiness, and inbox records.
If a branch changes after the finish report, state becomes `stale-report` and
finish must rerun.

Commit finish artifacts as a small final commit when the gate passes:

```bash
git add .codestable/features/YYYY-MM-DD-{slug}/{slug}-learning-report.md \
  .codestable/features/YYYY-MM-DD-{slug}/{slug}-learning-context-check.json \
  .codestable/features/YYYY-MM-DD-{slug}/{slug}-merge-readiness.json
git commit -m "docs: add {slug} finish report"
```

Before commit or final report:

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/features/YYYY-MM-DD-{slug}
```

Useful status tools:

```bash
python3 .codestable/tools/codestable-doctor.py --root . --json
python3 .codestable/tools/codestable-backlog.py --root . --json
python3 .codestable/tools/codestable-worktree-inbox.py --root . --json
```

Snooze accepted merge deferrals:

```bash
python3 .codestable/tools/codestable-worktree-inbox.py --root . --snooze codex_slug --until 2026-06-12T00:00:00Z --json
```

## Subagent Implementation Choice

Review requires subagents when available. Implementation subagents are optional
and should be proposed when work crosses more than three subsystems, needs
parallel slices, touches high-risk migration / concurrency / runtime contracts,
or exceeds single-thread context. The main thread keeps integration,
verification, and final review ownership.
