---
name: cs-explore
description: "定向解释代码或调查模块，需要归档时保存可追溯证据。"
---

# cs-explore

## 启动必读

遵循项目入口和 `.codestable/attention.md` 中的约束；已加载且未变化的上下文直接复用。按当前任务读取相关记录和引用，缺少可选骨架不阻塞工作。

同一个问题第一次花两小时查代码，第二次应该五分钟内找到答案——前提是第一次做完留下证据化的记录。cs-explore 把"提问 → 读代码 → 得结论"沉淀成可检索的探索文档。

---

## 适用场景

- 新人入仓快速理解模块边界 / 调用链 / 入口
- 用户提具体问题但暂时不要求直接产出方案 / 修复
- feature-design / issue-analyze / issue-fix 前先补一轮证据化探索
- 技术方向还在讨论，需要轻量 spike（只探索不拍板）

本技能负责证据化探索。定向问答直接给结论和必要证据；用户要求存档、module-overview 或 spike 报告时再创建探索文档。需要其他阶段时按已有授权继续相关技能，不让用户只为选技能停一轮。

> 需要归档时按需查 `.codestable/reference/shared-conventions.md`。产物写入 `.codestable/compound/`，命名 `YYYY-MM-DD-explore-{slug}.md`，frontmatter 带 `doc_type: explore`。

---

## 三种探索类型

frontmatter 的 `type` 字段：

| 类型 | 适用情境 |
|---|---|
| `question` | 围绕一个具体问题查代码并给结论 |
| `module-overview` | 快速梳理某模块结构 / 边界 / 入口 / 依赖 |
| `spike` | 对多个可能方向做轻量技术探查（不做最终决策） |

---

## 文档格式

frontmatter / 正文结构 / 各节写法说明和示例见同目录 `reference.md`。流程约束：

- **速答必须先于证据出现**——读者打开先看到结论再决定要不要往下看证据
- 结论必须可回溯到证据，不允许纯猜测
- 证据不足时 `confidence` 必须降为 `medium` 或 `low`
- 旧探索过期：旧文档标 `outdated`，新增当前版本

---

## 工作流阶段

### Phase 1：收敛探索问题

最多两个问题：

1. "你最想先回答的一个问题是什么？"
2. "希望聚焦哪个模块 / 目录？"

用户描述已清楚直接进 Phase 1.5。

### Phase 1.5：复用相关证据

用户提及旧记录或需要归档时按需查重；归档更新遵循 `shared-conventions.md` §6 第 5/6 条：

- 含"更新 / 复查 / 某次 explore / 这个模块之前探过"或指向某份旧 explore → 走**更新或 supersede**。explore 特性：**代码已变导致旧结论失效**时旧文档 `status: outdated` + 新建一份（supersede）；只补证据 / 收紧结论但核心结论未变时走"更新已有"
- 命中相关旧记录时判断适用范围与时效；以当前代码核验易变的关键结论后复用，不重复询问复用还是重探。

**更新路径**：读旧文档 → 按 Phase 2 补证据 → 改写速答节 → 写回原文件 + `updated: YYYY-MM-DD`。

### Phase 2：证据化探索

- 遵循项目的代码定位方式读取当前源码，不靠猜
- 边读边积累证据；**同步思考每条证据支撑哪个结论**——不支撑任何结论的证据不记录
- 保留足以支撑结论的关键证据并标注 `文件:行号`，不凑条数
- 调用关系更适合图示时使用 Mermaid；简单关系用文字即可
- 形成初步结论后主动检查：已有证据能否说服持怀疑态度的人？够了就停不必扩大搜索

为什么"够了就停"：探索不是穷举，是建立到"读者能信"为止的证据链。继续扩大只会让文档变长而不变可信。

### Phase 3：交付结果

- 先给结论，再给支撑证据、适用范围和未确认部分。
- 问答可在回复中交付；需要报告时按 `reference.md` 生成并直接归档，无需重复确认。
- 探索不替 owner 批准产品方向；需要决策时提供有证据的选项。

### Phase 4：归档（需要持久报告时）

- 新建：写入 `.codestable/compound/YYYY-MM-DD-explore-{slug}.md`，frontmatter 带 `doc_type: explore`
- 更新：写回 Phase 1.5 定位的原文件 + `updated: YYYY-MM-DD`
- supersede：按 `shared-conventions.md` §6 第 5 条；旧文档 `status: outdated` + `superseded-by`

新建条目 `evidence: observed` 起步，不在创建它的同一个任务里标 `validated`；晋级 / 退役 / 应用规则见 `.codestable/reference/evidence-lifecycle.md`。

### Phase 5：给出下一步建议

只在尚有实际后续工作时说明下一步；已授权的后续工作继续执行，不因探索结束而再次索取同一授权。

---

## 搜索工具

> 完整语法见 `.codestable/reference/tools.md`。

```bash
# 按类型筛选

python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=explore --filter type=module-overview --filter status=active

# 归档后查重叠

python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=explore --query "{关键词}" --json
```

---

## 退出条件

- [ ] 已明确探索问题与范围
- [ ] 速答节给出核心结论（结论前置）
- [ ] 关键证据标 file:line 并支撑结论
- [ ] 需要持久报告时已按文档格式归档到 `compound/`

---

## 守护规则

> 归档类共享规则见 `shared-conventions.md` 第 6 节。本技能特有反模式：

- 不读代码直接给结论
- 证据只写"看起来像"不写 file:line
- 结论写在证据之后——速答节必须在关键证据节之前
- 证据节比速答节长数倍——精简证据，不支撑结论的删掉
- 提前拍板——explore 只记"看到了什么"不下"以后应该怎么做"
- 直接给处方没证据链——每条结论必须回溯到 file:line
- 历史 explore 已过期却继续引用，不做 `status` 标注
- 把其他类型文档改写成 explore；读取相关设计和实现证据不受此限制
