# 证据成熟度（evidence 生命周期）

归档类文档（`.codestable/compound/` 下的 learning / trick / decision / explore）的结论不是一落盘就可信。`evidence` 字段记录它被验证到哪一步。

由 `cs-onboard` 从技能包复制到 `.codestable/reference/evidence-lifecycle.md`。`cs-learn` / `cs-trick` / `cs-decide` / `cs-explore` 写入时用它，四个执行技能检索命中时用它。

`evidence` 与 `status` 正交，不要混用：`status` 说的是**这份文档还算不算数**（active / superseded / outdated / deprecated），`evidence` 说的是**里面的结论被验证到什么程度**。一条 `status: active` 的 learning 完全可以是 `evidence: observed`。

## 三态

| evidence | 判据 |
|---|---|
| `observed` | 单次任务已有证据，尚未在独立后续任务中验证 |
| `validated` | 在**非创建该文档的任务**中有效命中，真实改变了计划或验证，或明确排除了一个具体且合理的错误路径，并验证成功 |
| `retired` | 被仓库事实反证、scope 完全失效，或已有更强的 canonical owner 承接 |

## 硬规则

1. **新文档一律从 `observed` 开始。**
2. **不能自证 `validated`**——创建该文档的同一个任务不能把它标成 validated；命中次数、模型自评置信度都不是晋级依据。
3. `observed → validated` 只在独立后续任务确实采用并验证成功时发生，**只补一次代表性证据**：记录它实际改变的计划或验证（或明确排除的错误路径）+ 本次通过的验收证据。不追加逐次命中日志。
4. `→ retired` 只写反证 / 替代原因与指针。**retired 上的新结论必须另建 `observed` 文档**，不继承旧条目的 validated 身份，也不复活原结论。
5. 旧文档缺 `evidence` 字段按 `observed` 读取，**不批量迁移**；只在真实状态变化或本来就要更新时补字段。
6. 稳定的 validated 命中不产生文件 churn——命中了但没有状态变化就不写文件。

## 应用侧（读的人）

`retired` 不应用；`observed` / `validated` 都要先用当前代码、测试或 canonical 文档核实再用。

做**一次有界、最低成本**的定向核实，核实不了就跳过该条，不阻塞正常任务，不为核实一条经验去跑大范围测试或反复复现。当前事实明确反证时立即停止应用，证据不足时不猜。

**命中报告格式**：

```text
经验命中：{path}（{evidence}）；核验：{fact}；影响：{plan_or_check}
```

只是相关但没有改变行为时不报，不制造复用证据。

## 预算与优先级

**预算**：`.codestable/compound/` 维持约 50 条。达到预算先整理、晋升、合并或退役，不简单扩容。

**机械 guard 优先**：能被测试、checker、lint、类型或 deterministic helper 阻止的重复错误，优先机械化，不另写一条重复的归档文档。只有当机械化会扩大当前任务 scope 时，才降级为写文档 + 建议后续机械化。
