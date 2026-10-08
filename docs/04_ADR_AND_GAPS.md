# Codex 必读：现有交付资料缺口与待决策问题

这些是交付包制作时通过内容审查发现的**实施缺口**，并非已修复的软件 Bug。Codex 应在 `docs/ADR.md` 记录每个决定，不得自行臆造小说情节。

| ID | 已识别的缺口 | P0/P1 处理建议 |
|---|---|---|
| GAP-01 | DEMO 有场景与物品 ID，但没有完整的动作-结果映射、位置邻接关系、救援过程定义 | P1 以可信 `test_fixture` 事件验证任务与命运；端到端真实行动编排须增版本化规则，不能由 AI 自发改变 `witness_rescued` |
| GAP-02 | `GameEvent` 合同只有一个可选 `causationId`，原技术规格要求更完整的 `causedByEventIds[]` 审计 | 在实现中明确因果指针约定；不破坏原 Schema 时可将多个上游事件放在另一个审计结构，必须 ADR |
| GAP-03 | 命运候选事件的状态（已排程/取消/触发）在 `GameState` 只有 ID 队列，没有元数据 | 设计内部 FateEventState / scheduler record，事件是否发生与候选是否取消分开 |
| GAP-04 | 原始接口 `RulesEngine.adjudicate` 异步，而确定性 P1 不应依赖外部网络 | 推荐纯同步 core + 异步 orchestrator 包装，接口适配方式 ADR 记录 |
| GAP-05 | 人物认识一个事实的原始状态分散在 `world.facts.initialKnownTo` 与 `characters.initialState.knownFactIds` | 明确两者的初始化合并与冲突检测策略；不能让私密知识泄漏给别的角色 |
| GAP-06 | `revoke_event` 的对象 `event.witness_death` 可能是未来候选，也可能已经是已发生历史 | 定义为只取消尚未提交的候选；已发生必须保留不可变记录 |
| GAP-07 | 时间 `timeScale` 和 cutoff 边界已有文字约定，但实时调用与原著定时事件的裁定顺序未代码化 | 先实现 P1 的离散分钟和 `deadlineMinute`；P4 再对接真实 UTC 推演 |
| GAP-08 | 任务 `locked` 到 `active` 的进入条件及自动接单含糊 | P1 规定显式 `available` 与 `active` 转换政策，记录 ADR 并测试 |
| GAP-09 | 来源契约含浏览器 Media Adapter、ZIP 导入接口，但 P1 尚不实现 | 允许保留抽象合同，不得把未实现接口当作“已具备能力” |
| GAP-10 | 包内只有原创虚构 Demo，不是用户具体小说的改编剧情 | 不要擅自向用户索取小说以阻塞 P0/P1；正式内容需独立授权与制作流程 |

## ADR 写入要求

每条 ADR 至少有：问题、备选方案、最终决定、为何不采用其他方案、影响的文件/Schema/测试、兼容性版本、是否未来需重新评审。

## 建议的执行边界

- P1 优先保证故事世界的一致性与任务命运可验证；不追求模型任意自由行动都能自动映射到作者未定义的场景。
- 当测试需要产生 `set_flag(witness_rescued, true)`，只允许测试专用的 `trusted_event`，明确证明浏览器玩家/AI 无权调用该入口。
- 如果扩展 v1.0 Schema，请同时提供迁移策略，且继续能加载老的 DEMO（或明确升级新版本）。
