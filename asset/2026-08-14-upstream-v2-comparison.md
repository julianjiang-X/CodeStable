# julianjiang-X/CodeStable vs codestable/CodeStable 差异报告

日期：2026-08-14

> **执行状态（2026-08-14 同日更新）**：A 级与 B 级已全部吸纳，发布为 `1.1.0`，见
> [CHANGELOG.md](../CHANGELOG.md)。C 级评估结论记录在 [docs/adr/001–003](../docs/adr/)：
> 三条都**不吸纳**，但其中 C2 暴露的失效模式（项目 reference 副本静默过期）真实存在且当时
> 无人检测，已通过 `reference/MANIFEST.json` + doctor `reference_drift` 补上。
> 详见文末"C 级评估结论"。

## 比较对象

| 项 | julianjiang-X | codestable |
|---|---|---|
| HEAD | `9f4c671` Revert "fix(browser-bridge): isolate runtime dependencies" | `ec47e8e` chore: cancel the continuous learning epic |
| 最后提交 | 2026-07-27 John | 2026-08-10 dafang |
| 提交总数 | 158 | 225 |
| 版本 | 无版本号 | 2.0.2（有 CHANGELOG） |
| md 总行数 | 14335 | 9555 |

共同祖先：`5377548`（2026-05-06，`feat: Add simphtml.py`）
分叉状态：`git rev-list --left-right --count HEAD...upstream/main` = **72 ahead / 139 behind**

两边从同一祖先出发，各自走了三个月，已经不是"落后几个 commit"，而是**两套不同的产品哲学**。

## 一句话结论

上游做了 v1 → v2 的彻底重写：**32 个 skill 收敛为 8 个，删掉全部项目 runtime 分发，改用"薄壳 + 风险驱动保障"**。julian 版走的是相反方向：**更多专用入口 + 更厚的机械化 runtime（工具、hooks、gate、harness）**。

不能整体合并。应该按模块吸纳上游的**方法论文本和契约协议**，拒绝吸纳会删除 maintainer / harness / tools 的结构性收敛。

---

## 一、结构差异

### 目录布局

julian（扁平，仓库根即 skill 源）：

```text
cs/ cs-arch/ cs-audit/ cs-brainstorm/ cs-decide/ cs-explore/
cs-feat/ cs-feat-accept/ cs-feat-design/ cs-feat-ff/ cs-feat-impl/
cs-goal/ cs-guide/ cs-issue/ cs-issue-analyze/ cs-issue-fix/ cs-issue-report/
cs-learn/ cs-note/ cs-onboard/ cs-refactor/ cs-refactor-ff/ cs-req/
cs-roadmap/ cs-trick/ using-codestable/
browser-bridge/ codestable-maintainer/ tests/
```

上游（插件包分发）：

```text
plugins/codestable/
  .claude-plugin/plugin.json   # version 2.0.2
  .codex-plugin/plugin.json
  skills/{cs, cs-onboard, cs-feat, cs-issue, cs-refactor, cs-review, cs-epic, cs-keep, cs-code-review}
docs/adr/001..008
experiments/    # 17 组 eval fixtures
tools/check-plugin-package.py
tests/          # 5 个契约测试
CHANGELOG / UPGRADE / SKILL_CATALOG / WORKFLOW / ROADMAP（各含 .en 版）
```

### skill 数量与体量

- julian：27 个 skill 入口，`SKILL.md` 合计 5336 行，最大单个 280 行（cs-feat-accept）
- 上游：8 个主 skill + 1 个兼容别名，整包（含 references / manifests）合计 1219 行

上游 `cs/SKILL.md` 只有 60 行，julian 的是 265 行。

---

## 二、上游 v2 的核心改动（julian 完全没有的）

### 1. 32 → 8 收敛，24 个入口无 shim 退役

| v1 名称 | v2 做法 |
|---|---|
| `cs-feat-design` / `-design-review` / `-impl` / `-qa` / `-accept` / `-ff` | 统一进 `cs-feat`，风险决定强度 |
| `cs-issue-report` / `-analyze` / `-fix` | 统一进 `cs-issue` |
| `cs-refactor-ff` | 进 `cs-refactor` |
| `cs-audit` | `cs-review` 的 audit 模式 |
| `cs-goal` / `cs-roadmap` / `-review` / `-impl-goal` | 进 `cs-epic` |
| `cs-brainstorm` / `cs-domain` / `cs-req` | `cs` 在当前会话对齐后同轮移交 |
| `cs-docs` / `-neat` / `cs-doc-api` / `-tutorial` | 在开发任务中同步文档 |
| `cs-note` | 进 `cs-keep` |
| `cs-feedback` | 进 `cs-keep` / 仓库 issue |

只有 `cs-code-review → cs-review` 保留唯一兼容别名（11 行纯转发）。

### 2. 风险驱动保障模型（最重要的方法论改动）

替代了 v1 的"任务形状决定流程档位"：

```text
执行流程 = 最小闭环 + 每个未排除风险所要求的最少保障
```

- 最小闭环 = 理解事实 → 最小完整改动 → 最窄权威验证 → 交付
- **独立 review 不再是默认步骤**，只在信任边界 / 持久化数据 / 并发语义 / 不可恢复副作用等具体风险触发
- 每个新增门槛必须说明"风险事实 → 增加的保障"
- 明确写死：行数、文件数、文案/代码类型、task kind **都不是风险的替代指标**
- 用户说"流程太重"是重算触发信号，不是无条件跳过安全门槛

对应 ADR-007 `minimum-sufficient-assurance`。

### 3. `cs-keep` 与 lesson 生命周期

julian 用 4 个 skill 做沉淀（`cs-learn` / `cs-trick` / `cs-decide` / `cs-note`）；上游合成 1 个 `cs-keep`，并引入真正的状态机：

| status | 判据 |
|---|---|
| `observed` | 单次任务已有证据，未在独立后续任务验证 |
| `validated` | **非创建该 lesson 的任务和 agent invocation** 中有效命中并验证成功 |
| `retired` | 被仓库事实反证 / scope 失效 / 已有更强 canonical owner |

配套硬约束：

- 不能自证 validated，不因命中次数或模型自评晋级
- retired 上的新结论必须另建 observed，不继承 validated 身份
- 约 50 条预算，达到先整理不扩容
- 落点路由五级：机械 guard > attention.md（≤25 条）> ADR > 项目既有文档 > lessons/ staging
- **机械 guard 优先**：能被测试/checker/lint 阻止的重复错误直接机械化，不另写重复 lesson

### 4. reviewer lineage 协议

- 每个独立审查阶段首轮必须由主流程创建 **fresh reviewer**
- design review / change review / contract review / Epic final acceptance 是**不同阶段**
- 仅因本阶段 findings 的修复复审才沿用同一 reviewer 的**同一 session**
- 复审必须逐项报告 `resolved` / `unresolved` / `new findings`，不得只核对旧 finding
- 同阶段累计最多 **3 轮**，更换 reviewer 不重置计数
- 审查前必须**冻结目标**：staged diff / 明确 range / 文档版本 / 全文 + SHA-256
- reviewer 健康度判定：running 或 `Awaiting` 且 run identity 可查 → 等待，不重复创建

### 5. `cs-review` 作为叶子执行器

- 禁止创建、委派或唤醒任何子 agent
- 禁止再次调用 `cs-review` / `cs-code-review`
- 每次调用必须返回终态结果；上下文不足返回 `NeedsContext`，不得以 `idle` 结束

这条防的是 review 递归和 agent 悬挂，julian 版没有等价约束。

### 6. `cs-epic` 双层文档

- **永久** `.codestable/epics/`：目标、范围、已批准子项、决策、交付索引、终态验收
- **临时** `.codestable/work/epic-{slug}.md`：批准 revision、执行进度、`item_progression` / `milestone_commit` / `remote_publish` 策略；终态删除游标保留档案
- 三道 owner gate：拆解确认 / 边界变化重确认 / fresh reviewer 终态整体验收
- 2.0.2 新增 owner-gated `item_progression: parallel`：主流程是唯一 orchestrator 和游标写者，worker 在隔离 workspace 执行依赖无关子项，集成串行化

### 7. `references/economy.md` + `code-design.md`

两份自足的高质量方法论文本（45 行 / 61 行），julian 完全没有：

- **economy.md**：五级"从不新增"梯子；最小充分 ≠ 最小 diff；有界简化必须三要素齐（已知上限 / 升级触发 / 升级方向）；"没有上限或触发条件的'先这样'不是有界简化"；不能虚构节省数字
- **code-design.md**：先定归属和名字再做深；删除测试（假想删掉这个模块）；"一个 adapter 只是想象中的接缝，两个 adapter 才说明真有变化维度"；穿刺协议（锁定风险表 → 按不确定×失败代价降序 → 逐点最小打通 → 主路径端到端）

两份都标注"源自 codestable-lite 分支的实践沉淀"。

### 8. 分发与版本治理

- `plugins/codestable/` 插件包 + Claude / Codex 双 manifest + marketplace
- 语义化版本 2.0.0 / 2.0.1 / 2.0.2 + CHANGELOG
- UPGRADE.md 明确警告：**不要把 `npx skills@latest update` 当完整升级**，会误删 package 内 sibling skills；升级前必须精确 `remove` 24 个退役名称
- `tools/check-plugin-package.py` + 5 个契约测试（package / skill contracts / CLI distribution / v2 architecture / v2 documentation）

### 9. `docs/adr/` 8 条架构决策

带 frontmatter（`status` / `superseded-by` / `applies-to` / `enforcement` / `lint`），决策本身可被测试强制。

---

## 三、julian 独有、上游没有的（不可丢）

### 1. `browser-bridge/`（上游明确删除）

CHANGELOG 0.1.0 写着"Removed the root-level `browser-bridge` standalone skill from this distribution branch"。julian 这边还在演进（常驻 bridge master 冷启动优化）。上游没有任何替代品。

### 2. `codestable-maintainer/` + 行为回归 harness

- `tools/agent-behavior-harness.py` + `tools/verify.py`
- **75 个 critical 场景 YAML** + 5 个 live 场景
- 覆盖 approval report / backlog / worktree gate / grill 模式 / 路由 / spec drift / secret 脱敏 等

上游用 `experiments/`（17 组 eval fixtures）做类似的事，但 julian 的场景覆盖面更广、更贴近实际回归。

### 3. `cs-onboard/tools/` 18 个 Python 工具

`codestable-doctor` / `codestable-worktree-gate` / `codestable-ai-branch-guard` / `build-review-packet` / `build-context-packet` / `check-context-sufficiency` / `codestable-finish-worktree` / `codestable-worktree-inbox` / `codestable-freshness-check` / `codestable-spec-governance` / `codestable-backlog` / `codestable-main-publish` / `plan-commits` / `search-yaml` / `validate-yaml` / `validate-implementation-review` / `codestable-implementation-gate.sh` / `codestable_common.py`

**这块与上游正面冲突**，见第四节。

### 4. 全局交互模式（interview / grill）

`cs-onboard/reference/interaction-modes.md`：路由前的对话模式，中英触发词，小任务不自动升级 grill，grill 上下文可持久化。上游没有等价物（只有 `cs` 的会话内讨论）。

### 5. 其他

- AI branch guard hooks（`hooks/hooks.codex.json`）+ main publish guard
- approval reports（审批留痕）
- 双语报告策略
- `using-codestable` 自动入口（已接入仓库自动路由到 `cs`）
- `cs-arch`（只记现状的系统地图）——上游 v2 删除，无直接替代
- 7 个 pytest 套件

---

## 四、正面冲突：厚 runtime vs 薄壳

这是吸纳时最需要 owner 拍板的一点。

上游 **ADR-001** 曾经和 julian 现在做的是同一件事——把共享 Python 工具从 skill 包运行。它的 `lint` 字段甚至指向 `tests/test_codestable_doctor.py`，**就是 julian 现在还在维护的那个测试**。

然后 ADR-001 被 **ADR-004** 取代，ADR-004 又被 **ADR-005** 取代，方向是一路砍：

> v1 通过 `cs-onboard` 分发共享 reference、gate、Python runtime 和 manifest……升级时，项目副本、已安装 runtime 与 skill 文本可能处于不同版本；简单任务也要恢复并维护与实际工作无关的状态。

**ADR-002**（Accepted，未被取代）更直接：

> CodeStable 的 feature、issue、refactor、epic 和 review skills **不得规定默认 worktree、branch guard、finish-worktree 或 merge-inbox 流程**。

也就是说：julian 的 worktree gate、branch guard、finish inbox、review packet 这一整套，恰好是上游**试过、写成 ADR、然后明确废弃**的路线。

这不代表 julian 错了——上游的理由是"版本漂移 + 简单任务被迫维护无关状态"，julian 的理由是"机械化 guard 比文字纪律可靠"。但吸纳时必须知道：**这两条路不能同时走**。

---

## 五、吸纳建议

### A 级：直接吸纳，低风险高价值

这些是自足文本 / 契约条款，不依赖上游的目录结构，可以直接搬进 julian 的对应 skill。

| # | 内容 | 落点 |
|---|---|---|
| A1 | `references/economy.md` 全文 | `cs-feat/references/`，`cs-feat-impl` / `cs-refactor` 引用 |
| A2 | `references/code-design.md` 全文（含穿刺协议） | 同上 |
| A3 | 风险驱动保障公式 + "行数/文件数/task kind 不是风险代理指标" | `cs-feat` / `cs-issue` / `cs-refactor` 的保障选择节 |
| A4 | lesson 三态生命周期 `observed/validated/retired` + 不可自证晋级 + 50 条预算 | `cs-learn` / `cs-note` |
| A5 | reviewer lineage 五条（fresh reviewer / 阶段划分 / 同 session follow-up / 逐项 resolved-unresolved-new / 3 轮上限） | 已有的实现 review gate |
| A6 | `cs-review` 叶子执行器约束（禁止子 agent、必须返回终态、`NeedsContext`） | julian 的 review 入口 |
| A7 | 审查目标冻结（staged diff / range / 文档版本 / 全文+SHA-256） | 同上 |
| A8 | reviewer 健康度判定（running / `Awaiting` + run identity 可查才等待，不重复创建） | 同上 |

A5–A8 对 julian 尤其值钱：julian 已经有 subagent review gate，但没有 lineage、轮次上限和悬挂检测，实际跑起来容易出现无限对轮或重复创建 reviewer。

### B 级：值得吸纳，需要改造

| # | 内容 | 改造点 |
|---|---|---|
| B1 | 插件包分发结构 + 双 manifest + 语义化版本 + CHANGELOG | julian 需要保留 `browser-bridge` / `codestable-maintainer` 在包外或另立包 |
| B2 | UPGRADE.md 的 `skills` CLI 陷阱说明 | 直接适用，改掉退役名单 |
| B3 | `docs/adr/` 带 `enforcement` / `lint` frontmatter 的 ADR 实践 | julian 的 `cs-decide` 可以升级成这个形式 |
| B4 | 沉淀四合一（learn/trick/decide/note → keep） | 与 A4 一起做；julian 若保留分类语义，至少统一生命周期字段 |
| B5 | 共享语言条件触发（只在歧义会改变行为/契约时收敛，不新增 glossary） | 补进 `cs-feat-design` |
| B6 | `cs-epic` 永久文档 + 临时游标分离 | julian 的 `cs-goal` + `cs-roadmap` 可以借这个结构，但不必放弃 goal 入口 |
| B7 | v1 历史目录只读检索规则（九目录不生成、不改写、不迁移） | julian 若做任何收敛都需要这条 |

### C 级：不建议吸纳

| # | 内容 | 理由 |
|---|---|---|
| C1 | 整体 32 → 8 收敛 | 会删掉 `codestable-maintainer`、harness、75 个场景、18 个工具、7 个测试套件 |
| C2 | 删除全部项目 runtime 分发（ADR-004/005） | 与 julian 的机械化 guard 路线正面冲突，是 owner 级产品判断 |
| C3 | ADR-002 "skills 不拥有 worktree 策略" | julian 的 worktree gate / branch guard / finish inbox 全部建立在相反前提上 |
| C4 | 删除 `cs-arch` | 上游无替代；"只记现状的系统地图"在 julian 体系里仍有独立价值 |
| C5 | 删除 `browser-bridge` | 上游单纯不要，不是改进 |

### D 级：julian 独有，可考虑回推上游

- `browser-bridge` 常驻 master
- 行为回归 harness + 75 场景
- interview / grill 全局交互模式

---

## 六、建议执行顺序

1. **先做 A1–A2**（两份 reference 文本）：纯新增，零冲突，立刻提升 `cs-feat-impl` / `cs-refactor` 的实现质量。
2. **再做 A5–A8**（review 协议）：julian 现有 review gate 的实际缺口，改动集中在一处。
3. **然后 A3 + A4**：需要改多个 skill 的保障选择节和沉淀节，配套更新 harness 场景。
4. **B1–B3 单独立项**：分发结构和版本治理是独立议题，不要和方法论吸纳混在一起。
5. **C2 / C3 提交 owner 决策**：不要由实现顺手决定；这是"厚 runtime vs 薄壳"的路线选择。

每一步都应跑 `python3 -m pytest tests/` 和 `codestable-maintainer/tools/agent-behavior-harness.py`，A3/A4 还需要同步更新受影响的 critical 场景 YAML。

---

## C 级评估结论

问题不是"上游为什么删"，而是"它删掉的东西解决的问题，在本仓库存不存在，以及有没有更便宜的解法"。

### C2：删除项目 runtime —— **诊断对，处方不吸纳**

上游 ADR-004 的两条理由，逐条核对：

| 上游理由 | 在本仓库是否成立 | 证据 |
|---|---|---|
| 版本分叉：项目副本 / 已安装 runtime / skill 文本可能不同版本 | **成立，且当时完全无人检测** | `codestable-freshness-check.py` 只比对已安装 skill copy 与远端 main；`codestable-doctor.py` 无任何 reference / 版本 / 漂移检查；全仓库无 `runtime-manifest.json` 或等价物 |
| 简单任务被迫维护无关状态 | **不成立** | 本仓库工具是按需调用的检查器，不是每任务恢复的状态机 |

第一条尤其危险的地方在于**它给人一种已经覆盖了的错觉**——仓库里有个叫 "freshness check" 的东西，
但它看的不是这个轴。而 1.1.0 新增四份共享 reference 后，老项目的技能会直接指向不存在的
`.codestable/reference/economy.md`，缺口会立刻发作。

但删掉整个 runtime 不是唯一处方：**版本分叉的根因是没有版本标识，不是有共享资产**。
已采用的解法是给共享 reference 加 `MANIFEST.json`，让 doctor 离线判定
`ok` / `version-mismatch`(P1) / `incomplete`(P1) / `unversioned`(P2) / `absent`。

固有成本没有消失——升级后仍要逐仓库刷新副本。改变的是这个成本从**静默失效**变成
**P1 阻断 + 可执行修复指引**。详见 [ADR-001](../docs/adr/001-keep-shared-project-runtime.md)。

### C3：放弃 worktree 所有权 —— **不吸纳**

上游 ADR-002 的论点是关注点分离，成立的前提是"owner 或宿主已经选好了安全的 checkout 环境"。
本仓库的 branch guard 和 worktree gate 恰恰是为这个前提**不成立**时准备的（AI 在主检出直接
`git switch`、在 main 上实现、完成后忘记 finish）。

这与 1.1.0 吸纳的"机械 guard 优先"是同一条原则的不同应用范围：上游把它用在 lesson 上，
本仓库同时用在执行环境上。代价（耦合执行环境、worktree 能力无法独立演进）已接受并记录。
详见 [ADR-002](../docs/adr/002-keep-worktree-ownership.md)。

### C1：32 → 8 收敛 —— **不吸纳，但吸纳它的解法**

上游诊断正确：**阶段化入口容易变成流程档位的代理指标**。但"入口数量"和"流程重量"是两个可以
分开的变量：

- 上游：合并入口，单 skill 内按风险决定强度；
- 本仓库：保留入口，把 `assurance.md` 注入所有执行技能，明确写死"task kind 不是风险的替代指标"。

两者解决同一个问题。上游更彻底但要求整体重写；本仓库保留了阶段入口的可发现性和 harness 场景
覆盖，代价是"入口名暗示流程重量"的引力仍在，靠 `assurance.md` 持续对冲。

直接收敛还会一并删除 `codestable-maintainer`、75 个 harness 场景、18 个工具和 7 个测试套件——
上游有 `experiments/` 承接，本仓库没有等价替代品。
详见 [ADR-003](../docs/adr/003-keep-staged-skill-topology.md)。

### C4 / C5：删除 `cs-arch`、`browser-bridge` —— **不吸纳，无需 ADR**

这两条不是取舍，是上游单纯不要：`cs-arch`（只记现状的系统地图）在上游 v2 没有任何替代品；
`browser-bridge` 在上游 CHANGELOG 0.1.0 被明确移出分发分支。两者在本仓库都有独立价值且无冲突，
保留不产生需要记录的架构后果。

### B7 未执行的说明

原报告 B7"v1 历史目录只读检索规则"的前提是"julian 若做任何收敛"。C1 已决定不收敛，
本仓库也不存在 v1 → v2 的入口断代，因此该规则无适用场景，未引入。

---

## 附：复现命令

```bash
git clone https://github.com/julianjiang-X/CodeStable.git julian
git clone https://github.com/codestable/CodeStable.git upstream
cd julian && git remote add up ../upstream && git fetch up
git merge-base HEAD up/main
git rev-list --left-right --count HEAD...up/main
```
