# Global Route Governance

## Purpose

Use the lightest workflow that completes the user's task while preserving actual
product contracts, authorization, and machine state. This is a maintainer design
reference, not an extra runtime checklist. Runtime details belong to the relevant
skill and shared conventions; do not duplicate them into every skill.

## Routing And Context

Choose a route and continue authorized work. Explain the choice only when it
helps the user understand scope or a material tradeoff. Do not emit mandatory
route / level / exclusion / escalation fields for every task.

Ask when missing information materially affects the result or the owner must
resolve conflicting product intent. Ambiguity between equivalent workflow names
is an implementation choice, not a reason to create an intake approval report.
Read only context relevant to the chosen work; do not traverse the workflow
family or archive to prove that alternatives were excluded.

The following levels are design vocabulary for maintainers, not required output
labels or mandatory packages:

| Context need | Useful material |
|---|---|
| Executing an authorized plan or reporting status | Current evidence and result |
| Local, reversible work | Scope and proportionate verification |
| Unresolved product / scope / risk decision | Concrete options, recommendation, evidence, consequences |
| Changing an established contract | Affected canonical source, change and authorization, consumer evidence |
| Conflicting or stale specifications | Targeted inventory, conflict evidence, repair decision |

## Execution Boundaries

- Small self-contained work need not create a formal unit. Formal feature,
  issue, refactor, and goal units retain their state transitions and required
  artifacts; follow `execution-conventions.md` and `goal-conventions.md`.
- Existing authorization persists. Do not add review / route / implementation
  approvals merely because a stage changes. A material new product decision or
  an external action outside authorization still requires the owner.
- Updating wording, links, or current-state documentation within the requested
  scope does not automatically require a requirement delta or owner-stop.
  Conflicting normative intent cannot be silently rewritten from code evidence.
- Review and tests follow actual failure risk. Formal execution review artifacts
  remain required by current tools. When `assurance.md` requires added review
  for an actual risk, preserve that independent stage; fast lanes do not waive
  it. Do not repeat passing checks without a new change, failure, or unresolved
  concern.
- A finish report must cover the current candidate. Preserve `covered_head`,
  stale-report, review, and inbox semantics; completion is not merge permission.
- Explicit `interview me` / `grill me` requests select their interaction modes.
  Ordinary work does not trigger an unsolicited interview. `grill-context`
  remains human discussion context with `source_of_truth: false`.

## Skill Maintenance

Each skill should state the outcome it owns, its non-obvious constraints, and
links to conditional references. Shared authorization, execution, and metadata
contracts have one canonical definition. Do not require a context level,
skip-record format, nearby-route catalog, or identical governance section in
every skill. Add artifacts only for a concrete decision, state requirement,
handoff, or requested record.

When revising prompts, test a meaningful behavior boundary rather than matching
a prescribed sentence or heading. Distinguish a prompt change from a tool
contract change: do not claim that a required formal gate can be bypassed unless
the tools and their behavioral tests have also changed.

## Behavioral Coverage

Use bounded scenarios for changed behavior, especially:

- clear small work proceeds with proportionate checks and no gratuitous reports;
- a real unresolved product boundary gets concrete decision context;
- prior authorization is reused through stage transitions;
- formal units retain required state, review, and finish evidence;
- explicit interview / grill behavior respects intent and context provenance;
  `global-small-task-does-not-trigger-grill` covers the small-task boundary;
- resume recovers current next action from artifacts without replaying work;
- failures, stale reports, and unresolved decisions are not reported as complete.

Existing scenarios named `cs-route-brief-minimal`,
`cs-root-route-choice-approval-report`, and `route-choice-owner-context` originated
under a mandatory-route-brief design. Their names do not establish current
runtime requirements. Keep or revise their expectations to test useful routing
and material decision boundaries, not mechanical reporting or owner-stop for
routine workflow selection. Maintainer harness documentation owns the current
scenario details.
