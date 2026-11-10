---
adr: "004"
title: "合并阶段入口，保留阶段正文"
status: Accepted
supersedes: ["003"]
date: 2026-11-10
applies-to:
  - "cs*/SKILL.md"
  - "cs*/stages/"
enforcement: test
stage: [design, review, release]
lint: "python3 -m pytest tests/test_skill_openai_metadata.py tests/test_package_contract.py tests/test_codestable_behavior_harness.py"
---

# ADR-004: 合并阶段入口，保留阶段正文

## Context

ADR-003 决定保留 27 个分阶段入口，理由有两条：阶段入口带来可发现性；直接收敛到上游的 8 个入口
会连带删除 maintainer、行为 harness、共享工具和测试套件。

2026-11 对 owner 此前 40 天的会话做了扫描（130 个 Claude Code 会话、24 个有人类消息的 Codex
交互会话），结果改变了第一条理由的权重：

- owner 从未按名字调用过阶段技能。Codex 里 146 次技能读取全部由 agent 自行触发，Claude Code
  里没有任何 `/cs-*` 命令。可发现性对 owner 没有产生价值。
- 被合并的入口里有六个在两个工具里合计只用过 0 到 1 次（`cs-arch`、`cs-learn`、`cs-refactor`、
  `cs-req`、`cs-trick`、`cs-note`）。
- 28 个描述常驻上下文，技能还在未接入的仓库里被自动加载（桌面规则、手机配置、课程作业）。

ADR-003 的第二条理由仍然成立，所以本决定不采用上游的做法。

## Decision

- 入口从 28 个合并为 15 个。阶段不取消：阶段技能的正文原样移到父技能的 `stages/<阶段>.md`，
  父技能的 `SKILL.md` 负责路由。
  - `cs-feat`：design / ff / impl / accept
  - `cs-issue`：report / analyze / fix
  - `cs-refactor`：ff
  - `cs-keep`（新）：note / learn / trick / decide / req / arch
- 正文里用 `cs-feat design`、`cs-keep note` 这种写法指代阶段。
- maintainer、行为 harness、工具和测试套件全部保留。
- ADR-003 的另两条继续有效：由 `assurance.md` 统一"风险决定保障强度"；单个入口内部不得按
  task kind 自建流程档位。

## Consequences

- 破坏性发布（3.0.0）：14 个旧名字退役，安装副本要先删旧目录，见 `UPGRADE.md`。
- 项目文档、`attention.md` 和派工模板里点了旧名字的地方需要改写；历史档案不动。
- 一次任务读的正文量基本不变（路由文件加一个阶段文件），减少的是常驻的描述数量和触发面。
- 与上游的入口拓扑仍然不同：上游把阶段正文重写进单个技能，本仓库保留阶段文件。

## Rejected alternatives

- **维持 ADR-003**。拒绝：它依赖的可发现性收益在实际使用里没有出现，而触发面过宽的代价出现了。
- **跟随上游收敛到 8 个入口并重写正文**。拒绝：理由同 ADR-003，删除面覆盖 harness 与测试，
  且阶段正文是经过验证的资产。
- **保留旧名字作为转发别名**。拒绝：别名继续占用描述预算并保留旧的触发面，正是要消除的东西。

## Evidence and limits

扫描方法、数字和局限见 `docs/claude-models-iteration.md`。数据只覆盖一位 owner 的 40 天；
合并后的行为只经过确定性 harness 验证，没有做真实模型对照。
