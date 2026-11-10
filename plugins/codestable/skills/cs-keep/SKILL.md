---
name: cs-keep
description: "维护项目的长期知识：常驻提示、踩坑经验与复盘、技巧、已接受的决定、需求记录，以及架构记录的更新与漂移核验。仅用于已接入 CodeStable 的仓库，或用户点名时。"
---

# cs-keep

> `{SKILL_DIR}` 指本技能目录（本文件所在目录）。正文里的相对路径（`stages/`、`references/`、`reference/`、`shared/`、`tools/`）都相对于它；本技能没有的子目录就是用不到。

把值得留下的东西放到下次能被读到的地方。本技能判断内容属于哪一类，然后在同一任务中读取对应的阶段文件并照做；用户只问"该放哪"时只解释选择。

## 启动必读

遵循项目入口和 `.codestable/attention.md` 中的约束；已加载且未变化的上下文直接复用。只读取本次要写入的那一类所需的记录。

## 六类内容

| 内容 | 模式 | 阶段文件 | 归宿 |
|---|---|---|---|
| 简短、长期生效、多数任务都要知道的命令或约束；owner 说出的跨任务范围 / 授权规矩 | `note` | `stages/note.md` | `.codestable/attention.md` |
| 已验证的踩坑经验：坑因和修法 | `learn` | `stages/learn.md` | `.codestable/compound/`（`doc_type: learning`） |
| 可复用的编程方法、库用法 | `trick` | `stages/trick.md` | `.codestable/compound/`（`doc_type: trick`） |
| 已接受的技术选型、架构决定、长期约束 | `decide` | `stages/decide.md` | `.codestable/compound/`（`doc_type: decision`） |
| 能力边界、用户故事、验收意图 | `req` | `stages/req.md` | `.codestable/requirements/` |
| 模块职责、边界、实现漂移 | `arch` | `stages/arch.md` | `.codestable/architecture/` |

进入某一类时读取 `{SKILL_DIR}/stages/<模式>.md`。其他技能或文档里写的 `cs-keep note`、`cs-keep learn`、`cs-keep req backfill`、`cs-keep arch check` 等，指的就是对应模式及其子模式。

## 怎么选

- 根据内容自主选择模式，不为分类本身询问 owner。
- 一条内容只放一处。详细背景放 `learn` / `decide`，`attention.md` 里只留一两行并链接过去。
- `learn` / `trick` / `decide` 要有可追溯的证据；尚未拍板的方案不进 `decide` 或 `req`。
- 用户已经要求记住的直接写，不再确认；自己发现的候选只在有持续价值时简短建议，用户拒绝后不重复。
- 临时任务状态、本周计划、git 已完整表达的事实不沉淀。

## 相关文档

- `shared/shared-conventions.md` — 目录结构、frontmatter 口径、检索范围
- `shared/evidence-lifecycle.md` — 归档文档 `evidence` 三态与晋级规则
