---
doc_type: feature-design
feature: 2026-04-25-deepseek-thinking-provider
requirement:
status: approved
summary: 将 DeepSeek 官方 OpenAI-compatible API 正式接入 March，覆盖普通对话、Thinking Mode 与工具调用中的 reasoning_content 轮内回传
tags: [provider, deepseek, reasoning, tool-calls]
---

# DeepSeek Thinking Provider Design

本索引保留原入口路径，完整设计拆分到下列 part 文件，以满足单 Markdown 不超过 300 行的规则。

## Parts

- [Part 1: Decisions And Request Policy](deepseek-thinking-provider-design-part1-decisions-and-policy.md)
- [Part 2: Parsing And UI Timeline](deepseek-thinking-provider-design-part2-parsing-and-ui.md)
- [Part 3: Implementation Notes And References](deepseek-thinking-provider-design-part3-implementation.md)
