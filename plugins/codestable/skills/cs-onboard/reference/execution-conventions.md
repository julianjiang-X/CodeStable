# Execution Conventions

This file is copied by `cs-onboard` to
`.codestable/reference/execution-conventions.md`. It owns shared execution,
worktree, review, finish, and handoff rules.

## Main Coordination And Worktree Execution

Use the lightest execution path that preserves the task's actual constraints.
Self-contained work without a formal unit needs appropriate validation, not an
invented worktree / approval / review package.

For a formal feature / issue / refactor unit, keep its code isolated in an
execution worktree and `codex/...` branch. The coordination checkout carries
shared plans. An existing authorized execution checkout can be reused; create a
worktree autonomously when isolation is needed. Follow an owner's explicit
checkout choice and record any required worktree-gate override honestly.

Goal work follows the child feature / issue / refactor contracts when such units
exist. Read only the sections below relevant to the current operation.

## Shared Planning Surface

Use this worktree and synchronized plans as the execution baseline. Read sibling
unmerged code only when the user requests comparison or explicit stacked work;
do not treat it as approved or integrated. Shared intent travels through:

- `.codestable/goals/**`
- `.codestable/features/**`, `.codestable/issues/**`, `.codestable/refactors/**`
- `.codestable/roadmap/**`
- `.codestable/compound/**`
- owner-designated temporary coordination docs

Record derived plan changes within authorized scope on the shared planning
surface. Ask for owner judgment only for unresolved product / scope / risk
decisions; use the existing stage report or `approval-report.md`.

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

- Execute against this worktree and synchronized shared plans.
- Escalate material product / scope conflicts; resolve routine implementation choices.
- Treat missing env / secrets as environment blockers, not code failures.

## Independent Code Review

Review effort follows risk. Self-contained work outside a formal execution unit
can use inline review and the smallest authoritative validation. Do not create a
subagent merely to review a trivial batch or repeat an already-sufficient check.

Formal execution units still require an independent implementation review before
completion: the current worktree / finish tools validate that artifact. Group a
coherent implementation candidate for review rather than dispatching on every
small edit. Additional spec, security, or verification reviews follow the actual
risk requirements in `assurance.md`; a fast lane does not remove those safeguards.

Use delegation only when available and permitted by the current environment and
user instructions. Reuse existing authorization; do not create a separate
approval checkpoint for a review that is already authorized. If permission is
actually missing and formal closure depends on it, prepare the candidate and
review packet before asking, identifying the specific gate requirement.

Generate the smallest useful review packet:

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

Do not include `.env`, tokens, secrets, or local credentials.

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

Keep a healthy reviewer running and retain its run identity. Do not replace an
active reviewer just to change dispatch methods. On a failed run with no report,
check agent / packet state and make one bounded retry or escalate. Failed runs
without reports do not consume the three-round review budget.

### Reviewer Is A Leaf

The reviewer must not create, delegate to, or wake any sub-agent. It returns a
terminal report with findings or `NeedsContext` identifying missing evidence and
scope already checked. The main thread owns fixes; unresolved blocking findings
cannot be reported as a pass.

### When The Reviewer Returns No Report

If the final message lacks a report, inspect the accessible transcript once.
A complete recovered report is a valid terminal report. Never invent findings or
rerun completed analysis solely because the final message is empty. When no
report is recoverable, use the bounded recovery in Reviewer Health.

## Context Packets

For multi-stage handoff:

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience handoff --output /tmp/codestable-handoff.md --decided "{已决定}" --remaining "{下一步}"
```

For human-facing handoffs that need a generated context packet:

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience human-reviewer --language {en-or-zh} --output /tmp/codestable-human-review.md --decided "{decided}" --remaining "{next step}" --evidence "{verification evidence}"
```

Choose `{en-or-zh}` by mapping `.codestable/attention.md` to a supported tool
language. If the project's report language policy is not covered by the tool's
`--language` choices, write or adapt the human-facing report in the project
language instead of passing the raw attention prose as a CLI value.

When using a generated handoff packet, run its sufficiency gate before sending:

```bash
python3 .codestable/tools/check-context-sufficiency.py --file /tmp/codestable-human-review.md --strict --json
```

## Finish And Commit Gates

For a formal unit, before finish / merge:

```bash
python3 .codestable/tools/codestable-finish-worktree.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --json --validation "{验证命令} -> {结果}"
```

Finish gate writes learning, context-check, merge-readiness, and inbox records.
If a branch changes after the finish report, state becomes `stale-report` and
finish must rerun.

Within existing commit authorization, commit finish artifacts when the gate passes:

```bash
git add .codestable/features/YYYY-MM-DD-{slug}/{slug}-learning-report.md \
  .codestable/features/YYYY-MM-DD-{slug}/{slug}-learning-context-check.json \
  .codestable/features/YYYY-MM-DD-{slug}/{slug}-merge-readiness.json
git commit -m "docs: add {slug} finish report"
```

For a formal execution unit, before commit or completion report:

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

Delegate only a concrete, bounded task that can proceed independently while the
main thread does useful work, and only when delegation is authorized. Independent
review of a risky candidate or parallel investigation of distinct uncertainties
can help; task size or subsystem count alone does not justify agents. Keep
integration, verification, and final reporting with the main thread.
