# Approval Conventions

This file is copied by `cs-onboard` to
`.codestable/reference/approval-conventions.md`. It owns the global rule for
human approval reports.

## Core Rule

Use existing user authorization throughout the task. Routine implementation,
verification, workflow selection, and reversible edits within scope do not need
fresh approval. Ask only when a material product / scope decision is unresolved,
an action needs authorization not already given, or an enforced gate genuinely
requires an owner decision. Complete independent preparation first so the owner
can review a concrete choice.

For such decisions, use the existing canonical stage report or write a concise
human-readable approval report in the relevant `.codestable` unit. A simple
missing fact can be asked directly; it does not require a new unit or report.

Routine grill pressure-test rounds use `grill-context` docs instead. A
`grill-context` preserves owner discussion for human review, but it is not an
approval report and must not be treated as a source of truth.

Canonical stage reports can satisfy this rule when they already contain the
decision, options, recommendation, tradeoffs, evidence, consequence, and next
action. Examples:

- `cs-feat-design` design review;
- `cs-issue-analyze` fix-option analysis;
- `cs-issue-fix` fix-note / implementation review;
- `cs-feat-accept` acceptance report.

When no such stage report exists, write:

```text
{unit}/approval-report.md
```

Do not ask a bare multi-choice question when the decision needs context.

Use the report language policy from `.codestable/attention.md` for prose. If
attention has no report language policy, use the owner's current conversation
language. Keep the heading names stable so agents can parse the report reliably.

## Unit Path

Use the closest durable workflow directory:

- goal: `.codestable/goals/YYYY-MM-DD-{slug}/approval-report.md`
- feature: `.codestable/features/YYYY-MM-DD-{slug}/approval-report.md`
- issue: `.codestable/issues/YYYY-MM-DD-{slug}/approval-report.md`
- refactor: `.codestable/refactors/YYYY-MM-DD-{slug}/approval-report.md`
- roadmap: `.codestable/roadmap/{slug}/approval-report.md`
- brainstorm / interview: `.codestable/brainstorms/{slug}/approval-report.md`
- root route choice with no existing unit:
  `.codestable/brainstorms/{slug}/approval-report.md`
- unknown route: choose the closest applicable unit; do not ask the owner to
  resolve a routine directory or workflow choice.

## Triggers

Use a report when the owner must decide:

- unresolved product contracts, material scope changes, or incompatible canonical specs;
- destructive / irreversible actions, purchases, merge, deploy, or external effects
  outside existing authorization;
- a required gate override, accepted risk, or a blocker requiring owner action.

An interview / grill answer needs an approval report only when it makes one of
these decisions. Review, implementation delegation, route selection, and routine
fixes within authorized scope do not create approval checkpoints by themselves.
Respect platform delegation permissions; never invent permission from this file.

## Template

```markdown
---
doc_type: approval-report
unit: {unit path or slug}
status: pending
reason: {interview | route-choice | review-authorization | risk | merge | blocker | other}
created_at: YYYY-MM-DD
---

# Approval Report

## Decision History

## Decision Needed

## Why Now

## Context

## Options

## Recommendation

## Risks And Tradeoffs

## Non-Automatic Actions

## After You Answer
```

Omit `Decision History` for the first approval in a unit. `Options` should be
concrete and mutually exclusive. Mark the recommended option explicitly.
`Non-Automatic Actions` identifies actions still outside current authorization.
Do not list already-authorized work as awaiting another permission. Keep required
headings for tool compatibility; write only the context needed to decide.

## After Approval

After the owner answers:

1. update `status` to `approved`, `rejected`, or `superseded`;
2. record the selected option and answer date;
3. continue from `After You Answer`;
4. keep the report as history instead of deleting it.

If the same unit later needs another approval, reuse `approval-report.md` as the
single approval surface: add a dated decision-history entry for the old answer,
then replace the pending sections with the new decision. Never silently
overwrite an unresolved pending approval.
