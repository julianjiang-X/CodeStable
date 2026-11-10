# Claude model iteration (Fable 5.2, Opus 5.5, Sonnet 5.5)

This change set tunes CodeStable for the Claude models the owner runs today. It
follows the fully read [Prompting Claude Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)
guide and [Spending your effort](https://claude.dev/blog/spending-your-effort/),
retrieved November 9, 2026, and a scan of the owner's own sessions from the
preceding 40 days (130 Claude Code sessions and 24 interactive Codex sessions
with human messages).

## What the sessions showed

| Observation | Evidence |
|---|---|
| Over-asking was not the friction | No "stop asking" complaints in either tool. Of 59 stops in CodeStable sessions, none was answered with a bare go-ahead. |
| Progress and next step were unclear | "How is progress" was the most frequent short message. Owners asked "what is the next step" after approval reports. |
| Standing rules had to be repeated | "No PR, no merge" three times in one unit. "Only my part, minimum necessary" at least five times across projects. |
| "Verified" was claimed too early | At least four results were overturned by the owner's own test. |
| Agents listed next steps and stopped | The owner had to reply "continue" with nothing to decide. |
| Option menus read as no ownership | Two negative reports about `cs-brainstorm`, one explicit. |
| Skills loaded outside onboarded repos | Desktop rules, a phone setup task, a service restart and two coursework repositories. |
| The review round budget caused a stop | The owner was asked twice in a row to authorize a fourth round. |
| Shared tools and references were idle | 18 tool scripts ran 0 times. 12 of 19 reference files were never read. |

## What changed

1. **Scope gate.** `cs` and `using-codestable` now state that CodeStable applies
   only where `.codestable/attention.md` exists, or when the user names a skill
   or asks for setup. Skill descriptions carry the same condition.
2. **Standing owner rules.** A scope or authorization rule the owner states is
   recorded in `attention.md` in the same turn (`cs`, `using-codestable`,
   `cs-keep note`). `cs-keep note` also asks for scoped, reasoned cautions and for pruning,
   because Claude Fable 5.2 applies cautions as written and they accumulate.
3. **Reporting.** Reports name what was and was not exercised and end with the
   next step, which is taken when already authorized.
4. **Round budget.** The rule now says what to do at the budget instead of
   implying a stop. One converging extra round is pre-authorized.
5. **Discussion stance.** `cs-brainstorm` leads with a position and reasons.
   `cs-feat design` separates what the agent decides from what the owner decides.
   Explicit `interview me` and `grill me` are unchanged.

## Structural change in 3.0.0

The owner approved the structural part after the first round.

- 28 skill entries became 15. Stage skills moved unchanged into `stages/` of
  `cs-feat`, `cs-issue` and `cs-refactor`. Six record skills became modes of the
  new `cs-keep`. The owner never invoked a stage skill by name in the scanned
  sessions, and six of the merged skills had zero or one use.
- Shared references and tools ship inside each skill. Projects no longer hold a
  `reference/` or `tools/` copy to refresh. In the scan, the copied tool scripts
  ran 0 times and the most active project had no copy at all.

Lifecycle records, review independence, worktree gates and publication gates
are unchanged. Approval triggers are unchanged except for the two items above:
a converging fourth review round no longer needs the owner, and an owner-stated
scope rule counts as authorization to record it.

## Work directories are working state (3.0.0, same scan)

The scan and the owner's confirmation gave five facts. After a task ends, its
design, checklist, review record and acceptance report are opened by nobody but
agents; the times an archive helped were all during the task (resuming after a
compaction, reviewing against the contract) and never a later task reading an
old feature's design. `.codestable/` grew fast: one project reached 307 files
(about 2 MB) in 25 days, another 474 files (about 3 MB), and old records are
retrieval noise that drift from the code. "How is progress" was the most frequent
short message because progress was spread over dozens of units with no
authoritative place. Sessions delegated by another agent produced full
design + checklist + acceptance files nobody read, because the delegation said
"follow the CodeStable process". And some projects required every CodeStable
text as a full English block plus a full Chinese block; the owner agreed that
files only agents read need no bilingual copy.

| Change | Where |
|---|---|
| A work directory is working state, not an archive, and is not created by default. It is created only when the task spans sessions or is handed off, has a contract the owner must approve, needs a formal independent review under `assurance.md`, or the owner asks for a record. Delegation text such as "follow the CodeStable process" does not change this. | `cs-feat`, `cs-issue`, `cs-refactor`, `assurance.md`, `shared-conventions.md` section 3 |
| At closure (accepted, fix verified, refactor done, or cancelled): graduate what is still needed (every item in the list has a home or "no need to keep"), write the closing commit message as the long-term record, run the finish gate if it applies, then delete the work directory in its own commit (deletion plus non-implementation `.codestable/**` changes only; the gates read the unit from HEAD, so a deletion cannot skip the review check). Not deleted when blocked, with an open approval report, when the owner asks to keep it, or with unresolved audit findings. | `cs-feat accept`, `cs-feat ff`, `cs-issue fix`, `cs-refactor`, `cs-goal`, `cs-audit` |
| No stored progress page. A progress question (and a resumed session) is answered by looking: work directories in this checkout and every linked worktree (units with a completion marker that the branch changed since forking from the default branch are listed as closing; unchanged finished records from before 3.0.0 are only counted), branches ahead of the default branch or with uncommitted changes, undecided approval reports, unmerged finished worktrees and open PRs, the last ~10 default-branch commits, and the roadmap or in-progress units for what is next. The answer goes to the owner in the conversation, with a pointer on every line and what was not checked. `codestable-status.py` gathers it in one read-only call. A stored `status.md` was considered and rejected (ADR 006). | `shared-conventions.md` section 8, `cs`, `using-codestable`, `codestable-status.py` |
| Files only agents read are written in one language, named by `attention.md`. The bilingual check now covers only `approval-report.md`, which is written for the owner. | `shared-conventions.md`, `codestable_common.py` |
| Opening searches read `attention.md`, `requirements/`, `architecture/`, `compound/` and in-progress work directories. Ended units left from before 3.0.0 are read only when the owner points at one or the task continues it. | `shared-conventions.md` section 5, stage files |

Old units in existing projects are not migrated or deleted. The tools cope with a
commit that deletes a whole finished unit (commit gate, doctor, inbox, review
validator); this is covered by `tests/test_codestable_closed_units.py`.
Decision record: `docs/adr/006-work-directories-graduate-and-delete.md`.

## Model and effort by stage

Model and effort are chosen by the owner, not by a skill, so this is guidance
only. Source: [Which Claude model should you build with](https://claude.dev/blog/which-claude-model-should-you-build-with/),
read on 2026-11-10, plus the effort blog above. The model article's points used
here: the default starting point is Opus 5.5 at medium effort; well-specified
coding against a spec fits Sonnet 5.5 (medium, then high); major refactors,
architecture planning and work with many subagents fit Fable 5.2 (medium, then
high); checkable subtasks such as finding files, reading logs and summarizing fit
Haiku 5.5 or Sonnet 5.5; spending beyond high effort can cost as much as a larger
model; keep the context of the expensive model lean. The effort blog reports that
higher effort removes missed edge cases but does not correct a wrong reading of
the task, and that it makes more assumptions on the owner's behalf.

| Stage | Model | Effort | Reason |
|---|---|---|---|
| Brainstorm, interview, design discussion | Fable 5.2 or Opus 5.5 | medium | The owner is in the loop. A wrong reading is fixed by asking, not by effort. |
| Implementation from an approved design | Sonnet 5.5 (a hypothesis to test, see below) | medium, then high | The contract is fixed. Raise effort for brownfield or risky paths. |
| Acceptance, audit, issue analysis, review | the session default (Opus 5.5) | high | Verification and hidden edge cases are where effort pays. |
| Long unattended goal runs | Opus 5.5; Fable 5.2 with many subagents or a major refactor | high, xhigh only with a measured gain | Lower levels stop early more often. |
| Finding files, reading logs, summarizing | Haiku 5.5 or Sonnet 5.5 | low to medium | The answer is easy to check. |

The Sonnet row is untested here. The article is cautious about "a large model
plans, a small model edits", so try it on a few tasks and compare against the
default before relying on it.

When a model is not good enough, escalate in this order: first add automatic
verification (tests, checkers), then raise effort one level, and only then move
to a larger model, starting that model at a lower effort. Past high effort the
cost may match a larger model, which is why the order ends there.

Rerun this table for each model release. It was written for the models above.

## Limits

These edits are text changes validated by the deterministic harness only. No
live model comparison was run for them. The session scan is one owner's usage
over 40 days and its classifications came from model judges. Deleting work
directories at closure has not been observed yet: whether the closing commit
message is enough, and whether progress
questions drop are all unverified. `codestable-status.py` is covered by tests; it
reports what exists, not why a unit is stuck.

---

# Claude 模型迭代（Fable 5.2、Opus 5.5、Sonnet 5.5）

本次改动按 owner 目前使用的 Claude 模型调整 CodeStable。依据是完整阅读的
[Prompting Claude Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)
与 [Spending your effort](https://claude.dev/blog/spending-your-effort/)（读取日期
2026-11-09），以及对 owner 此前 40 天会话的扫描（130 个 Claude Code 会话、24 个有
人类消息的 Codex 交互会话）。

## 会话显示了什么

| 现象 | 证据 |
|---|---|
| 摩擦不在"问太多" | 两个工具里都没有"别问"类抱怨。CodeStable 会话的 59 次停下，没有一次得到纯放行式回复。 |
| 进度和下一步不清楚 | "进度如何"是最高频的短消息。审批报告之后 owner 追问"下一步是什么"。 |
| 规矩要重复说 | 同一 unit 内"不建 PR、不合并"说了三次。"只做我的部分、最小必要"跨项目至少五次。 |
| "已验证"说早了 | 至少四个结论被 owner 实测推翻。 |
| 列完下一步就停 | owner 只能回"继续"，其实没有要决定的事。 |
| 选项菜单被视为没有 ownership | `cs-brainstorm` 两次负面反馈，其中一次是明确批评。 |
| 技能在未接入的仓库被加载 | 桌面规则、手机配置、服务重启和两个课程作业仓库。 |
| 审查轮次上限造成停顿 | 连续两次请 owner 授权第四轮。 |
| 共享工具和参考闲置 | 18 个工具脚本执行 0 次。19 个参考文件里 12 个从未被读。 |

## 改了什么

1. **范围门槛。** `cs` 与 `using-codestable` 写明：仓库有 `.codestable/attention.md`，
   或用户点名技能、要求接入时才启用。各技能的描述带同一条件。
2. **owner 的常驻规矩。** owner 说出的范围或授权规矩当场写入 `attention.md`
   （`cs`、`using-codestable`、`cs-keep note`）。`cs-keep note` 还要求谨慎条款写明范围和原因
   、原因不成立时提出删除，因为 Claude Fable 5.2 会照字面执行这类条款，而它们会越积越多。
3. **汇报。** 汇报写明哪些跑过、哪些没跑，末尾写出下一步；已有授权时直接做。
4. **轮次上限。** 规则现在写明到上限后怎么办，不再隐含"停下"。收敛中的额外一轮
   预先授权。
5. **讨论方式。** `cs-brainstorm` 先给主张和理由。`cs-feat design` 区分 agent 自己
   定的事和 owner 定的事。显式 `interview me` 与 `grill me` 不变。

## 3.0.0 的结构改动

第一轮之后 owner 批准了结构部分。

- 28 个技能入口变成 15 个。阶段技能的正文原样移进 `cs-feat`、`cs-issue`、
  `cs-refactor` 的 `stages/`；六个记录类技能变成新技能 `cs-keep` 的模式。扫描到的
  会话里 owner 从未点名调用过阶段技能，被合并的技能里有六个只用过 0 到 1 次。
- 共享参考和工具随各技能分发，项目里不再有需要刷新的 `reference/`、`tools/` 副本。
  扫描期间复制到项目的工具脚本执行了 0 次，最活跃的项目里根本没有副本。

生命周期档案、审查独立性、worktree 门禁和发布门禁都不变。审批触发条件除上面两处外
不变：收敛中的第四轮审查不再需要 owner，owner 说出的范围规矩本身算记录授权。

## 工作目录是工作状态（3.0.0，同一轮扫描）

扫描加上 owner 的确认，得到五条事实。任务做完之后，设计、清单、审查记录和验收报告
只有 agent 会打开；档案帮上忙的几次都发生在任务进行中（压缩上下文后续上同一任务、
审查对照契约），没有一次是后来的任务去读旧功能的设计。`.codestable/` 膨胀很快：
一个项目 25 天长到 307 个文件约 2 MB，另一个 474 个文件约 3 MB，旧档案是检索噪声，
和代码漂移后还要专门修。"进度如何"是最高频的短消息，原因是进度散在几十个单元里，
没有一处是权威的。被别的 agent 派工的会话，因为派工说明里一句"照 CodeStable 流程"，
产出了没人读的完整设计 + 清单 + 验收文件。有的项目规定 CodeStable 文字写完整英文块
加完整中文块，owner 已同意只给 agent 读的文件不需要双语。

| 改动 | 位置 |
|---|---|
| 工作目录是工作状态，不是档案，默认不建。只在任务会跨会话或要交接、有待 owner 批准的契约、按 `assurance.md` 需要正式独立审查、owner 要求留痕之一成立时创建。派工说明里的"照 CodeStable 流程"不改变这一点。 | `cs-feat`、`cs-issue`、`cs-refactor`、`assurance.md`、`shared-conventions.md` 第 3 节 |
| 收尾（验收通过、修复验证完成、重构完成或被取消）：毕业（清单里每项有去处或"不需保留"）、结案提交（提交信息是长期记录）、适用时跑 finish gate、最后在单独的提交里删除工作目录（只含目录删除和非实现的 `.codestable/**` 改动；门禁按 HEAD 里的内容判断，删除绕不过 review 检查）。阻塞未完成、有未决 approval report、owner 要求保留、审计有未解决 finding 时不删。 | `cs-feat accept`、`cs-feat ff`、`cs-issue fix`、`cs-refactor`、`cs-goal`、`cs-audit` |
| 不存进度页。被问进度（以及会话接续）时现看：本检出和各 linked worktree 里的工作目录（有完成标记且自分叉以来被该分支改动过的算收尾中，照样列出；没改动过的早期已完成记录只计数）、领先默认分支或有改动的分支、未决 approval report、已完成未合并的 worktree 和打开的 PR、默认分支最近约 10 个提交，下一步取 roadmap 或进行中单元。答案在对话里给 owner，每行带指针并说明没查的部分。`codestable-status.py` 只读、一次取齐。曾考虑存 `status.md` 后拒绝（ADR 006）。 | `shared-conventions.md` 第 8 节、`cs`、`using-codestable`、`codestable-status.py` |
| 只给 agent 读的文件用一种语言，由 `attention.md` 指定。双语检查收窄到写给 owner 的 `approval-report.md`。 | `shared-conventions.md`、`codestable_common.py` |
| 开工检索读 `attention.md`、`requirements/`、`architecture/`、`compound/` 和进行中的工作目录。3.0.0 之前留下的已结束单元只在 owner 指到或当前任务接续它时才读。 | `shared-conventions.md` 第 5 节、各阶段文件 |

既有项目里的旧单元不迁移、不删除。工具能处理"一个提交删除整个已完成单元"（commit gate、
doctor、inbox、审查校验），由 `tests/test_codestable_closed_units.py` 覆盖。决策记录见
`docs/adr/006-work-directories-graduate-and-delete.md`。

## 各阶段的模型和努力级别

模型和努力级别由 owner 选择，技能无法设置，所以这里只是建议。依据是
[Which Claude model should you build with](https://claude.dev/blog/which-claude-model-should-you-build-with/)
（读取日期 2026-11-10）和上面的努力级别博客。模型文章里用到的要点：默认起点是
Opus 5.5 加 medium；范围明确、照规格做的编码用 Sonnet 5.5（medium，再 high）；重大重构、
架构规划、带多个子代理用 Fable 5.2（medium，再 high）；找文件、读日志、汇总这类容易验
对错的子任务用 Haiku 5.5 或 Sonnet 5.5；超过 high 之后的花费可能和换更大的模型一样多；
让贵模型的上下文保持精简。努力级别博客的数据是：更高的努力能减少漏掉的边界情况，但
纠正不了对任务的错误理解，并且会替 owner 做更多假设。

| 阶段 | 模型 | 努力级别 | 原因 |
|---|---|---|---|
| 脑暴、访谈、设计讨论 | Fable 5.2 或 Opus 5.5 | medium | owner 在场。理解错了靠提问纠正，不靠努力。 |
| 按已批准设计实现 | Sonnet 5.5（待测的假设，见下） | medium，再 high | 契约已定。存量代码或高风险路径再调高。 |
| 验收、审计、问题分析、审查 | 会话默认模型（Opus 5.5） | high | 验证和隐藏边界情况是努力最有回报的地方。 |
| 长时间无人值守的 goal | Opus 5.5；子代理多或大重构用 Fable 5.2 | high；xhigh 仅在实测有收益时 | 低级别更容易提前停。 |
| 找文件、读日志、汇总 | Haiku 5.5 或 Sonnet 5.5 | low 到 medium | 答案容易验对错。 |

Sonnet 这一行在本仓库未经验证。文章对"大模型规划、小模型改代码"持保留态度，所以先在
几个任务上和默认模型对比，再决定是否依赖。

模型不够好时按这个顺序升级：先加自动验证（测试、检查器），再提一档努力级别，最后才换
更大的模型，并从较低的努力级别起步。超过 high 之后的花费可能和换更大的模型一样多，所以
顺序到此为止。

每次模型发布后重做这张表。它是按上面列出的模型写的。

## 局限

这些是文字改动，只经过确定性 harness 验证，没有为它们做真实模型对照。会话扫描
只覆盖一位 owner 40 天的使用，其中的分类来自模型评判。收尾时删除工作目录的效果尚未观察到：
结案提交信息是否够用、进度类提问是否减少，都未验证。`codestable-status.py` 有测试覆盖，
只报告现有状态，不判断单元为什么卡住。
