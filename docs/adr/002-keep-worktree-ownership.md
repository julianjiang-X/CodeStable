---
adr: "002"
title: "CodeStable 继续拥有 worktree 与 branch guard 策略"
status: Accepted
date: 2026-08-14
applies-to:
  - "cs-onboard/tools/codestable-worktree-gate.py"
  - "cs-onboard/tools/codestable-ai-branch-guard.py"
  - "cs-onboard/tools/codestable-finish-worktree.py"
  - "cs-onboard/tools/codestable-worktree-inbox.py"
  - "cs-onboard/reference/execution-conventions.md"
enforcement: test
stage: [design, review, check]
lint: "python3 -m pytest tests/test_codestable_worktree_gate.py tests/test_codestable_ai_branch_guard.py"
---

# ADR-002: CodeStable 继续拥有 worktree 与 branch guard 策略

## Context

上游 ADR-002（`Accepted`，未被取代）规定：

> CodeStable 的 feature、issue、refactor、epic 和 review skills **不得规定默认 worktree、
> branch guard、finish-worktree 或 merge-inbox 流程**。它们应在宿主或 owner 已选择的
> checkout 环境中推进。

理由：把 workflow 指导和 branch policy 混在一起，会让 agent 把 worktree 创建当成 feature /
issue / refactor 的默认执行内容；而 worktree 和分支决策属于执行环境与 owner policy。

本仓库的 `execution-conventions.md`、worktree gate、AI branch guard hooks、finish inbox
与 main publish guard 全部建立在相反前提上。

## 评估

上游的论点是**关注点分离**：workflow skill 不该绑定执行环境策略。这在"CodeStable 作为可插拔
skill 包分发给任意宿主"的定位下是对的——不同宿主的分支策略不同，硬编码会造成不必要耦合。

但它依赖一个前提：**owner 或宿主已经选好了安全的 checkout 环境**。

本仓库的机械 guard 恰恰是为了处理这个前提**不成立**的情况：AI 在主检出上直接
`git switch` 后实现、在 `main` 上写代码、完成后忘记 finish。这些不是假想风险，是 branch guard
hooks 和 worktree gate 被加进来的原因（见对应 test 与 harness 场景）。

上游把这类风险交还给 owner policy；本仓库的产品判断是：**agent 会漂移，能机械拦的就机械拦**，
这与 1.1.0 吸纳的"机械 guard 优先"是同一条原则的不同应用范围——上游把它用在 lesson 上，
本仓库把它同时用在执行环境上。

代价是真实的：耦合了执行环境，worktree 能力无法独立演进，也让本仓库更难被当作通用 skill 包
分发到任意宿主。接受这个代价。

## Decision

- 保留 worktree gate、AI branch guard hooks、finish worktree、worktree inbox 与 main publish guard。
- 保留 `execution-conventions.md` 中的 worktree / finish / commit 门槛。
- 不吸纳上游 ADR-002。

## Consequences

- 本仓库的执行流程假定 git worktree 可用；不支持 worktree 的宿主需要显式降级路径。
- worktree 策略与 workflow skill 保持耦合，两者要一起演进。
- 与上游在这一点上永久分歧。

## Rejected alternatives

- **吸纳上游 ADR-002，把 worktree 交给 owner policy**。拒绝：会移除本仓库现有的漂移拦截，
  而这些拦截有测试和 harness 场景支撑。
- **把 worktree 规则做成可选开关**。暂缓：可选开关等于默认关闭时无保护，且需要一套配置面。
  真出现不支持 worktree 的宿主时再单独立项。
