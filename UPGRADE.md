# CodeStable 升级指南

升级前先看 [CHANGELOG.md](./CHANGELOG.md)，确认这一版改了什么。

## 安装 / 升级

用最初的安装入口重新装一次：

```bash
npx skills add https://github.com/julianjiang-X/CodeStable/tree/main/plugins/codestable
```

也可以走插件入口：

```bash
codex plugin marketplace add https://github.com/julianjiang-X/CodeStable
codex plugin add codestable@codestable
```

Claude Code 用 `/plugin marketplace add https://github.com/julianjiang-X/CodeStable`，
再 `/plugin install codestable@codestable`，装完重启使新版生效。

不要把 `npx skills@latest update` 当作完整升级方式：它可能只刷新自己记录过的条目，漏掉同一来源
里新增的技能。从来源根目录重新 `add` 才会按当前仓库内容发现完整技能集。

## 从 2.x 升级到 3.0.0

3.0.0 是破坏性发布：技能入口从 28 个合并为 15 个，共享参考和工具不再复制进项目。

### 1. 删除已退役的技能入口

`skills` CLI 的 `add` 不会删除新版里已经没有的旧技能，所以首次升级要先按名字删掉 14 个旧入口，
再重新安装：

```bash
npx skills@latest remove \
  cs-arch cs-decide cs-feat-accept cs-feat-design cs-feat-ff cs-feat-impl \
  cs-issue-analyze cs-issue-fix cs-issue-report cs-learn cs-note \
  cs-refactor-ff cs-req cs-trick \
  -g -y
npx skills add https://github.com/julianjiang-X/CodeStable/tree/main/plugins/codestable
```

这条命令按名字删除，不校验来源。如果你有同名的自定义技能，先备份并从命令里去掉它。项目级安装
去掉 `-g`，在项目目录里执行。用 `codestable-maintainer` 的 `verify.py --sync-installed` 部署的
安装副本会自动清掉这些旧目录。

### 2. 旧入口到新入口

阶段没有消失，只是变成了合并后技能里的阶段文件。

| 旧入口 | 现在 |
|---|---|
| `cs-feat-design` / `cs-feat-ff` / `cs-feat-impl` / `cs-feat-accept` | `cs-feat` 的 design / ff / impl / accept 阶段 |
| `cs-issue-report` / `cs-issue-analyze` / `cs-issue-fix` | `cs-issue` 的 report / analyze / fix 阶段 |
| `cs-refactor-ff` | `cs-refactor` 的 ff 阶段 |
| `cs-note` / `cs-learn` / `cs-trick` / `cs-decide` / `cs-req` / `cs-arch` | `cs-keep` 的 note / learn / trick / decide / req / arch 模式 |

文档里写作 `cs-feat design`、`cs-keep note` 等。项目文档、`attention.md` 或派工模板里如果点了旧
名字，按上表改写；历史档案里的旧名字不用动。

### 3. 项目里的 `reference/` 和 `tools/` 不再需要

共享参考和工具脚本现在随各技能分发，位于技能自己目录下的 `shared/` 与 `tools/`。升级技能包就
全部更新，**不再需要在每个已接入的项目里重跑 `cs-onboard` 或手工复制**。

- 项目里已有的 `.codestable/reference/` 与 `.codestable/tools/` 不再被任何技能读取，也不会再刷新。
- 确认没有 git hook 或 CI 指向 `.codestable/tools/` 后可以删除这两个目录。启用了 branch guard
  hook 的项目保留 hook 用到的脚本，见 `cs-onboard/reference/branch-guard-hooks.md`。
- `codestable-doctor.py` 对过期的旧副本只给一条 P2 提示，不再阻塞。项目没有 `reference/` 目录是
  正常状态。

项目自己的 `attention.md`、`requirements/`、`features/` 等内容不受影响，既有产物格式不变。

### 4. 工作目录收尾时删除

这是一条行为变化，不是格式变化。

- `features/`、`issues/`、`refactors/`、`goals/` 下的带日期目录现在是**工作目录**：任务进行中的工作状态，
  不是档案，默认不建。只在任务会跨会话或要交接、有待 owner 批准的契约、需要正式独立审查、
  owner 要求留痕时创建。其余任务不建目录，证据是 diff、测试输出和交付说明；被别的 agent 派工时也一样。
- 任务收尾时先毕业（把以后还要用的内容写进 `requirements/`、`architecture/`、`cs-keep decide` /
  `learn`、`attention.md`），做结案提交（代码 + 毕业写入的文档 + 目录里还剩的内容，提交信息写清做了什么、
  取舍、证据、没验证的部分），适用时跑 finish gate，最后在**单独一个提交**里删除工作目录（只含目录删除和非实现的
  `.codestable/**` 改动）。门禁按 HEAD 里的内容判断：需要 review 的单元，HEAD 里没有 subagent review 证据就删不掉；
  未结束的 goal 目录也删不掉。阻塞未完成、有未决 approval report、owner 要求保留、审计有未解决 finding 时不删。
- **旧项目里已有的旧单元不会被动**：不迁移、不批量删除，工具也不会删它们。它们默认不再被开工检索读取，
  只在 owner 指到或当前任务接续它时才读，读到的内容先对照当前代码核实。想清理由 owner 自己决定，
  git 历史里仍可找回。
- 只给 agent 读的文件用一种语言写，由 `attention.md` 指定；项目里原来要求"先英文后中文"的，
  双语检查现在只对写给 owner 的 `approval-report.md` 生效，其他文件不再被拦。

### 5. 其他行为变化

范围门槛、owner 规矩当场记录、汇报格式、审查轮次上限和讨论方式的变化见
[docs/claude-models-iteration.md](./docs/claude-models-iteration.md)。

## 检查安装副本是否落后

```bash
python3 <SKILLS_ROOT>/cs-onboard/tools/codestable-freshness-check.py --json
```

`<SKILLS_ROOT>` 是装着各个技能目录的那一层：`skills` CLI 装的是 `~/.claude/skills` 或
`${CODEX_HOME:-$HOME/.codex}/skills`，插件装的是 `<插件目录>/skills`，源码仓库是
`<repo>/plugins/codestable/skills`。`should_prompt_update: true` 表示安装副本落后于远端 `main`。

## 更早的版本

- 1.x → 2.0.0：安装来源从仓库根目录改为 `plugins/codestable`，技能名和项目结构不变。
- 既有归档文档（`.codestable/compound/`）缺 `evidence` 字段的按 `observed` 读取，不需要批量迁移。

## 升级后检查

- 调用 `/cs`，确认根入口可用。
- `ls <SKILLS_ROOT>` 应看到 15 个技能目录，且没有上面列出的 14 个旧名字。
- 在一个已接入的项目里让 `cs-feat` 走一次小改动，确认它读取的是技能目录下的阶段文件。

返回 [README](./README.md)。
