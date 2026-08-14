# Changelog

本仓库的版本号只描述**技能包内容**的变化。安装副本是否落后仍由
`cs-onboard/tools/codestable-freshness-check.py` 按 git ref 判断——版本号回答的是"我落后了什么"，
freshness check 回答的是"我落后了没有"。

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
