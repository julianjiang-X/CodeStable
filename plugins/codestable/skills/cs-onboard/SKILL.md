---
name: cs-onboard
description: "接入或升级项目的 CodeStable 目录与项目记忆，保留既有规范。"
---

# cs-onboard

把仓库**接入 CodeStable 工作流体系**——白纸或已有零散文档的都行。本技能只做两件事：**搭骨架**、**归旧档**。骨架搭好后子工作流（feature / issue / compound 等）即可直接运行。

---

## 两条路径

| 路径 | 适用 | 产出 |
|---|---|---|
| **空仓库** | 仓库内无 spec 类文档，也没有 `.codestable/` | 完整骨架 + 必要骨架文件 |
| **迁移** | 仓库内有零散文档 / `docs/` / 部分 `.codestable/` 结构 | 审计报告 + 迁移映射方案（用户逐条确认）+ 落盘 |

启动后**先扫一次自动判断**，不要让用户选——TA 大概率不知道项目里现有哪些文档。扫描结果模糊（如只有 README）就明说判断依据并问用户。

---

## 标准骨架（目标状态）

> `{SKILL_DIR}` 指本技能目录。共享路径与命名约定的权威版本是 `{SKILL_DIR}/reference/shared-conventions.md`。下面只列 onboard 创建 / 检查的骨架文件。

```
.codestable/
├── attention.md                CodeStable 技能启动必读的项目注意事项
├── requirements/               需求聚合根（空目录 .gitkeep）
├── architecture/
│   └── ARCHITECTURE.md         架构总入口（首次创建为占位模板）
├── roadmap/                    规划层聚合根
├── goals/                      自主迭代目标的工作目录父目录（只放进行中的）
├── features/                   feature 工作目录的父目录（只放进行中的）
├── issues/                     issue 工作目录的父目录（只放进行中的）
├── refactors/                  refactor 工作目录的父目录（只放进行中的）
├── brainstorms/                brainstorming 记录（被 design 或 roadmap 消费后删除）
└── compound/                   沉淀类统一目录（learning / trick / decision / explore）
```

### 共享参考和工具不进项目

从 3.0.0 起，共享参考和工具脚本不再复制到项目里。每个技能在自己的目录下带着它用到的 `shared/*.md` 和 `tools/*`，升级技能包就全部更新，项目里没有需要刷新的副本。

- 本技能目录的 `reference/` 是共享参考的源，文件清单以 `reference/MANIFEST.json` 为准；`reference/` 里的文件互相用 `shared/<名字>.md` 引用，在本技能里对应 `reference/<名字>.md`。
- 本技能目录的 `tools/` 是完整工具集的源。
- 已有项目里旧的 `.codestable/reference/` 与 `.codestable/tools/` 不再被任何技能读取，也不再刷新。确认没有 git hook 或 CI 指向 `.codestable/tools/` 后可以删除；删不删由 owner 决定，onboard 不替用户删。
- 唯一仍会放进项目的是 git hook 回退和 main 发布用的三个文件（两个脚本加 `codestable_common.py`），仅在项目要启用它们时按 `reference/branch-guard-hooks.md` 的命令复制。agent hook 不需要项目副本，它会回退到已安装的本技能目录。

---

## 启动检查

**先检查一次现状**：

1. **检查 `.codestable/`**：不存在 → 空仓库候选；存在但不完整 → 迁移（部分补齐）
2. **旧 CodeStable兼容** CodeStable 经过多次改名，从 easysdd 到 codestable 再到 .codestable，如果遇到旧版的codestable目录，提示用户：

   > 检测到旧版codestable。建议直接 `git mv easysdd .codestable`，结构 / frontmatter 完全兼容，rename 后即用。要我执行吗？

   同意 → `git mv easysdd .codestable`，按迁移路径走（这时只需补齐可能缺失的 `attention.md`）。想保留旧目录 → 告诉他子技能只读 `.codestable/`，旧目录不会被读；按空仓库路径走新骨架

3. **Glob 全仓库 `.md`**（排除 `node_modules/` `.git/`）：根目录 `DESIGN.md` / `ARCHITECTURE.md` / `SPEC.md` / `README.md`；`docs/` `doc/` `design/` `spec/` `wiki/`；现有 `.codestable/` 下文件
4. **检查 `.codestable/attention.md`**：缺失则列为骨架待补齐项
5. **汇报扫描结论**：找到的相关文档（列路径）+ 走哪条路径 + 判断依据 + 不确定项

---

## 空仓库路径

**步骤 1：和用户确认范围**

- 项目名 / 简介（用于填 `ARCHITECTURE.md` 占位）
- attention.md 只建最小骨架；用户已经给出的项目硬约束才写入，不凭空代填

**步骤 2：创建目录骨架**

按下面顺序执行，**不等用户逐步确认**——骨架是整体一次性的：

- `.codestable/{requirements,roadmap,goals,features,issues,refactors,compound,brainstorms}/.gitkeep`
- `.codestable/attention.md`（最小骨架模板见同目录 `reference.md`）
- `.codestable/architecture/ARCHITECTURE.md`（占位模板见同目录 `reference.md`）

**步骤 3：attention.md 提醒**

attention.md 已创建但默认只有空骨架。汇报时提醒用户：有编译前置、测试命令、目录禁区、凭证规则、报告语言偏好这类"每次 CodeStable 技能启动都必须知道"的信息，后续用 `cs-keep note` 一条条追加。

**步骤 4：验收汇报**

列建了哪些文件：

> CodeStable 骨架已就绪。现在可以：达成目标 `cs-goal` / 开始新功能 `cs-feat` / 报告问题 `cs-issue` / 沉淀知识 `cs-keep learn`

---

## 迁移路径

**步骤 1：生成审计报告**

| 现有文件 | 推测内容类型 | 建议归入 CodeStable | 置信度 |
|---|---|---|---|
| `docs/DESIGN.md` | 项目架构 | `.codestable/architecture/ARCHITECTURE.md` | 高 |
| `docs/feature-auth.md` | 已落地功能的设计稿 | 能力描述归入 `.codestable/requirements/auth.md`，结构部分归入 `architecture/`；其余保留原位 | 中 |
| `SPEC.md` | 功能需求？ | 需用户确认 | 低 |

**置信度**：高 = 语义明确匹配；中 = 可推断有歧义；低 = 不明确或映射多个位置都合理。

`features/`、`issues/`、`refactors/`、`goals/` 只放进行中的工作目录。已经结束的功能设计稿、问题记录不必迁进去（迁进去就成了默认检索范围之外的旧目录）：有长期价值的内容归入 `requirements/` / `architecture/` / `compound/`，其余保留原位。

**步骤 2：逐条对齐**

中 / 低置信度的用 `AskUserQuestion` 问：

- 中：给推断理由，问"按这个方式归位？"
- 低：描述文件内容，给 2-3 个候选位置 + "跳过"

高置信度不逐条问但要在汇报里列，给用户复审机会——逐条问会让节奏失控。

**步骤 3：处理已部分存在的 .codestable/**

- 命名不符规范（`YYYY-MM-DD-{slug}` 格式）但有内容 → 提示用户问是否重命名
- 空占位（`.gitkeep` / 空 `.md`）→ 直接补齐不问

**步骤 4：补齐缺失骨架**

对照标准骨架补齐**用户确认后仍缺失**的目录 / 文件。已有内容不覆盖。

项目里已有旧的 `.codestable/reference/` 或 `.codestable/tools/` 时不刷新、不覆盖，在汇报里说明它们已不再被读取，按上面"共享参考和工具不进项目"一节处理。

**步骤 5：处理不迁移的文件**

用户选"跳过"的文件：**不移动 / 不删除 / 不重命名**，汇报标"保留原位（未纳入 CodeStable）"。**绝不允许未经确认就动**——onboard 只允许 AI 整理不允许替用户做删除决定。

**步骤 6：attention.md 提醒**（同空仓库路径步骤 3）

**步骤 7：验收汇报**

列：迁移文件清单（from → to）、新建骨架、未迁移文件（保留原位）、下一步建议。

---

## 骨架文件模板

`ARCHITECTURE.md` 占位模板和 `attention.md` 最小模板见同目录 `reference.md`。

---

## 退出条件

- [ ] `.codestable/` 九个子目录都存在
- [ ] `.codestable/attention.md` 已建
- [ ] `.codestable/architecture/ARCHITECTURE.md` 已建
- [ ] 迁移路径：每条映射都有明确处理结果（迁移 / 保留原位）
- [ ] 迁移路径：没有未经确认就移动的文件
- [ ] 验收汇报已给出

---

## 容易踩的坑

- **未经确认就移动 / 删除已有文件**——迁移核心原则是用户拍板
- **替用户填 attention.md 实质内容**——必须项目 owner 来定，AI 只提供模板
- **重新引入 `AGENTS.md` / `CLAUDE.md` 兼容路径**——CodeStable 的启动注意事项入口固定为 `.codestable/attention.md`
- **建完骨架立刻开始 feature/issue**——onboard 是"搭环境"不是"开始干活"
- **低置信度直接执行**——低 = 必须问
- **把 `reference/` 或 `tools/` 复制进项目**——3.0.0 起它们随技能分发，项目副本只会过期
- **替用户删除旧的 `.codestable/reference/` / `.codestable/tools/`**——可能有 hook 或 CI 指向它们，由 owner 决定
- **Glob 时忘记排除 `node_modules/` `.git/`**——会让扫描结果充斥噪声
- **让 AI 在主协调检出里 `git switch/checkout`**——需要执行分支时用 git worktree；可用 `branch-guard-hooks.md` 配 command hook 硬拦

---

## 相关文档

- `reference/system-overview.md` — CodeStable 体系总览
- `reference/shared-conventions.md` — 目录结构、共享口径、工作目录与收尾、回答进度（第 8 节）的权威版本
- `reference/execution-conventions.md` — worktree / review / finish / commit 执行约定
- `reference/approval-conventions.md` — owner 审批报告和 `approval-report.md` 约定
- `reference/goal-conventions.md` — goal 状态模型、报告和 owner-stop 约定
- `reference/interaction-modes.md` — `interview me` / `grill me` 的全局对话模式约定
- `reference/assurance.md` — 风险驱动的保障强度选择（地板之上加多少）
- `reference/economy.md` — 实现经济性：最少新增复杂度、有界简化
- `reference/code-design.md` — 模块深度、归属命名、接缝真实性、穿刺协议
- `reference/evidence-lifecycle.md` — 归档文档 `evidence` 三态与晋级规则
- `{SKILL_DIR}/tools/codestable-freshness-check.py` — 检查 installed CodeStable skill copy 是否落后于远端 `main`
- `reference/branch-guard-hooks.md` — 禁止 AI 切主检出分支 / 在 main 或 master 上实现的 hook 配置
- `.codestable/attention.md` — CodeStable 技能启动必读的项目注意事项
- `.codestable/architecture/ARCHITECTURE.md` — 架构总入口骨架
