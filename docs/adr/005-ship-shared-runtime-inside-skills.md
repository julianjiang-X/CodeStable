---
adr: "005"
title: "共享参考和工具随技能分发，不再复制进项目"
status: Accepted
supersedes: ["001"]
date: 2026-11-10
applies-to:
  - "cs-onboard/reference/"
  - "cs-onboard/tools/"
  - "cs*/shared/"
  - "cs*/tools/"
  - "codestable-maintainer/tools/sync-shared.py"
enforcement: test
stage: [onboard, check, release]
lint: "python3 -m pytest tests/test_package_contract.py tests/test_codestable_doctor.py"
---

# ADR-005: 共享参考和工具随技能分发，不再复制进项目

## Context

ADR-001 决定保留"`cs-onboard` 把 reference 和 tools 释放到项目 `.codestable/`"的路线，并用
`MANIFEST.json` 加 doctor 的 `reference_drift` 检测版本分叉。它的判断是：分叉的根因是没有
版本标识，而不是有共享资产。

此后的实际使用显示，检测到分叉并不等于分叉被修复：

- 修复动作是"在每个已接入的项目里重新释放"。owner 有三十多个带 `.codestable/` 的工作目录，
  `UPGRADE.md` 自己把漏刷新称为"升级后最常见的故障"。
- 2026-11 的会话扫描里，释放到项目的 18 个工具脚本执行了 0 次；19 个参考文件有 12 个从未被读。
- 最活跃的项目的 `.codestable/` 里根本没有 `tools/` 和 `reference/`，技能里的门禁命令在那里
  无法执行，`.codestable/reference/*.md` 指针全部悬空。

ADR-001 保留机械 guard 的目的仍然成立。要改的是分发方式。

## Decision

- 共享参考和工具不再复制进项目。每个技能在自己的包内带副本：`shared/*.md` 与 `tools/*`。
- 源只有一份：`cs-onboard/reference/` 与 `cs-onboard/tools/`。
- `codestable-maintainer/tools/sync-shared.py` 按引用关系生成副本；测试保证副本与源逐字节一致，
  并拦住悬空引用。
- 执行类技能（`cs-feat`、`cs-issue`、`cs-refactor`、`cs-goal`）带齐共享约定里提到的全部工具；
  其他技能只带自己正文调用的工具。
- `cs-onboard` 不再释放 `reference/` 与 `tools/`。doctor 对项目里过期的旧副本报 P2，不阻塞；
  项目没有该目录是正常状态。
- 例外：git hook 回退和 main 发布脚本按项目路径调用，启用它们的项目自行复制三个文件，
  见 `cs-onboard/reference/branch-guard-hooks.md`。

## Consequences

- 升级技能包即全部更新，不存在"项目副本落后于技能正文"的状态。
- 机械 guard 在任何已接入的项目里都可执行，不取决于项目有没有被重新 onboard。
- 技能包体积变大（同一份参考和脚本在多个技能里各有一份）。副本是生成物，禁止手改。
- 这与上游最初的方案（工具从已安装的 skill 包运行）方向一致，与上游后来删除全部 runtime 的
  方案不同：本仓库保留工具。
- `MANIFEST.json`、`PACKAGE_VERSION` 与 `reference_drift` 保留，用于识别旧项目里的遗留副本。

## Rejected alternatives

- **维持 ADR-001**。拒绝：检测存在，但修复依赖逐项目的人工动作，实际没有发生。
- **删除全部工具（上游 v2）**。拒绝：理由同 ADR-001，机械 guard 是本仓库的核心差异。
- **技能运行时读取 `cs-onboard` 的目录**。拒绝：违反独立安装边界，安装方式不同路径也不同。

## Evidence and limits

扫描方法、数字和局限见 `docs/claude-models-iteration.md`。"工具执行 0 次"来自一位 owner 40 天
的 Codex 会话；工具随技能分发后是否会被实际调用，尚未验证。
