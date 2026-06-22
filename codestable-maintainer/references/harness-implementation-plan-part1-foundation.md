# CodeStable Harness Implementation Plan

## Goal

Turn the current CodeStable process from prompt-only discipline into a small set
of deterministic gates and status tools. The target failure mode is simple:
when an agent says a CodeStable-managed task is done, the repository state,
worktree topology, review evidence, commit scope, follow-up backlog, and
installed CodeStable copy should all be checkable from commands.

This plan solves the issues observed in recent GammaSource, BetaSoul, and
CodeStable maintenance work:

- implementation can happen in the coordinator checkout instead of an execution
  worktree;
- a clean `git status` can hide implementation commits already made on `main`;
- data, logs, code, docs, and migration changes can be packed into one commit;
- subagent review catches real issues, but review packets are prepared manually;
- `needs-human-review`, follow-ups, accepted P2s, and `attention.md` candidates
  can disappear after a final report;
- CodeStable source changes can be pushed while installed global skill copies
  remain stale;
- agents can forget to start from the CodeStable source checkout for
  CodeStable changes;
- workflow prompt changes can appear correct in the original high-context
  conversation but fail when a fresh or compacted agent receives the same user
  input in a test repository.

## Work Package 1: `codestable-doctor`

Implement the source script in CodeStable at
`cs-onboard/tools/codestable-doctor.py`. When CodeStable is onboarded into a
project, the runtime command path must be:

```bash
python3 .codestable/tools/codestable-doctor.py --root . --json
```

Skills and project docs must reference the runtime `.codestable/tools/...`
path, not the CodeStable source-tree path, unless they are explicitly describing
work inside the CodeStable source checkout.

Responsibilities:

- report active feature, issue, refactor, roadmap, and maintenance units;
- report current branch, default branch, linked worktree status, and whether the
  checkout looks like a coordinator or execution worktree;
- group dirty files into code, tests, docs, migrations, data, logs, CodeStable
  artifacts, and unknown;
- list `needs-human-review`, `Human review required`, unresolved `Follow-up`,
  accepted/deferred P2, and `attention.md` candidate items;
- report missing implementation-review evidence for completed implementation
  units;
- emit one `next_action` string for agents and dashboards.

Required tests:

- empty repo with no CodeStable unit reports `status=idle`;
- planning-only dirty docs report planning-safe;
- dirty `src/` change on `main` reports worktree violation;
- completed feature without `{slug}-implementation-review.md` reports blocked;
- `needs-human-review` appears in JSON output with file and line.

Acceptance:

- the command never mutates files;
- JSON output is stable enough for hooks and future UI display;
- it can explain both dirty-tree and clean-tree blocked states.

## Work Package 2: Worktree Start, Commit, And Recovery Gates

Implement the source script in CodeStable at
`cs-onboard/tools/codestable-worktree-gate.py`. When CodeStable is onboarded
into a project, the runtime command paths must be:

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . start --unit <path-or-slug>
python3 .codestable/tools/codestable-worktree-gate.py --root . commit --unit <path-or-slug>
python3 .codestable/tools/codestable-worktree-gate.py --root . quarantine --unit <path-or-slug>
```

Start gate:

- allow planning and analysis docs in the coordinator checkout;
- require a non-default linked worktree before implementation paths are edited;
- record a task baseline containing default-branch HEAD, current branch,
  worktree path, unit path, and timestamp;
- allow override only when the unit contains `worktree-override.md` with reason,
  scope, and human approval.

Commit gate:

- fail if staged implementation changes are on `main`;
- fail if default branch has implementation commits after the recorded baseline,
  even when the working tree is clean;
- fail completed implementation units without subagent review evidence unless a
  platform-level self-review fallback is explicitly enabled;
- warn when staged files belong to multiple commit buckets.

Recovery gate:

- default to dry-run output that describes the proposed branch/worktree and file
  moves without mutating anything;
- require `--apply` plus an explicit human-approved override before creating
  branches, creating worktrees, moving files, or altering the index;
- create or name a quarantine branch/worktree for accidental implementation
  changes started in the coordinator checkout only after that approval;
- move only implementation-scope changes into the execution worktree when
  possible;
- leave data/log churn visible for the commit planner instead of hiding it.

Required tests:

- start gate fails on `main` for an implementation unit;
- start gate passes in a linked `codex/...` worktree;
- commit gate catches a clean `main` that contains a post-baseline implementation
  commit;
- override file permits an explicitly approved exception and records the reason;
- quarantine dry-run proposes a recovery plan without mutating the repo;
- quarantine `--apply` is required before branch/worktree creation or file moves;
- quarantine refuses to run when untracked secrets or env files are present.

Acceptance:

- this package directly prevents "task completed outside the worktree";
- it also detects the harder case where the task already committed to `main`.

## Work Package 3: Review Packet Generator

Implement the source script in CodeStable at
`cs-onboard/tools/build-review-packet.py`. When CodeStable is onboarded into a
project, the runtime command path must be:

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit <path-or-slug> --stage quality --output /tmp/review.md
```

Responsibilities:

- collect the design/report/analysis doc, checklist state, relevant architecture
  or requirement docs, and current diff;
- include `git diff --stat`, focused source diff, and validation commands/results
  provided by the owner;
- include risk prompts for DB, migrations, concurrency, idempotency,
  crash-resume, provider cost, production writes, and deterministic LLM
  boundary;
- include stage-specific reviewer instructions for `implementation`, `spec`,
  `quality`, and `verification`;
- redact `.env`, token-looking values, and local credentials.

Required tests:

- packet includes unit docs and focused diff;
- staged packets include the right reviewer mission;
- verification-stage packets require validation evidence;
- packet excludes secret-like files and values;
- packet can be used by a subagent without hidden prior context.

Acceptance:

- `cs-feat-impl`, `cs-issue-fix`, and `cs-refactor-ff` can call this before
  subagent review;
- review evidence remains comparable across runs.

## Work Package 4: Commit Planner

Implement the source script in CodeStable at `cs-onboard/tools/plan-commits.py`.
When CodeStable is onboarded into a project, the runtime command path must be:

```bash
python3 .codestable/tools/plan-commits.py --root . --json
```

Responsibilities:

- classify changed paths into buckets: code/docs/tests, migrations/database docs,
  data, logs/runtime artifacts, CodeStable docs, installed skill deployment, and
  unknown;
- warn when a migration lacks matching database contract docs;
- warn when source code changes lack mapped runbook docs when a project mapping
  is available;
- warn on tracked ignored paths, large files, and changing file sizes that imply
  live writers;
- never stage or commit by itself.

Required tests:

- mixed GammaSource-like dirty tree produces separate code, data, log, and docs
  buckets;
- migration without docs is flagged;
- tracked ignored runtime file is flagged;
- planner output is deterministic and does not mutate files.

Acceptance:

- agents can produce separate logical commits without relying on memory;
- data/log churn no longer gets hidden inside code commits.
