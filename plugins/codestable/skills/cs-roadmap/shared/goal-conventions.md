# Goal Conventions

This file ships inside each skill that uses it, as `shared/goal-conventions.md` in that skill's
directory. Its source is `cs-onboard/reference/goal-conventions.md`. It defines the shared runtime shape
for `cs-goal`.

## Purpose

Goals are bounded start/end work units. The owner defines the outcome and
acceptance signal; AI aligns the boundary, writes a start report, implements,
verifies, self-iterates, and writes iteration reports. A goal can close only
after subagent functional acceptance of the produced result.

Use goals when the request says "reach this result", "run until accepted",
"self-iterate", "AI implements autonomously", or "grill me first, then
implement" with a bounded done signal.

If the owner explicitly says `grill me` or a grill alias in a bounded goal
request, goal alignment may be relentless: walk every relevant objective,
acceptance, risk, and non-goal branch one question at a time, provide your
recommended answer, and inspect code or existing CodeStable docs instead of
asking questions those sources can answer.

In that explicit owner-heavy mode, write or continue `grill-context` docs. Route
unclear rounds live under `.codestable/brainstorms/{slug}/grill/`; after owner
acceptance, copy or migrate the accepted context into the goal unit `grill/`
directory. Keep `source_of_truth: false`: `state.yaml` and `goal.md` remain the
goal records.

Do not route standalone "grill me" prompts here unless a bounded destination is
known. Without a start/end objective or observable acceptance, use the global
interaction modes in `shared/interaction-modes.md`, usually via
`cs-brainstorm`.

## Report Language

Goal files are read by agents: write each in one language, the one
`.codestable/attention.md` names, or the language of the project's existing
records when it names none. Content for the owner (final report,
`approval-report.md`, conversation) uses the owner's language. Do not write
bilingual copies; add a second language only to a document whose human reader
attention names.

Use the canonical unsuffixed files below.

## Directory

```text
.codestable/goals/YYYY-MM-DD-{slug}/
├── state.yaml
├── goal.md
├── functional-acceptance.md
├── grill/
│   └── round-NNN-{axis}.md
└── iterations/
    └── 001.md
```

The directory date is the goal creation date. `state.yaml.goal` remains the bare
slug so humans and agents can compare related dated units without parsing the
filesystem name.

`state.yaml` is the machine source of truth. Markdown is human-readable context.
Recovery priority is `state.yaml` > latest iteration frontmatter > Markdown
body.

A goal directory is working state, not an archive. At a terminal state it follows
the shared closure rule in `shared/shared-conventions.md` section 3: graduate,
closing commit (outcome in its message), finish gate if it applies, then delete
the directory in its own commit. At
`blocked`, prune and delete nothing: the directory is the recovery record.

`functional-acceptance.md` is created only during the terminal acceptance gate,
not as an empty file at goal start.

`goal.md` is the start report from interview / grill. It must exist before
implementation and include objective, start point, acceptance, non-goals, owner
decisions, unresolved assumptions, and next action.

## State Model

```text
active | complete | blocked
```

Required `state.yaml` fields:

- `schema_version`
- `goal`
- `status`
- `objective`
- `start_point`
- `acceptance`
- `non_goals`
- `budget`
- `current_iteration`
- `next_action`
- `blocker_signature`
- `blocker_count`
- `owner_stop`
- `updated_at`

`current_iteration` means the last completed iteration, not the next
in-progress attempt.

## Iteration Numbering

Before changing `current_iteration`, compute the next `{nnn}` as:

```text
max(state.yaml.current_iteration, highest existing iterations/{nnn}*.md) + 1
```

Write `iterations/{nnn}.md`, then leave `state.yaml.current_iteration` equal to
that completed number. Never overwrite an existing iteration file. A
`iterations/{nnn}.{lang}.md` copy exists only when attention names the human
reader who needs that language.

## Reporting

Each completed iteration writes the canonical report:

- `iterations/{nnn}.md`

Reports are not command logs. One iteration equals a coherent implementation and
verification attempt. Include: understanding, implementation approach,
changes, verification evidence, problems, next attempt, and state update.

Before `status: complete`, write:

- `functional-acceptance.md`

This report records subagent functional acceptance of the product / artifact
against the owner acceptance criteria. Include reviewer, scope, functional
evidence, verdict, residual risks, and the final iteration that cites it. Tests
alone are not enough to complete a goal.

## Strict Owner Stops

Stop only when:

- acceptance criteria conflict;
- objective / start / terminal condition has major ambiguity;
- continuing changes long-lived specs, public contract, or capability boundary
  beyond the recorded goal;
- the same blocker repeats for three consecutive iterations;
- budget is exhausted or nearly exhausted;
- risk acceptance, secrets, destructive action, external purchase, merge, or
  deployment approval is required;
- required functional acceptance is unavailable or refused.

Routine technical choices and ordinary failed attempts stay AI-owned.
