# Interaction Modes

This file is copied by `cs-onboard` to
`.codestable/reference/interaction-modes.md`. It defines shared conversational
modes that run before a concrete `cs-*` lifecycle route is fully selected.

## Purpose

`interview me` and `grill me` are interaction modes, not standalone lifecycle
entities. They help CodeStable gather or stress-test owner intent before
routing to `cs-goal`, `cs-brainstorm`, `cs-feat`, `cs-issue`, or another
workflow.

Do not create a standalone `cs-interview` workflow unless it later gains its
own durable artifact model. Today, interview mode is a lightweight route-time
conversation.

Grill mode is different: in a CodeStable context, an explicit `grill me` or
grill alias means the owner has chosen a heavy pressure-test conversation.
Small tasks must not auto-trigger full grill mode. If the agent needs one
clarifying question for a small task, ask it without calling the exchange grill
and without creating grill artifacts.

## Modes

| Mode | Trigger examples | Intent | Default exit |
|---|---|---|---|
| `interview` | "interview me", "采访我", "先问我", "问清楚再说" | Elicit context gently: problem, background, constraints, success signal. | Route once enough context exists. |
| `grill` | "grill me", "拷问我", "追问我", "多问几轮" | Relentlessly pressure-test every relevant aspect of the plan or design: boundary, acceptance, non-goals, risks, hidden coupling, and dependent decisions. | Route, stop with open questions, or promote accepted context. |

## Routing

Use the requested mode first, then choose the lifecycle route:

- bounded start/end goal + acceptance + autonomous execution intent →
  `cs-goal` with goal grill alignment;
- fuzzy product or design idea without a known end state → `cs-brainstorm`;
- bug, regression, or wrong documentation → `cs-issue`;
- behavior-preserving cleanup → `cs-refactor`;
- pure explanation, status, or postmortem preparation → answer directly or use a
  context packet audience when appropriate.

If the user says `grill me first, then implement`, prefer `cs-goal` only when
the prompt includes, or the grill can quickly recover, an observable done signal.
Without a bounded destination, route to `cs-brainstorm` instead.

## Grill Context Docs

Explicit grill mode defaults to a temporary context document because it is a
heavy owner conversation. All paths inside CodeStable artifacts must be
repository-relative paths.

Before the lifecycle route is clear, write each self-contained round under:

```text
.codestable/brainstorms/{slug}/grill/round-NNN-{axis}.md
```

When the route is clear, the document may become `route-ready`: enough context
exists to choose the next workflow. `route-ready` is not approval and is not a
source of truth for implementation or spec mutation.

After the owner explicitly accepts the grill result, copy or migrate the
accepted context into the target unit:

```text
.codestable/{workflow}/{unit}/grill/round-NNN-{axis}.md
```

Leave a repo-relative pointer in the brainstorm path, either by keeping the
original file with `status: superseded` and `promoted_to`, or by writing a small
`index.md`. The promoted file stays in the repository for future human review.

Use this frontmatter shape:

```yaml
---
doc_type: grill-context
status: draft # draft | route-ready | accepted | superseded
source_of_truth: false
owner_review_use: true
route: undecided
promoted_to: null
---
```

The document records context, assumptions, alternatives, risks, evidence read,
owner answers, and the next route question. It must clearly distinguish sourced
facts from agent inference. Code, requirements, design docs, issue analysis,
roadmaps, decisions, architecture docs, and `state.yaml` remain the real sources
of truth. A grill context can inform human review, but it must not be treated as
proof that code, public contract, or long-lived specs are correct.

If an owner answer changes route, scope, or next work, write or update the
relevant `approval-report.md` unless a canonical stage report already carries
the decision context. The grill context itself is not an approval report.

## Question Shape

Both modes ask one question per turn. If a question can be answered by reading
the codebase or existing CodeStable docs, inspect those sources instead of
asking the owner.

Interview mode:

- gentle and clarifying;
- prefer 2-4 concrete choices when useful;
- focus on purpose, context, constraints, and success criteria;
- do not challenge every answer.

Grill mode:

- sharper and assumption-seeking;
- when the owner explicitly says `grill me` or a grill alias while using
  CodeStable, may walk every relevant branch of the plan or design tree until
  shared understanding is reached;
- each round uses one question plus 2-4 meaningfully different choices;
- include your recommended answer for the current question when useful, marking
  uncertainty if the recommendation depends on missing evidence;
- challenge scope, acceptance, non-goals, risk, and hidden coupling;
- keep each round self-contained instead of one rolling scratch note;
- stop when no new information appears, the owner says "先这样", or the next
  answer can only be learned by implementation or a spike.

## Relationship To `interviewee`

`interviewee` in `build-context-packet.py --audience interviewee` is a report
audience for real interviews or retrospectives. It prepares an evidence-backed
explanation of work already done or being reviewed.

It is not the same as interactive `interview me` mode. Do not route ordinary
`interview me` prompts to the `interviewee` audience unless the user is asking
for a postmortem, presentation, or real interview preparation packet.

## Guardrails

- Do not ask routine technical implementation choices before routing.
- Do not create grill artifacts for interview mode or small clarifications.
- Do create grill-context docs for explicit owner-heavy grill mode.
- Do not let `grill me` alone imply `cs-goal`; goal still needs a bounded
  destination.
- Do not treat `route-ready` as `accepted`; acceptance needs explicit owner
  confirmation.
- Do not treat an agent-written grill context as a source of truth.
- Do not keep interviewing after the route and next action are clear.
- If the owner asks for more context before answering a checkpoint, restart with
  the human judgment context shape from spec governance.
