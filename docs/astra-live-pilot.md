# Astra live package comparison pilot

## Decision and evidence

Retain the current Astra workflow simplification. This single-turn pilot supports lower workflow overhead on the tested tasks. It does not establish broad model stability or a production productivity effect. No further skill wording was changed to fit these tasks.

Baseline: `a73ad9b253edffeb33ea7a3c02b2ba1257d36a5b`. Candidate: `1f053d17b8881c8cab93a4999ae6ea1959f0886c`.
Model: `gpt-6-astra`; effort: `low`; CLI: `codex-cli 0.153.4`.

One frozen evaluator ran four task families twice per package, alternating AB/BA order: **16 valid runs, 8/8 objective passes per package**. All runs had a successful completion event. Read-only and contract guards, exact spelling output, and independent slug-function assertions passed. No commit/merge violations were found.

| Metric, median across 8 runs | Baseline | Candidate | Reduction |
|---|---:|---:|---:|
| Wall seconds | 60.7 | 47.6 | 21.7% |
| Input tokens (including cached) | 152,156.5 | 79,175.0 | 48.0% |
| Cached input tokens | 124,672 | 69,952 | 43.9% |
| Output tokens | 823.5 | 799.0 | 3.0% |
| Completed tool events | 6.5 | 5.0 | 23.1% |

All valid runs passed objective checks, so valid-run and objective-success-only summaries coincide. Token counts are the CLI usage fields, not transcript-length estimates. No dollar-cost estimate is made; cached input and output have different billing implications. Wall time includes fixture setup and CLI overhead.

| Task | Baseline seconds, median | Candidate seconds, median | Objective passes |
|---|---:|---:|---|
| typo | 56.2 | 35.5 | 2/2 each |
| readonly | 57.8 | 37.8 | 2/2 each |
| approved-fix | 117.1 | 58.8 | 2/2 each |
| contract-conflict | 70.1 | 57.4 | 2/2 each |

Candidate wall time was lower in seven of eight matched task/repetition pairs. One contract-conflict repetition was slightly slower. Output-token median changed only 3%, so the main observed difference is context/tool overhead, not much shorter final work.

## How the protocol was iterated

1. The original 48-run, eight-family proposal was reduced to a 16-run single-turn pilot after review. The existing ephemeral CLI cannot truthfully test mid-turn steering or user-answer continuation.
2. The Homebrew CLI 0.147.0 was rejected by the server for Astra. The bundled 0.153.4 CLI completed a real readiness call; global configuration was not changed.
3. Two initial comparison preflight runs revealed automatic plugin loading. They are excluded from the formal comparison. One baseline run also created extra lifecycle files for the typo, showing why a single sample is insufficient.
4. Remote plugins/apps, hooks, memory imports, shell snapshots, and skill search were disabled. A second two-run preflight passed; both repaired only README. Temporary configuration homes were removed.
5. Scoring was repaired before the formal pilot: nonzero exits and missing completion events fail; live changes compare pre/post snapshots; initial dirty setup is not agent mutation; HEAD guards catch commits; completed tool events are counted by ID.
6. Independent code review found compound-command commit detection and omitted file/MCP tool counts. Both were fixed and re-reviewed. Targeted independent tests: 33 passed. Full suite: **177 passed**.

The four preflight model runs remain separate from the 16 formal runs. Invalid setup attempts and scoring fixes are not evidence of model-behavior improvement.

## Independent semantic review

A fresh reviewer saw all 16 runs under opaque IDs without the arm mapping.
It checked prompts, assistant messages, command evidence, final files, and
changed paths. Skill wording could still reveal treatment style, so this was
label-blinded review, not guaranteed blinding.

- All **16 substantive results were correct**. All eight API assessments explain
  the object/field and pagination incompatibility; none merely supplies a false
  boolean with an empty explanation.
- **No run asked the user an actual clarification question.** This pilot therefore
  does not demonstrate a reduction in clarification frequency.
- Both baseline repair runs delivered correct code and passing contract tests,
  but explicitly reported blocked workflow completion. Both candidate repairs
  delivered the repair and regression tests without a workflow block.
- The baseline closure reports cite unavailable independent review. One gate
  rejects missing review evidence; the other rejects self-review. The claimed
  platform dispatch failure is not independently established by the supplied
  raw event evidence. Record it as a reported cause, not a verified platform fault.
- One baseline repair invokes its commit gate before creating the unit, causing
  a confirmed avoidable failure. Repeating the gate after creating the unit is
  meaningful because the state changed.
- Baseline small tasks repeatedly load freshness checks, framework inventories,
  overviews, and routing skills. These are workflow-imposed costs. Candidate
  contract-conflict runs create approval reports duplicating parts of the
  requested assessment; this follows the approval convention and is not a
  demonstrated scope violation.

Do not count uncommitted changes as failed delivery: these prompts do not request
commits. Functional success remains 8/8 per arm; explicitly blocked workflow
closure is a separate observation (baseline 2/8, candidate 0/8).

## Scope and reproducibility

- The treatment is the complete CodeStable package: skills, references, and runtime tools. Both arms use one frozen evaluator and identical task prompts/graders.
- Skill discovery and Codex configuration are isolated. The host OS/shell remain shared. Baseline freshness tooling read the host source/installed-copy metadata; observed source HEAD was the pinned baseline and global installs were unchanged. This is not a hermetic OS experiment.
- Two repetitions per family are descriptive evidence, not an equivalence or statistical superiority test. No aggregate framework-wide acceptance claim follows.
- No workflow prompt was adjusted using pilot results. Future workflow fixes need unseen fixture/prompt holdouts.
- Formal feature closure with subagent review, genuinely ambiguous owner choices, mid-turn steering, and live compaction remain outside this pilot.

Reproduction instructions: [comparison protocol](../plugins/codestable/skills/codestable-maintainer/references/live-comparison-protocol.md). Package/evaluator/scenario hashes and all 16 per-run usage/cost-proxy records: [results JSON](astra-live-pilot-results.json). Raw JSONL, complete fixtures, diffs, and initial/final snapshots are retained locally; credentials and temporary Codex homes are not retained.

Installation status: `not installed: N/A` for README, tests, and this report; they are repository-level evidence. Maintainer tools/references are installable package content. Real global skill roots require a separate remote-main publication and verified synchronization.

## 中文结论

保留当前 Astra 流程精简。本次先修复评测器与隔离问题，再完成 16 次正式真实模型运行；两版各 8 次，功能与文件边界检查均通过。新版输入 token 中位数下降 **48.0%**、耗时中位数下降 **21.7%**，输出 token 中位数只下降 3.0%。这支持在已测四类单轮任务中减少上下文和流程开销，尚不能推导整个 CodeStable 的生产效率或稳定性。

原计划中的运行中追加需求、用户回答后的继续执行，不能用当前单轮 ephemeral CLI 真实验证，因此未用单条 prompt 伪造。两次预检各两轮，独立于正式 16 轮；首次预检存在插件自动加载，未纳入对照。

此次迭代主要修复“启动失败也能通过”“预置文件算作修改”“提交后隐藏改动”“复合 Git 命令漏检”“工具事件重复或遗漏”等评测问题，没有为了让用例通过继续改写技能规则。正式运行使用冻结的旧包、新包和同一评测器。

独立语义复核确认 16 次实质结果均正确、没有实际向用户追问。旧版两个修复任务虽已交付正确代码和通过的验证，却明确报告流程收尾受阻；新版两个修复没有这种阻塞。应记录为“功能已完成、流程报告未闭环”，不能因未提交就判失败。报告中所称的独立审查平台错误缺少原始 dispatch 返回，因此不作为已证实的平台故障。

当前停止继续改写技能：已观察到的主要差异支持保留精简；小样本未显示需要修复的新版功能或契约回归。若进一步简化审批报告，应另用未见任务检验“已有交付物是否足够承载决策”，不能单为这两个样例删除正式决策证据。
