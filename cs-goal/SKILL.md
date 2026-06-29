---
name: cs-goal
description: 目标达成工作流——处理有明确起点/终点、验收结果或预算边界的自主迭代任务。触发：用户给出 desired outcome / acceptance result / budget，或说"帮我达成这个 goal"、"run until accepted"、"self-iterate"、"autonomous iteration"，或在有 bounded done signal 时要求"先 grill me 再开干"。产物写入 `.codestable/goals/`，包含目标起点报告、iteration 报告和完成前功能验收。
---

# cs-goal

`cs-goal` handles bounded goals: the owner gives the starting point and desired
end state, then CodeStable aligns the goal boundary, writes a start report,
implements autonomously, verifies, self-iterates, and records functional
acceptance before completion.

This is a goal wrapper, not a replacement for feature / issue / refactor rules.
When the goal crosses a capability boundary, exposes a bug root cause, or needs
behavior-preserving refactor governance, create or reference the matching
feature / issue / refactor artifacts inside the goal iteration.

Read `reference.md` for artifact templates, `state.yaml` schema, report
headings, and recovery rules.

---

## Startup

Before acting:

1. Read `.codestable/attention.md`.
2. Read `.codestable/reference/system-overview.md` if present.
3. Read this skill's `reference.md`.
4. Read `.codestable/reference/goal-conventions.md` if present.
5. Read `.codestable/reference/approval-conventions.md` if present.
6. Read `.codestable/reference/interaction-modes.md` if present and the prompt
   mentions `interview me`, `grill me`, "采访我", or "拷问我".
7. Before code edits, review, commit, finish, or merge work, read
   `.codestable/reference/execution-conventions.md` if present.
8. Inspect `.codestable/goals/` for an active matching goal.
9. Search `.codestable/compound/` and relevant feature / issue / refactor docs
   when the goal names an existing area.

If `.codestable/` is missing, route to `cs-onboard`.

---

## When To Use

Use `cs-goal` when the owner expresses a bounded destination:

- "starting from this broken state, make the tests pass";
- "reach this acceptance result";
- "run autonomously and self-iterate";
- "keep trying until complete or blocked";
- "grill me first, then implement";
- "I care about the outcome, not the technical choices".

Do not use it for:

- pure design, roadmap, or discussion requests with no implementation goal;
- open-ended brainstorming where the owner does not yet know the end state;
- standalone "grill me" prompts that do not include a bounded destination;
- status checks or audits that do not ask the AI to drive toward completion.

---

## State Model

Mirror Codex's simple goal state:

```text
active | complete | blocked
```

`state.yaml` is the machine source of truth. Markdown is for humans. Recovery
priority is:

1. `.codestable/goals/YYYY-MM-DD-{slug}/state.yaml`
2. latest iteration frontmatter
3. Markdown body text

Never infer the current machine state from narrative prose when `state.yaml` has
a clear value.

---

## Report Language

Use the report language policy in `.codestable/attention.md` for all
human-facing prose. If attention has no report language policy, use the owner's
current conversation language.

Default to canonical unsuffixed files: `goal.md`, `iterations/{nnn}.md`, and
`functional-acceptance.md`. Add language-suffixed copies only when attention
explicitly requires multiple language copies.

---

## Phase 1: Grill Alignment

Always align the goal boundary before creating a new goal. This is lightweight
goal alignment, not full owner-heavy grill mode: keep it short, owner-level, and
limited to the goal boundary.

If the owner explicitly said `grill me` or a grill alias, allow a relentless
pass across every relevant goal, acceptance, risk, and non-goal branch before
creating the goal. In that explicit mode, write or continue the shared
`grill-context`: route-unclear rounds live under `.codestable/brainstorms/{slug}/grill/`;
after owner acceptance, copy or migrate the accepted context into the goal unit
`grill/` directory. `grill-context` must keep `source_of_truth: false`; `goal.md`
and `state.yaml` remain the goal records.

Otherwise keep alignment short and do not create grill-context docs.

Each round uses one question plus 2-4 meaningfully different choices. Include
your recommended answer when useful, marking uncertainty if the recommendation
depends on missing evidence. If a question can be answered by reading the
codebase or existing CodeStable docs, inspect those sources instead of asking
the owner. Avoid asking for implementation details unless the answer changes the
goal boundary.

Collect only:

- objective;
- starting point;
- acceptance / done signal;
- non-goals;
- budget or stopping preference if given;
- strict owner-stop conditions that are specific to this goal.

If the owner already gave enough information, summarize it and proceed.

---

## Phase 2: Create Or Resume Goal

New goal directory:

```text
.codestable/goals/YYYY-MM-DD-{slug}/
├── state.yaml
├── goal.md
└── iterations/
```

`goal.md` is the start report from interview / grill. It must exist before
implementation and include objective, start point, acceptance, non-goals, owner
decisions, unresolved assumptions, and next action.

If an active matching goal exists, resume it instead of creating a duplicate.
Read `state.yaml`, then the latest `iterations/{nnn}*.md`.

---

## Phase 3: Autonomous Iteration

One iteration is a coherent implementation / verification attempt, not a single
command.

Loop while `status: active`:

1. Choose the smallest useful next attempt from `state.yaml`.
2. Implement using existing CodeStable constraints, including worktree, review,
   spec-governance, and commit rules when they apply.
3. Verify with fresh commands or evidence.
4. Before changing `state.yaml.current_iteration`, derive the next zero-padded
   iteration number from `state.yaml.current_iteration` and existing
   `iterations/{nnn}*.md` files; never overwrite a prior report.
5. Update `state.yaml` for the completed attempt, leaving
   `current_iteration: {n}`.
6. Write exactly one canonical report for that completed iteration:
   `iterations/{nnn}.md`.
7. Continue autonomously unless an owner-stop condition fires.

Do not write reports after every command. Reports are iteration summaries.

---

## Phase 4: Functional Acceptance

Before setting `status: complete`, dispatch a subagent for product-facing
functional acceptance whenever the platform supports subagents. Record the
result in `functional-acceptance.md`.

The report must include:

- reviewer and role;
- acceptance criteria checked;
- functional evidence;
- verdict;
- residual risks;
- the final iteration that cites this acceptance.

Tests, linters, and builds are verification evidence, but they do not by
themselves close a goal. If subagent dispatch is unavailable or not authorized,
write `approval-report.md` and owner-stop instead of marking the goal complete.

---

## Strict Owner Stops

Stop and ask the owner only when:

- acceptance criteria conflict or are no longer enough to decide completion;
- the objective, start point, or terminal condition has a major ambiguity;
- continuing would change long-lived specs, public contract, or capability
  boundary beyond the recorded goal;
- the same blocker repeats for three consecutive iterations;
- budget is exhausted or nearly exhausted;
- the next step requires explicit human risk acceptance, secrets, destructive
  action, external purchase, or merge / deployment approval;
- required functional acceptance is unavailable or refused.

Write or update `approval-report.md` before stopping when no existing stage
report carries the decision context.

Normal technical choices, test failures, implementation alternatives, and local
refactors are AI-owned unless they cross one of the stops above.

---

## Exit

A goal run exits with one of:

- `complete`: acceptance evidence and functional acceptance recorded.
- `blocked`: blocker evidence and owner question recorded.
- `active`: iteration report written and next action recorded, but the current
  turn or budget ends before more work can be done.

Final replies should be short and point to `goal.md`, `functional-acceptance.md`
when present, and the latest iteration report.

---

## Guardrails

- Do not ask the owner to choose routine technical details.
- Do not let Markdown prose override `state.yaml`.
- Do not create duplicate active goals for the same objective.
- Do not skip the start report before implementation.
- Do not skip iteration reports after meaningful work.
- Do not mark complete without functional acceptance.
- Do not keep iterating after a strict owner-stop fires.
- Keep every Markdown artifact under 300 lines; split long reports.
