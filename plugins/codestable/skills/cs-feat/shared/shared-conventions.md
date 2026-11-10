# CodeStable 共享口径

本文件随用到它的技能分发，位于该技能目录下的 `shared/shared-conventions.md`；源文件在 `cs-onboard/reference/`。它是跨子技能共享但不适合堆在单个技能里的规范的唯一权威版本。

skill 本身不共享文件系统（每个 skill 是独立安装单元），共享口径不能放在某个 skill 内部被别的 skill 引用。放在"工作项目"里对所有 skill 都可达。

## 0. 目录结构与路径命名

onboard 完成后骨架（`cs-onboard` 负责搭建）：

```
.codestable/
├── attention.md           CodeStable 技能启动必读的项目注意事项
├── requirements/          能力愿景层（"用户需要什么、系统提供什么能力来满足"，过去/现在/未来）
│   ├── VISION.md           中心索引（按 status 分组，每条带 pitch 一句话）
│   └── {slug}.md           一个能力一份，扁平（cs-keep req 产出）
├── architecture/          架构中心目录（"用什么结构实现"，只记现状）
│   ├── ARCHITECTURE.md    总入口（索引 + 关键架构决定）
│   └── {type}-{slug}.md   子系统 / 模块 doc（cs-keep arch 产出）
├── roadmap/               规划层（"接下来怎么做这块大需求 + 模块怎么切 + 接口怎么定"）
│   └── {slug}/            一个大需求一个子目录（cs-roadmap 产出）
│       ├── {slug}-roadmap.md   主文档：背景 / 范围 / 模块拆分 / 接口契约 / 子 feature 清单 / 排期
│       ├── {slug}-items.yaml   机器可读子 feature 清单，acceptance 回写状态
│       ├── grill/              可选，accepted grill-context，供 human review
│       └── drafts/             可选
├── goals/                 限定起点/终点的自主迭代目标（起点报告 / iteration / 功能验收）
│                          （goals / features / issues / refactors 下的带日期目录是工作目录：
│                           只在满足第 3 节条件时创建，收尾时毕业后删除，不是档案）
│   └── YYYY-MM-DD-{slug}/
│       ├── state.yaml
│       ├── goal.md
│       ├── functional-acceptance.md
│       ├── approval-report.md  （需要 owner 审批但最近迭代报告未承载上下文时）
│       ├── grill/              可选，accepted grill-context，供 human review
│       └── iterations/
├── features/              feature 工作目录的父目录
│   └── YYYY-MM-DD-{slug}/  每个 feature 一个目录
│       ├── {slug}-brainstorm.md  （可选，case 2 时产出）
│       ├── {slug}-design.md      （标准流程）
│       ├── {slug}-checklist.yaml （标准流程）
│       ├── grill/               可选，accepted grill-context，供 human review
│       ├── {slug}-implementation-review.md （实现完成门禁）
│       ├── {slug}-acceptance.md  （标准流程）
│       └── {slug}-ff-note.md     （fastforward 通道在建了工作目录时的唯一产物，与上面四份互斥）
├── issues/                issue 工作目录的父目录
│   └── YYYY-MM-DD-{slug}/
│       ├── {slug}-report.md
│       ├── {slug}-analysis.md   （根因不显然才有）
│       ├── grill/               可选，accepted grill-context，供 human review
│       ├── {slug}-implementation-review.md
│       └── {slug}-fix-note.md
├── refactors/             refactor 工作目录的父目录
│   └── YYYY-MM-DD-{slug}/
│       ├── {slug}-scan.md
│       ├── {slug}-refactor-design.md
│       ├── {slug}-checklist.yaml
│       ├── {slug}-implementation-review.md
│       └── {slug}-apply-notes.md
├── compound/              沉淀类文档统一目录
│   └── YYYY-MM-DD-{doc_type}-{slug}.md
│                          doc_type ∈ {learning, trick, decision, explore}
├── brainstorms/           brainstorm / pre-route grill / spike 临时产出（被 design 或 roadmap 消费后删除，未消费的保留）
│   └── {slug}/
│       ├── brainstorm.md        可选，open brainstorm 记录
│       ├── grill/               route 未定前的 grill-context round docs
│       └── spike files          可选，文件名随意；结论回写到对应 note
└── tools/                 可选：启用 git hook 回退的项目才有，只放守卫脚本
```

共享参考和工具脚本不放在项目里：它们在各技能自己的目录下（`shared/`、`tools/`）。文中 `shared/<名字>.md` 指当前技能目录下的文件，`{SKILL_DIR}/tools/<名字>` 指当前技能目录下的脚本。技能只带自己会调用的脚本，完整工具集在 `cs-onboard`；当前技能没带的脚本就手工完成对应检查并说明。项目里旧的 `.codestable/reference/` 与 `.codestable/tools/` 副本不再被读取。

### 命名规则

- 需求文档：`requirements/{slug}.md`（能力愿景，不带日期前缀，扁平不分组）；中心索引 `requirements/VISION.md`
- roadmap：`roadmap/{slug}/`（不带日期前缀，平铺不嵌套）
- goal：`goals/YYYY-MM-DD-{slug}/`（带创建日期；状态模型和报告见 `shared/goal-conventions.md`）
- feature / issue / refactor 目录：带日期前缀 `YYYY-MM-DD-{slug}`
- 沉淀类：`compound/YYYY-MM-DD-{doc_type}-{slug}.md`，日期用**归档当天**
- 架构 doc：`architecture/{type}-{slug}.md`（长效，不带日期前缀）；总入口固定 `ARCHITECTURE.md`
- grill context：route 未定前写
  `brainstorms/{slug}/grill/round-NNN-{axis}.md`；route-ready 后可复制或迁移到
  `{workflow}/{unit}/grill/round-NNN-{axis}.md`，原 brainstorm 路径保留
  repo-relative 指针。`doc_type: grill-context` 必须带
  `source_of_truth: false`，只能作为 human review context。
- 项目注意事项入口固定为 `.codestable/attention.md`，使用 CodeStable 时读取一次，未变化不重读；同时遵守实际生效的 `AGENTS.md` / `CLAUDE.md` 等项目入口，冲突时按指令优先级处理

### 报告语言策略

- 只给 agent 读的文件（工作目录里的文件、`compound/` 等记录）用一种语言写，不写双语副本。用哪种由 `attention.md` 指定；未指定时沿用该项目现有记录的语言
- 写给 owner 看的内容（审批报告、最终汇报、对话）用 owner 的语言
- 只有 `attention.md` 点名了具体的人类读者时，才为那份文档提供第二种语言（额外写 `{name}.{lang}.md`，或在同一文件里先后写完整两份）
- `approval-report.md` 是写给 owner 的，`attention.md` 要求"先英文后中文"时，它必须是完整英文正文加完整中文正文；只追加 `中文摘要` 不满足，会被 backlog / doctor 标为 blocking `bilingual-report-policy`。其余文件不被这条检查
- 机器状态以 YAML / JSON / `state.yaml` 为准，不从不同语言的叙述反推状态

### 架构 doc 分组规则（同类聚合）

`architecture/` 下用文件名第一段作 type 标记：`ui-chat.md` 和 `ui-events.md` 同 `ui` 类。**所有架构 doc 必须 `{type}-{slug}.md`**——只有一份的也要带合理 type 段（如 `cli-entry.md`），否则未来同类出现时聚合不了。

**触发**：某 type 在 `architecture/` 根目录达到 ≥6 份时（即新加第 6 份那次），把这一类全部收进同名子目录。

**收入后**：去掉 type 前缀。`ui-chat.md` → `ui/chat.md`。

**只升不降**：删到 ≤5 份也不折回平铺。

**触发时谁负责**：`cs-keep arch` 的 `backfill` / `update` 模式在 Phase 6 落盘前主动检查并搬迁；命中阈值时这次操作要把"本次新加 / 改的 + 已有同类全部"一起搬，并同步改 `ARCHITECTURE.md` 链接（记录搬迁和链接更新；超出授权范围才询问）。`check` 模式不主动搬迁，但发现 ≥6 仍平铺时在报告末尾列为观察项。

改 `cs-onboard/reference/shared-conventions.md` 这份源文件，再运行维护者的同步脚本刷新各技能的 `shared/` 副本；项目里没有需要同步的副本。

## 1. 共享元数据口径

**feature spec**：brainstorm / design / acceptance 共用 `doc_type` / `feature` / `status` / `summary` / `tags`。子技能只补特有字段。`status`：brainstorm = `confirmed`（落盘即确认无 draft）；design = `draft` / `approved`；acceptance 见对应技能。

**issue spec**：report / analysis / fix-note 共用 `doc_type` / `issue` / `status` / `tags`。`severity` / `root_cause_type` / `path` 由对应阶段按需补。

**归档类（compound）**：

- learning / trick / decision / explore 四类**统一写入 `.codestable/compound/`**
- 每个文档 frontmatter 顶部带 `doc_type`（learning / trick / decision / explore）作跨子技能归属判定
- 文件名 `YYYY-MM-DD-{doc_type}-{slug}.md`——日期打头便于 `ls` 排序，type 段在中间便于 grep
- 各子技能在 `doc_type` 之外保留专属 frontmatter（learning 的 `track` / trick 的 `type` / decision 的 `category` / explore 的 `type`）
- 各子技能只认自己的 `doc_type` 不读写别家
- `status` 等通用字段语义和本文件保持一致
- 统一带 `evidence` 字段标证据成熟度（`observed` / `validated` / `retired`），语义见第 6.1 节

`status` 和 `evidence`是两个正交维度，不要混用：`status` 说的是**这份文档还算不算数**（active / superseded / outdated / deprecated），`evidence` 说的是**里面的结论被验证到什么程度**。一条 `status: active` 的 learning 完全可以是 `evidence: observed`。

**外部读者文档**：由 `cs-guide` 维护 `dev-guide` / `user-guide` / `api-reference` 三种模式。无特殊说明：`draft` = 待 review，`current` = 当前有效，`outdated` = 代码已变更待同步。

**写作约束**：子技能提字段时优先写"额外字段"或"阶段状态变化"，不重复展开整套通用字段。

## 2. {slug}-checklist.yaml 生命周期

- 是 feature 工作流的唯一执行清单
- 由 `cs-feat design` 在 design 确认通过后一次生成 `steps` + `checks`
- `cs-feat ff` **不生成** checklist（也不写 design / acceptance），是跳过 spec 流程直接写代码的超轻量通道；默认不留文件（交付说明写进汇报和提交信息）；只有满足第 3 节工作目录条件时才回写 `{slug}-ff-note.md`（轻量回顾，参与 scoped-commit，收尾时随目录删除）

`steps` 的粒度是 **编排-计算分离维度的切片策略**——按"先编排骨架、后计算节点、最后持久化与测试"写（最简 Workflow 先行 → 逐个节点填充），**不下沉到 file:line / 函数级**。具体改哪个文件由 implement 阶段决定。

**design 的职责**：

- 提取 `steps`（按工作规模划分，每步有可验证退出信号）：后端节奏 = 编排骨架 → 计算节点逐个填 → 接通持久化 → 测试覆盖；前端 = 静态结构 → 交互逻辑 → 状态接入 → 联调收尾
- 提取 `checks`：第 1 节"明确不做"→ 范围守护；第 2.1 接口 → 名词契约；第 2.2 主流程 + 流程级约束 → 编排骨架；第 2.3 挂载点 → 挂载点；第 3 节场景清单 → 验收场景

**implement 的职责**：

- 按 `steps` 顺序执行，每步完成把 status `pending` → `done`
- 在已授权范围内可追加 / 拆分 steps、完成必要的局部重构并记录原因；改变产品契约、范围或风险承诺时才请求 owner 决策
- 不改写 `checks`

**acceptance 的职责**：只更新 `checks[].status`（`pending` → `passed` / `failed`），不重写 `steps`。

**写作约束**：子技能描述 checklist 时只补本阶段读 / 写哪一部分，不重新定义生命周期。

## 2.5 roadmap ↔ feature 衔接协议

`.codestable/roadmap/{slug}/{slug}-items.yaml` 是规划层和 feature 执行层的唯一接口。三个技能共同读写它——是 skill 都读写项目共享产物，不算耦合。

**items.yaml 状态机**：

```
planned  → in-progress  （cs-feat design 启动 feature 时改）
in-progress → done      （cs-feat accept 验收完成时改；同时写 commit）
planned  → dropped      （cs-roadmap update 模式，用户决定不做时改）
```

`done` / `dropped` 是终态。需要回退重做的新加一条 slug 略改的条目，不改终态。

**`feature` 是不透明标识，不是路径**：启动时写 `YYYY-MM-DD-{slug}`，用来在提交和 PR 里反查，对应的工作目录收尾后会被删，不必存在。条目到 `done` 时同时写 `commit:`——合并提交或 PR（编号或链接）；写 done 时还不知道，先写 `commit: pending`，在删除工作目录的那个提交里补上（它允许带非实现的 `.codestable/**` 改动）。

**没有工作目录、没有 design 的路径（ff 通道）谁写 items.yaml**：执行任务的会话自己写——开工时把条目改 `in-progress` 并填 `feature`，完成时改 `done` 并填 `commit`，同步主文档子 feature 清单，并校验 yaml。没有 design frontmatter 可读，条目 slug 以用户指定的为准。

**cs-roadmap 的职责**：生成和维护 roadmap 主文档 + items.yaml；把 `planned` 改 `dropped`（用户放弃时）；不改 `in-progress` / `done`（feature 技能负责）。

**cs-feat design 的职责**（从 roadmap 起头时）：

1. design.md frontmatter 加 `roadmap: {roadmap-slug}` + `roadmap_item: {子 feature slug}`
2. items.yaml 对应条目 `status: in-progress` + `feature: YYYY-MM-DD-{slug}`（标识，目录不必一直存在）
3. 校验 yaml

直接起 feature（非 roadmap 来）两字段留空，不触发 roadmap 写。

**cs-feat accept 的职责**：

1. 读 design frontmatter `roadmap` / `roadmap_item`
2. 空 → 跳过
3. 有值 → items.yaml 对应条目 `status: done` + `commit:`（合并提交或 PR，见上）；同步主文档子 feature 清单显示状态；校验 yaml

回写是**实际写文件的动作**，验收报告要明确记录回写结果。

**最小闭环标记**：items.yaml 每份只有一条 `minimal_loop: true`，标记"做完后系统能端到端跑通最窄路径"。design 启动 `minimal_loop` 条目时优先级最高。

## 2.6 main 协调 + worktree 执行

执行拓扑、worktree gate、implementation review、finish gate、context
packet 和 subagent 执行选择已拆到
`shared/execution-conventions.md`。子技能只在本文件记录目录
和生命周期共享口径；涉及实际改代码、review、commit、finish 或 merge 前，
按需读取 execution conventions 对应章节；同一任务内未变化不重读。

## 3. 阶段收尾与工作目录

**工作目录是工作状态，不是档案。** 工作目录（`.codestable/features|issues|refactors/YYYY-MM-DD-{slug}/`，goal 同理）是任务进行中的工作状态。只在下列任一条件成立时创建：(1) 任务会跨会话，或要交接给别的 agent 或人；(2) 有需要 owner 决定或批准的契约；(3) 按 `assurance.md` 的风险判断需要正式的独立审查；(4) owner 要求留痕。其余任务不建目录：证据是 diff、测试输出和交付说明。被别的 agent 派工时同样适用：结果以报告和提交交回派工方，不因为派工说明里写了「照 CodeStable 流程」就产出设计、清单、验收文件。

**任务收尾**（验收通过、修复验证完成、重构完成，或被 owner 取消）时：

1. **毕业**：把以后还要用的内容写到它该在的地方。能力或边界变化 → `requirements/`；结构变化 → `architecture/`；难回退的决定 → `cs-keep decide`；踩过的坑 → `cs-keep learn`；常驻约束 → `attention.md`。能写成测试或检查器的约束优先机械化。先列出毕业清单，清单里每一项都要有去处，或写明「不需保留」。
2. **结案提交**：代码 + 毕业写入的文档 + 工作目录里还剩的所有内容（实现 review 证据在内）。提交信息写清做了什么、关键取舍和理由、验收证据（跑了什么、结果如何）、没有验证的部分。这是这次任务的长期记录。
3. **worktree finish gate**：适用时（见 `execution-conventions.md`）此时工作树是干净的，跑它并提交它的产物。
4. **删除工作目录**，单独一个提交，不与结案提交合并。这个提交只能包含该单元的删除，加非实现的 `.codestable/**` 改动，不能带代码。git 历史里仍可找回。工具会拦：删除一个在 HEAD 里需要 review 的单元，HEAD 里必须已有 `reviewer: subagent` 的证据；删除未结束的 goal 目录（`state.yaml` 不是终态）也会被拒。

顺序固定：先毕业并做结案提交，再 finish gate，最后单独删除。

**不删的情况**：任务阻塞或未完成（目录就是恢复记录）；有未决的 approval report；owner 要求保留；审计里还有未解决的 finding。

范围：`audits/` 下的审计目录在 finding 全部解决或被 owner 接受后按同一规则删除，未解决时保留。`compound/` 下的 learning / trick / decision / explore 是知识，不受本节影响。`brainstorms/` 见第 0 节目录说明。`goals/` 的终态处理见 `shared/goal-conventions.md`。

只更新本次行为或契约变化实际影响的文档；没有新增知识就不生成文档或逐项询问。已授权提交时直接完成 scoped-commit。

## 4. 收尾提交（scoped-commit）

acceptance / issue-fix 走完后，在已有提交授权内按独立逻辑变更提交（第 3 节的结案提交）：

- **范围**：本次工作改到的代码 + 毕业写入的文档（架构 doc、requirements、roadmap items.yaml / 主文档、compound 记录）+ 工作目录里还剩的内容。工作目录的删除不在这个提交里，是第 3 节的单独一个提交（不建工作目录的任务没有这一项）
- **不该进**：和本次工作无关的顺手修改；属于"下次另起 feature / issue"的扩大范围
- **提交授权**：当前任务已授权 commit / push 时不重复询问；没有提交授权时交付可审阅改动，不能从完成实现推断 merge / deploy 授权
- **commit message**：按第 3 节写清做了什么、关键取舍和理由、验收证据、没验证的部分；不贴已删除的工作目录路径

dirty tree 混有多类产物或提交边界不明确时，用只读 commit planner 辅助划分：

```bash
python3 {SKILL_DIR}/tools/plan-commits.py --root . --json
```

planner 只读，不替你 stage。它会把 code/docs/tests、migrations/database_docs、data、logs、CodeStable 文档、installed skill deployment、unknown 分开，并提示 migration/database docs、runbook doc-sync、tracked ignored、large file、live writer 风险。

子技能只描述本阶段特有提交范围，通用规则看这里。

## 5. 检索范围

开工检索默认只读：`attention.md`、`requirements/`、`architecture/`、`compound/`，以及与本任务相关的进行中工作目录。3.0.0 之前留下的已结束单元（`features/`、`issues/`、`refactors/`、`goals/` 下的旧目录）不在默认检索范围内，只在 owner 指到、或当前任务明确接续它时才读；读到的内容先对照当前代码核实再用。

- 按任务关键词定位 `architecture/` 或 `compound/` 相关条目；自包含的小改无需遍历
- 在 `compound/` 用 `doc_type` 过滤（learning / trick / decision / explore）
- 搜到的结果只作参考输入，不盲目套用——可能已 `outdated` 或不适合当前上下文
- 搜到和当前方向冲突的 decision → **必须**正面回应"为什么仍然这么做"或调整方向

**命中后先核实再用**（read-repair）：`evidence: retired` 不应用；`observed` / `validated` 都要用当前代码、测试或 canonical 文档做**一次有界、最低成本**的定向核实。核实不了就跳过该条，不阻塞正常任务，**不为核实一条经验去跑大范围测试或反复复现**。

有效命中按固定格式报告：

```text
经验命中：{path}（{evidence}）；核验：{fact}；影响：{plan_or_check}
```

只是相关但没有真正改变计划或验证时不报，不制造复用证据。完整口径见 `shared/evidence-lifecycle.md`。

子技能只补本阶段查询命令。完整搜索语法看 `shared/tools.md`。

## 6. 沉淀类（compound）子技能共享守护规则

`cs-keep learn` / `cs-keep trick` / `cs-keep decide` / `cs-explore` 共享下面这组规则。子技能正文只写特有反模式，通用看这里：

1. **只增不删**（仅 `compound/`，工作目录不适用）——已沉淀除非被明确取代（`status=superseded`）否则不删；理由丢失成本极高
2. **宁缺毋滥**——用户说不出理由的节直接省略，不要 AI 编造
3. **不替用户写实质内容**——AI 负责起草结构和串联语言，实质结论必须来自用户或可追溯的代码证据
4. **attention.md 检查**——写完后若沉淀暴露出"每次启动都该知道"的一两行硬约束，提示用户用 `cs-keep note` 追加到 `.codestable/attention.md`；不要直接改外部 AI 入口
5. **起草前先查重叠**——动手写前用 `search-yaml.py --query` 查语义相近的旧文档。按用户意图选择以下路径；实质结论冲突才请用户决定：
   - **更新已有**（默认优先）：沿用原文件名和原创建日期，**不新建**；frontmatter 补 `updated: YYYY-MM-DD`；超出小修在文末加"YYYY-MM-DD 更新"简述
   - **supersede**：旧文档保留原文，`status: superseded` + `superseded-by: {新文件名}`，正文顶部加 `**[已取代]** 见 {新 slug}`；新文档 frontmatter 带 `supersedes: {旧文件名}`
   - **确实是不同主题**：新建，文末"相关文档"列出已有那条说明区别
6. **识别用户意图是"改已有"还是"记新的"**——用户说"改 / 更新 / 修订 / 补充 {某条}"、明确指向某条旧文档、或话题高度重合时默认走"更新已有"，不要闷头新建。分不清就问。

各子技能只认自己的 `doc_type`，不读写别家产物。

## 6.1 证据成熟度（evidence 生命周期）

归档类文档统一带 `evidence` 字段（`observed` / `validated` / `retired`）标证据成熟度。
三态判据、不可自证晋级规则、应用侧核实与命中报告格式、50 条预算与机械 guard 优先，
完整口径见 `shared/evidence-lifecycle.md`。

## 7. 局部实现判断

在既有职责内完成最小完整改动。文件长度、参数数目或出现分支本身不是重构理由；职责混杂、重复逻辑或错误抽象确实妨碍当前任务时，可在授权范围内局部调整并验证。扩大公共契约、架构方向或产品范围的变化另行说明并取得必要决定，不为每次拆函数或重命名中断执行。

## 8. 回答进度

进度不存页面，被问时现看。owner 问进度、还差什么、下一步、卡在哪，或会话接续工作时，看四处：

- **进行中**：本检出和各 linked worktree 里在做的工作目录，阶段读该单元自己的文件（goal 的 blocked 读 `state.yaml`）；没有目录但分支领先默认分支或工作树有改动的 worktree 也算，没有 worktree 的领先分支只计数。3.0.0 起收尾（毕业、结案提交、删除）先于合并：已有完成标记且自该分支从默认分支分叉以来被改动过的，是收尾中，照样列出；没被改动过的已完成或已取消单元是早期记录，不算（缺 review 由 doctor 报）；比较不了时当作在做。
- **等待**：未决的 approval report、已完成但未合并的 worktree、打开的 PR。
- **最近完成**：默认分支最近约 10 个提交，结案提交信息就是记录。
- **下一步**：有 `roadmap/` 取其进行中 / 计划中条目；否则取进行中单元下一个未做的步骤；都没有就说没有记录，不编造。

没有该命令的 skill（目录里没有 `tools/codestable-status.py`）按上面四处手动看。一条只读命令取齐（同一单元和同一 approval report 在多个 worktree 里只报一条；不联网；`--prs` 才通过 `gh` 查打开的 PR，`gh` 不可用或失败记入 `not_checked`，不算错误）：

```bash
python3 {SKILL_DIR}/tools/codestable-status.py --root . [--json] [--prs]
```

回答直接在对话里给 owner，用 owner 的语言，按这四节各写几行；每行带能核对的指针（路径、分支、提交或 PR），并写明没查的部分（如远端没 fetch）。别人的工作或远端状态，在已有授权内实际去查（fetch、看 PR），授权不够就写「未核对」。答案不写进文件。没接入 CodeStable 的仓库同样直接从 git 回答（`git worktree list`、分支、`git log`）。
