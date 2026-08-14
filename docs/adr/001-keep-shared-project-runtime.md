---
adr: "001"
title: "保留共享项目 runtime，并为它补上漂移检测"
status: Accepted
date: 2026-08-14
applies-to:
  - "cs-onboard/tools/"
  - "cs-onboard/reference/"
  - ".codestable/tools/"
  - ".codestable/reference/"
enforcement: test
stage: [onboard, check, release]
lint: "python3 -m pytest tests/test_package_contract.py tests/test_codestable_doctor.py"
---

# ADR-001: 保留共享项目 runtime，并为它补上漂移检测

## Context

上游 `codestable/CodeStable` 在 v2 删除了全部项目 runtime 分发。这个决定有完整的推理链：
ADR-001（工具从已安装 skill 包运行）被 ADR-004 取代，ADR-004 又被 ADR-005 取代，方向一路收敛。

上游 ADR-004 给出的理由是两条：

1. **版本分叉**——"升级时，项目副本、已安装 runtime 与 skill 文本可能处于不同版本"；
2. **无关状态**——"简单任务也要恢复并维护与实际工作无关的状态"。

它明确拒绝了本 ADR 采取的方案：*"恢复 cs-onboard 的共享 runtime。拒绝：重新制造版本分叉，
并违反独立安装边界。"*

本仓库走的是相反路线：`cs-onboard` 把 18 个 Python 工具和一组共享 reference 释放到项目的
`.codestable/`，用机械 guard（doctor / worktree gate / branch guard / review packet）约束 agent
行为，而不是靠技能正文的文字纪律。

## 评估

**上游的理由 1 在本仓库成立，而且此前无人检测。**

核查结果：

- `codestable-freshness-check.py` 比对的是**已安装 skill copy 与远端 main**，不看项目里的
  `.codestable/reference/` 副本；
- `codestable-doctor.py` 此前完全没有 reference / 版本 / 漂移相关检查；
- 全仓库没有 `runtime-manifest.json` 或任何等价机制。

也就是说：项目副本可以静默过期，子技能按过时口径工作，而"有 freshness check"会给人一种
已经覆盖了的错觉。1.1.0 新增四份共享 reference 后这个缺口会立刻发作——老项目的技能会指向
不存在的 `.codestable/reference/economy.md`。

**上游的理由 2 在本仓库不成立。** 本仓库的工具是按需调用的检查器，不是每个任务都要恢复的
状态机；简单任务不触发 doctor 以外的任何工具。

**结论**：上游诊断对了病（版本分叉真实存在），但它开的药（删掉整个 runtime）不是唯一处方。
版本分叉的根因是**没有版本标识**，不是**有共享资产**。

## Decision

- 保留 `cs-onboard` 的共享 runtime 分发路线，不吸纳上游 ADR-004 / ADR-005 的删除决定。
- 为共享 reference 增加版本标识：`cs-onboard/reference/MANIFEST.json` 记录 `version` 与文件清单，
  随 reference 一起释放。
- `codestable_common.PACKAGE_VERSION` 与仓库 `VERSION` 保持一致，由测试守住。
- `codestable-doctor.py` 报告 `reference_drift`：版本不一致或清单文件缺失为 P1（阻断），
  无 manifest 的老副本为 P2（提示）。
- 保留 `codestable-freshness-check.py` 的既有职责不变。两者是**不同轴**：freshness 看
  "installed skill copy 相对远端是否落后"，doctor 看"项目副本相对本地 tools 是否一致完整"。

## Consequences

- 版本分叉从"静默失效"变成"P1 阻断 + 可执行修复指引"。
- 每次改 `cs-onboard/reference/` 都必须同步 `MANIFEST.json` 和 `VERSION`，由
  `tests/test_package_contract.py` 强制。
- 仍然保留上游指出的固有成本：升级后必须逐仓库刷新副本。本 ADR 只保证这个成本**可见**，
  不消除它。
- 与上游的分歧被永久固化：本仓库不再能低成本地跟进上游 v2 的 skill 独立安装边界。

## Rejected alternatives

- **跟随上游删除项目 runtime**。拒绝：会同时删掉 doctor、worktree gate、branch guard、
  review packet 与 7 个测试套件所依赖的整个机械 guard 层，而本仓库的产品判断是机械 guard
  比文字纪律可靠（见 [ADR-002](002-keep-worktree-ownership.md)）。
- **只加文档提醒用户刷新**。拒绝：这正是失效前的状态。能被一个命令验证的约束不应该只写成文档
  （同 `cs-decide` 的 `enforcement` 规则）。
- **让 doctor 直接 diff 技能包源目录**。拒绝：doctor 以 `.codestable/tools/` 副本形式运行，
  运行时拿不到技能包路径。manifest 是唯一可离线判定的方案。
