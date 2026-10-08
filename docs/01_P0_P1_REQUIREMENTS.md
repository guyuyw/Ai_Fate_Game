# P0 / P1 实施范围、接口和通过标准

## P0：将设计交接转化为可编译工程

### 必须交付

- 单一 Node.js LTS + npm 工作区；根目录 `package.json`、锁文件、`tsconfig.json`、测试和 lint 工具链，避免脱离项目的散落脚本。
- `reference/architecture` 和 `reference/demo_storypack` 保持只读的设计来源；新增真正的运行实现放在 `packages/engine`。
- Ajv draft-07 对**全部八类**定义和 Demo 样例进行验证；针对作者包字段、ID、条件/效果引用执行跨文件完整性检查。
- 设计审计，明确数据与实现冲突及 ADR；**不得假设原 Demo 已包含完整场景可操作行动**。
- 允许 `npm run preflight`、`npm run typecheck`、`npm run test:p1`、`npm run test:coverage` 等可运行命令；完成时必须有审计报告。

### P0 Gate

- 参考文件完整；Json Schema、引用与坏数据负例检查真实通过。
- TypeScript strict 完整通过；能够不接入云端模型运行测试。
- 所有合同差异已经进入 ADR，不能用删字段或跳过 Schema 来隐藏不一致。

## P1：确定性本地游戏核心引擎

### 必须模块

1. **StoryDefinition Loader**：将校验过的 `manifest/world/characters/roles/scenes/tasks/fate/opening` 构建为内存只读故事定义，区分 authored truths 和某局世界状态。
2. **GameState Factory**：由包、身份和 seed 生成独立的游戏局；确保不同用户存档互不干扰。
3. **Condition DSL Interpreter**：实现所有既有操作码；未知操作、无效 ID、无限递归必须返回明确错误。
4. **Effect Validator / Reducer**：实现八类已约定效果，约束人物、事实、任务与场景 ID；更新状态纯函数化。
5. **Task Evaluator**：`locked/available/active/succeeded/failed/cancelled`；条件变化触发任务重新评估；完成/失败后仅触发一次相应效果；禁止循环重入。
6. **Fate Reconciler**：跟踪原著基准事件候选、是否到期、是否取消、是否完成，已发生事件不得逆向删改。
7. **Event Log / Idempotency**：事件 ID 和幂等键唯一；含因果指针，支持重放恢复和稳定摘要。
8. **Deterministic Scheduler**：注入时钟和 seed，明确时序冲突、同时事件优先级、补算窗口与预算边界。
9. **Actor Knowledge View**：仅可见事实、可观察场景、可获知任务；不同人物知识隔离测试。
10. **Proposal Validator + FakeModel**：对白提议来自模型但不直接修改世界；行动必须合法且能被本地引擎裁定。
11. **In-memory Repository + Snapshot**：具备原子更新语义的内存实现、快照/恢复接口；IndexedDB 和浏览器 ZIP Save 可在 P4 实现。
12. **CLI DEMO**：分别运行成功、失败、截止临界场景并输出可审核的事件序列与终态。

### 主体调用协议（建议，允许 ADR 确定具体命名）

```ts
// P1 实际代码应以实现后的 types 为准。
loadStory(files: Record<string, unknown>): StoryDefinition;
createRun(story: StoryDefinition, identityId: string, seed: string): GameState;
evaluateCondition(rule: Condition, state: GameState): boolean;
validateProposal(proposal: ActionProposal, state: GameState, story: StoryDefinition): Verdict;
applyCommittedEvent(state: GameState, event: GameEvent, story: StoryDefinition): GameState;
evaluateTasks(state: GameState, story: StoryDefinition): { next: GameState; events: GameEvent[] };
reconcileFate(state: GameState, story: StoryDefinition): { next: GameState; events: GameEvent[] };
advanceTo(state: GameState, targetStoryMinute: number): GameState;
replay(initial: GameState, events: GameEvent[]): GameState;
projectActorView(story: StoryDefinition, state: GameState, actorId: string): ActorPromptContext;
```

不得让 `ActionProposal` 或 `ChatMessage` 拥有写世界事实的权限；只有验证后的 `GameEvent` 包含 Effect。

### P1 Gate

- ≥30 条规则层集成测试 + ≥10 条命运演化回归测试，**全部真实执行且通过**。
- 成功/失败/边界 3 条 DEMO 路径展示行为与事件，至少两种不同合理结果。
- 同一输入状态、同一个 seed / clock、同一事件顺序，重放哈希严格一致。
- 禁止提前泄露秘密、非法写状态、重复奖励与已经失效的原著事件复活。
- 关键 reducer 与条件 DSL 分支覆盖率目标 ≥90%，测试报告提供真实覆盖数据；若不达标，不得宣称 Gate 已通过。

## 后续阶段（不在本次交付范围）

- P2：聊天 UI、上下文编译、真实 LLM Connector。
- P3：玩家身份的 UI、图像与语音。
- P4：完整浏览器 PWA、ZIP 导入、Dexie/IndexedDB、真实存档导出/导入、on_resume UI。
- P5：真实小说故事单元和多设备端到端 QA。

**不要为了演示容易，而把尚未发生的未来剧情提早注入主角的提示词。**
