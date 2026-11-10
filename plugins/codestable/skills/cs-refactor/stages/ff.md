# cs-refactor · ff

读取本会话尚未读过的 `.codestable/attention.md`。只加载任务相关上下文，已读且未改变的资料不重复读取。共享路径、worktree、审查及提交约定见 `shared/shared-conventions.md` 第 0、2.6、4 节。

任务状态或执行环境不明确时才运行 `codestable-doctor.py --root . --json`。

## 适用范围

目标是保持外部行为。新能力或 bug 修复使用对应流程；范围明确、等价证据容易取得时直接执行。少量跨文件移动或浏览器验证不自动升级；证据不足时先补相称刻画测试或观察。

### 第 4 条：风险核对（不过不退流程，加保障）

上面三条判的是行为等价、规模和可自证性，**挡不住小而危险的改动**——一次纯结构调整照样可能落在权限判断、迁移脚本或并发路径上。

动手前对要碰的路径和调用方做一次**静默核对**。八类风险与 `shared/assurance.md` 风险映射表逐行对应：目标 / 根因不确定或存在真实取舍 · 破坏兼容或多消费者公开契约 · 权限 / 安全 / 隐私 / 凭证 / token / 信任边界 · 持久化数据 / schema / 迁移 · 并发 / 顺序 / 一致性 · 不可恢复的代码外副作用 · 性能敏感路径 · 影响面广或失败可跨模块传播（公共 helper、共享配置、feature flag）。

命中后先读 `assurance.md`，**照搬命中那一行列出的全部保障**——格子是复合的，`+` 连接的每项都要做，标着确认的还要 owner 拍板；所谓只加对应保障，限定的是不启用别的行，不是把一行砍成一条。**review 随命中的行走：**命中任何一行要求「加审」或「确认」的，工作目录的条件 (3)（要 owner 确认时同时是条件 (2)）成立：创建工作目录、按正式 unit 走，实现 review 必须是 subagent，「加审」要在它之外再多一轮对应目的的审查，不能拿实现 review 顶替；没命中这类行，inline review 就够。在 refactor 里，增加的保障通常体现为把自证从跑一遍测试提升到该风险要求的具体证据。

只命中风险、规模仍合格时**不切回**完整流程——加保障后继续在 ff 里做完。

做完在一句话汇报里写明「风险事实 → 增加的保障」；不命中就带一句 `风险核对：无命中`，不写产物、不额外提问——让这次核对可被观察到，避免变成可以静默跳过的步骤。

行为等价不代表风险为零：**等价的是行为，不是失败代价。**


## 执行与验证

简述方向后完成已授权工作，不重复求批；只读评估请求不授权修改。沿用模块职责，不混入无关优化。经典重构方法按需参考，不强制方法编号或完整方法库阅读。

按实际风险选择测试、类型检查、引用核查或浏览器操作；通过后无新改动/失败/疑问不重复扩大测试。性能优化必须有适合实际负载的证据，不凭代码变短宣称提速。

无正式 unit 的低风险工作可 fresh self-review。正式 unit 使用独立 subagent review；仅环境确无 subagent 能力时按共享规则使用 fresh self-review fallback 并记录环境原因。保留 `{slug}-implementation-review.md` 的目标、审查方式、验证证据和 findings，P0/P1 先修复并复核。不将 self-review 冒称独立审查。

简要报告变化、证据、实际审查方式和「风险事实 → 增加的保障」或 `风险核对：无命中`。

## 文件与门禁

默认不建工作目录，也不建 scan / design / checklist：证据是 diff、测试输出和交付说明（最终汇报加提交信息，写清做了什么、取舍、等价性证据、没验证的部分）；被别的 agent 派工时同样适用。只在 `cs-refactor` 路由文件里工作目录的四个条件之一成立时写 `.codestable/refactors/YYYY-MM-DD-{slug}/{slug}-refactor-note.md`，正式 review 证据放同 unit 的 `{slug}-implementation-review.md`；收尾同 `cs-refactor`：毕业、结案提交，之后在单独的提交里删除目录。存在正式 unit 时：

按 shared-conventions 第 2.6 节使用执行 worktree，保留无关改动、共享计划面及既有 override 契约。改动前执行 start gate；完成证据写入后执行 commit gate：

```bash
python3 {SKILL_DIR}/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/refactors/YYYY-MM-DD-{slug}
python3 {SKILL_DIR}/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/refactors/YYYY-MM-DD-{slug}
```

正式 review packet 需要时使用：

```bash
python3 {SKILL_DIR}/tools/build-review-packet.py --root . --unit .codestable/refactors/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

风险要求的 spec / verification 审查及 fresh command output 仍保留。不要等到 gate 才检查证据是否齐备。

继续已有提交/推送授权，完成重构不自动授权合并。

## 什么时候跳出 fastforward

范围或依赖无法在轻量工作中清楚界定，或等价验证需要迁移计划，是实际规模信号；以规模信号为准转 `cs-refactor`。保留已有证据与改动，不自动 restore 或提交。新增实质 owner 取舍才请求决定，其他计划可在原授权内补齐继续。

只命中风险而规模可控时不切回，按风险段加保障；新行为不能伪装成重构。

## 相关

完整计划见本技能的 `SKILL.md`，方法细节按需读本技能目录下的 `reference/methods.md`。
