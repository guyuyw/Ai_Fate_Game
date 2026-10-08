# P1 游戏引擎语义规范

## A. 四种独立数据域

1. `StoryDefinition`：**只读**作者原始资料和原著基准时间线；不是玩家当前局的事实真相。
2. `GameState`：一个玩家当前的权威运行投影；包含时钟、角色、任务、地点、关系、旗标、事件队列。
3. `GameEvent[]`：已被本地规则系统确认的不可变事件流；有 `id`, `idempotencyKey`, `causationId`, `storyMinute`, `effects` 和事件来源。
4. `ChatMessage[]`：展示与交互载体，不能自行变更前三种数据。

推荐纯函数：`reduce(state, event) => nextState`。计算前先结构校验和引用检查，不能提交半个事件；只有持久化成功才允许 UI 宣布不可逆成功。可先在内存实现事务语义，浏览器存储后续接入。

## B. 条件表达式 DSL

应与原始 `contracts/runtime.ts` 和 `schemas/task.schema.json` 严格对应：

| 操作码 | 语义 |
|---|---|
| `all` / `any` | 短路求值，空 `all=[]` 为 true，空 `any=[]` 为 false |
| `not` | 布尔取反 |
| `flag_eq` | 严格类型和值比较，不进行字符串数字自动转换 |
| `fact_known` | 仅检查目标角色已授权/经历得知的 fact ID |
| `actor_alive` | 检查当前生死状态 |
| `event_occurred` | 检查已提交权威事件，非模型文字 |
| `task_state` | 检查状态机的真实状态 |
| `relation_gte` | 比较指定方向的关系维度（非对称） |
| `story_time_gte` | 叙事分钟整数比较 |

不认识的 op 一律拒绝；递归深度、数组节点数、ID 长度都需资源限额。不允许函数、JS 表达式、外部 URL 直接进入规则 DSL。

## C. 可信与不可信事件来源

- `authored_scheduled`：作者编写、按规则到期的剧情事件。
- `adjudicated_action`：模型提出动作，裁定引擎批准后产生的事件。
- `authorized_system`：已由身份权限验证且剧情包允许的特权效果。
- `test_fixture`：**测试专用**，用于在缺少完整行动编排的 DEMO 中注入规定的权威事件（生产环境禁止暴露该入口）。

必须明确证明：玩家消息、模型输出和描述性图片分析既不是 `Effect`，也不是 `GameEvent`。用户问“直接将目击者设为获救”不能绕过世界内授权条件。

## D. 任务状态机与最终条件

建议状态：`locked` 预置；前置成立→`available`；已接受任务→`active`；完成判定成立→`succeeded`；失败或错过最后期限→`failed`；被故事条件废止→`cancelled`。每个任务完成/失败效果**最多执行一次**。重复重算不应再奖励关系值。

允许由已授权内部事件驱动任务转换；不能直接通过玩家文本修改任务状态。若状态机发生循环、冲突、两个互斥终态应检测并拒绝或采用文档定义的优先级。完整任务依赖图需要环检测。

## E. 命运候选事件的生命周期

作者提供的 `referenceEventId` 可以处于 `scheduled / revoked / occurred / superseded` 等引擎内部状态。`cancelIf` 在触发前可取消候选；一旦 event 已 committed，不能“撤销历史”，只能通过后续独立补偿事件改动当前世界。补偿不等于旧事件没发生。

任务效果 `revoke_event` 的作用是**阻止尚未发生的事件候选**；若事件已经发生，必须以明确错误拒绝或记录无效操作，不能抹掉 `occurredEventIds`。

每次事实/任务/角色变化后重新评估候选事件及其依赖。原著“角色死亡”的后果不应在其被救后继续触发。

## F. 时间边界

- 时间为离散故事分钟；时间单调增加，不允许无审计的倒退。
- `deadlineMinute=120` 的营救必须在 `<120` 产生权威成功事实。事件到期时优先结算先前已提交的行动、再结算到期 fate、最后处理同一时刻才来的新请求。
- 事件每次应用都校验 `storyMinute` 与当前时钟；确立稳定的排序键，例如 `(storyMinute, phase, priority, eventId)`。
- 长时间 `advanceTo` 应考虑事件预算并可分段恢复；禁止死循环或无上限模型调用。
- 随机结果用注入 seed 的确定性 PRNG，不能在引擎深处直接读取 `Math.random()`、`Date.now()` 作为裁定依据。

## G. 对话与角色知识

- `KnowledgeProjection` 只取当前 actor 已知事实及合法可见场景，不包含全量 `world.facts`。
- 针对 `char.lin` 的提示词不能携带 `char.chen` 独占的 `fact.source_of_fog`。
- 模型叙述“我看到了 XX”只是待验证文本；只有 `inspect()` 对真实可调查对象成功后才能提交 `grant_fact`。
- NPC 对于攻略/信任不设单一阈值自动同意。关系变化需由发生的行动和 NPC 选择触发。

## H. 保守复用现有 DEMO

既有 `reference/demo_storypack` 包含人物、事实、任务与命运候选，但**没有完整的地点邻接、对象交互、救援动作和开放式对白剧情脚本**。P1 可以用 `fixtures/p1_scenarios.json` 的 `test_fixture` 已授权事件测试状态/任务/命运；**不得宣称**已经实现完整可玩案件或自动从玩家任意文字中推理出救援成功。

要做到端到端操作后达成救援，需设计可校验的场景互动规则或 ActionOutcomeSpec；若本次扩展故事包 Schema，必须在 ADR 记录兼容性和版本影响。
