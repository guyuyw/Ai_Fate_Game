# Codex 首次执行指令｜P0 + P1

请把下面的正文作为一次执行任务。无需用户另外说明小说内容，所有测试使用包内虚构 DEMO。

---

你接手的是一个已经完成设计、尚未实现核心引擎的本地仓库。请先阅读 `AGENTS.md`，并严格按照它给出的优先级、范围和门槛执行。

## 当前开发目标

**连续完成 P0（契约审计与工程初始化）+ P1（确定性世界/任务/命运核心引擎）。不要进入 P2 聊天 UI、多模态与真实 AI API。**

### P0 要做

- 检查所有原始设计文件是否齐全，运行 `node scripts/preflight.mjs`。
- 审计 `reference/architecture` 的 TypeScript 契约、8 类 JSON Schema 与 `reference/demo_storypack` 样例；重点处理 `docs/04_ADR_AND_GAPS.md` 列出的缺口。
- 初始化 Node.js LTS + TypeScript strict + Vitest + Ajv，生成可复现的 `package-lock.json`；加入必要的 ESLint 规则。
- 对剧情数据做 JSON Schema 和跨文件引用检查。已知局部未建模领域不得默默视为已实现。
- 建立 `docs/ADR.md` 和 `reports/P0_AUDIT.md`，将新增约束和设计取舍记录下来。

### P1 要做

1. 无 DOM 的 `@aifate/engine` 包：`GameState`、`GameEvent`、`Effect`、`Condition`、`ActionProposal` 和只读 `StoryDefinition`。
2. 条件 DSL：`all/any/not/flag_eq/fact_known/actor_alive/event_occurred/task_state/relation_gte/story_time_gte`，未知操作拒绝，递归深度和引用环受控。
3. 纯函数 reducer：事件应用、状态版本、幂等键、知识授予、角色状态、关系更新、锁定/解锁场景。
4. 任务状态机：locked→available→active→succeeded/failed/cancelled，前置、成功、失败、截止时间和一次性副作用。
5. 命运引擎：作者原著事件是参考候选，不是必须发生；可取消未触发事件，后续依赖必须重新求值；已发生事件不能被静默删改。
6. 确定性调度：可注入时钟、seeded PRNG、同一时间顺序、重复执行保护、预算边界；与网络时钟脱钩。
7. Actor 知识投影：不同角色看到的事实严格隔离；玩家文本/模型叙述不能被当作世界真相。
8. 白名单行动提议校验，可信剧情事件及 FakeModel；至少能演示救援成功、营救失败、恰在截止时间无法营救三种路径。
9. 事件重放、内存快照与存档接口原型；为未来 IndexedDB/ZIP 导入留清晰的适配边界。
10. 运行真实单测/集成测试和覆盖率，修复不通过的用例。

### 必须证明的系统性质

- 玩家在第 119 分钟前完成合法救援 → 原著第 120 分钟死亡事件取消；叶宁存活，死后依赖链不再错误触发。
- 玩家未营救，第 120 分钟事件条件成立 → 叶宁死亡，救援任务失败。
- 玩家第 120 分钟才提出救援，即使 AI 声称“救出了”，也不能改写已经到期的事件。
- 未掌握研究室位置时，角色上下文不包含研究室秘密；其他 NPC 的私人秘密也不会泄漏给主角。
- 相同初始状态、输入事件、seed 和时钟得到相同最终状态哈希；重复事件不产生二次奖励。
- 无许可证、无凭证、无真实模型，以上测试也可以在本地跑通。

### 交付文件

- 经过实现的 `packages/engine/src/` 和测试；项目 README、示例运行命令。
- `package-lock.json` 和 TypeScript/lint/test 配置。
- `docs/ADR.md`（发现的问题、决定、取舍和兼容性影响）。
- `reports/P0_AUDIT.md`、`reports/P1_QA.md`（实际执行命令、成功/失败统计、覆盖率、已知问题）。
- `npm run demo:p1` 可演示至少两条不同命运路径（需由你创建此脚本）。

### 不要做

- 不先开发手机聊天 UI、语音/图像、真实 API 连接、用户账号、后端服务或付费系统。
- 不把 `fixtures/p1_scenarios.json` 当成已经执行的测试结果。
- 不把所有模型输出直接当成 GameEvent。
- 不私自上传云盘、公开代码或购买服务。
- 不用 `skip` 隐藏尚未通过的测试。

若开发遇到可解决的编译或测试问题，请在本次任务内继续修复，不要把尚未运行的工作标成完成。最后给出源代码位置、可运行命令和 P0/P1 Gate 是否通过。
