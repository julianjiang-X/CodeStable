## Relationship To Global Route Governance

The context levels, route matrix, route-time contract, flow-time contract,
finish-time contract, skip rules, and route-level harness scenarios are defined
in `global-route-governance.md`.

This roadmap only owns the L3/L4 specialization:

- how a route proves it has crossed from local work into long-lived spec change;
- which spec artifacts are allowed to change;
- how clarifications and requirement deltas are recorded;
- how old or conflicting specs are rehabilitated;
- how analyze findings block, warn, or become owner decisions.

The global matrix must stay the source of truth for whether a lightweight route
can remain L0/L1. This file must not require heavy spec artifacts for small
feature fast paths, local refactors, simple bug fixes, status checks, or docs
updates that do not change capability boundaries or future agent behavior.

## Areas Requiring Further Detail

The global route matrix must become executable before this spec roadmap can be
called stable. This roadmap still needs these L3/L4 details before the phase is
implemented:

- Artifact schemas: exact frontmatter and required sections for owner context,
  clarifications, req deltas, compaction reviews, inventory, and analyze reports.
- Owner-stop semantics for spec changes: which spec edits must stop for
  approval, which can continue with a recorded default, and how current-turn
  approval is recognized.
- Skip thresholds for spec artifacts: concrete rules for when small UI tweaks,
  local refactors, or bug fixes do not need requirement deltas or roadmap
  updates.
- Severity model: how analyze findings become blocking, warning, deferred
  backlog, or non-goal.
- Canonical conflict policy: how to ask the owner when code, tests, acceptance,
  requirements, decisions, and architecture disagree.
- Rehabilitation classification criteria: exact evidence needed for
  `current-trusted`, `current-unreviewed`, `drift-suspected`, `historical`,
  `superseded`, and `orphaned`.
- Compaction safety: how to prove a shortened spec preserves human-important
  detail, and where removed detail is archived.
- Language and length budget: which owner-facing artifacts must be Chinese and
  how short their owner brief must stay.
- Behavior scenario coverage: which sterile/compacted scenarios prove each rule
  instead of only proving that the prompt mentions it.

## Skill Integration Roadmap

### SG0: Global Route Governance Dependency

Implement the root protocol in `global-route-governance.md` before treating any
spec-facing update as stable.

Acceptance:

- every routed `cs-*` workflow declares default context level, escalation
  triggers, owner-stop conditions, allowed artifacts, skip-record format,
  finish-time checks, and matching harness scenarios;
- global route scenarios prove that small paths stay light and risky paths
  escalate before the spec-specific rules below run;
- this spec roadmap is only invoked when the global route matrix reaches L3 or
  L4.

### SG1: Owner Decision Context

Update `cs-brainstorm` so convergence into feature, roadmap, or requirement work
produces owner decision context and stops for approval.

Acceptance:

- brainstorm can remain freeform while exploratory;
- once proceeding, an owner-readable decision artifact exists;
- the default chat reply stays concise and points to the artifact.

### SG2: Spec Judgment Context

Add judgment preface rules to spec-changing paths in `cs-brainstorm`,
`cs-roadmap`, `cs-feat-design`, `cs-feat-accept`, `cs-req`, `cs-decide`,
`cs-onboard`, and `codestable-maintainer`.

Acceptance:

- any prompt that asks a human to choose, approve, authorize, accept, defer, or
  sign off defines non-obvious terms before asking about them;
- each checkpoint states why it matters, the options or expected answer shape,
  the recommendation, and what the answer changes;
- owner can ask for more context and the agent restarts the checkpoint instead
  of continuing the original low-context flow.

### SG3: Spec Router

Add routing rules and output templates to `cs-feat-design`, `cs-roadmap`,
`cs-req`, and `cs-feat-accept`.

Acceptance:

- selected and excluded specs are visible before edits;
- multiple plausible requirement docs trigger clarification;
- small local changes can explicitly skip requirement deltas.

### SG4: Clarification Gate

Add clarification scanning to `cs-feat-design` and `cs-roadmap` approval paths.

Acceptance:

- at most five high-impact questions;
- answers are appended to `## Clarifications`;
- design/checklist generation does not proceed while blocking clarifications are
  unanswered.

### SG5: Requirement Delta And Mechanical Apply

Add `{slug}-req-delta.md` creation in design/roadmap flows and mechanical apply
in `cs-feat-accept`.

Acceptance:

- capability-boundary changes use deltas;
- small local changes do not create deltas;
- accept updates the target requirement and change log only from an approved
  delta.

### SG6: Historical Spec Rehabilitation

Add a maintainer/onboard path for inventorying and classifying old specs before
new governance rules are enforced.

Acceptance:

- old specs are classified before migration;
- drift findings ask owner whether code, docs, or both need repair;
- no long-lived spec is rewritten without a delta, clarification, archive marker,
  or compaction review.

### SG7: Analyze Pass

Add a read-only analyze pass that can be run before design approval and during
acceptance.

Acceptance:

- terminology drift, requirement/checklist coverage gaps, and decision conflicts
  are reported;
- the pass never mutates files;
- findings can become backlog items if the owner defers them.

### SG8: Documentation And Tool Surface

Document the new runtime behavior in `cs-onboard/reference/shared-conventions.md`
and `cs-onboard/reference/tools.md` after the tools or prompt flows exist.

Acceptance:

- onboarded projects receive the updated conventions;
- project agents know which artifacts are long-lived specs, deltas, historical
  records, and owner review context.

## Behavior Harness Validation Matrix

Every work package above must be paired with behavior scenarios. These scenarios
prove the rule in a sterile or compacted actor context.

| Problem | Scenario | Expected proof |
|---|---|---|
| Global route governance is only described, not reproducible | `cs-route-brief-minimal`, `fast-path-stays-light`, `fast-path-escalates-on-boundary` | The global route scenarios pass before spec-specific scenarios are considered stable. |
| Brainstorm result is too terse to approve | `brainstorm-owner-context` | Owner context artifact exists and the agent stops before formal spec changes. |
| Human judgment checkpoint lacks context | `owner-judgment-context` | The actor defines terms, explains why the judgment matters, states option tradeoffs, shows evidence, and restarts if the owner asks for more context. |
| Agent chooses the wrong requirement | `feat-design-clarify` | Spec router lists selected and excluded docs, then asks clarification if ambiguous. |
| Small UI tweak pollutes requirements | `small-ui-no-req-delta` | Requirement files remain unchanged; local feature artifact records the work. |
| Capability boundary changes need durable owner review | `capability-boundary-req-delta` | A req delta is created and the long-lived requirement is not rewritten directly. |
| Old specs are already drifted | `drifted-spec-inventory` | Inventory and drift findings are created; no silent cleanup rewrite occurs. |
| AI compaction loses workflow state | `compact-resume-next-action` | A fresh actor recovers the same next action from artifacts and tools. |
| Long context makes CS seem implemented only in the original chat | `long-context-noise-routing` | The actor still reads attention, runs router, and obeys forbidden mutation checks. |
| AI claims subagent review without authorization | `subagent-permission-boundary` | The actor stops for owner authorization and cannot forge reviewer evidence. |
| Acceptance misses spec drift | `accept-analyze-spec-drift` | Analyze findings block or record owner decisions before accept completes. |

## Definition Of Done

The spec governance system is not considered implemented until:

- the skill prompts and reference docs define the behavior;
- deterministic validators or artifact schemas exist where practical;
- behavior harness scenarios pass in `sterile` mode for the core flows;
- compact/resume scenarios prove state recovery from artifacts, not chat memory;
- every known failure from this discussion has a regression scenario or an
  explicit non-goal.
