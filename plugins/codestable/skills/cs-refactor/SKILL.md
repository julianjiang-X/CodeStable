---
name: cs-refactor
description: "在保持行为的前提下优化代码结构，按风险验证并记录变化。"
---

# cs-refactor

读取本会话尚未读过的 `.codestable/attention.md`。只加载任务相关上下文，已读且未改变的资料不重复读取。共享路径、worktree、审查及提交约定见 `.codestable/reference/shared-conventions.md` 第 0、2.6、4 节。

保持外部可观察行为并改善具体结构或性能问题。范围明确的小重构走 `cs-refactor-ff`；较大任务用 scan / design / apply 保持可追溯。文件数、行数和浏览器验证需求不单独决定流程。

## 文件与授权

正式 unit 位于 `.codestable/refactors/YYYY-MM-DD-{slug}/`：

- `{slug}-scan.md`：问题与候选范围。
- `{slug}-refactor-design.md`：批准范围与等价验证方案。
- `{slug}-checklist.yaml`：执行和验证状态。
- `{slug}-apply-notes.md`、`{slug}-implementation-review.md`：结果证据。

`grill/*.md` 仅在相关时读；只将 `doc_type: grill-context`、`status: accepted`、`source_of_truth: false` 的文件作为 human review context，不能覆盖上述记录或行为等价证据。

用户已要求完成具体重构时，不逐阶段、逐条勾选重复审批；只读扫描/评估请求保持只读。实质行为、架构权责或未决范围取舍由 owner 决定。

## 1. scan

从用户指明的文件或模块开始，较大范围按依赖划分可验证批次，不用固定行数阈值让用户缩范围。定位具体重复、职责冲突或性能代价，零项是有效结果，不凑数量。

遇到生成源、跨模块或证据不足问题时按需读 `reference/refusal-routing.md`；不要机械中止可完成的定位和准备。输出格式见 `reference/scan-checklist-format.md`。方法细节确需参考时才读 `reference/methods.md` 索引和相关分篇，不强制每项对应方法编号。

## 2. design

依据已有用户授权选择条目并记录依据；只有未决实质取舍需要用户选择。计划包含依赖顺序、行为等价边界、退出证据和回滚方式，生成 checklist 的 steps / checks 并用 `validate-yaml.py` 校验。已有范围授权且无新取舍时同步 approved 状态，不伪造逐项审批。

### design 文件结构

```markdown
---
doc_type: refactor-design
refactor: {YYYY-MM-DD}-{slug}
status: draft | approved
scope: {扫描范围一句话}
summary: {本次要做的几条是什么，一句话}
---

# {slug} refactor design

## 1. 本次范围
- 从 scan 勾选了哪几条（编号）
- 明确不做的（被 ✗ 的）和理由
- 预估总工作量 / 总风险档位

## 2. 前置依赖
- 测试覆盖补齐（如需）
- 调用方搜索（如需）
- 其他一次性准备

## 3. 执行顺序
按步骤列，每步一块：
- 步骤 N：{一句话动作}
- 引用方法：M-Ln-NN {方法名}
- 具体操作：{照方法库步骤落到本项目具体文件 / 函数}
- 退出信号：{AI 跑什么测试 / HUMAN 看什么页面}
- 验证责任：AI 自证 ｜ HUMAN
- 回滚：{出问题怎么还原，通常 git revert 某步}

## 4. 风险与看点
- 高风险步骤汇总
- 容易出错的点（跨步骤数据流变化等）
```


## 3. apply

按依赖推进 checklist，可自主细分或调整同一批准范围内顺序并记录。确有独立回滚意义的步骤保留退出证据。内部实现选择不重复求批，改变行为或实质架构权责才请求 owner。

AI 能完成的测试、浏览器或引用核查自行完成；只有必须由用户操作或明确要求的人类判断才标 HUMAN。未取得必要证据时不标 passed，可继续不依赖它的工作。

### apply-notes 格式

```markdown
---
doc_type: refactor-apply-notes
refactor: {YYYY-MM-DD}-{slug}
---

# {slug} apply notes

## 步骤 1: {动作}
- 完成时间: {date}
- 改动文件: {file list}
- 验证结果: {测试输出 / HUMAN 确认语录}
- 偏离: {无 / 具体描述}

## 步骤 2: ...

## 独立 code review
- reviewer: {实际 reviewer；环境无能力时 fallback 并写明原因}
- evidence: {slug}-implementation-review.md
- 结果: {P0/P1 无阻塞 / 已修复清单}
- P2: {无 / 后续 issue / 用户接受风险}
```


## 验证与审查

验证受影响行为、公开契约和声称改善的性能；选择相称测试、类型检查、浏览器或 benchmark，不无条件全量测试加 lint。无新改动或未解决疑问不重复验证。

正式 unit 使用独立 subagent review；仅环境确无 subagent 能力时按共享规则使用 fresh self-review fallback 并记录环境原因。保留 `{slug}-implementation-review.md` 的目标、审查方式、验证证据和 findings，P0/P1 先修复并复核。不将 self-review 冒称独立审查。

按 shared-conventions 第 2.6 节使用执行 worktree，保留无关改动、共享计划面及既有 override 契约。改动前执行 start gate；完成证据写入后执行 commit gate：

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/refactors/YYYY-MM-DD-{slug}
python3 .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/refactors/YYYY-MM-DD-{slug}
```

正式 review packet 需要时使用：

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit .codestable/refactors/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

风险要求的 spec / verification 审查及 fresh command output 仍保留。不要等到 gate 才检查证据是否齐备。

## 完成

checklist 与证据一致，scan / design / apply-notes / review 反映实际结果且 P0/P1 无阻塞后报告完成。未取得必要人类验证时明确未完成，不伪造通过。继续已有提交/推送授权，完成重构不自动授权合并或发布。

新能力与 bug 修复不混入重构；跨模块边界重划若缺少批准，先说明提案和影响，不把提案写入现状 architecture。只提出有具体价值的后续 learning / decision 建议。
