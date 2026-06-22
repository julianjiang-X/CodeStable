### 6. Follow-Up And Human-Review Backlog

Extend `codestable-doctor` or add:

```bash
.codestable/tools/codestable-backlog.py --json
```

It should scan CodeStable artifacts for:

- `needs-human-review`;
- `Human review required`;
- `Follow-up` / `Follow-Ups`;
- accepted or deferred P2 findings;
- `attention.md Candidates`;
- requirement / roadmap / architecture backwrite TODOs.

Acceptance:

- Human decision points are visible after the original acceptance turn ends.
- Each backlog item links to the source file and line number when practical.

### 7. CodeStable Source-Push-Clone-Install Verification

Add or document a maintainer-only workflow:

```bash
codestable-maintainer verify --branch <branch>
```

Minimum manual sequence:

1. edit the current CodeStable source checkout;
2. run local tests and skill validation;
3. commit and push branch;
4. fresh clone pushed branch;
5. validate from clone;
6. sync installed global skill copy from clone;
7. diff installed copy against clone.

Acceptance:

- A source change cannot be called complete from only the original checkout.
- Installed global skill copy is either diff-clean against the clone or the
  final report says installation was intentionally skipped.

### 8. Agent Behavior Regression Harness

Add a maintainer-only behavior harness that runs CodeStable scenarios in clean
fixture repositories with a fresh agent actor:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --scenario codestable-maintainer/scenarios/feat-design-clarify.yaml \
  --runs 3 \
  --actor sterile
```

It should evaluate behavior through trace, artifacts, and repository state, not
through a broad "looks good" answer judgment:

- fixture repositories for clean, ambiguous, drifted, and finished-worktree
  states;
- scripted user turns that simulate real CodeStable usage;
- actor modes for `sterile`, `compacted`, and `realistic` contexts;
- transcript checks for required checkpoints and owner stops;
- trajectory checks for required/forbidden workflow actions;
- artifact checks for generated files, frontmatter, sections, and JSON/YAML
  schemas;
- repo-state checks for forbidden mutations and allowed diff scopes;
- command checks for `doctor`, worktree gates, backlog, finish inbox, and
  maintainer verify outputs;
- repeated runs so a single lucky pass is not treated as stability.

Acceptance:

- a fresh no-history actor can reproduce core CodeStable routing behavior from a
  fixture repo and user prompt;
- compact/resume scenarios recover the same `next_action` from artifacts and
  status tools, not from chat memory;
- drifted-spec scenarios produce inventory, clarification, or delta artifacts
  instead of freely rewriting long-lived specs;
- permission-boundary scenarios stop for owner authorization and cannot forge
  subagent review evidence;
- behavior regression failures can be promoted into new scenario YAML files.

### 9. Global Route Governance And Spec Drift Control

Add the root route behavior defined in
`codestable-maintainer/references/global-route-governance.md`, then add the
L3/L4 spec behavior defined in
`codestable-maintainer/references/spec-governance-roadmap.md`:

- route-time brief for `cs` and root routers;
- flow-time contract for every `cs-*` skill: default level, escalation triggers,
  owner-stop conditions, allowed artifacts, skip record, finish checks, and
  behavior scenario;
- light paths that stay L0/L1 unless real risk appears;
- escalation before fast paths mutate long-lived facts, future-agent
  instructions, capability boundaries, or finish/merge state;
- owner decision context after brainstorm convergence;
- owner judgment context before approval, route, review, authorization,
  acceptance, finish, merge, or interview-style checkpoints;
- spec router before design, roadmap, requirement, or acceptance work;
- clarification gates with durable `## Clarifications` entries;
- requirement deltas instead of whole-document rewrites;
- no-free-rewrite constraints for long-lived specs;
- historical spec rehabilitation through inventory and drift findings;
- read-only analyze pass before high-risk design approval or acceptance.

Acceptance:

- every routed workflow declares its context level, escalation triggers,
  owner-stop conditions, allowed artifacts, skip-record format, finish checks,
  and harness scenarios;
- small local paths stay light and record short skips instead of producing
  heavyweight governance artifacts;
- risky paths escalate before mutating long-lived specs or future agent inputs;
- owners review small decision contexts and deltas rather than regenerated
  long-lived specs;
- human judgment checkpoints include enough terms, tradeoffs, evidence, and
  consequences before the answer is collected;
- old specs are classified before migration instead of silently cleaned up;
- requirement updates are mechanically traceable to approved deltas or
  clarifications;
- behavior harness scenarios prove the original routing, overweight-process,
  drift, compaction, and human-review failures are fixed.

## Suggested Roadmap

### Phase 1: Doctor And Worktree Gate

- Add `codestable-doctor.py`.
- Add `codestable-worktree-gate.py`.
- Extend tests for main checkout, linked worktree, override, and post-baseline
  commits.
- Update `cs-feat-impl`, `cs-issue-fix`, `cs-refactor-ff`, and
  `shared-conventions.md` to call the start gate before implementation.

### Phase 2: Review And Commit Harness

- Add `build-review-packet.py`.
- Add `plan-commits.py`.
- Update implementation skills to generate packets before subagent review.
- Update final reporting templates to include commit plan buckets.

### Phase 3: Backlog And Source Install Verification

- Add backlog scanning.
- Add maintainer skill and source-push-clone-install workflow.
- Add README entries and onboarded reference docs.

### Phase 4: Human/Subagent Context Harness

- Extend `build-review-packet.py` with `--stage spec|quality|verification`.
- Add `build-context-packet.py --audience handoff`.
- Update shared conventions and implementation skills with risk-tiered review
  defaults.

### Phase 5: Worktree Finish And Merge Reminders

- Add `codestable-finish-worktree.py`.
- Add `codestable-worktree-inbox.py`.
- Integrate inbox reminders into `codestable-doctor.py`.
- Require a fresh learner report before worktree finish readiness.

### Phase 6: Agent Behavior Regression Harness

- Add scenario YAML fixtures for clean routing, clarify, drifted specs,
  permission boundaries, compact/resume, and finish inbox reminders.
- Add a maintainer-only runner that executes those scenarios with sterile,
  compacted, and realistic actor contexts.
- Add deterministic graders for transcript checkpoints, trajectory actions,
  artifacts, git diff scope, and tool JSON output.
- Extend `codestable-maintainer/tools/verify.py` so behavior regression becomes
  part of CodeStable workflow changes once the runner is stable.

### Phase 7: Global Route Governance And Spec Drift Control

- Implement `references/global-route-governance.md`.
- Implement the L3/L4 specialization in `references/spec-governance-roadmap.md`.
- Update `cs`, all root routers, all `cs-*` skills, review authorization, and
  finish/merge workflows with context levels, escalation triggers, owner-stop
  conditions, allowed artifacts, skip records, finish checks, and harness
  scenario coverage.
- Add behavior scenarios for light paths, escalation paths, spec drift,
  compaction recovery, and finish/merge readiness before calling the behavior
  stable.

## Non-Goals

- Do not turn CodeStable into a multi-agent orchestration framework.
- Do not remove human checkpoints.
- Do not auto-commit or auto-publish from planner tools.
- Do not make installed skill copies the source of truth.
- Do not make LLM-as-judge the primary pass/fail mechanism for lifecycle
  correctness.

## Design Principle

Prompt instructions remain useful, but lifecycle correctness must be checked by
small deterministic tools. Agent behavior must also be checked from clean
scenario replays, because a workflow that only works in a long, high-context
conversation is not stable enough to call implemented.
