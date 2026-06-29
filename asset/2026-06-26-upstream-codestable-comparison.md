# 上游 CodeStable 差异比较报告

日期：2026-06-26

## 范围

本报告用于判断 `fork/main` 中的内容是否值得吸纳到当前上游 `origin/main`。

- 当前上游：`origin/main` = `14131a4`，`fix: use cs display names for codestable skills`
- 候选分支：`fork/main` = `74f1aa3`，`refactor: 精简 cs-* 体系——compound 四件套合一、外部文档改名、删 architecture 立 cs-domain`
- 共同祖先：`5377548`，`feat: Add simphtml.py for enhanced HTML optimization and analysis`
- 旁路分支：`fork/add-writing-to-sell-skill` = `2b68108`，相对 `origin/main` 无独有 commit，本次不作为吸纳对象

## 结论先行

不要整体吸纳 `fork/main`。

`fork/main` 有两个有价值方向：`browser-bridge` 常驻 master 的冷启动优化，以及 `cs-*` 体系简化的产品判断。但它同时落后当前上游 65 个 commit，直接合并会删除当前已经形成的 maintainer verifier、行为 harness、review / worktree / backlog / spec governance 工具、`using-codestable` 自动入口、`cs-goal`、OpenAI skill metadata 和大量回归测试。

建议吸纳方式：

1. 单独 cherry-pick 或重做 `011d08c` 的 `browser-bridge` 常驻 master。
2. 把 `74f1aa3` 拆成多个设计议题评审，不直接合并提交。
3. 明确拒绝吸纳 `74f1aa3` 中删除 maintainer / harness / tests / agents metadata 的部分。

## Commit 差异

`git rev-list --left-right --count --cherry-pick origin/main...fork/main`：

```text
65  2
```

含义：

- `origin/main` 独有 65 个 commit。
- `fork/main` 独有 2 个 commit。

`fork/main` 独有 commit：

| commit | 内容 | 初判 |
|---|---|---|
| `011d08c` | `browser-bridge` 增加常驻 master，减少短命 CLI 等待扩展重连的冷启动成本 | 可单独吸纳 |
| `74f1aa3` | 大规模简化 `cs-*` 体系：合并 compound 四件套、外部文档技能改名、删除 architecture 改立 `cs-domain` | 只能拆议题评审 |

## 实际内容差异

从 `origin/main` 到 `fork/main` 的实际 diff：

```text
202 files changed, 2762 insertions(+), 19959 deletions(-)
```

主要影响面：

| 区域 | 实际变化 | 风险 |
|---|---|---|
| `codestable-maintainer/` | 整个 maintainer skill、fresh clone verifier、行为 harness 参考和场景测试被删除 | 阻断当前 CodeStable 自维护闭环 |
| `cs-onboard/tools/` | `codestable-doctor`、worktree gate、review packet、context packet、finish inbox、freshness check、spec governance 等工具被删除 | 破坏当前 agent 漂移控制和验收证据链 |
| `tests/` | maintainer / behavior harness / metadata / gate 相关测试被删除 | 失去回归保护 |
| `agents/openai.yaml` | 多数 skill metadata 被删除 | 破坏当前 display name、触发入口和自动加载约束 |
| `using-codestable/` | 自动入口删除 | 已接入仓库不再自动路由到 `cs` |
| `cs-goal/` | bounded goal 工作流删除 | 回退近期已采用的目标达成闭环 |
| `cs-arch/` | architecture skill 删除 | 取消当前“只记现状系统地图”的长效档案 |
| `cs-domain/` | 新增 CONTEXT / ADR / context topology 管理 | 方向有价值，但不能替代所有 architecture 场景 |
| `cs-keep/` | 用纯 markdown + grep 合并 learn / trick / decide / explore | 方向清爽，但会丢掉现有分类语义和 frontmatter 检索 |
| `cs-guide` / `cs-libdoc` | 改名为 `cs-doc-tutorial` / `cs-doc-api` | 命名更清楚，但需要兼容别名和 README / metadata / tests 同步 |

另一个质量信号：`git diff --check origin/main..fork/main` 报出旧 asset 合并文档中的 trailing whitespace。这个问题不一定来自两个独有 commit 的核心路径，但说明整体分支不能直接作为干净吸纳源。

## 可吸纳内容

### 1. `browser-bridge` 常驻 master

来源：`011d08c`

改动：

- 新增 `browser-bridge/scripts/browser_master.py`
- 在 `browser-bridge/SKILL.md` 增加常驻 master 使用说明
- 调整 `tmwd_bridge/__init__.py`：减少无意义等待，并在未指定 tab 时选择第一个 session

价值：

- 频繁浏览器操作时避免每次短命 CLI 都等待 Chrome 扩展重连。
- 对核心 CodeStable 工作流影响小，能独立验证。

吸纳建议：

- 单独 cherry-pick 或手工重做。
- 先验证 `browser.py` 是否已经有 `/link` 转发契约；若没有，必须补齐转发或修正文档。
- 验证项至少包括 `python -m py_compile`、一次 `tabs` / `exec --no-monitor` smoke，以及 `git diff --check`。

### 2. 外部文档入口收敛

来源：`74f1aa3`

fork 改动：

- `cs-guide` -> `cs-doc-tutorial`
- `cs-libdoc` -> `cs-doc-api`

价值：

- `tutorial` / `api` 比 `guide` / `libdoc` 更贴近读者心智。
- 能减少“外部文档到底写教程还是 API reference”的歧义。

owner 决策：

- CodeStable 要求从简；无非必要，勿增实体。
- 不引入 `cs-doc-*` 或父级 `cs-doc`。
- 保留一个外部文档入口 `cs-guide`，把原 `cs-libdoc` 职责合入为 `api-reference` 模式。
- 不保留独立 `cs-libdoc`；安装副本中残留的旧技能应由 freshness / verifier 识别和清理。

### 3. `cs-domain` 的 ADR / 术语表方向

来源：`74f1aa3`

价值：

- 把领域术语、ADR 和单/多 context 拓扑放在 `requirements/` 下，比把所有长期决策塞进 architecture 更聚焦。
- ADR 的“三判据”和 Nygard 四节有可执行性。

吸纳建议：

- 可以作为新增技能或 RFC 吸收，但不要同时删除 `cs-arch`。
- 更合理的边界是：`cs-domain` 管术语和决策，`cs-arch` 管当前系统结构地图。两者互相引用，不互相替代。

### 4. `cs-keep` 的轻量知识沉淀

来源：`74f1aa3`

价值：

- 纯 markdown + grep 降低维护成本。
- “背景 / 结论 / 证据”三段结构适合快速沉淀。

吸纳建议：

- 可先作为快速通道加入，而不是删除 `cs-learn` / `cs-trick` / `cs-decide` / `cs-explore`。
- 如果未来要合并四件套，需要先做迁移计划：现有 frontmatter 如何处理、检索工具如何降级、旧技能触发如何兼容。

## 不建议吸纳内容

1. 删除 `codestable-maintainer`、verifier、harness、测试和场景用例。
2. 删除 `using-codestable` 自动入口。
3. 删除 `cs-goal`。
4. 删除全部或大部分 `agents/openai.yaml`。
5. 直接废弃 `.codestable/architecture/`。
6. 把 `.codestable/compound/` 从结构化 frontmatter 一步切到纯 markdown，且不提供迁移和兼容策略。

## 推荐吸纳路径

### Phase 1：低风险独立改动

- 吸纳 `browser-bridge` 常驻 master。
- 单独 commit：`feat(browser-bridge): add persistent bridge master`

### Phase 2：外部文档入口收敛

- 将 `cs-libdoc` 合入 `cs-guide` 的 `api-reference` 模式。
- 删除独立 `cs-libdoc` 源目录，不新增 `cs-doc-*`。
- 更新 README、相关技能交叉表述、metadata tests、freshness / verifier retired skill 行为。

### Phase 3：domain / architecture 边界 RFC

- 起草 `cs-domain` 设计，但默认和 `cs-arch` 共存。
- 明确 CONTEXT、ADR、architecture map、requirements capability doc 的边界。
- 增加行为 harness 场景，防止 feature acceptance 越权重写长期架构。

### Phase 4：compound 简化实验

- 先增加 `cs-keep` 快速通道。
- 用真实项目试运行后，再判断是否废弃 learn / trick / decide / explore 四件套。
- 若要废弃，必须提供旧文件迁移和旧 skill 触发兼容。

## 验收要求

任何真正吸纳 PR 至少需要：

- 变更技能的 frontmatter / line count 校验。
- `git diff --check`。
- `uvx --with pytest python -m pytest` 或对应 focused tests。
- 对改名 / 删除 / 路由变化补行为 harness 或 metadata regression。
- 分支推送后运行 maintainer verifier：`python3 codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root "$tmp_installed" --sync-installed --json`。

## 最终判断

`fork/main` 不是可直接合并的上游，而是一个产品方向样本。

真正值得吸纳的是：

- `browser-bridge` 的常驻进程性能优化。
- 外部文档职责收敛到单一 `cs-guide` 入口的方向。
- `cs-domain` 中 ADR / 术语 / context topology 的边界意识。
- `cs-keep` 中轻量知识沉淀的使用体验。

不应吸纳的是：

- 以删除当前 maintainer harness、测试、自动入口和目标工作流为代价的整体精简。
