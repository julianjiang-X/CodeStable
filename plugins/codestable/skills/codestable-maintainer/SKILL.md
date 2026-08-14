---
name: codestable-maintainer
description: Maintain the CodeStable skill library and harness. Use when changing CodeStable source skills, shared references, onboarded tools, validator scripts, README skill lists, installed skill copies, when making pushed CodeStable changes available locally, or when planning CodeStable harness improvements. Enforces source-repo edits, remote push, fresh-clone verification, and main-only installed-copy sync.
---

# CodeStable Maintainer

Use this skill for any CodeStable library change. Work from the current
CodeStable source checkout, not from an installed skill copy. Installed copies
are deployment artifacts.

## Source Of Truth

- Source repo: the current CodeStable source checkout; commands below assume
  they are run from the repository root and use `--repo .`.
- Installed skill roots are machine-local deployment artifacts, commonly
  `${HOME}/.agents/skills` and `${CODEX_HOME:-$HOME/.codex}/skills`.
- Fresh-clone verification root: create a temporary directory under `/tmp` or
  the system temp directory.

If the user asks to change a CodeStable skill, workflow, shared convention,
validator, harness tool, or README, switch to the source repo before editing.

## Required Workflow

1. Inspect source repo status and remotes:
   `git status --short --branch` and `git remote -v`.
2. Create or use a focused linked worktree on a `codex/...` branch unless the
   user explicitly requires another branch. Do not `git switch` / `git checkout`
   the stable source checkout for AI development.
3. Edit only source repo files. Do not patch installed roots such as
   `${HOME}/.agents/skills/*` or `${CODEX_HOME:-$HOME/.codex}/skills/*` until
   after the source change is committed and verified.
4. If the change creates or updates a skill, use the active skill-creator
   workflow when it is available. In all cases, validate frontmatter, keep
   `SKILL.md` concise, and place detailed material in `references/` when
   useful.
5. Run relevant local validation:
   - Discover the active skill-creator validator with a home-relative search:
     `find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.agents" -name quick_validate.py -print`
     and run `uvx --with PyYAML python <quick_validate.py> <skill-dir>` for
     changed skills.
   - `pytest` or focused tests for changed harness scripts when tests exist.
   - `git diff --check`.
6. Use a subagent reviewer for implementation review when available. If the
   platform truly cannot launch one, record a fresh self-review fallback
   explicitly in the final report.
7. Commit source changes with a Conventional Commit message.
8. Push the branch to a remote.
9. Run the maintainer verifier from the source checkout against a temporary
   installed root:
   `tmp_installed="$(mktemp -d)/skills"; python3 plugins/codestable/skills/codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root "$tmp_installed" --sync-installed --json`.
   This command fresh-clones the pushed branch, validates changed skills, runs
   harness tests when needed, syncs changed installed skill directories into the
   temporary root, and diff-checks that temporary copy.
   Do not suggest shorthand wrappers such as `codestable-maintainer verify` or
   `--sync`; the maintained contract is the explicit `python3
   plugins/codestable/skills/codestable-maintainer/tools/verify.py ... --sync-installed --json` command.
10. Do not sync real installed roots from a feature branch. To make a CodeStable
    change globally available, merge it to `main`, push `origin/main`, then run
    the verifier from a clean `main` checkout. Protected-branch merge / push
    should be wrapped in `codestable-main-publish.py begin` / `end` with
    explicit owner intent; do not use bare `--no-verify` as the normal path:
    `python3 plugins/codestable/skills/codestable-maintainer/tools/verify.py --repo . --branch main --remote origin --installed-root "${CODEX_HOME:-$HOME/.codex}/skills" --sync-installed --json`.
    Real installed roots are synchronized only from remote `main`.
11. For changed source files that are not installed directly, record
    `not installed: N/A` in the final report with the reason from verifier
    output.

## Fresh Clone Verification

For feature branches, prefer the maintainer verifier with a temporary installed
root:

```bash
tmp_installed="$(mktemp -d)/skills"
python3 plugins/codestable/skills/codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root "$tmp_installed" --sync-installed --json
```

For real installed-copy deployment, first merge and push `origin/main`, then run:

```bash
python3 plugins/codestable/skills/cs-onboard/tools/codestable-main-publish.py --root . --json begin --owner-intent "owner approved publishing CodeStable changes to main" --branch <branch>
# merge, validate, and push main while the intent is active
python3 plugins/codestable/skills/cs-onboard/tools/codestable-main-publish.py --root . --json end
python3 plugins/codestable/skills/codestable-maintainer/tools/verify.py --repo . --branch main --remote origin --installed-root "${CODEX_HOME:-$HOME/.codex}/skills" --sync-installed --json
```

Use the manual branch-aware clone flow only when the verifier itself is broken:

```bash
tmpdir="$(mktemp -d)"
git clone --branch <branch> --single-branch <remote-url> "$tmpdir/CodeStable"
cd "$tmpdir/CodeStable"
validator="$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.agents" -name quick_validate.py -print -quit)"
uvx --with PyYAML python "$validator" <skill-dir>
```

For temporary installed-copy verification, enumerate every changed installable
unit, then compare each fresh clone skill directory to its temporary installed
directory:

```bash
for skill_dir in <changed-skill-dir> ...; do
  diff -ru "$tmpdir/CodeStable/$skill_dir" "$tmp_installed/$skill_dir"
done
```

If a changed file is not meant to be installed immediately, say that explicitly
and skip the installed-copy diff only with a reason. Do not treat one clean
skill diff as proof that all installable CodeStable changes were deployed.

## Harness Improvement Planning

For CodeStable harness roadmap or design work, read
`references/harness-improvement-plan.md` first and then the relevant
`harness-improvement-plan-part*.md` file. Read
`references/harness-implementation-plan.md` and relevant
`harness-implementation-plan-part*.md` files when the task asks what to build
next. For the implemented behavior runner, read
`references/behavior-harness-tool.md`. For global `cs` routing, owner approval reports,
context levels, owner-stop/skip rules, finish-time checks, or harness coverage
across routed workflows, also read `references/global-route-governance.md`. For
spec drift, requirement delta, clarification, or human-readable spec governance
work, read `references/spec-governance-roadmap.md` and the relevant
`spec-governance-roadmap-part*.md` file. Older references to owner context,
owner decision context, or owner judgment context mean auxiliary context only;
current approval checkpoints write `approval-report.md` unless a canonical
stage report fully satisfies the L2 rule. Human-facing reports follow the
project report language policy in `.codestable/attention.md`. Together they
capture the current proposal derived from GammaSource, BetaSoul, and CodeStable
workflow failures:

- `codestable-doctor`
- worktree start/commit/recovery gates
- review packet generation
- commit planner
- follow-up and human-review backlog detection
- source-push-clone-install verification
- worktree finish reports and merge reminders
- clean-agent behavior regression
- global route governance, spec governance, and drift control

## Hard Stops

- Do not edit installed copies before source repo changes are committed and
  pushed.
- Do not claim a CodeStable source change is finished without fresh-clone
  verification.
- Do not claim installed global behavior is updated until the installed copy
  was synced from remote `main` and diff-checked.
- Do not sync `${HOME}/.agents/skills` or `${CODEX_HOME:-$HOME/.codex}/skills`
  from feature branches, sibling worktrees, or hand-copied patches.
- Do not push directly to `main` unless the user explicitly asks for that.
