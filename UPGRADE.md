# CodeStable 升级指南

升级前先看 [CHANGELOG.md](./CHANGELOG.md)，确认这一版改了什么。

## 安装 / 升级

用最初的安装入口重新装一次：

```bash
npx skills add https://github.com/julianjiang-X/CodeStable/tree/main/plugins/codestable
```

从 2.0.0 起技能在 `plugins/codestable/skills/` 下发现，`add` 会按当前 `main` 的内容刷新全部入口。

也可以走插件入口（2.0.0 新增）：

```bash
codex plugin marketplace add https://github.com/julianjiang-X/CodeStable
codex plugin add codestable@codestable
```

Claude Code 用 `/plugin marketplace add https://github.com/julianjiang-X/CodeStable`，
再 `/plugin install codestable@codestable`，装完重启使新版生效。

## 从 1.x 升级：安装来源变了

2.0.0 把技能移进了插件包，**安装 URL 必须换**，否则 `add` 找不到任何技能：

```text
旧：https://github.com/julianjiang-X/CodeStable
新：https://github.com/julianjiang-X/CodeStable/tree/main/plugins/codestable
```

**已安装副本的目录结构不变**——仍是扁平的 `<installed_root>/<skill>`，技能名一个没改、
一个没退役。只有"从哪里装"变了，不需要先删旧技能。

项目里的 `.codestable/` 也不受影响。

## 不要用裸 `update`

不要把 `npx skills@latest update` 当作完整升级方式。外部 CLI 的**更新发现**与**安装发现**并不等价：
`update` 可能只刷新它自己记录过的条目，漏掉同一来源里新增的 sibling skill，也可能误删它认不出的成员。

从来源根目录重新 `add` 才会按当前仓库内容发现完整技能集。

## 升级后必须刷新项目副本

技能包升级**不会**自动更新已 onboard 项目里的 `.codestable/`。

`.codestable/tools/` 和 `.codestable/reference/` 是技能包维护的共享资产，项目里的只是落盘副本。
权威源在 `plugins/codestable/skills/cs-onboard/tools/` 和 `plugins/codestable/skills/cs-onboard/reference/`。留着旧副本会让子技能按**过时口径**工作——
这是升级后最常见的故障。

在每个已接入的项目里重跑 `cs-onboard`，或手工覆盖：

```bash
cp -rf <SKILLS_ROOT>/cs-onboard/reference/. .codestable/reference/
```

`<SKILLS_ROOT>` 是**装着各个技能目录的那一层**——`ls` 它能看到 `cs-onboard` 这个目录：
`skills` CLI 装的是 `~/.claude/skills` 或 `${CODEX_HOME:-$HOME/.codex}/skills`，
插件装的是 `<插件目录>/skills`，源码仓库是 `<repo>/plugins/codestable/skills`。
**别指到 `cs-onboard/` 本身**，那会拼出 `cs-onboard/cs-onboard/reference/`。
拷完 `ls .codestable/reference/` 验证。

**这两个目录用新版本覆盖，不走"不覆盖"保守策略。** 项目自己的 `attention.md`、
`requirements/`、`features/` 等内容不受影响。

刷新是否到位由 doctor 检查，不用靠记：

```bash
python3 .codestable/tools/codestable-doctor.py --root . --json
```

`reference_drift.state` 的含义：

| state | 含义 | 严重度 |
|---|---|---|
| `ok` | reference 和 tools 来自同一版本，文件齐全 | — |
| `version-mismatch` | 只刷新了一半，子技能会按过时口径工作 | P1 |
| `incomplete` | 清单里的文件没拷全，引用它们的技能会指向不存在的路径 | P1 |
| `unversioned` | 老副本，从未刷新过 | P2 |
| `absent` | 项目还没有 `.codestable/reference/` | — |

## 检查安装副本是否落后

```bash
python3 .codestable/tools/codestable-freshness-check.py --json
```

`should_prompt_update: true` 表示 installed copy 落后于远端 `main`。版本号回答"落后了什么"，
这个检查回答"落后了没有"，两者配合看。

## 1.x → 2.0.0 的内容变化

除了安装来源，这一版**只加不减**：没有退役任何技能入口，没有改项目 `.codestable/` 结构，没有改既有产物格式。

必须做的一件事：**刷新 `.codestable/reference/`**，否则拿不到新增的四份共享参考
（`assurance.md` / `economy.md` / `code-design.md` / `evidence-lifecycle.md`），
引用它们的技能会指向不存在的文件。

可选、不强制：

- 既有归档文档（`.codestable/compound/`）缺 `evidence` 字段的**按 `observed` 读取**，
  不需要批量迁移。只在本来就要更新那份文档时顺带补字段。
- 既有 decision 文档不需要回填 `enforcement` / `lint`，新写的才要求。

## 升级后检查

- 调用 `/cs`，确认根入口可用。
- `ls .codestable/reference/` 应能看到 `assurance.md`、`economy.md`、`code-design.md`、
  `evidence-lifecycle.md`。
- 跑一次 `python3 .codestable/tools/codestable-doctor.py --root . --json`。

返回 [README](./README.md)。
