# Codex 工程执行日程（按依赖，而非日历时间）

**检查点 A（P0）**：读取原始资料 → 运行 preflight → 审计 contract/schema → 安装依赖 → 类型检查 → ADR → P0_AUDIT。只有可复现的环境准备完成，才进入核心规则。

**检查点 B（P1.1）**：StoryDefinition + GameState Factory + 条件 DSL + validated Effects + reducer + knowledge projection。先测试事实不可泄漏、不能无证据成功。

**检查点 C（P1.2）**：Task Evaluator + Fate Reconciler + deterministic clock + idempotency + event replay。先测试 119/120 分钟临界逻辑。

**检查点 D（P1.3）**：Proposal Validator + FakeModel + Demo CLI + Snapshot/Repository。运行成功/失败/超时三条路径，审查因果事件列表。

**检查点 E（Gate）**：覆盖测试并修复；至少 30 core + 10 fate；分支覆盖率目标 90%；写真实 QA；P1 未通过不得进入 P2。

执行过程中保持简明的阶段日志，真正遇到阻塞再向用户报告。**不等待用户逐次批准每个小模块。**
