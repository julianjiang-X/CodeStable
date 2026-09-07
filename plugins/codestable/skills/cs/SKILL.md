---
name: cs
description: Choose a CodeStable workflow or explain the system when routing or the next stage is unclear.
---

# cs

触发简称是 `cs`。用户已指明技能或阶段时直接使用它。
读取并复用 `.codestable/attention.md`；其他上下文按任务查找。
用户明确指令优先于技能指南。小改和定向问答可直接完成，不自动创建单元。
没有接入时仍可普通工作；仅在用户要求接入时使用 `cs-onboard`。

## 路由并继续

根据意图与相关现有单元选择阶段，简短说明并继续已授权工作。
不为选择技能暂停、不重复阶段审批、不每轮遍历所有目录或检查技能更新。
只有未解决的目标、契约或授权会改变结果时询问。复用相关单元；不同目标
分别记录，可以在同一请求内推进。

| 诉求 | 技能 |
|---|---|
| 项目接入或升级 | `cs-onboard` |
| 限定起点、终点与验收结果的自主迭代 | `cs-goal` |
| 方向探索、权衡、显式 grill | `cs-brainstorm` |
| 跨功能规划与接口拆分 | `cs-roadmap` |
| 新增能力 | `cs-feat`：design / ff / impl / accept |
| 缺陷 | `cs-issue`：report / analyze / fix |
| 保持行为的优化 | `cs-refactor` / `cs-refactor-ff` |
| 定向理解代码 | `cs-explore` |
| 只读风险审查 | `cs-audit` |
| 需求与架构 | `cs-req` / `cs-arch` |
| 决策、经验、技巧、常驻提示 | `cs-decide` / `cs-learn` / `cs-trick` / `cs-note` |
| 对外指南 | `cs-guide` |
| CodeStable 源码、harness、发布与安装 | `codestable-maintainer` |

## 决策边界

只读分析、设计讨论或 audit 不擅自扩为实现。已授权实现持续至相关验证
完成；未批准的产品契约变更先准备证据，再交 owner 决策。代码或历史草稿
不构成批准。正式阶段保留所需状态与证据。

有实质 owner 决策时按 `.codestable/reference/approval-conventions.md`
使用已有阶段报告；它不足以承载决策时才补 `approval-report.md`。
普通路由不生成审批报告。项目的 L0–L4 等级描述决策范围，不自动新增审批。

小任务不自动触发 full grill。`interview me` / “采访我” / “先问我”补足缺失上下文；
`grill me` / “拷问我” / “追问我” / “多问几轮”进入显式
深度讨论，按需读 `.codestable/reference/interaction-modes.md`。
无限定终点的 grill 不转为 goal。grill-context 保留 `source_of_truth: false`，
不能替代正式 spec。用户只问体系时简答，完整结构按需读
`.codestable/reference/system-overview.md`。

## 安装边界

共享安装目录是部署产物。源码改动使用 `codestable-maintainer`：功能分支
推送后用 fresh clone 和临时安装根验证；真实 installed root 只从远端
`main` 同步。推分支不授权合并或推 main，也不允许手工覆盖真实安装副本。
