---
adr: "006"
title: "工作目录是工作状态，收尾时毕业并删除；进度现看，不存页面"
status: Accepted
date: 2026-11-10
applies-to:
  - "cs-onboard/reference/shared-conventions.md"
  - "cs-feat/"
  - "cs-issue/"
  - "cs-refactor/"
  - "cs-goal/"
  - "cs-audit/"
  - "cs-onboard/tools/"
enforcement: test
stage: [design, impl, accept, release]
lint: "python3 -m pytest tests/test_codestable_closed_units.py tests/test_package_contract.py"
---

# ADR-006: 工作目录是工作状态，收尾时毕业并删除；进度现看，不存页面

## Context

2026-11 对 owner 近 40 天会话的扫描（见 `docs/claude-models-iteration.md`）加上 owner 的确认，得到：

- 任务做完之后，设计文档、清单、审查记录、验收报告没有人再打开，只有 agent 读。档案帮上忙的几次都发生在任务进行中
  （压缩上下文后续上同一任务、审查对照契约）。没有一次是后来的任务去读旧功能的设计。
- `.codestable/` 膨胀很快：一个项目 25 天长到 307 个文件约 2 MB，另一个 474 个文件约 3 MB。旧档案是检索噪声，
  和事实漂移后还要专门修；上下文越大每一轮的缓存读取越贵。
- owner 问得最多的是「进度如何 / 还差什么 / 下一步是什么 / 现在呢」。原因是进度状态散在几十个单元里，没有一处能快速回答。
- owner 在多个 git worktree 里并行跑多个 agent，默认分支受保护、只能经合并变更。
- 被别的 agent 派工、无人值守的会话，因为派工说明里一句「照 CodeStable 流程」，各自产出了完整的设计 + 清单 + 验收文件，没人读。
- 有的项目规定 CodeStable 文字写完整英文块加完整中文块。owner 同意只给 agent 读的文件不需要双语。

## Decision

1. **工作目录是工作状态，不是档案，默认不建。** `features|issues|refactors|goals/YYYY-MM-DD-{slug}/` 只在
   (1) 任务会跨会话或要交接，(2) 有待 owner 决定或批准的契约，(3) 按 `assurance.md` 需要正式独立审查，
   (4) owner 要求留痕 之一成立时创建。其余任务的证据是 diff、测试输出和交付说明。被别的 agent 派工时同样适用。
   目录位置和命名不变，工具照常能找到它们。
2. **收尾顺序固定：毕业、结案提交、finish gate、单独删除。** 毕业清单里每项有去处（requirements / architecture /
   `cs-keep decide` / `cs-keep learn` / `attention.md` / 测试或检查器）或写明「不需保留」；结案提交含
   代码、毕业写入的文档和目录里还剩的全部内容（review 证据在内），提交信息写清做了什么、取舍、验收证据、没验证的部分，
   是这次任务的长期记录；适用 worktree finish gate 时在此时（工作树干净）跑并提交产物；最后工作目录在**单独一个提交**里
   删除，该提交只能含该单元的删除和非实现的 `.codestable/**` 改动。工具强制：删除一个在 HEAD 里需要 review 的单元，
   HEAD 里必须已有 `reviewer: subagent` 的证据；带代码的删除提交被拒；`state.yaml` 不是终态的 goal 目录不能删。
   任务阻塞未完成、有未决
   approval report、owner 要求保留、审计里还有未解决的 finding 时不删。`cs-goal` 终态、`cs-audit` 同规则；
   `compound/` 是知识，不受影响；`brainstorms/` 被 design 或 roadmap 消费后删除。
3. **进度不存页面，被问时现看。** 3.0.0 起工作目录在收尾时删除，所以「进行中」就是本检出和各 linked
   worktree 里在做的工作目录，加上没有目录但领先默认分支或有改动的 worktree；已有完成标记且自分支从默认分支分叉以来被改动过的是「收尾中」，照样列出，因为完成标记先于 review、毕业和删除；没被改动过的已完成或已取消单元是早期留下的记录（不迁移、不删除），只在 `notes` 里计数；「等待」是未决 approval report、已完成未合并的 worktree、打开的 PR；「最近完成」是
   默认分支最近的提交，结案提交信息就是记录；「下一步」取 roadmap 条目，没有就取进行中单元的下一步，都没有就说没有记录。
   回答给 owner 在对话里，每行带可核对的指针并说明没查的部分，不写进文件。规则见 `shared-conventions.md` 第 8 节，
   `codestable-status.py` 一次取齐（只读，默认不联网）。
4. **语言：** 只给 agent 读的文件用一种语言，由 `attention.md` 指定。`bilingual-report-policy` 检查收窄到写给 owner 的
   `approval-report.md`。
5. **检索：** 开工默认只读 `attention.md`、`requirements/`、`architecture/`、`compound/` 和相关的进行中
   工作目录；3.0.0 之前留下的已结束单元不在默认范围。
6. **旧项目不迁移、不批量删除。** 本决定只定义新任务的行为。

## Consequences

- `.codestable/` 的体积随在途工作而不是随历史增长；git 历史里仍可找回已删除的目录。
- 工具必须能处理「删除整个已完成单元的提交」：commit gate 识别已收尾单元，并按 HEAD 里的内容判断是否需要 review
  （删除不能绕过 review 门禁）；doctor 不再把已收尾单元的 baseline 当阻塞；worktree inbox 允许 finish 报告之后出现
  删除和非实现的 `.codestable/**` 改动，源码改动仍使报告失效。`start` 与 finish gate 对已收尾单元明确报错。
- 提交信息承担了过去验收报告的长期记录职责，写得草率就没有别处可查。
- 只写一种语言后，人类读者想看英文或中文版本时需要在 `attention.md` 点名。
- 破坏性较小：旧项目里的旧单元不动，只是默认不再被检索。

## Rejected alternatives

- **保留所有单元，只改检索范围。** 拒绝：体积与漂移问题仍在，且仍要为没人读的文件付写入成本。
- **收尾时移到 `archive/` 目录。** 拒绝：换个位置仍是检索噪声，git 历史已经是归档。
- **把进度写进 roadmap。** 拒绝：roadmap 只覆盖大需求，不覆盖 issue、重构和在途分支，也不回答「卡在谁那里」。
- **存一份 `.codestable/status.md` 进度页。** 曾列入 3.0.0 方案（未发布），后拒绝：(1) 多个 worktree 并行时每个分支都改同一页，
  必然冲突；(2) 默认分支受保护，页面只能经合并变更，永远滞后于实际；(3) 四节里三节能从现场推出（进行中 = 在做和收尾中的
  工作目录与有改动的分支；等待 = 未决审批、未合并 worktree、打开的 PR；最近完成 = 默认分支历史，结案提交信息就是记录）；
  (4) 过期的「等你决定」比没有更伤信任，而 owner 的项目里进度文档已漂移过。改为按需现看。

## Evidence and limits

证据与数字见 `docs/claude-models-iteration.md`，只覆盖一位 owner 的 40 天，分类来自模型评判。删除工作目录后的效果
（提交信息是否真的够用、现看的进度回答是否足够快、进度类提问是否减少）尚未验证；`codestable-status.py` 有测试覆盖
其汇总逻辑，但它不判断某个单元「实际卡在哪」，那部分仍靠 agent 读单元文件。
