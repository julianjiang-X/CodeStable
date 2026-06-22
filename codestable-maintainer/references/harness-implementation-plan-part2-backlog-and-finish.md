## Work Package 5: Human-Review And Follow-Up Backlog

Implement this as part of `codestable-doctor` or as source script
`cs-onboard/tools/codestable-backlog.py`. When CodeStable is onboarded into a
project, the runtime command path for the separate command must be:

```bash
python3 .codestable/tools/codestable-backlog.py --root . --json
```

Responsibilities:

- scan CodeStable artifacts for `needs-human-review`, `Human review required`,
  `Follow-up`, `Follow-Ups`, accepted/deferred P2, and `attention.md`
  candidates;
- report file, line, unit, severity, and suggested owner action;
- distinguish blocked human decision points from optional future cleanup.

Required tests:

- backlog items survive after acceptance docs are written;
- accepted P2 items are visible until explicitly closed or converted to an issue;
- output includes line numbers when practical.

Acceptance:

- no final report can make unresolved human decisions disappear from the next
  agent's view.

## Work Package 6: CodeStable Maintainer Verification Command

Add a maintainer-only helper:

```bash
python3 codestable-maintainer/tools/verify.py --branch <branch> --remote origin
```

Responsibilities:

- assert current checkout is the CodeStable source checkout or an approved
  CodeStable source clone;
- assert branch is pushed to remote;
- fresh-clone the branch;
- validate every changed skill with the active skill-creator validator;
- run relevant tests when harness scripts changed;
- enumerate every changed installable unit and diff-check installed copies;
- report non-installed source files as `not installed: N/A`.

Required tests:

- unpushed branch fails;
- fresh clone missing the changed file fails;
- changed skill validates and installs cleanly;
- installed copy mismatch fails;
- README-only source docs are reported as not installed.

Acceptance:

- CodeStable source changes cannot be called complete from only the original
  checkout;
- installed global skill behavior is provably in sync with the pushed source.

## Work Package 7: Worktree Inbox And Finish Gate

Add two project-runtime helpers:

```bash
python3 .codestable/tools/codestable-finish-worktree.py --root . --unit <path-or-slug> --json
python3 .codestable/tools/codestable-worktree-inbox.py --root . --json
```

The goal is to prevent completed execution worktrees from being forgotten after
the chat context moves elsewhere. The reminder state must live in Git private
repo state, not in a single worktree branch, chat memory, or a tracked file that
can disappear after branch checkout.

### Shared Local Inbox

Use the repository's Git common directory:

```text
$(git rev-parse --git-common-dir)/codestable/worktree-inbox/*.json
```

Each inbox record is local machine state shared by all worktrees of the same
repository. The record is not committed and is visible from any branch or
worktree that points at the same common Git directory.

Record shape:

```json
{
  "schema_version": 1,
  "branch": "codex/example",
  "worktree": ".codex/worktrees/example",
  "unit": ".codestable/features/2026-06-09-example",
  "status": "ready-to-merge",
  "base_ref": "main",
  "covered_head": "abc123",
  "covered_diff": "main...abc123",
  "learning_report": ".codestable/features/2026-06-09-example/example-learning-report.md",
  "learning_report_abs": "/repo/.codestable/features/2026-06-09-example/example-learning-report.md",
  "context_check": ".codestable/features/2026-06-09-example/example-learning-context-check.json",
  "merge_readiness": ".codestable/features/2026-06-09-example/example-merge-readiness.json",
  "created_at": "2026-06-09T00:00:00Z",
  "last_seen_at": "2026-06-09T00:00:00Z",
  "snoozed_until": null,
  "next_action": "merge codex/example into main after owner approval"
}
```

Statuses:

- `active`: worktree exists but finish gate has not passed.
- `blocked`: finish gate found missing review, tests, owner decision, or stale
  learner report.
- `ready-to-merge`: finish gate passed and branch is not merged into base.
- `stale-report`: branch HEAD differs from learner report `covered_head`.
- `merged`: branch is already contained in base and worktree can be cleaned.
- `abandoned`: owner explicitly canceled the worktree.

### Finish Gate Responsibilities

`codestable-finish-worktree.py` is the only command that can create or refresh a
`ready-to-merge` inbox record.

Responsibilities:

- assert the current checkout is an execution worktree, not the coordinator
  checkout or default branch;
- resolve the unit path and current branch;
- compute base ref, current HEAD, and diff range;
- fail if the worktree has uncommitted changes outside the finish gate's own
  generated report/readiness artifacts;
- generate or refresh a Chinese learner report with `audience=learner` before
  the worktree is considered finish-ready;
- write `covered_head`, `covered_diff`, branch, worktree path, unit, validation
  evidence, and follow-up summary into the learner report frontmatter;
- run `check-context-sufficiency.py --strict` for the learner report and persist
  the JSON result next to it;
- fail if implementation review evidence is missing for implementation work;
- fail if blocking backlog exists for the unit;
- record the clean branch HEAD as `covered_head`; if the branch later advances
  with non-finish-artifact changes, the inbox must classify the record as
  `stale-report` until the finish gate is rerun;
- write `merge-readiness.json` in the unit and a matching Git-private inbox
  record when all checks pass;
- never merge, rebase, delete a branch, or delete a worktree.

Learner report path:

```text
{unit}/{slug}-learning-report.md
{unit}/{slug}-learning-context-check.json
{unit}/{slug}-merge-readiness.json
```

Required learner report frontmatter:

```yaml
doc_type: learner-report
unit: .codestable/features/2026-06-09-example
branch: codex/example
base_ref: main
covered_head: abc123
covered_diff: main...abc123
status: ready-to-merge
```

Required learner report sections:

- why the work happened;
- what changed;
- what explicitly did not change;
- key decisions future agents should preserve;
- subagent review findings and follow-up fixes;
- validation commands and results;
- merge-before/merge-after notes;
- remaining follow-ups or `None`.

### Inbox Responsibilities

`codestable-worktree-inbox.py` reads the Git-private inbox plus `git worktree
list` and reports owner-facing merge reminders.

Responsibilities:

- load every local inbox record from the Git common directory;
- verify whether each branch still exists;
- verify whether the referenced worktree still exists;
- verify whether `covered_head` is contained in `base_ref`;
- verify whether current branch HEAD still equals `covered_head`;
- classify records as `ready-to-merge`, `stale-report`, `merged`, `blocked`,
  `active`, or `abandoned`;
- support `--snooze <record> --until <timestamp>` for local reminder control;
- support `--abandon <record> --reason <text>` only with explicit owner action;
- emit JSON that `codestable-doctor.py` can embed.

Reminder severity:

- first `ready-to-merge`: P2 reminder;
- still unmerged after 24 hours: P2 reminder with age;
- still unmerged after 3 days: P1 owner decision required;
- `stale-report`: P1 because learner report no longer covers HEAD;
- `merged`: P3 cleanup suggestion until worktree is removed or record is
  archived.

### Doctor Integration

`codestable-doctor.py` should call the inbox reader by default and include:

- `ready_to_merge_worktrees`;
- `stale_learning_reports`;
- `merged_worktrees_ready_for_cleanup`;
- one `next_action` that prefers merge reminders over ordinary optional cleanup
  when any record is P1/P2.

The doctor must not generate reports or mutate inbox records. Generation stays
in the finish gate; doctor only reminds.

Required tests:

- finish gate fails in default branch/coordinator checkout;
- finish gate creates learner report, context check JSON, merge readiness JSON,
  and Git-private inbox record for an execution worktree;
- finish gate refreshes a stale learner report by writing a new `covered_head`;
- inbox reports `ready-to-merge` from a different branch/worktree than the one
  that created the record;
- inbox upgrades stale learner report to P1 after new commit on the worktree
  branch;
- inbox reports `merged` after base branch contains `covered_head`;
- inbox still reports `merged` after the already-merged branch is deleted;
- doctor includes ready-to-merge records without mutating files.

Acceptance:

- every finished execution worktree has at least one learner report covering the
  exact branch HEAD that is proposed for merge;
- merge reminders are visible from any branch or sibling worktree in the same
  local repository;
- agents cannot call a worktree finish-ready when the learner report is missing
  or stale;
- the system reminds the owner to merge, snooze, abandon, or clean up without
  ever merging automatically.
