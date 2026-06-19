## 8. check-context-sufficiency.py

context packet 完整性检查器。它只读已生成的 handoff / audience report，检查结构是否可识别、是否还有未脱敏 secret-like 文本（含常见裸 token 形态如 `sk-...` / `ghp_...`）；`--strict` 还要求有至少一个 concrete file 和 evidence 条目。

```bash
python3 .codestable/tools/check-context-sufficiency.py --file /tmp/codestable-human-review.md --strict --json
```

适用时机：

- dispatch human reviewer / subagent reviewer 前，确认 packet 不依赖隐藏聊天历史。
- 给 owner 决策或学习报告前，确认文件和证据没有空着。
- 发现输出里仍有 token / secret / api key 时，先重新生成或手动脱敏，再发给接收方。

JSON 关键字段：

- `ok`：是否通过。
- `shape`：`handoff` / `audience-report` / `null`。
- `findings`：P1 问题清单，包含 `missing_files`、`missing_evidence`、`unredacted_secret_like_text`、`unknown_context_shape`。

---

## 9. codestable-finish-worktree.py

execution worktree 合并前 finish gate。它会生成中文学习报告、跑 context sufficiency、写 merge readiness，并把 ready-to-merge 提醒登记到 Git common-dir 本地 inbox。它不会 merge、rebase、commit 或删除 worktree。

```bash
python3 .codestable/tools/codestable-finish-worktree.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --json \
  --validation "uv run pytest -> passed" \
  --validation "CLI smoke -> passed"
```

会生成：

- `{slug}-learning-report.md`
- `{slug}-learning-context-check.json`
- `{slug}-merge-readiness.json`
- `$(git rev-parse --git-common-dir)/codestable/worktree-inbox/{branch}.json`

关键规则：

- 必须在 linked execution worktree 运行，不能在 default branch / coordinator checkout 里标记 ready。
- 运行前必须没有未提交的普通变更；只允许本工具上次生成的
  `*-learning-report.md` / `*-learning-context-check.json` /
  `*-merge-readiness.json` 处于未提交状态并被刷新。
- implementation unit 需要已有 subagent review evidence。
- learner report frontmatter 会写 `covered_head`；branch 后续有新 commit 时 inbox 会报 `stale-report`。
- 如果后续 commit 只包含 finish gate 产物，inbox 仍视为同一份报告覆盖的
  ready-to-merge 状态；普通实现 / 文档 / 测试 commit 仍会变成 `stale-report`。
- 缺 validation、缺 review、unit 内还有 blocking backlog 时失败。

推荐收尾提交：

```bash
git add .codestable/features/YYYY-MM-DD-{slug}/{slug}-learning-report.md \
  .codestable/features/YYYY-MM-DD-{slug}/{slug}-learning-context-check.json \
  .codestable/features/YYYY-MM-DD-{slug}/{slug}-merge-readiness.json
git commit -m "docs: add {slug} finish report"
```

这一步只把学习报告和 readiness 产物固化到当前功能分支；不合并 `main`，也不替代用户明确授权的 merge / push。只包含 finish gate 产物的提交不会让 inbox 变成 `stale-report`。

---

## 10. codestable-worktree-inbox.py

跨 branch/worktree 的本地 merge reminder。它读取 Git common-dir 下的 inbox 记录，所以即使你之后切到另一个 branch，也能看到之前完成但未合并的 worktree。

```bash
python3 .codestable/tools/codestable-worktree-inbox.py --root . --json
```

状态：

- `ready-to-merge`：finish gate 已过，branch 尚未进入 base。
- `stale-report`：branch HEAD 已不同于 learner report 的 `covered_head`，必须重跑 finish gate。
- `merged`：base 已包含 `covered_head`，可以清理 worktree 或归档记录。
- `blocked`：branch / covered_head 等关键状态缺失。
- `abandoned`：owner 显式取消。

本地控制：

```bash
python3 .codestable/tools/codestable-worktree-inbox.py --root . --snooze codex_slug --until 2026-06-12T00:00:00Z --json
python3 .codestable/tools/codestable-worktree-inbox.py --root . --abandon codex_slug --reason "owner canceled" --json
```

未到期的 snooze 记录仍会出现在 `items` / `snoozed`，但不会进入
`ready_to_merge`，也不会让 doctor 提醒 owner 合并。branch 在 snooze 期间产生新
commit 时，状态仍会升级为 `stale-report` 并恢复 P1 提醒。

---

## 11. plan-commits.py

提交规划器。只读，不 stage、不 commit。用于提交前把 dirty tree 按逻辑 bucket 拆开，并发现 migration doc-sync、runbook doc-sync、tracked ignored、large file、live writer 等风险。

```bash
python3 .codestable/tools/plan-commits.py --root . --json
```

主要 bucket：

- `code` / `tests` / `docs`
- `migrations` / `database_docs`
- `data`
- `logs`
- `codestable`
- `installed_skill`
- `unknown`

典型 findings：

- migration 有变化但缺少 `docs/database/` 合同文档；
- 项目 `AGENTS.md` 声明了 source ↔ docs 映射，但 source 改了对应 runbook 没改；
- 已追踪文件现在被 `.gitignore` 忽略；
- 大文件或正在被写入的文件混进提交。

这个工具只给出建议。是否拆 commit、怎么 stage，仍由执行者按项目规则决定。

---

## 12. codestable-backlog.py

CodeStable 人审 / 后续事项积压扫描器。它只读 `.codestable/`，用于最终汇报前确认没有把人工决策点或 follow-up 隐藏掉。

```bash
python3 .codestable/tools/codestable-backlog.py --root . --json
```

会扫描：

- `needs-human-review`
- `Human review required`
- 显式 `Follow-up:` 行，以及 `## Follow-Ups` 章节下的 bullet
- accepted / deferred P2
- `attention.md` candidates

扫描会跳过 `.codestable/reference/` 和 `*-review-packet.md`，避免把工具说明或 reviewer 输入包里的示例文字当成当前 backlog。已解决的 follow-up 记录（例如 follow-up fixes / review closure / no remaining P0-P2）不会重复上报；canonical lifecycle 文件（`*-acceptance.md` / `*-ff-note.md` / `*-fix-note.md` / `*-apply-notes.md`）里 `status: canceled/cancelled/abandoned` 的 feature / issue / refactor 单元会被当作历史记录跳过；但当前单元的 `## Follow-Ups` 章节下的 bullet 会被视为当前 backlog。

JSON 每个 item 带 `kind`、`severity`、`blocking`、`file`、`line`、`unit`、`action`、`excerpt`。`needs-human-review` / `Human review required` 一律 P1；带 `required`、`must`、`blocking`、`before merge/publish/release/ship/completion` 的 follow-up 也会升为 P1。其他 follow-up / P2 / attention candidates 是 P2，必须解决、转 issue，或明确延期。
