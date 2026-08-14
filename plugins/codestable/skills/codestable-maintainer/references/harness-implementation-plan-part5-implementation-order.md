## Implementation Order

### Phase 1: Stop Wrong-Worktree Completion

Build `codestable-doctor.py` and `codestable-worktree-gate.py`.

This phase solves:

- work done in the coordinator checkout;
- clean `git status` hiding post-baseline `main` implementation commits;
- missing review evidence for completed implementation units.

Exit criteria:

- all worktree-gate tests pass;
- implementation skills mention the start/commit gate;
- `cs-onboard/reference/tools.md` documents the runtime `.codestable/tools/...`
  commands;
- a dirty or post-baseline `main` implementation cannot pass the gate.

### Phase 2: Make Review And Commits Mechanical

Build `build-review-packet.py` and `plan-commits.py`.

Status: implemented in the CodeStable source tree. Future work should treat
these commands as the baseline behavior and extend tests before changing their
contracts.

This phase solves:

- inconsistent subagent review inputs;
- mixed commits containing code, data, logs, docs, or migrations;
- missed project doc-sync warnings when path mappings are available.

Exit criteria:

- reviewer packet can be generated from a real feature/issue/refactor unit;
- commit planner splits a mixed GammaSource-like tree into separate buckets;
- `cs-onboard/reference/tools.md` documents review-packet and commit-planner
  commands with examples;
- skills require packet generation before implementation-review output.

### Phase 3: Preserve Backlog And Verify CodeStable Deployment

Build `codestable-backlog.py` or extend doctor, then build
`plugins/codestable/skills/codestable-maintainer/tools/verify.py`.

Status: implemented in the CodeStable source tree. Future work should preserve
the pushed-branch, fresh-clone, installed-copy diff, and backlog visibility
contracts unless a new plan explicitly replaces them.

This phase solves:

- human-review and follow-up items disappearing after acceptance;
- stale installed CodeStable skill copies;
- source-only verification without remote/fresh-clone proof.

Exit criteria:

- backlog output lists every unresolved human decision point with file/line;
- maintainer verify fails on unpushed branches and installed-copy mismatch;
- CodeStable source change reports include pushed branch, fresh clone path,
  validator result, install units, and installed-copy diff result.

### Phase 4: Human/Subagent Context Harness

Extend `build-review-packet.py` with staged review purposes and add
`build-context-packet.py` for lightweight stage handoffs and audience-specific
human reports.

Status: implemented in the CodeStable source tree. Future work should keep the
default review path lightweight and use multiple stages only when risk warrants
it.

This phase solves:

- spec compliance, code quality, and verification evidence getting mixed into a
  single vague review;
- reviewers depending on hidden chat history instead of a curated packet;
- next-stage agents losing decisions, rejected options, risks, files, remaining
  work, or evidence;
- human reviewers, owners, learners, and judgment participants needing a Chinese
  report with complete working context instead of hidden chat history.

Exit criteria:

- `build-review-packet.py --stage spec` focuses on requirement compliance;
- `build-review-packet.py --stage quality` focuses on maintainability,
  security, tests, and edge cases;
- `build-review-packet.py --stage verification` requires fresh validation
  evidence;
- `build-context-packet.py --audience handoff` emits `Decided`, `Rejected`,
  `Risks`, `Files`, `Remaining`, and `Evidence`;
- `build-context-packet.py --audience human-reviewer|owner-decision|owner-judgment|learner|interviewee --language zh`
  emits `Decision Brief`, `Working Context`, and `Evidence Appendix`;
- `check-context-sufficiency.py --strict` validates packet shape, concrete file
  references, evidence items, and unredacted secret-like text before dispatch;
- skills document the risk-tiered default instead of requiring a full staged
  team pipeline for every small change.

### Phase 5: Worktree Finish And Merge Reminders

Build `codestable-finish-worktree.py`, `codestable-worktree-inbox.py`, and the
doctor integration for merge reminders.

Status: implemented in the CodeStable source tree on
`codex/backlog-semantic-upstream`.

This phase solves:

- execution worktrees being completed but forgotten after the chat context moves
  to another branch;
- learner reports being optional or stale when a branch is ready to merge;
- merge reminders living only in memory instead of repo-local state visible from
  any worktree;
- agents relying on manual owner memory to know which branches are ready.

Exit criteria:

- finish gate generates a Chinese learner report and strict context check before
  declaring a worktree ready to merge;
- finish gate records `covered_head`; after any new non-finish-artifact commit,
  the inbox reports `stale-report` until the learner report is refreshed;
- worktree inbox records ready-to-merge state under Git common-dir local state;
- doctor shows ready-to-merge and stale-report reminders from any branch;
- no command auto-merges, auto-rebases, or deletes a worktree.

### Phase 6: Agent Behavior Regression Harness

Build `agent-behavior-harness.py`, scenario fixtures, deterministic graders, and
the first critical regression suite.

This phase solves:

- workflows that only work in the current high-context design conversation;
- prompt changes that look implemented but fail in a fresh agent thread;
- compact/resume drift where the next actor ignores artifacts and invents a new
  path;
- spec-maintenance rules that are documented but not reproduced by clean agents;
- behavior regressions that are fixed once but never added to a regression bank.

Exit criteria:

- the scenario DSL supports transcript, trajectory, artifact, repo-state, and
  command assertions;
- the required critical regression scenarios above pass in `sterile` mode;
- `compact-resume-next-action` passes by recovering state from artifacts and
  status commands;
- behavior reports include per-run traces and deterministic grader failures;
- maintainer verification can run a critical behavior suite for workflow changes.

### Phase 7: Global Route Governance And Spec Drift Control

Build the root route protocol from `global-route-governance.md`, then build the
owner-review and drift-control mechanisms from `spec-governance-roadmap.md`.
Prove both layers with Phase 6 behavior scenarios before calling either stable.

This phase solves:

- `cs` automatic routing that only works in the original high-context thread;
- workflows that become too heavy because every path is treated like a spec
  change;
- fast paths that accidentally bypass spec, decision, or finish gates;
- brainstorm conclusions that lack enough human-review context;
- long-lived specs that are agent-readable but human-unfriendly;
- Q&A decisions that remain only in chat;
- wrong requirement routing when multiple docs overlap;
- uncontrolled growth or unsafe compaction of requirement documents;
- historical specs that are already drifted or organized under older rules;
- acceptance flows that miss requirement, architecture, or decision drift.

Exit criteria:

- every routed workflow declares default context level, escalation triggers,
  owner-stop conditions, allowed artifacts, skip-record format, finish-time
  checks, and harness scenario coverage;
- light paths stay L0/L1 and risky paths escalate before mutating long-lived
  facts;
- owner decision context, spec routing, clarification, requirement delta, owner
  judgment context, no-free-rewrite, rehabilitation, and analyze-pass rules are
  documented;
- affected `cs-*` skills point to the new rules and stop at the required owner
  checkpoints;
- historical spec rehabilitation can classify old docs without rewriting them;
- the behavior harness validation matrices in `global-route-governance.md` and
  `spec-governance-roadmap.md` have passing critical scenarios in `sterile`
  mode before the phase is called stable.

## Global Acceptance Criteria

The harness is considered effective only when all of these are true:

- An agent cannot complete implementation on `main` without an explicit override
  artifact.
- A clean working tree with implementation commits already made on `main` is
  still detected as blocked.
- A mixed dirty tree produces a commit plan with separate buckets.
- Every completed implementation unit has subagent review evidence or an
  explicit platform fallback.
- High-risk implementation units separate spec compliance, quality, and
  verification evidence instead of using one generic review.
- Stage handoffs are stored as compact artifacts when work crosses agents or
  lifecycle stages.
- Worktree finish readiness requires a learner report that covers the exact
  branch HEAD proposed for merge.
- Ready-to-merge worktrees are visible from any branch through the local inbox
  and doctor output.
- Human-review and follow-up backlog items remain visible across turns.
- CodeStable changes are edited in source, pushed, fresh-cloned, validated, and
  installed/diff-checked before being called done.
- Core workflow changes are behavior-regressed with sterile or compacted actors
  before they are treated as stable.
- Global route governance and spec governance changes are not considered stable
  until the corresponding behavior harness scenarios prove the original routing,
  overweight-process, drift, compaction, and human-review failures are fixed.

## Non-Goals

- Do not auto-commit or auto-merge.
- Do not replace human review decisions.
- Do not turn CodeStable into a heavyweight orchestration framework.
- Do not use installed skill copies as the source of truth.
- Do not rely on LLM-as-judge as the primary correctness mechanism for workflow
  behavior.
