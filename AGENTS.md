# Codex 项目工作指令（自动读取）

## 任务与优先级

你是本地 **AI 命运改写互动剧情游戏** 的实现工程师。当前仅完成 P0+P1。请在写代码前阅读：

1. `README_开始使用.md`；
2. `docs/00_PRODUCT_LOCKS.md` 和 `docs/01_P0_P1_REQUIREMENTS.md`；
3. `reference/architecture/01_MVP_技术规格_v1.0.md`、`reference/architecture/contracts/runtime.ts`；
4. `reference/architecture/schemas/` 全部八类 Schema、`reference/demo_storypack/` 全部 JSON；
5. `docs/02_ENGINE_SEMANTICS.md`、`docs/03_QA_ACCEPTANCE.md` 和 `docs/04_ADR_AND_GAPS.md`。

约束冲突时优先级：**本次用户明确产品决策 > `docs/00_PRODUCT_LOCKS.md` > 已执行证据与安全边界 > 本文件 / P0-P1 要求 > 原始设计规格 > DEMO 示例数据**。工程细节可以合理决策，所有兼容性、逻辑与验收偏差必须记入 `docs/ADR.md`，不得悄悄篡改资料。

## 必须遵守

- **持续执行 P0→P1**，除需要外部密钥/权限或会产生不可逆损失的真正阻塞事项外，无需反复确认。
- **本地优先、浏览器优先、PWA 最终产品、玩家 BYOK、无自建游戏后端**；但当前 P1 只做独立纯 TypeScript 引擎。
- 不引入 SillyTavern 运行时依赖；它仅是可选测试工具。
- 不使用外部真实收费模型测试；实现 `FakeModel` 或受控的固定响应，运行结果可重复。
- 不给 AI 模型修改权：模型生成 `ActionProposal`，**只有经过校验/裁定并提交的事件**才可改变世界。
- 不因玩家要求强制成功，也不因原著结果强制失败；所有成败来自已知世界事实、角色选择、行动规则和因果。
- 严格区分原著基准、世界客观事实、角色各自知识、状态与聊天文本；角色提示上下文绝不能直接注入未知秘密。
- NPC 及主角具有自己的目标、拒绝权与关系边界；高好感不等于自动同意。
- 先处理硬约束、后处理确定性带种子随机裁定，时间及重复提交必须有明确序列和幂等策略。
- 不执行剧情包携带的 JS/HTML/SVG，不用 `eval` 或 `new Function`。
- 不在代码、日志、单元测试和导出中插入真实 API Key。DEMO 数据全部虚构。
- 只在本地工作目录内工作；未经要求，不上传 Drive/GitHub、不推送公共仓库、不作部署，不发送数据给模型服务商。

## 完成顺序（不可跳跃）

1. P0：`node scripts/preflight.mjs`，审计原始契约和已知缺口，提出实施 ADR，建立工具链和可复现的 lockfile。
2. P1a：类型、条件 DSL、角色知识投影、状态 reducer、事件日志及幂等机制。
3. P1b：任务生命周期、命运基准裁定、事件取消/重评、调度边界、确定性重放。
4. P1c：行动提议白名单、可信动作来源、FakeModel、3 条剧情路径、失败与临界时刻测试。
5. 执行 lint/typecheck/tests/coverage，纠错直至真实通过；填写 `reports/P0_AUDIT.md` 和 `reports/P1_QA.md`，列出仍未完成的内容。

## Gate 与诚实报告

- P0：脚手架、锁文件、Schema 校验、引用审计、ADR 已提交。
- P1：≥30 条规则层集成测试，≥10 条命运改写回归测试，全部跑通；输出覆盖率和失败清单；同种子/同事件的重放哈希一致；救援成功与失败两条路径的因果链一致。
- 原始 6/6 资料校验只是 P0 参考，不计作游戏运行测试。
- 初始 `packages/engine/tests/P1_GATE.test.ts` **故意失败**，Codex 应在完成真实 P1 测试后删除/替换它；不能跳过或者 `test.skip` 使假绿。
- P2/P3/P4/P5 包括聊天 UI、真实 API、语音、PWA 和 IndexedDB 浏览器持久化，不在本次范围。

## 代码与交付要求

- TypeScript `strict`；纯函数状态更新优先；确定性时钟和可注入随机种子；无 DOM 的引擎主包。
- 约束 DSL 必须在未知操作码时拒绝，不得默认成功；所有关联 ID 检查失败都抛出可追踪错误。
- 所有破坏性数据迁移需要显式版本号与可回退步骤。
- 使用清楚的模块命名、结构化错误码、单一状态来源、事务或模拟事务原子操作。
- 交付源码、演示 CLI、测试、QA 报告、ADR 和 README；本次结束不需要重新打 ZIP，除非使用者要求。
