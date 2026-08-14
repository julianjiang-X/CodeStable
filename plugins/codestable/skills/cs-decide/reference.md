# decisions 参考模板

本文件提供 `cs-decide` 使用的 frontmatter、正文模板和示例。

## 1. frontmatter

```yaml
---
doc_type: decision
category: tech-stack | architecture | constraint | convention
date: YYYY-MM-DD
slug: {英文描述，连字符分隔}
status: active | superseded | deprecated
evidence: observed | validated | retired
superseded-by: {可选}
supersedes: {可选}
area: {受影响领域}
applies-to: []        # 可选：这条决策约束哪些路径
enforcement: none | review | test    # 可选，默认 none
lint: {可选，enforcement=test 时必填：能验证这条决策仍成立的命令}
tags: []
---
```

### enforcement 字段

决策写下来不等于会被遵守。`enforcement` 声明这条决策**靠什么维持**：

| 值 | 含义 |
|---|---|
| `none` | 纯记录，靠人读（默认） |
| `review` | 审查时要对照检查，写进 `applies-to` 让 reviewer 知道看哪些路径 |
| `test` | 有可执行检查，`lint` 填能跑的命令 |

**能填 `test` 就不要填 `none`。** 一条能被测试守住的决策，写成文档等于把维护成本转嫁给未来的读者——这和 `evidence-lifecycle.md` 的"机械 guard 优先"是同一条原则。

`lint` 命令必须能在仓库根目录直接执行，失败即表示决策已被破坏。

文件名：`.codestable/compound/YYYY-MM-DD-decision-{slug}.md`。

## 2. 正文模板

```markdown
## 背景

## 决定

## 理由

## 考虑过的替代方案

## 后果

## 相关文档
```

`考虑过的替代方案` 和 `相关文档` 都是可选节。

## 3. 技术选型示例

```markdown
---
doc_type: decision
category: tech-stack
date: 2026-04-11
slug: vite-as-bundler
status: active
area: frontend
tags: [vite, bundler, build-tool]
---

## 背景

项目启动时需要选择前端构建工具。

## 决定

使用 Vite 作为开发和生产构建工具。
```