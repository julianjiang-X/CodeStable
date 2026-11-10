# 架构决策记录（ADR）

本目录记录**本仓库自身**难以回退的架构决定——不是项目使用 CodeStable 时产生的决策
（那些走 `cs-keep decide`，落在项目的 `.codestable/compound/`）。

## 什么进这里

同时满足三条才写 ADR：

1. **难回退**——改变它需要动多个技能或工具；
2. **缺少上下文会令人意外**——后来者看到现状会问"为什么不用更常见的做法"；
3. **源于真实取舍**——存在被认真考虑过的替代方案。

只是"我们这么做"而没有取舍的，写进对应技能正文或 `cs-onboard/reference/`。

## frontmatter

```yaml
---
adr: "NNN"
title: "一句话决定"
status: Accepted | Superseded | Deprecated
superseded-by: "NNN"        # 可选
supersedes: ["NNN"]         # 可选
date: YYYY-MM-DD
applies-to: []              # 这条决策约束哪些路径
enforcement: none | review | test
stage: []                   # 在哪些环节需要对照检查
lint: "能验证这条决策仍成立的命令"   # enforcement=test 时必填
---
```

`enforcement` 的取值语义与 `cs-keep decide` 的 decision 文档一致：**能填 `test` 就不要填 `none`**。
写下来但没人守的决策会静默腐烂。

## 现有 ADR

| # | 决定 | status |
|---|---|---|
| [001](001-keep-shared-project-runtime.md) | 保留共享项目 runtime，并为它补上漂移检测 | Superseded by 005 |
| [002](002-keep-worktree-ownership.md) | CodeStable 继续拥有 worktree 与 branch guard 策略 | Accepted |
| [003](003-keep-staged-skill-topology.md) | 保留分阶段技能拓扑，用风险模型控制流程重量 | Superseded by 004 |
| [004](004-merge-stage-entries-keep-stage-text.md) | 合并阶段入口，保留阶段正文 | Accepted |
| [005](005-ship-shared-runtime-inside-skills.md) | 共享参考和工具随技能分发，不再复制进项目 | Accepted |
| [006](006-work-directories-graduate-and-delete.md) | 工作目录是工作状态，收尾时毕业并删除；进度现看，不存页面 | Accepted |

001–003 是 1.1.0 从上游 `codestable/CodeStable` v2 吸纳时，对**不吸纳**部分的评估结论。
完整差异分析见 `asset/2026-08-14-upstream-v2-comparison.md`。

004、005 是 3.0.0 依据 owner 的实际会话使用情况对 003、001 的修订，006 是同一轮扫描得出的
工作目录生命周期决定，见 `docs/claude-models-iteration.md`。
