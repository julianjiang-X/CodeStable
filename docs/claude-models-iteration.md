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

## Effort by stage

Effort is set by the owner, not by a skill, so this is guidance only. The blog
reports that higher effort removes missed edge cases but does not correct a
wrong reading of the task, and that it makes more assumptions on the owner's
behalf.

| Stage | Suggested effort | Reason |
|---|---|---|
| Brainstorm, interview, design discussion | medium | The owner is in the loop. A wrong reading is fixed by asking, not by effort. |
| Implementation from an approved design | medium to high | The contract is fixed. Raise effort for brownfield or risky paths. |
| Acceptance, audit, issue analysis, review | high | Verification and hidden edge cases are where effort pays. |
| Long unattended goal runs | high, xhigh only with a measured gain | Lower levels stop early more often. |

Rerun this table for each model release. It was written for the models above.

## Limits

These edits are text changes validated by the deterministic harness only. No
live model comparison was run for them. The session scan is one owner's usage
over 40 days and its classifications came from model judges.

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

## 各阶段的努力级别

努力级别由 owner 设置，技能无法设置，所以这里只是建议。博客的数据是：更高的努力
能减少漏掉的边界情况，但纠正不了对任务的错误理解，并且会替 owner 做更多假设。

| 阶段 | 建议级别 | 原因 |
|---|---|---|
| 脑暴、访谈、设计讨论 | medium | owner 在场。理解错了靠提问纠正，不靠努力。 |
| 按已批准设计实现 | medium 到 high | 契约已定。存量代码或高风险路径再调高。 |
| 验收、审计、问题分析、审查 | high | 验证和隐藏边界情况是努力最有回报的地方。 |
| 长时间无人值守的 goal | high；xhigh 仅在实测有收益时 | 低级别更容易提前停。 |

每次模型发布后重做这张表。它是按上面列出的模型写的。

## 局限

这些是文字改动，只经过确定性 harness 验证，没有为它们做真实模型对照。会话扫描
只覆盖一位 owner 40 天的使用，其中的分类来自模型评判。
