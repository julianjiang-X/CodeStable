# Branch Guard Hooks

`codestable-ai-branch-guard.py` protects the stable coordinator checkout. It is
meant to run before AI tool calls, and it can also install Git hook fallbacks.

## Policy

- AI must not run `git switch` or `git checkout` in an existing checkout.
- AI must not edit implementation files on `main` or `master`.
- AI must use a linked execution worktree on a `codex/...` branch for code work.
- Planning files such as `.codestable/**` can still be edited in the coordinator
  checkout when the agent hook payload names those files directly.
- Owner-approved main publishing uses `codestable-main-publish.py begin` / `end`
  to create a short-lived audited intent. Do not use bare `--no-verify` as the
  normal path for merge / push.

Git cannot stop branch switches before they happen, so command-hook enforcement
is the primary guard. Git hooks only catch commit, merge, rebase, and push
fallbacks.

## Agent Hook

Configure the agent's pre-tool command hook to run:

```bash
python3 .codestable/tools/codestable-ai-branch-guard.py --root "$PWD"
```

The hook reads JSON from stdin. It recognizes common `tool_name` /
`tool_input.command` payloads for shell tools and common `file_path` fields for
edit tools. A blocked action exits with status `2` and prints the reason to
stderr.

## Git Hook Fallback

Install local Git hook fallbacks from a project that has been onboarded:

```bash
python3 .codestable/tools/codestable-ai-branch-guard.py --root . --install-git-hooks
```

Installed fallbacks:

- `pre-commit`: blocks staged implementation files on `main` / `master`.
- `pre-merge-commit`: blocks protected-branch merge commits.
- `pre-rebase`: blocks protected-branch rebases.
- `pre-push`: blocks protected-branch pushes.

Use `--force` only when replacing an existing local hook is intentional.

For an owner-approved main publish:

```bash
python3 .codestable/tools/codestable-main-publish.py --root . --json begin --owner-intent "owner approved publishing this branch to main" --branch codex/example
# merge the declared branch, validate, push main
python3 .codestable/tools/codestable-main-publish.py --root . --json end
```

The intent must name the target branch, remote, owner intent, and declared merge
refs. The branch guard still blocks branch switching, force pushes, undeclared
merge refs, and pushes to non-target branches.

## Recovery

If work has already started in the coordinator checkout, stop and create a
linked execution worktree from the current target baseline. Move or recreate the
work there, then run the normal CodeStable start / commit gates.
