1. 不同的技能之间不要相互耦合，即 A 技能在非必须情况下不要看 B 技能。
2. skill 是独立安装单元，运行时每个 skill 只能看到自己包内的文件。A 技能的 SKILL.md 里写 `B-skill/reference/xxx.md` 这种引用在运行时**根本读不到**——skill 之间没有共享的文件系统父目录。跨 skill 共享的参考文档和工具只有一份源：`cs-onboard/reference/` 与 `cs-onboard/tools/`。用到它们的 skill 在自己包内带副本（`shared/xxx.md`、`tools/xxx`），正文用 `shared/xxx.md` 和 `{SKILL_DIR}/tools/xxx` 引用。副本由 `codestable-maintainer/tools/sync-shared.py --write` 生成，不手改；改共享口径时改源文件再跑同步，测试会拦住不一致的副本。从 3.0.0 起不再往工作项目的 `.codestable/` 复制这些文件。

增加、更新技能时注意更新其他相关技能中的表述。


单md文档不能超过300行，超过必须拆分。


### 核心原则
言简意赅