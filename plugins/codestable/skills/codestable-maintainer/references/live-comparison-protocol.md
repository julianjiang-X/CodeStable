# Live comparison protocol

## Purpose and treatment

Compare two immutable CodeStable package revisions with one frozen evaluator.
The treatment includes skills, shared references, and onboarded runtime tools;
this is not an isolated estimate of SKILL.md wording. Keep task prompts, fixture
builder, graders, CLI, model, effort, permissions, and run order policy fixed.
Never run the two revisions' own evaluators against one another.

## Pilot before expansion

Begin with four single-turn task families, two repetitions per version (16 runs):
exact README repair, read-only API assessment, an approved-contract bug repair,
and a proposed change that conflicts with an approved public contract.
These test small-task routing and contract boundaries, not complete formal
feature acceptance or general coding ability. Alternate AB and BA order.

The original eight-family, three-repeat proposal (48 runs) is an expansion,
not a prerequisite. First establish valid runtime access, scoring, and meaningful
candidate exposure. Expand when failures or cost variance need more evidence.
A scenario edited after seeing results becomes development data. Use unseen
fixtures and prompts for confirmation after changing workflow instructions.

## Isolation and reproducibility

Resolve refs to commit IDs and export package snapshots. Save evaluator and
scenario hashes, package commits, model ID, reasoning effort, CLI version,
explicit arguments, run order, and visible-skill configuration. Give each run a
fresh repository and temporary Codex configuration area. Disable host skill
copies so they cannot shadow the intended snapshot. Do not alter global config.
Authentication material is runtime-only and must not enter reports or archives.

Check the active CLI with a real model call before spending the full run budget.
An installed binary accepting the flags does not prove server compatibility.
Do not silently substitute another model when Astra is unavailable.

## Scoring

First reject invalid runtime results: nonzero CLI exit, missing successful
completion event, and timeout. Keep these separate from observed model behavior.
Then grade exact files, hidden functional assertions, changes relative to the
pre-actor snapshot, and relevant Git state. Initial setup files must not count as
agent mutations; commits must not hide a mutation. Count live tool items once
by stable event ID, retaining the completed event.

A correct substring plus unrelated corruption fails. Read-only success requires
both an unchanged repository and a substantively correct assessment. A nonempty
reason alone is only a structural check; independent blinded review checks
whether it explains the affected public contract.

Report wall time and original usage fields (input, cached input, output, and any
additional fields available), unique tool calls, objective pass/fail, and runtime
validity per run. Report costs for all valid runs and successful runs separately.
Missing usage is unknown, never zero. No token estimate from transcript length.
Question count and repeated reads/tests need semantic review: repetition may be
necessary, and a question mark alone does not establish an approval pause.

## Blinded review and iteration

Give a reviewer task prompts, final output, trajectories, and artifacts under
opaque run labels without the revision mapping. Ask for task completion,
unnecessary versus necessary clarification, scope violations, and avoidable
work. The reviewer may infer a version from skill content, so describe this as
label-blinded, not guaranteed blinding.

Classify each finding as evaluator defect, environment failure, fixture problem,
or workflow behavior. Fix the first three before changing skills. Keep failed
and invalid attempts in an attempt ledger. Change workflow instructions only
when the observed behavior supports that change, then run independent holdouts.
No observed regression in a small pilot is not proof of equivalence. A fast
failed run is not an efficiency win. State effect sizes and uncertainty without
statistical superiority claims from two repetitions.

## Uncovered capabilities

The current ephemeral CLI adapter is single-turn. It cannot demonstrate actual
mid-turn steering, user-answer continuation, or live compaction recovery.
A resume adapter can test between-turn continuation separately; only an adapter
that delivers input during execution can test mid-turn steering. Do not simulate
these by putting both user turns into one initial prompt.

Live comparison stays opt-in and outside the deterministic release verifier.

## Command

Run from the source checkout with a compatible Codex CLI on PATH. The following
one-family command runs four trials; repeat `--scenario` for each additional
family to build the 16-run pilot. Output must be a new directory.

```bash
python3 plugins/codestable/skills/codestable-maintainer/tools/live-comparison.py \
  --baseline <old-commit> --candidate <new-commit> \
  --scenario plugins/codestable/skills/codestable-maintainer/scenarios/comparison/typo.yaml \
  --repeats 2 --model gpt-6-astra --effort low \
  --output /tmp/codestable-comparison
```

Other pilot filenames are `readonly.yaml`, `approved-fix.yaml`, and
`contract-conflict.yaml` in the same directory. Use `--codex-bin` to select a
compatible binary explicitly. `--prepare-only` freezes inputs without model
calls. Run with PyYAML available for general YAML; the bundled comparison files
also parse as JSON. The runner requires a Python with tar extraction filters.

The runner disables remote plugins, apps, hooks, shell snapshots, memories, skill
search, and automatic skill dependency installation, as well as known host skill
paths. Temporary runtime homes are removed even on failed runs. It leaves
artifacts, events, configuration metadata, and hashes in the output directory.
