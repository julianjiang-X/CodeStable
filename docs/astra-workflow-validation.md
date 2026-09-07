# Astra workflow validation

This audit follows the fully read [OpenAI Astra guidance](https://developers.openai.com/api/docs/guides/latest-model) and [Eric Provencher article](https://x.com/pvncher/status/2095991462416490862), retrieved September 6, 2026. It reduces unconditional context loading and repeated approval while preserving formal lifecycle evidence and deployment boundaries.

An independent agent exercised the actual updated entry skills in isolated fixtures:

| Request | Observed result |
|---|---|
| Fix a README typo with using-codestable | Changed only the typo, read back the result, created no lifecycle records and requested no input. |
| Evaluate returning a bare array with cs | Identified the accepted items/next_cursor contract, checked the current return value and left files unchanged. |

Independent diff review found an inconsistent no-unit self-review exemption in cs-feat-ff. It was removed: using that skill creates an ff-note and thus a formal unit, with the corresponding independent review requirements. Ordinary edits may use the direct path without that skill. The reviewer rechecked this fix and marked it resolved.

These observations are bounded trials, not a statistical performance claim. The first automated live-codex attempt could not start the installed CLI because it rejected the host configuration (`invalid type: map, expected a boolean` in `features`). No host configuration was changed. The new manual live scenarios preserve repeatable requests and artifact/state assertions for a compatible CLI. The separate deterministic harness validates tooling and fixture contracts; it does not demonstrate live model behavior.

---

# Astra 工作流验证

本次完整阅读了 [OpenAI Astra 官方指导](https://developers.openai.com/api/docs/guides/latest-model) 与 [Eric Provencher 原文](https://x.com/pvncher/status/2095991462416490862)，读取日期为 2026-09-06。精简无条件上下文加载和重复审批，保留正式生命周期证据与部署边界。

独立 agent 使用实际更新入口和隔离 fixture：拼写任务只改目标拼写并回读，不创建流程档案或询问；API 只读评估识别 items/next_cursor 契约并检查当前返回值，没有改文件。

独立差异审查发现 cs-feat-ff 中无正式 unit self-review 豁免与必需 ff-note 冲突。已删除该豁免：使用该技能生成 ff-note 即进入正式 unit，保留独立审查要求；普通微改可直接处理而不进入该技能。审查者已复核并确认解决。

以上为有限试验，不是统计性能结论。首次自动 live-codex 尝试因本机 CLI 无法解析现有 features 配置而未启动，未修改主机配置。新增手动 live 场景可在兼容 CLI 重跑；确定性 harness 验证工具与 fixture 契约，不等于真实模型行为验收。

A later controlled 16-run comparison is recorded in [the live pilot report](astra-live-pilot.md), including repaired scoring, isolation, measured results, and remaining limits.

后续 16 轮受控真实模型对照见[试点评测报告](astra-live-pilot.md)，包含评分修正、隔离方式、实测结果与覆盖边界。
