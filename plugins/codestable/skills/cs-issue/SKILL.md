---
name: cs-issue
description: "选择并继续缺陷报告、根因分析或修复阶段，复用相关现有记录。"
---

# cs-issue

## 启动必读

遵循项目入口和 `.codestable/attention.md` 中的约束；已加载且未变化的上下文直接复用。按当前任务读取相关记录和引用，缺少可选骨架不阻塞工作。

issue 工作流保留可复现问题、根因、修复和验证证据。按复杂度选择标准或快速路径，避免为已明确的小问题重复建立上下文：

```
发现问题 → 清晰记录（report）→ 根因分析（analyze）→ 定点修复 + 验证（fix）
```

本技能判断当前阶段并在同一任务中继续对应子技能；用户只询问路由时再只解释选择。

---

## 文件放哪儿

```
.codestable/issues/{YYYY-MM-DD}-{slug}/
├── {slug}-report.md           ← 阶段 1 问题报告
├── {slug}-analysis.md         ← 阶段 2 根因分析
├── grill/                     ← 可选，accepted grill-context，供 human review
└── {slug}-fix-note.md         ← 阶段 3 修复记录（必出产物）
```

日期取**发现 / 提报问题当天**定了不动。slug 能一眼看出是什么问题（`auth-token-leak`、`null-pointer-on-empty-list`）。

`{slug}-fix-note.md` 是阶段 3 **必出产物**——无论修复简单还是复杂都要写。它不是仪式，是回溯凭证：没有它下次类似问题来你只能从 git log 反推。

所有 issue 文档带 YAML frontmatter（`doc_type` 分别为 `issue-report` / `issue-analysis` / `issue-fix`）便于 `search-yaml.py` 按 severity / tags / status 检索。

如果目录里有 `grill/*.md`，只把 `doc_type: grill-context` 且 `status: accepted`
的文件当 human review context 读；它必须 `source_of_truth: false`，不能覆盖
report / analysis / fix-note 或代码证据。

---

## 两条路径

### 标准路径（问题复杂或根因不明）

| 阶段 | 子技能 | 主导 | 产出 |
|---|---|---|---|
| 1 问题报告 | `cs-issue-report` | 用户描述，AI 引导 | `{slug}-report.md` |
| 2 根因分析 | `cs-issue-analyze` | AI 依据证据判断根因 | `{slug}-analysis.md` |
| 3 修复验证 | `cs-issue-fix` | AI 定点修复并验证 | 代码 + `{slug}-fix-note.md`；按授权提交 |

已授权修复可连续推进各阶段，不重复询问开工或完成确认。根因由证据判断；真正未决的产品契约或范围变化需要 owner 决定，用户仅要求分析时不修改实现。

### 快速通道（问题简单、根因一眼确定）

下面**同时满足**才进：

1. AI 读完代码后对根因高度有把握（能明确指出 file:line + 原因）
2. 修复范围明确且风险有限
3. 无跨模块影响风险

流程压缩成：读取相关证据 → 说明根因与修复方案 → 在授权范围内修复并验证 → 写 `{slug}-fix-note.md`。只有实质未决选择或用户指定的人工验收才停下询问。只产出一份 `fix-note.md`，省掉 report 和 analysis。

**判定口径**：由 `cs-issue-report` 的启动检查选择路径，已有明确判断则复用。新证据改变风险时可调整路径并同步正式 unit 状态，不为每个阶段重新分诊。

根因仍不清楚、跨模块风险尚未界定或用户要求完整分析存档时使用标准路径；需要复现本身不是重流程的理由。

---

## 路由

优先定位用户指定或问题相关的 issue，核对判断阶段所需的状态与证据；无需遍历全部 issue 或通读无关文件。

| 当前状态 | 触发哪个子技能 |
|---|---|
| 刚发现问题，没有任何文件 | `cs-issue-report`（那里判断走标准还是快速） |
| `report.md` 已存在，没 `analysis.md` | `cs-issue-analyze` |
| `analysis.md` 已存在，代码还没改 | `cs-issue-fix` |
| 代码已改，还没修复验证记录 | `cs-issue-fix`（走验证） |
| 不确定 | 自己读已有文件按上表对号 |

用户描述的是新功能需求时，在已有授权范围内继续 `cs-feat`。

---

## 与 feature 工作流的边界

- issue：本来应该好的东西坏了——已有代码里的 bug / 异常行为 / 文档错误 / 性能问题
- feature：从来没有的东西要加进来——新功能 / 新能力

灰色地带：真正修复需要新增产品能力时，记录已证实根因和具体契约缺口，请 owner 决定未授权的能力变化；必要实现细节在已有授权范围内自主处理，不为了流程补齐无关产物。

---

## 相关文档

- `.codestable/reference/system-overview.md` — CodeStable 体系总览
- `.codestable/reference/shared-conventions.md` — 跨阶段共享口径
- `.codestable/reference/assurance.md` — 这次要做多重：风险驱动的保障强度选择
- `.codestable/attention.md` — CodeStable 启动注意事项和项目硬约束
- `.codestable/architecture/ARCHITECTURE.md` — 根因分析时可能要查
