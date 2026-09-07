---
name: cs-feat-impl
description: "按已批准设计与清单实现功能，验证行为并记录正式审查证据。"
---

# cs-feat-impl

读取本会话尚未读过的 `.codestable/attention.md`。只加载任务相关上下文，已读且未改变的资料不重复读取。共享路径、worktree、审查及提交约定见 `.codestable/reference/shared-conventions.md` 第 0、2.6、4 节。

## 输入与范围

读取本功能 approved design、checklist 及当前实现。design 的 `doc_type=feature-design`、`feature`、`status=approved` 与任务一致，保留所需 summary / tags 等元数据。用户已批准而状态尚未同步时依据已有授权同步，不重复求批。

`{slug}-checklist.yaml` 的 `feature` 一致，steps / checks 非空。缺少必要契约时补齐或回 `cs-feat-design`；不因格式细节拒绝已充分说明的任务。标准 design 第 3 节是验收契约，fastforward design 对照第 2 节；具体测试和文件落点由实现判断。

## 实现

从首个未完成 step 继续，按依赖推进并更新 `status: done`。可自主细分或调整同一批准范围内的顺序并同步 checklist；保留确有独立验证/回滚意义的步骤边界。

内部命名、正常边界和错误处理自主判断。沿用项目领域概念；新增或改变对外概念时同步术语/接口说明，不为每个变量、条件分支或未逐字列出的文件求批。

只完成本功能和必要前置，不夹带无关重构。必要小结构调整可独立验证后继续；改变已批准行为、公开契约、架构所有权或存在实质产品取舍时，说明选择及影响，请求缺失的 owner 决定。不能通过回填 design 将意外行为伪装成批准结果。结构取舍确需帮助时才读 economy.md / code-design.md。

## 验证与审查

对关键场景及反向约束提供可观察证据。按风险选择类型检查、现有测试、针对性测试或浏览器操作；不机械给每处改动新增测试。通过后仅在新改动、失败或未解决疑问需要时扩大或重复验证。

正式 unit 使用独立 subagent review；仅环境确无 subagent 能力时按共享规则使用 fresh self-review fallback 并记录环境原因。保留 `{slug}-implementation-review.md` 的目标、审查方式、验证证据和 findings，P0/P1 先修复并复核。不将 self-review 冒称独立审查。

按 shared-conventions 第 2.6 节使用执行 worktree，保留无关改动、共享计划面及既有 override 契约。改动前执行 start gate；完成证据写入后执行 commit gate：

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/features/YYYY-MM-DD-{slug}
python3 .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/features/YYYY-MM-DD-{slug}
```

正式 review packet 需要时使用：

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

风险要求的 spec / verification 审查及 fresh command output 仍保留。不要等到 gate 才检查证据是否齐备。

## 完成

steps 完成、契约有证据、阻塞 findings 已处理且文档与范围一致后，简要报告结果、关键改动、验证和剩余限制，无需逐函数复述 diff。

用户已授权完成整个功能时继续 `cs-feat-accept`；只要求实现或明确设置 review checkpoint 时在该边界交付。提交/推送/发布沿用已有授权，完成实现不自动授权合并。只提出有具体价值的沉淀建议，不逐项询问固定收尾清单。
