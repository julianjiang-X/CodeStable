# Changelog

本仓库的版本号只描述**技能包内容**的变化。安装副本是否落后仍由
`cs-onboard/tools/codestable-freshness-check.py` 按 git ref 判断——版本号回答的是"我落后了什么"，
freshness check 回答的是"我落后了没有"。

## 3.0.0

**breaking：技能入口从 28 个合并为 15 个；共享参考和工具不再复制进项目；工作目录收尾时删除。** 升级步骤见
[UPGRADE.md](./UPGRADE.md)，依据与局限见 `docs/claude-models-iteration.md`。

Structure / 结构：

- Merge stage skills into their parent: `cs-feat` (design / ff / impl / accept),
  `cs-issue` (report / analyze / fix), `cs-refactor` (ff). Stage text moved
  unchanged into `stages/` inside the skill.
- Add `cs-keep` with six modes (note / learn / trick / decide / req / arch),
  replacing `cs-note`, `cs-learn`, `cs-trick`, `cs-decide`, `cs-req`, `cs-arch`.
- Ship shared references and the tools a skill calls inside that skill
  (`shared/`, `tools/`). Sources stay in `cs-onboard/reference/` and
  `cs-onboard/tools/`; `codestable-maintainer/tools/sync-shared.py` keeps the
  copies equal and a test enforces it.
- `cs-onboard` no longer releases `reference/` or `tools/` into projects. The
  doctor reports an out-of-date legacy copy as P2 instead of blocking.
- Register the 14 retired names in `verify.py` so installed-copy sync prunes them.

- 阶段技能并入父技能：`cs-feat`（design / ff / impl / accept）、`cs-issue`
  （report / analyze / fix）、`cs-refactor`（ff）。阶段正文原样移到技能内的 `stages/`。
- 新增 `cs-keep`，六种模式（note / learn / trick / decide / req / arch），取代
  `cs-note`、`cs-learn`、`cs-trick`、`cs-decide`、`cs-req`、`cs-arch`。
- 共享参考和技能会调用的工具随技能分发（`shared/`、`tools/`）。源仍在
  `cs-onboard/reference/` 与 `cs-onboard/tools/`，由 `sync-shared.py` 同步，测试保证一致。
- `cs-onboard` 不再把 `reference/`、`tools/` 释放到项目。doctor 对过期的旧副本只报 P2。
- `verify.py` 登记 14 个退役名字，同步安装副本时自动清理。

Behavior for Claude models / 针对 Claude 模型的行为调整（Fable 5.2、Opus 5.5、Sonnet 5.5）：

- Apply CodeStable only in onboarded repositories or on explicit request.
- Record owner-stated scope and authorization rules at first statement; keep
  cautions scoped, reasoned and pruned.
- Report what was and was not exercised, end with the next step, and take it
  when authorized.
- State what happens at the review round budget; pre-authorize one converging
  extra round.
- Lead discussion with a position in `cs-brainstorm` and the `cs-feat` design stage.
  Evidence and limits: `docs/claude-models-iteration.md`.

- 仅在已接入的仓库或用户明确要求时启用 CodeStable。
- owner 说出的范围与授权规矩当场记录；谨慎条款写明范围和原因，原因不成立时清理。
- 汇报写明跑过和没跑的内容，末尾给出下一步，已有授权时直接做。
- 写明审查轮次到上限后的处理；收敛中的额外一轮预先授权。
- `cs-brainstorm` 与 `cs-feat` 的 design 阶段先给主张再讨论。依据与局限见上述文档。

Work directories and progress / 工作目录与进度（同一版本，3.0.0 尚未发布）：

- Work directories (`features|issues|refactors|goals/YYYY-MM-DD-{slug}/`) are working
  state, not archives, and are not created by default; they are created only when the
  task spans sessions or is handed off, has a contract awaiting owner approval, needs
  a formal independent review, or the owner asks for a record. Delegation text such as
  "follow the CodeStable process" does not change this.
- At closure, graduate what is still needed, write the closing commit message as the
  long-term record, run the finish gate if it applies, then delete the work directory in its own commit (not when blocked, with an open
  approval report, on owner request, or with unresolved audit findings). `cs-goal`
  and `cs-audit` follow the same rule; `brainstorms/` records are deleted once consumed.
- Progress is derived on request, not stored: `shared-conventions.md` section 8 says
  to look at work directories (main checkout and every linked worktree; units with a
  completion marker that the branch changed since forking from the default branch are
  listed as closing, and unchanged finished records from before 3.0.0 are only counted),
  worktrees ahead of the default branch or dirty, undecided approval reports, unmerged finished worktrees and open PRs,
  and the last ~10 default-branch commits, with the roadmap or in-progress units
  giving the next step. Add the read-only `codestable-status.py` (`--json`, opt-in
  `--prs` through `gh`, no network by default) that gathers it. A stored status page
  was rejected (ADR 006).
- Files only agents read use one language named by `attention.md`; the
  `bilingual-report-policy` check now covers only `approval-report.md`.
- Opening searches skip ended units left from before 3.0.0 unless the owner points
  at one or the task continues it. Existing projects are not migrated.
- Closure order is fixed: closing commit, finish gate, then the deletion in its own
  commit. Tools handle that deletion: the commit gate reports `unit_removed` and
  judges the unit from HEAD (no review evidence in HEAD means no deletion; code in
  the same change or an unfinished goal is rejected), the doctor ignores the baseline
  of a closed unit, and the worktree inbox keeps a finish report valid across the
  deletion and non-implementation `.codestable/**` edits. New tests in
  `tests/test_codestable_closed_units.py`. Decision: `docs/adr/006-*.md`.
- `docs/claude-models-iteration.md` gains a model column and an escalation order
  (verification, then effort, then a larger model) from the 2026-11-10 model guide.

- 工作目录（`features|issues|refactors|goals/YYYY-MM-DD-{slug}/`）是任务进行中的工作状态，
  不是档案，默认不建；只在任务会跨会话或要交接、有待 owner 批准的契约、需要正式独立审查、
  owner 要求留痕时创建。派工说明里的"照 CodeStable 流程"不改变这一点。
- 收尾时先毕业，再用结案提交信息作长期记录，适用时跑 finish gate，最后在单独的提交里删除工作目录（阻塞未完成、有未决
  approval report、owner 要求保留、审计有未解决 finding 时不删）。`cs-goal`、`cs-audit`
  同规则；`brainstorms/` 记录被消费后删除。
- 进度不存页面，被问时现看：`shared-conventions.md` 第 8 节规定看工作目录（本检出和各 linked worktree；有完成标记且自分叉以来被该分支改动过的是收尾中，照样列出；
  没改动过的早期已完成记录只计数）、领先默认分支或有改动的 worktree、未决 approval report、已完成未合并的 worktree 和打开的 PR、默认分支
  最近约 10 个提交，下一步取 roadmap 或进行中单元。新增只读的 `codestable-status.py`
  （`--json`，`--prs` 才通过 `gh` 查 PR，默认不联网）一次取齐。存进度页的方案已被拒绝（ADR 006）。
- 只给 agent 读的文件用一种语言，由 `attention.md` 指定；`bilingual-report-policy` 检查
  收窄到 `approval-report.md`。
- 开工检索默认不读 3.0.0 之前留下的已结束单元，除非 owner 指到或当前任务接续它。
  既有项目不迁移。
- 收尾顺序固定：结案提交、finish gate、再单独一个提交删除目录。工具能处理这个删除：commit gate 输出
  `unit_removed` 并按 HEAD 判断（HEAD 里没有 review 证据就不让删，同一变更里带代码或删未结束的 goal 目录
  会被拒），doctor 忽略已收尾单元的 baseline，worktree inbox 在删除和非实现的 `.codestable/**` 改动后仍认
  finish 报告。新增
  `tests/test_codestable_closed_units.py`。决策见 `docs/adr/006-*.md`。
- `docs/claude-models-iteration.md` 增加模型列和升级顺序（先验证、再努力级别、最后换大模型），
  依据 2026-11-10 的模型选择文章。

## 2.1.0

Astra workflow simplification / Astra 工作流精简：

- Reuse project context, select known stages directly and continue authorized work.
- Remove routine routing approvals, automatic freshness checks and repeated broad
  searches. Calibrate verification to risk; keep formal review and publication gates.
- Shorten descriptions across 27 skills and synchronize shared/stage guidance.
  Add two manual live scenarios and replace obsolete approval-phrase probes with
  real gate/protocol checks. See `docs/astra-workflow-validation.md` for limitations.

- 项目上下文复用，直接进入已知阶段并完成授权工作。
- 取消普通路由审批、自动版本检查和重复广搜；按风险验证，保留正式审查及发布门禁。
- 精简 27 个技能描述与入口，同步共享和阶段约定。新增两个手动 live 场景，
  以真实门禁/协议检查替换过期审批句断言。验证边界见上述文档。

## 2.0.0

**breaking：安装路径变了。** 技能从仓库根目录移到 `plugins/codestable/skills/`，仓库现在是标准
插件包布局。安装命令见 [UPGRADE.md](./UPGRADE.md)；已安装副本的目录结构**不变**（仍是扁平的
`<installed_root>/<skill>`），只有安装来源路径变了。

打包与分发：

- 新增 `plugins/codestable/.claude-plugin/plugin.json` 与 `.codex-plugin/plugin.json`，
  可用 Claude / Codex 的插件入口安装。
- 28 个技能（`cs` / `cs-*` / `using-codestable` / `browser-bridge` / `codestable-maintainer`）
  全部移入 `plugins/codestable/skills/`，交付集合与 1.0.0 完全一致，只改源码布局。
- 源码侧路径统一走单一常量：`verify.py` 的 `SKILLS_PREFIX`、
  `codestable-freshness-check.py` 的 `SKILLS_PREFIX`、`tests/layout.py` 的 `SKILLS_RELPATH`、
  harness 的 `SKILLS_ROOT`。安装侧仍是扁平路径，两者由这些常量转换。
- 行为 harness 新增 `{skills}` 占位符：`{source}` 仍指仓库根，`{skills}` 指插件包。
  11 个引用技能文件的 scenario 已改用 `{skills}`。
- harness 的 `SKILLS_ROOT` 按**深度**推导（`parents[2]`），源码树和扁平安装副本两种布局都成立；
  `SOURCE_ROOT` 改为按标记向上查找，找不到就退回 `SKILLS_ROOT`。
- harness 解析不到任何 scenario 时**直接报错退出**，不再返回 `ok: true` + 0 个 scenario。
  这是一个验证工具最危险的失败模式：什么都没跑却报告通过。
- `verify.py` 的 `is_real_installed_root` 补上 `~/.claude/skills` 与插件 `**/skills` 目录，
  feature 分支同步真实 installed root 的护栏不再有缺口；plugin manifest 变更不再被标为
  "source-only"。

审查修复（本版内）：

- `reference_drift` 对格式错误的 manifest（非 object、`files` 非字符串列表、无法解析）
  返回新状态 `unreadable`，不再抛 `AttributeError` 把整份 doctor 报告变成 traceback。
- doctor 的 `incomplete` 文案改为"缺少其自身 manifest 列出的文件"（此前错说成"包提供的文件"）；
  漂移类 finding 移到生命周期 finding **之后**，不再挤掉主信号。
- `.codestable/` 存在但没有 `reference/` 时报 P2（骨架不全，不阻断无关工作）。
- 新增 `test_documented_commands_point_at_real_files`：扫描 README / UPGRADE / 所有 SKILL.md 里
  可复制的 `python3 <path>` 命令，断言文件真实存在。这条守护正是发现并修掉本次 31 处
  文档路径失效的机械手段。
- 新增 plugin manifest 版本一致性测试，六个版本载体（`VERSION` / CHANGELOG / `MANIFEST.json` /
  `PACKAGE_VERSION` / 两个 `plugin.json`）全部由测试守住。
- `cs-onboard` 的拷贝指引改用 `<SKILLS_ROOT>` 并明确"是装着各技能目录的那一层"，
  修掉原先会拼出 `cs-onboard/cs-onboard/tools/` 的路径重复。

以下方法论吸纳原计划作为 1.1.0 发布，未推送，现随本版一并发布。

### 从上游 `codestable/CodeStable` v2 吸纳（原 1.1.0）

不改变本仓库的技能拓扑和 runtime 路线。

#### 新增共享参考

（`cs-onboard/reference/`，onboard 时释放到 `.codestable/reference/`）：

- `economy.md` — 实现经济性：五级"从不新增"梯子、最小充分 ≠ 最小 diff、有界简化三要素
  （已知上限 / 升级触发 / 升级方向）、不可被"最少"删掉的部分、对收益保持诚实。
- `code-design.md` — 模块深度、先定归属和名字、结构跟着业务形状走、删除测试、接缝必须真实
  （一个 adapter 不算接缝）、接口就是测试面、重要接口设计两遍、穿刺协议。
- `assurance.md` — 风险驱动的保障强度选择：`执行流程 = 最小闭环 + 每个未排除风险所要求的最少保障`；
  明确行数 / 文件数 / task kind 不是风险代理指标；"流程太重"是重算触发而不是跳过门槛。
  CodeStable 的两条地板（独立实现 review、owner 授权门槛）不参与降级。
- `evidence-lifecycle.md` — 归档文档 `evidence` 三态（observed / validated / retired）、
  不可自证晋级、retired 不复活、read-repair 与命中报告格式、约 50 条预算、机械 guard 优先。

#### 协议强化

- `execution-conventions.md` 的 Independent Code Review 补齐 reviewer lineage：审查目标冻结
  （staged diff / range / 文档版本 / 全文 + SHA-256）、审查阶段划分、fresh reviewer、
  同 session follow-up、逐项 `resolved` / `unresolved` / `new findings`、每阶段 3 轮上限、
  reviewer 健康度判定与不重复派发、reviewer 作为叶子执行器（禁止子 agent、必须返回终态或
  `NeedsContext`）。
- 原按任务形状分档的 `Risk defaults` 被 `assurance.md` 的风险映射取代。

#### 工作流调整

- `cs-feat-design` 增加**条件触发**的术语对齐：只在引入新词、重载词或相邻概念边界会改变行为 /
  归属 / 契约 / 验收时收敛；普通改动不新增 glossary、不额外提问。
- `cs-goal` / `cs-roadmap` 明确**永久档案 vs 执行游标**职责互斥：主文档在 `active` 期间冻结，
  日常进展只更新游标，边界变更需 owner 重新确认；终态清理游标前先给毕业清单，`blocked` 不清理。
- `cs-decide` 决策文档增加 `applies-to` / `enforcement` / `lint`：能被命令验证的决策必须
  机械化，不能只写文档。
- 四个归档技能（`cs-learn` / `cs-trick` / `cs-decide` / `cs-explore`）frontmatter 统一增加
  `evidence` 字段。该字段与既有 `status` **正交**：`status` 说文档还算不算数，
  `evidence` 说结论被验证到什么程度。

#### 共享 runtime 漂移检测

- `cs-onboard/reference/MANIFEST.json` 随 reference 一起释放，记录版本与文件清单。
- `codestable-doctor.py` 增加 `reference_drift`：reference 与 tools 版本不一致或清单文件缺失
  报 P1，无 manifest 的老副本报 P2。这补上了此前**无人检测**的失效模式——项目里的
  `.codestable/reference/` 副本可以静默过期，而 `codestable-freshness-check.py` 只比对
  installed skill copy 与远端，不看项目副本。
- `tests/test_package_contract.py` 守住 VERSION / CHANGELOG / MANIFEST / `PACKAGE_VERSION`
  四者一致，并检查任何 `.codestable/reference/X.md` 引用都有对应模板、所有 md 不超过 300 行。

未吸纳（见 `asset/2026-08-14-upstream-v2-comparison.md`）：上游 32 → 8 的入口收敛、
删除项目 runtime 分发、放弃 worktree / branch guard 所有权。理由记录在 `docs/adr/`。

## 1.0.0

吸纳前基线，对应 `9f4c671`，技能位于仓库根目录。共 28 个技能：25 个 `cs` / `cs-*` 入口、
`using-codestable`、`browser-bridge`、`codestable-maintainer`；另有行为回归 harness、
`cs-onboard/tools/` 下 18 个共享工具、以及 7 个 pytest 套件。

此前的变更历史见 git log；本文件从 2.0.0 开始逐版本记录。
