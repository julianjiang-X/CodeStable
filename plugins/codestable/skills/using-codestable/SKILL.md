---
name: using-codestable
description: Apply an onboarded project's CodeStable context when a task needs its lifecycle records or workflows.
---

# Using CodeStable

Read `.codestable/attention.md` once for relevant project work and reuse it within
the task. Explicit user instructions take precedence over skill guidelines.
Follow project constraints and report language.

Select a known stage directly. Use `cs` for an overview or unclear routing;
do not start another routing conversation before already-authorized work.
Small edits and focused questions need no lifecycle unit unless requested by the
user or project. Explicitly requested skills still apply. Work directories
(`.codestable/features|issues|refactors|goals/YYYY-MM-DD-{slug}/`) are working
state, not archives: create one only when the task spans sessions or is handed
off, has a contract the owner must approve, needs a formal independent review,
or the owner asks for a record. Otherwise the evidence is the diff, test output
and the delivery note, including when another agent delegates the task with
"follow the CodeStable process". When a task ends, graduate what is still needed
to its proper home, record the outcome in the closing commit message, then
delete the work directory.

Progress is not stored in a page; derive it when asked. For questions about
progress, what remains, the next step or what is blocked, and when resuming work,
look at: work directories in this checkout and every linked worktree (a unit with
a completion marker that this branch changed since forking from the default
branch is closing and still counts; unchanged finished records from before 3.0.0
do not), worktrees ahead of the
default branch or dirty, undecided approval reports, finished-but-unmerged
worktrees and open PRs, and the last ~10 commits on the default branch; the next
step comes from the roadmap, else from the in-progress units, else say none is
recorded. Answer in the conversation, in the owner's language, with a checkable
pointer (path, branch, commit, PR) on every line and a note of what was not
checked; check other people's work and remote state when authorization allows.
Do not write the answer to a file. Ended directories left from before 3.0.0 are
not searched by default.

Load only relevant records and references. Missing optional tools do not require
installing the framework. Explain missing stage inputs and continue independent
work. Check library freshness only when updating or diagnosing CodeStable;
source and installation changes use `codestable-maintainer`.

CodeStable applies to repositories that carry `.codestable/attention.md`.
Without that file, do ordinary work: do not load `cs-*` workflows or create
`.codestable/` records, unless the user names a CodeStable
skill or asks for setup (`cs-onboard`). Personal tooling, coursework, device
setup and one-off operations stay outside CodeStable even when the task looks
like a bug fix or a feature. Respect requests to skip CodeStable. Narrowly
delegated agents use the supplied scope without restarting routing.

## Standing owner rules

In an onboarded repository, when the owner states a scope or authorization rule
(whose work to touch, what not to push, merge or open as a PR, what to leave
alone), record it in the same turn and say so in one line, so the owner does
not have to say it twice. A rule for one unit of work goes in that unit's
record; a rule that holds across tasks goes in `.codestable/attention.md`. Write
the actions it covers and the reason; when no reason was given, write "owner
instruction, reason not stated" instead of inventing one. In a repository that
is not onboarded, follow the rule for the session and do not create
`.codestable/` for it. Other candidate facts follow `cs-keep note`. When the reason
behind a recorded caution no longer holds, propose removing it instead of
working around it.

## Reporting

Write for a reader who has not seen the work. Say "verified" only for the path
that was actually exercised, and name what was not run. End with the next step;
when it is inside existing authorization, do it instead of listing it and
waiting.
