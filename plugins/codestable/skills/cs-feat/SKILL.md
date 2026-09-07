---
name: cs-feat
description: "选择并继续新功能的设计、快速实现、实现或验收阶段。"
---

# cs-feat

## 启动必读

遵循项目入口和 `.codestable/attention.md` 中的约束；已加载且未变化的上下文直接复用。按当前任务读取相关记录和引用，缺少可选骨架不阻塞工作。

功能流程保留需求、设计和验收的可追溯关系；按任务风险选择必要阶段。明确的小需求可用 fastforward，已有充分设计不重新展开。

```
(想法模糊先去 cs-brainstorm 分诊) → 方案设计（名词层 + 编排层 + 验收契约 + 推进策略切片）→ 分步实现 → 验收闭环
```

brainstorm 是讨论层独立入口，会分诊：case 1（清楚 → 直接 design）/ case 2（小需求继续讨论 → 落 brainstorm note）/ case 3（大需求 → 移交 `cs-roadmap`）。只有 case 2 在 feature 目录产出 brainstorm note。

本技能确定当前 feature 的阶段，然后在同一任务中继续对应子技能。用户只询问路由时再只解释选择。

---

## 文件放哪儿

```
.codestable/features/{feature}/
├── {slug}-brainstorm.md       ← 阶段 0 产物（仅 case 2 落盘）
├── {slug}-intent.md           ← 阶段 1 可选前置草稿（用户自己写半成品）
├── {slug}-design.md           ← 阶段 1 方案文件
├── {slug}-checklist.yaml      ← 阶段 1 生成 steps + checks，2/3 阶段更新 status
├── grill/                     ← 可选，accepted grill-context，供 human review
└── {slug}-acceptance.md       ← 阶段 3 验收报告
```

目录命名 `YYYY-MM-DD-{英文 slug}`，日期取首次创建当天定了不动；slug 小写字母 / 数字 / 连字符。

为什么聚一起：以后查"那个导出 CSV 功能当时怎么决定的"，brainstorm / design / acceptance 都在一处。feature 和 issue 分别放在 `.codestable/features/` 和 `.codestable/issues/` 因为归档逻辑不一样。

如果目录里有 `grill/*.md`，只把 `doc_type: grill-context` 且 `status: accepted`
的文件当 human review context 读；它必须 `source_of_truth: false`，不能覆盖
design / checklist / acceptance 或 requirement。

实现时发现无关 bug，单独报告或按授权记录 issue；完成已授权功能必需的修复可纳入方案并保留依据，不顺手扩大范围。

---

## 四个阶段

| 阶段 | 子技能 | 产出 | 谁主导 |
|---|---|---|---|
| 0 brainstorm（可选，独立入口） | `cs-brainstorm` | case 2 时产出 brainstorm note | AI 思考伙伴，用户拍板 |
| 1 方案设计 | `cs-feat-design` | design.md + checklist.yaml | AI 起草，未决产品选择由 owner 裁决 |
| 2 分步实现 | `cs-feat-impl` | 代码 + 阶段汇报 | AI 按方案执行 |
| 3 验收闭环 | `cs-feat-accept` | acceptance.md | AI 核对证据，按需人工验收 |

阶段边界用于核对契约与证据，不重复索取已有授权。正式 design / checklist 状态必须如实更新；未决产品方向、契约变化或明确要求的人工验收仍交 owner 决定，不能将尚未批准的提案标为 approved。

阶段 0 可选且是 feature 流程的**外部入口**——`cs-brainstorm` 同时服务 feature 和 roadmap。case 3（大需求）讨论被移交给 `cs-roadmap` 不再回 feature 流程；roadmap 拆出子 feature 后从 `cs-feat-design` 的"从 roadmap 条目起头"入口进来。

### Fastforward 模式

需求明确且风险有限时，使用 `cs-feat-ff` 保留精简 design 与验收记录后继续实现。用户说“快速模式”“fastforward”“直接开干”“别那么多步骤”也是此入口；已授权且无未决选择时不再要求阶段确认。

公共契约未定、实质术语冲突或跨子系统风险需要展开时，采用标准 design；步骤数量本身不决定流程重量。

---

## 路由：用户现在该走哪个子技能

优先检查用户指定或任务相关的 feature 记录，只读取判断阶段所需内容。已有证据足够时不遍历所有 feature，也不通读无关产物。

| 当前状态 | 触发哪个子技能 |
|---|---|
| 用户给出起点 + 终点 / 验收结果，并希望 AI 自主实现、自我迭代或每轮报告 | `cs-goal` |
| 想法模糊，说不清真问题 / 边界 / 不做什么 | `cs-brainstorm` |
| 想法清晰（知道做什么 / 为谁 / 怎么算成功） | `cs-feat-design` |
| 用户说"开一个新需求 / 起草稿 / 新建 feature"想自己写半成品 | `cs-feat-design` 的"初始化模式"（建目录 + 空 intent，让用户填完再回） |
| 用户主动说"先 brainstorm 一下"、"有个想法没想清楚" | `cs-brainstorm` |
| `{slug}-intent.md` 已填好 | `cs-feat-design`（读 intent 作输入） |
| 用户说"快速模式 / fastforward" | `cs-feat-ff` |
| `{slug}-brainstorm.md` 已存在，要进设计 | `cs-feat-design` |
| `{slug}-design.md` 已 approved、代码没动 | `cs-feat-impl` |
| fastforward design 已确认 | `cs-feat-impl` |
| 代码已写完要验收 | `cs-feat-accept` |
| 用户说"我想要一个 X 系统"大需求 | 转 `cs-brainstorm` 分诊（大概率 case 3 → `cs-roadmap`） |
| roadmap 里某条子 feature 该启动 | `cs-feat-design` 的"从 roadmap 条目起头"入口 |
| 不确定 design 是否完整 | 定向核对相关契约与状态后继续；实质缺口才询问 |

### 怎么判断该不该走阶段 0

仅当要解决的问题、关键行为或实质范围边界不清时才需要 brainstorm；不要求用户为了满足模板而补一条“不做什么”。

用户明确要求直接设计时直接进入；常规流程选择自主完成，不额外询问技能偏好。

### brainstorm vs intent

两者都是 design 前置，区别在**谁在主导收敛**：

- brainstorm：用户脑子里模糊，AI 问用户答。判 case 3 时移交 `cs-roadmap` 不回 feature；只有 case 2 产出 brainstorm note
- intent：用户自己想好大致做法（100 字描述 + 相关数据结构），懒得口述就写成 `{slug}-intent.md` 给 AI 读

用户要求自己写草稿时创建 intent；否则根据已知需求继续，仅询问影响功能边界的缺失信息。

---

## 与 issue 工作流的边界

- feature：从来没有的东西要加进来（新功能 / 新能力）
- issue：本来应该好的东西坏了（bug / 异常 / 文档错误）
- goal：用户定义起点和验收终点，让 AI 自主迭代直到完成或阻塞；goal 可包住 feature / issue / refactor，但状态归 `.codestable/goals/`

灰色地带：区分功能必需的修复与无关 bug，前者保留依据，后者不擅自扩入当前工作。

---

## 相关文档

- `.codestable/reference/system-overview.md` — CodeStable 体系总览
- `.codestable/reference/shared-conventions.md` — 跨阶段共享口径、目录结构、checklist 生命周期
- `.codestable/reference/assurance.md` — 这次要做多重：风险驱动的保障强度选择
- `.codestable/attention.md` — CodeStable 启动注意事项和项目硬约束
- 项目架构总入口 — 方案设计阶段需要查
