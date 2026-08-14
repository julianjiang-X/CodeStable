## Work Package 9: Global Route Governance And Spec Drift Control

Implement the root route protocol in
`codestable-maintainer/references/global-route-governance.md`, then implement
the L3/L4 spec specialization in
`codestable-maintainer/references/spec-governance-roadmap.md`.

This work package defines the actual CodeStable behavior for all routed flows
and the spec drift problems that the behavior harness will test:

- route-time brief for `cs` and root routers;
- flow-time contract for every `cs-*` skill: default level, escalation triggers,
  owner-stop conditions, allowed artifacts, skip record, finish checks, and
  behavior scenario;
- lightweight default behavior for local changes that do not alter long-lived
  intent;
- mandatory escalation when a fast path discovers capability-boundary changes,
  future-agent instruction changes, wrong specs, or finish/merge decisions;
- owner decision context after brainstorm convergence;
- owner judgment context before asking roadmap, governance, workflow, review,
  authorization, acceptance, finish, or merge decisions;
- spec router before feature, roadmap, requirement, or acceptance work;
- clarification gates before design or roadmap approval;
- requirement deltas and mechanical apply during acceptance;
- no-free-rewrite rules for long-lived requirement documents;
- historical spec rehabilitation through inventory, classification, drift
  findings, and owner decisions;
- read-only analyze passes for terminology, coverage, decision, architecture,
  and forbidden rewrite checks.

Acceptance:

- every route in the global route matrix has either a prompt/reference update, a
  deterministic validator, or an explicit future tool;
- every global route rule and every spec-governance item has at least one
  matching behavior harness scenario or explicit non-goal;
- `cs`, all root routers, and every `cs-*` skill declare default context level,
  escalation triggers, owner-stop conditions, allowed artifacts, skip-record
  format, finish-time checks, and harness scenario coverage;
- `cs-brainstorm`, `cs-feat-design`, `cs-roadmap`, `cs-req`, and
  `cs-feat-accept` get heavier spec updates only after the target artifacts and
  owner-stop rules are clear;
- no long-lived requirement can be rewritten by a standard workflow without
  delta, clarification, archive marker, or compaction review evidence.

## Skill Updates Required

Update these skills after the tools exist:

- `cs-feat-impl`: run worktree start gate before implementation and build review
  packet before subagent review.
- `cs-issue-fix`: same start gate and review packet behavior for fixes.
- `cs-refactor-ff`: keep the flow lightweight, but still run the worktree gate
  and subagent review packet for code edits.
- `cs-feat-ff`: allow fast-forward work, but call out explicit override when the
  user chooses the current checkout.
- `cs-onboard/reference/shared-conventions.md`: document gates as the source of
  truth for worktree and review requirements.
- `cs-onboard/reference/tools.md`: document every new `.codestable/tools/...`
  runtime command, arguments, JSON output shape, and safe usage examples.
- `codestable-maintainer`: replace the manual verify checklist with the new
  `verify.py` command once it exists.
- `cs-feat-impl`, `cs-issue-fix`, and `cs-refactor-ff`: call the finish gate
  before reporting that an execution worktree is ready to merge.
- `cs-onboard/reference/shared-conventions.md`: require a fresh learner report
  before worktree finish/merge readiness.

Phase 4 extends review purpose separation:

- `cs-feat-impl` and `cs-issue-fix`: use `--stage quality` by default, add
  `--stage spec` when requirement compliance is high risk, and add
  `--stage verification` for schema, security, core runtime, or production
  safety work.
- `cs-refactor-ff` and `cs-feat-ff`: keep fast paths lightweight with default
  quality review only.
- `cs-onboard/reference/shared-conventions.md`: document risk-tiered review and
  handoff context requirements.

Phase 6 extends maintainer verification:

- `codestable-maintainer`: document behavior regression as the proof that a
  workflow prompt change reproduces from a clean actor, not just in the original
  conversation.
- `plugins/codestable/skills/codestable-maintainer/tools/verify.py`: run the critical behavior suite for
  workflow-affecting changes after the behavior runner is stable.
- `cs-onboard/reference/tools.md`: document behavior harness output only as a
  maintainer tool, not as a project-runtime command copied into onboarded repos.

Phase 7 updates every routed skill after the global route governance matrix is
implemented:

- `cs`: emit route-time brief, context level, nearby route exclusions when
  ambiguous, escalation trigger, and next action.
- every `cs-*` skill: declare default context level, escalation triggers,
  owner-stop conditions, allowed artifacts, skip-record format, finish-time
  checks, and behavior scenario coverage.
- `cs-brainstorm`: generate owner decision context when discussion converges
  into feature, roadmap, or requirement work.
- `cs-feat-design` and `cs-roadmap`: run spec router and clarification gates
  before approval.
- `cs-req`: support requirement routing metadata, safe updates, and no-free-
  rewrite constraints.
- `cs-feat-accept`: apply approved requirement deltas mechanically and run a
  read-only analyze pass before completion.
- `cs-feat-ff`, `cs-issue-fix`, `cs-refactor-ff`, and `cs-guide`:
  stay lightweight by default, record explicit skips, and escalate when they
  discover capability-boundary, public-contract, or long-lived spec effects.
- `finish-worktree`: enforce learner/context report freshness, `covered_head`,
  inbox state, stale-report, and unresolved gate checks before merge readiness.
- `cs-onboard/reference/shared-conventions.md`: document global route
  governance, long-lived specs, deltas, owner context, clarification, and
  historical rehabilitation semantics.
