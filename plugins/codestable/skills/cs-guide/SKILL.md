---
name: cs-guide
description: "编写或更新开发者、用户与 API 指南，保持与行为及已批准契约一致。"
---

# cs-guide

## 启动必读

遵循项目入口和 `.codestable/attention.md` 中的约束；已加载且未变化的上下文直接复用。按当前任务读取相关记录和引用，缺少可选骨架不阻塞工作。

代码解决问题，文档让别人能用它解决问题。spec 记录"做了什么、为什么这么做"，但下游开发者和终端用户不需要、也不应该读 spec——他们需要面向自己角色的、可发布文档。

---

## 三种模式

| 模式 | 目标读者 | 典型内容 | 输出路径 |
|---|---|---|---|
| `dev-guide` | 贡献者、集成方、下游开发者 | 本地 setup、架构解说、API 说明、扩展方式 | `docs/dev/{slug}.md` |
| `user-guide` | 终端用户 | 功能概述、操作步骤、概念解释、常见问题 | `docs/user/{slug}.md` |
| `api-reference` | 集成方、库用户、下游开发者 | 公开 API、组件、函数、命令逐条目参考 | `docs/api/{slug}.md` + 可选 `docs/api/manifest.yaml` |

**模式选择从读者任务出发**：要完成一个场景用 guide；要查一个公开表面用 api-reference。API reference 是本技能的模式，不是新的 CodeStable 实体。

> `docs/dev/`、`docs/user/`、`docs/api/` 是默认约定，项目已有自己的 docs 结构就以项目为准。

---

## 触发时机

| 情境 | 说明 |
|---|---|
| feature-acceptance 结束 | 主动推：用户可见变更问 user-guide；开发者使用方式变更问 dev-guide；公开 API / 组件 / 命令变更问 api-reference |
| 用户主动触发 | "写文档"、"开发者指南"、"用户指南"、"API 文档"、"组件文档" |
| onboard 完成后 | 新仓库可触发补全基础文档骨架 |

主动推送一句话即可，用户说"不用"就别再提——多次推会让用户觉得 AI 在加戏。

---

## 涉及路径

对外文档产物**不在 `.codestable/` 下**——它是面向外部读者的可发布产物，和 spec 工件分开。

- dev-guide → `docs/dev/{slug}.md`
- user-guide → `docs/user/{slug}.md`
- api-reference → `docs/api/{slug}.md`
- api-reference manifest（可选）→ `docs/api/manifest.yaml`

文件命名 `{slug}.md`（英文小写连字符，**无日期前缀**）——文档持续更新按主题或条目管理。

已授权的文档修改直接起草、落盘并核验。若发现尚未决定的产品能力或公共契约变化，先完成不依赖该决定的工作，在关联 unit 的阶段报告中说明具体选项与影响，请 owner 裁决；只有现有报告不足以承载审批上下文时才补 `approval-report.md`。措辞修正或同步已批准契约不增加审批。

检索：

```
python3 .codestable/tools/search-yaml.py --dir docs/dev --filter doc_type=dev-guide --filter status=current
python3 .codestable/tools/search-yaml.py --dir docs/user --filter doc_type=user-guide --filter component={feature-slug}
python3 .codestable/tools/search-yaml.py --dir docs/api --filter doc_type=api-reference --filter status=current
python3 .codestable/tools/search-yaml.py --dir docs/api --filter doc_type=lib-api-ref --filter status=current
```

`lib-api-ref` 是已退休 `cs-libdoc` 的旧文档类型，只用于发现历史文档。遇到旧文档时按更新处理，就地迁到 `doc_type: api-reference`，不要新建第二份。

---

## YAML frontmatter

### dev-guide / user-guide

```yaml
---
doc_type: dev-guide | user-guide
slug: {英文连字符}
component: {关联模块名或 feature slug}
status: draft | current | outdated
summary: {一句话描述涵盖什么}
tags: []
last_reviewed: YYYY-MM-DD
---
```

### api-reference

```yaml
---
doc_type: api-reference
entry: {entry}
category: {category}
status: draft | current | outdated
source_files: [{source_files}]
summary: {summary}
tags: []
last_reviewed: YYYY-MM-DD
---
```

`status` 三态：`draft` 待 review；`current` 当前有效；`outdated` 对应代码已变文档没跟上（保留原文，标记后推送更新）。API manifest 可额外使用 `pending` / `skipped` 表示待生成或明确跳过。旧 `doc_type: lib-api-ref` 只作为历史输入识别，落盘必须改为 `api-reference`。

---

## 文档格式

### dev-guide

```markdown
## 概述
一段话描述功能定位和适用场景。

## 前置依赖
集成此模块所需的环境、依赖或配置（如有）。

## 快速上手
最小可运行示例。代码优先文字辅助。

## 核心概念
（可选）理解接口 / API / 模块行为所需的关键术语和设计决定。

## 接口参考
主要 API / 配置选项 / 事件 / 钩子。表格或逐项列举。

## 常见场景
2-4 个实际使用场景代码示例，覆盖 happy path 和常见边界。

## 已知限制与注意事项
（可选）边界、性能考虑、已知 bug 绕过方式。

## 相关文档
关联的 user-guide、api-reference、方案 doc、架构 doc 或外部参考。
```

### user-guide

```markdown
## 功能简介
一段话描述功能是什么、解决什么问题。

## 前置条件
（可选）使用前的前提（账号权限、需先完成的操作）。

## 如何使用
步骤化操作。每步一行，关键操作配截图占位（`![描述](./assets/xxx.png)` 或注明"此处需截图"）。

## 常见问题
Q: ...
A: ...

## 相关功能
（可选）关联功能跳转链接或说明。
```

### api-reference

```markdown
## 概述

## API 参考

## 基本用法

## 典型场景

## 注意事项

## 相关条目
```

模板是最大集，按条目实际情况裁剪。API reference 必须从源码提取接口签名、类型定义、默认值、已有注释、导出方式和项目类型特有表面；源码与方案不一致时，以源码为准写文档。

---

## 工作流步骤

1. **明确范围**——根据请求确定读者、覆盖范围和新建或更新模式。
2. **收集输入**——定向查找同主题现有文档，读取相关契约、术语和代码；兼容旧 `lib-api-ref` 类型，已有文档优先更新，证据足够时停止搜索。
3. **批量 API 参考**——维护 `docs/api/manifest.yaml`，按确定的粒度处理；只有读者定位或范围未定时才用样例对齐。每个条目须有对应源码依据，可批量读取共享来源，不复制改名。
4. **起草**——按读者需要裁剪模板，只使用真实接口和示例；文档不能借机改变产品契约。
5. **核验与落盘**——检查来源、示例和链接，直接写入授权目标并汇报。已核验且无未决审批时设 `status: current`、`last_reviewed` 为当天；用户只要草稿或确有未决契约时保留 `draft` 并说明缺口。
6. **维护版本**——优先更新 canonical 文件；确需独立历史版本时标 `outdated` 及替代关系，避免同时存在两个有效版本。

API reference 硬规则：

- 以源码为事实源，不靠猜
- 每个条目有对应源码依据，不复制改名
- 源码结构特殊（动态导出 / 代码生成）暂标 `skipped` 加 note
- 不把 spec 信息（不变量 / 测试约束 / 根因分析）写进 API 文档

---

## 与其他工作流的关系

| 来源 | 关系 |
|---|---|
| `cs-feat-accept` | 验收后主动推：开发者用法变更推 dev-guide，用户可见变更推 user-guide，公开表面变更推 api-reference |
| `cs-feat-design` | 方案第 2 节是 dev-guide / api-reference 补充信息源；第 1 节是 user-guide 主要信息源；API 仍以源码为准 |
| `cs-onboard` | 新仓库接入后可补全基础文档骨架 |
| `cs-arch` (check) | 检测到 design 与代码不一致时对应 guide 应同步标 `outdated` |
| `cs-decide` | dev-guide 引用的技术选型应来自 decisions，不独立发明 |
| `cs-trick` | dev-guide 用法示例若与 tricks 重合，交叉引用而不重复写 |

---

## 容易踩的坑

- 把方案 doc 里"实现提示"原文搬进 dev-guide——那是内部 spec
- 没检查已有 guide 就新建——可能两份冲突
- 未核验或待裁决文档误标 `current`；已完成且无未决事项的文档仍标 `draft`
- 代码已更新相关 guide 还是 `current`——应标 `outdated` 并推送更新
- dev-guide 和 user-guide 内容高度重叠——其中一份定位有误
- 没读源码就写 API 参考——API reference 核心价值是准确反映源码
- 复制上一个 API 条目改名——必然漏掉微妙差异
- 用 docs 存放 spec 信息（不变量 / 测试约束 / 根因分析）——这类内容属于 `.codestable/`
