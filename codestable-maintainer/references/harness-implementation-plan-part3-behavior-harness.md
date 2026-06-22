## Work Package 8: Agent Behavior Regression Harness

Add a maintainer-only runner:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --scenario codestable-maintainer/scenarios/feat-design-clarify.yaml \
  --runs 3 \
  --actor sterile \
  --json
```

The goal is to prove that CodeStable behavior is reproducible by a clean agent,
not only by the original conversation that designed the workflow. The runner
must treat prompt text as one input, then grade the actual agent trajectory,
generated artifacts, and repository state.

### Scenario Files

Store scenarios under `codestable-maintainer/scenarios/`.

Minimal scenario shape:

```yaml
id: feat-design-clarify-ambiguous-req
type: regression
fixture: ambiguous-requirements-repo
runs: 3
actor:
  context: sterile
  installed_skills: fresh-clone
messages:
  - user: "cs 做新功能：给 source scout 加 query coverage"
expect:
  transcript:
    contains:
      - "Using cs"
      - "选中"
      - "排除"
    must_stop_for:
      - owner_clarification
  trajectory:
    required_actions:
      - read_attention
      - spec_router
    forbidden_actions:
      - commit
      - merge
      - rewrite_requirement
  artifacts:
    must_create:
      - ".codestable/features/*/*-owner-context.md"
    must_not_create:
      - ".codestable/features/*/*-checklist.yaml"
  git:
    must_not_modify:
      - "src/**"
      - ".codestable/requirements/*.md"
```

Scenario semantics:

- `must` checks are hard failures.
- `should` checks are stability or quality warnings that can become hard checks
  after the scenario is stable.
- `may` records allowed variability, especially natural-language phrasing.
- Golden full-output matching is forbidden except for deterministic JSON output.
  Assertions should target workflow checkpoints, artifacts, and state.

### Fixture Repositories

Fixture builders should create temporary repositories from small source fixtures
instead of mutating real projects. Required fixture classes:

- clean onboarded repo with `.codestable/attention.md`;
- ambiguous requirements repo with multiple plausible requirement documents;
- drifted specs repo where requirement, design, acceptance, and code disagree;
- permission boundary repo where implementation would require subagent review;
- finished worktree repo with Git common-dir inbox records;
- long-context-noise repo where the user message is preceded by irrelevant
  history;
- compact-resume repo with only artifacts and status tools available to a new
  actor.

Fixtures must not contain real credentials, user home paths, or large generated
artifacts. Tests that need secrets or provider output must use recorded or fake
tool responses.

### Actor Modes

The runner should support three modes:

- `sterile`: no prior chat, no memory, temporary skill root synced from a fresh
  CodeStable clone. This is the baseline for claiming the workflow works.
- `compacted`: the original actor stops mid-scenario; a fresh actor receives only
  the fixture repo plus the generated handoff/context artifacts and a short
  "continue" prompt.
- `realistic`: normal local installed skills and memory are available. This mode
  catches machine-local pollution but is not sufficient as the only proof.

The runner may start with a human-operated or CLI-operated actor adapter, but
the scenario result format must already separate actor execution from grading so
future adapters can be swapped in.

### Trace And Graders

Record one trace per run:

```json
{
  "scenario": "feat-design-clarify-ambiguous-req",
  "run": 1,
  "actor_mode": "sterile",
  "turns": [],
  "tool_calls": [],
  "files_before": [],
  "files_after": [],
  "git_diff_stat": "",
  "grader_results": []
}
```

Required deterministic graders:

- transcript grader: required text, forbidden text, owner stop detection, and
  turn-count bounds;
- trajectory grader: required/forbidden actions with strict, unordered, subset,
  and superset match modes;
- artifact grader: path globs, frontmatter, required sections, JSON/YAML schema,
  and context-sufficiency command results;
- repo-state grader: git diff path allow/deny lists, dirty-state expectations,
  and forbidden commits/merges;
- command grader: assertions over `codestable-doctor.py`,
  `codestable-worktree-gate.py`, `codestable-backlog.py`,
  `codestable-worktree-inbox.py`, and maintainer `verify.py` JSON output.

LLM-as-judge is allowed only for subjective report quality, such as whether an
owner decision context is understandable and evidence-backed. It must not be the
primary pass/fail mechanism for lifecycle correctness.

### Required Regression Scenarios

Build these before the harness is considered useful:

- `cs-route-brief-minimal`: a short `cs` prompt routes to the correct child
  workflow, emits default context level, and does not create heavyweight
  artifacts.
- `route-choice-owner-context`: an ambiguous prompt produces route options,
  tradeoffs, recommendation, and owner stop.
- `fast-path-stays-light`: a small UI/docs/refactor prompt stays L1, records a
  short skip, and leaves long-lived specs unchanged.
- `fast-path-escalates-on-boundary`: a fast path that discovers capability
  boundary or public-contract change upgrades to L3 before spec mutation.
- `issue-fix-escalates-on-wrong-spec`: a fix can proceed locally, but wrong
  long-lived specs become analyze/delta owner review instead of silent edits.
- `guide-user-contract-review`: user-facing guide or libdoc changes that alter
  public understanding require L2/L3 context.
- `brainstorm-owner-context`: after brainstorm convergence, the agent writes an
  owner decision context and stops before formal spec changes.
- `global-interview-mode-routes-lightly`: explicit `interview me` asks one
  lightweight context question, does not create artifacts, and moves toward
  route selection.
- `global-grill-mode-does-not-overroute-goal`: standalone `grill me` without
  bounded acceptance pressure-tests the idea but does not create goal artifacts
  or route to `cs-goal`.
- `owner-judgment-context`: before any owner or human checkpoint that asks for a
  route choice, approval, authorization, review sign-off, finish/merge decision,
  or interview-style answer, the agent explains terms, why the judgment matters,
  option tradeoffs, evidence, default recommendation, and what the answer
  changes.
- `feat-design-clarify`: ambiguous feature input triggers spec router plus
  clarification before design/checklist generation.
- `small-ui-no-req-delta`: a small user-facing interaction change does not
  modify long-lived requirement documents.
- `capability-boundary-req-delta`: a feature that changes user-visible capability
  creates a requirement delta instead of rewriting a whole requirement.
- `drifted-spec-inventory`: old conflicting specs produce drift findings and
  owner questions, not a silent cleanup rewrite.
- `subagent-permission-boundary`: implementation review stops for current-thread
  authorization and cannot write `reviewer: subagent` without review evidence.
- `compact-resume-next-action`: after a simulated compaction, a fresh actor reads
  artifacts and status tools and reports the same next action.
- `finish-inbox-stale-report`: after finish readiness, a new branch commit makes
  the inbox report `stale-report` until finish is refreshed.

Every new CodeStable workflow rule should add or update at least one behavior
scenario or record an explicit non-goal. Every observed CodeStable behavior
failure should be minimized into a fixture and scenario before the fix is called
durable.

### Verification Integration

Extend `codestable-maintainer/tools/verify.py` after the runner is stable:

- run behavior regression when changed paths touch `cs-*`, `using-codestable`,
  `cs-onboard/reference/`, `cs-onboard/tools/`, or maintainer harness files;
- start with a small default suite of critical scenarios;
- allow `--behavior-suite full` for slower scenario sets;
- report scenario id, actor mode, run count, pass/fail, failing grader, trace
  path, and fixture path;
- fail verification when a hard `must` check fails in any run.

Acceptance:

- a sterile actor can reproduce core CodeStable routing and owner-stop behavior
  from fixture repos;
- compacted actors recover next actions from artifacts and status tools rather
  than hidden chat history;
- drifted-spec scenarios are handled through inventory, clarification, or delta
  artifacts instead of freeform rewrites;
- permission-boundary scenarios cannot pass by writing self-review or forged
  subagent markers;
- repeated runs catch unstable behavior rather than accepting a single lucky
  pass;
- behavior regression reports are machine-readable and short enough for the
  maintainer final report.
