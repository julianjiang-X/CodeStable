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
user or project. Explicitly requested skills still apply.

Load only relevant records and references. Missing optional tools do not require
installing the framework. Explain missing stage inputs and continue independent
work. Check library freshness only when updating or diagnosing CodeStable;
source and installation changes use `codestable-maintainer`.

CodeStable applies to repositories that carry `.codestable/attention.md`.
Without that file, do ordinary work: do not load `cs-*` workflows, create
`.codestable/` records or copy shared tools, unless the user names a CodeStable
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
`.codestable/` for it. Other candidate facts follow `cs-note`. When the reason
behind a recorded caution no longer holds, propose removing it instead of
working around it.

## Reporting

Write for a reader who has not seen the work. Say "verified" only for the path
that was actually exercised, and name what was not run. End with the next step;
when it is inside existing authorization, do it instead of listing it and
waiting.
