---
name: cs-issue-fix
description: "按已授权方案修复缺陷，验证根因消除并保存修复证据。"
---

# cs-issue-fix

读取本会话尚未读过的 `.codestable/attention.md`。只加载任务相关上下文，已读且未改变的资料不重复读取。共享路径、worktree、审查及提交约定见 `.codestable/reference/shared-conventions.md` 第 0、2.6、4 节。

## 两种入口

### 标准路径

读 confirmed analysis、report 和相关代码，核实当前根因证据及已选方案。用户已授权修复时直接执行，不重复确认起点或逐文件求批。仅在根因仍不确定、批准契约冲突或新增实质取舍时补分析并请求必要判断。相关 decision / learning 按需查询，不固定搜索所有归档类型。

### 快速通道

1. 用复现或现有证据定位根因，简述方向。修 bug 请求包含范围内修复授权，不等待固定确认语句。
2. 检查实际风险：
   - **风险核对（静默）**——快速通道省掉的是 analysis 文档，**不是风险判断**。一行修复照样可能落在权限判断、迁移路径或并发语义上；这条通道跳过了 analysis，所以根因仍不确定本身就是命中项之一。对要碰的路径做一次静默核对，八类风险与 `.codestable/reference/assurance.md` 风险映射表逐行对应：目标 / 根因不确定或存在真实取舍 · 破坏兼容或多消费者公开契约 · 权限 / 安全 / 隐私 / 凭证 / token / 信任边界 · 持久化数据 / schema / 迁移 · 并发 / 顺序 / 一致性 · 不可恢复的代码外副作用 · 性能敏感路径 · 影响面广或失败可跨模块传播（公共 helper、共享配置、feature flag）。
     命中后先读 `assurance.md`，**照搬命中那一行列出的全部保障**——格子是复合的，`+` 连接的每项都要做，标着确认的还要 owner 拍板；所谓只加对应保障，限定的是不启用别的行，不是把一行砍成一条。其中加审指在本通道已有的独立 review 之外**再加一轮**对应目的的审查，不是拿地板 review 顶替。在 fix 里，增加的保障通常体现为红到绿之外还要补的那份证据。
     命中后在 fix-note 写明「风险事实 → 增加的保障」，不命中就带一句 `风险核对：无命中`。只命中风险不因此升级回标准路径；但若核对发现根因判断本身站不住，回 `cs-issue-analyze` 重新定位。
3. 根因证据不足则回 `cs-issue-analyze` 补定位；先自主取得可取得的证据，不把普通调试交还用户。

## 执行与验证

修复针对根因，保留无关改动。必要的额外文件或内部结构调整可在原授权范围完成并同步 analysis；改变公开契约或扩大业务范围才需要新的 owner 判断。

验证原复现、期望行为及实际受影响路径。优先跑相关测试；可稳定自动复现且能保护真实回归的 bug 增加回归测试。UI 可见行为用浏览器验证，不用 typecheck 代替。通过后无新改动或疑问不重复扩大测试；无法取得的证据明确标未验证。

修复无效时更新根因假设，选择能区分假设的日志、断点、trace 或最小复现，不反复猜改。需要日志脚手架或 fix-note 模板时读 `reference.md`；清理临时敏感日志后交付。

## 审查与归档

正式 unit 使用独立 subagent review；仅环境确无 subagent 能力时按共享规则使用 fresh self-review fallback 并记录环境原因。保留 `{slug}-implementation-review.md` 的目标、审查方式、验证证据和 findings，P0/P1 先修复并复核。不将 self-review 冒称独立审查。

验证后写 `{slug}-fix-note.md`：标准路径引用 analysis，快速通道补根因和风险证据。保留 `doc_type: issue-fix`、issue、`path: standard | fast-track`、fix_date、tags 等字段。

按 shared-conventions 第 2.6 节使用执行 worktree，保留无关改动、共享计划面及既有 override 契约。改动前执行 start gate；完成证据写入后执行 commit gate：

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/issues/YYYY-MM-DD-{slug}
python3 .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/issues/YYYY-MM-DD-{slug}
```

正式 review packet 需要时使用：

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit .codestable/issues/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

风险要求的 spec / verification 审查及 fresh command output 仍保留。不要等到 gate 才检查证据是否齐备。

一次汇报修复前后行为、证据和限制，不在每处改动后停等回复。继续已有提交/推送授权；未授权的外部动作在具体结果就绪后再请求。新功能和无关优化另记，不混入修复。
