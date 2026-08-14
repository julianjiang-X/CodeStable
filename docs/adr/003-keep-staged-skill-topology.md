---
adr: "003"
title: "保留分阶段技能拓扑，用风险模型而不是合并入口来控制流程重量"
status: Accepted
date: 2026-08-14
applies-to:
  - "cs*/SKILL.md"
  - "cs-onboard/reference/assurance.md"
enforcement: test
stage: [design, review, release]
lint: "python3 -m pytest tests/test_skill_openai_metadata.py tests/test_package_contract.py"
---

# ADR-003: 保留分阶段技能拓扑，用风险模型而不是合并入口来控制流程重量

## Context

上游 v2 把 32 个技能入口收敛为 8 个，退役 24 个名称且不留兼容 shim，只保留
`cs-code-review → cs-review` 一个别名。

理由（CHANGELOG 2.0.0 + ADR-004）：阶段化入口让"该做多重"由**入口名**决定，而不是由实际风险
决定；保留 shim 会"扩大触发表面，让旧阶段模型继续影响 v2 决策"。

本仓库有 27 个入口，包含 `cs-feat-design` / `-impl` / `-accept` / `-ff` 这类阶段拆分。

## 评估

上游诊断的核心问题是对的：**阶段化入口容易变成流程档位的代理指标**。用户选了
`cs-feat-design` 就必然产出 design 文档，哪怕这次改动根本不需要——这正是上游用
`执行流程 = 最小闭环 + 每个未排除风险所要求的最少保障` 要消除的东西。

但"入口数量"和"流程重量"是两个可以分开的变量：

- **上游的解法**：合并入口，让单个 skill 内部按风险决定强度。
- **本仓库 1.1.0 的解法**：保留入口，把风险模型（`assurance.md`）作为共享 reference 注入到
  所有执行技能，并明确写死"task kind 不是风险的替代指标"。

两者解决同一个问题。上游的解法更彻底，代价是必须整体重写；本仓库的解法保留了阶段入口带来的
可发现性和 harness 场景覆盖，代价是"入口名暗示流程重量"的引力仍然存在，只能靠 `assurance.md`
持续对冲。

直接收敛还有一项本仓库特有的成本：会一并删除 `codestable-maintainer`、行为回归 harness
（75 个 critical 场景）、18 个共享工具和 7 个测试套件——这些都挂在现有拓扑上。上游有
`experiments/` 承接类似职责，本仓库没有等价替代品。

## Decision

- 保留现有 27 个技能入口，不做 32 → 8 式收敛。
- 通过 `assurance.md` 在所有执行技能中统一"风险决定保障强度"，抵消阶段入口的档位暗示。
- 单个入口内部不得再按 task kind 自建流程档位。

## Consequences

- 入口拓扑与上游永久分歧，无法直接消费上游的 8-skill 包。
- `assurance.md` 成为关键对冲件：它一旦失效，阶段入口会退回档位模型。
- 技能正文体量继续高于上游（14K vs 9.5K 行），维护成本更高。

## Rejected alternatives

- **跟随上游收敛到 8 个入口**。拒绝：删除面覆盖 maintainer / harness / tools / tests，
  且这些没有替代品。属于 owner 级路线选择，不在一次吸纳里顺手做。
- **保留入口但不引入风险模型**。拒绝：那样只保留了上游诊断出的问题，没吸纳它的解法。
- **部分收敛（只合并 feature 四件套）**。暂缓：值得单独立项评估，但要先确认 harness 场景
  与 `{slug}-checklist.yaml` 生命周期怎么迁移。
