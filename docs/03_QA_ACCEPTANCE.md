# P0/P1 QA 清单和实际验收规则

## P0

- [ ] QA-P0-01 完整资料路径、哈希与 ZIP 校验一致。
- [ ] QA-P0-02 八类 Schema 均通过有效样例，并拒绝关键负例。
- [ ] QA-P0-03 Demo 人物、任务、地点、事件、事实 ID 引用无悬空。
- [ ] QA-P0-04 TypeScript strict 编译无错。
- [ ] QA-P0-05 依赖 lockfile、入口命令、ADR 与本地运行说明齐全。

## P1：规则层核心集成测试（至少 30 条）

下面提供 32 条具体测试目标，可以拆成多个 Vitest 文件，但不可仅以伪数据或 `expect(true).toBe(true)` 填数。

| ID | 测试 |
|---|---|
| CORE-01 | 相同种子创建同样初始 GameState |
| CORE-02 | 不同 runId 状态独立，不发生对象引用串改 |
| CORE-03 | `all([])` 返回 true |
| CORE-04 | `any([])` 返回 false |
| CORE-05 | `not` 正确求反 |
| CORE-06 | `flag_eq` 不隐式转换数字/字符串 |
| CORE-07 | `fact_known` 只读目标 actor 的知识 |
| CORE-08 | `actor_alive` 与状态一致 |
| CORE-09 | `event_occurred` 忽略仅在聊天中出现的词 |
| CORE-10 | `task_state` 对锁定/激活/完成正确求值 |
| CORE-11 | `relation_gte` 有方向性，不自动对称 |
| CORE-12 | `story_time_gte` 临界时刻正确 |
| CORE-13 | 未知操作码拒绝、不得返回默认 true |
| CORE-14 | 嵌套超过上限时安全失败 |
| CORE-15 | 非法 actor / fact 引用被拒绝 |
| CORE-16 | 未授权 `grant_fact` 不能通过模型自由文本执行 |
| CORE-17 | `grant_fact` 重复执行不导致重复记录 |
| CORE-18 | `relation_delta` 重复事件不产生双重加分 |
| CORE-19 | `unlock_scene` 更新可达性且幂等 |
| CORE-20 | `schedule_event` 重复注册处理明确 |
| CORE-21 | `revoke_event` 禁止未来事件正确触发 |
| CORE-22 | `revoke_event` 不能删除已经发生事件 |
| CORE-23 | 任务前置不成立保持 locked |
| CORE-24 | 任务满足前置后进入 available/active |
| CORE-25 | 成功条件只有在事实确认后成立 |
| CORE-26 | 失败任务不会再奖励成功效果 |
| CORE-27 | 同条件重复重算不会执行副作用两次 |
| CORE-28 | 无效 proposal 被校验拒绝 |
| CORE-29 | 相同 idempotencyKey 只生效一次 |
| CORE-30 | 同样事件序列 replay 的终态与摘要相同 |
| CORE-31 | 多角色知识投影不泄露他人私密事实 |
| CORE-32 | 时间倒退/同刻冲突按照规范拒绝或定序 |

## P1：命运回归（至少 10 条）

| ID | 测试 |
|---|---|
| FATE-01 | 119 分钟完成合法救援、120 分钟不会再死亡 |
| FATE-02 | 无救援、120 分钟按条件死亡 |
| FATE-03 | 120 分钟才提出救援，不阻断截止事件 |
| FATE-04 | 救援成功令死亡依赖后续事件失效 |
| FATE-05 | 失败路径救援任务转 failed，成功奖励不触发 |
| FATE-06 | 成功路径关系奖励只发生一次 |
| FATE-07 | cancelIf 条件不成立，不能随意取消原著候选 |
| FATE-08 | 基准事件发生后，补偿事件不删除历史 |
| FATE-09 | 连续三次 reconcileFate 对同状态幂等 |
| FATE-10 | 不同建议/状态产生两种因果合理的结局，seed 可复现 |

### 演示 CLI 必须输出

`npm run demo:p1`（由 Codex 实现）应逐场景打印：seed、故事分钟、已提交事件 ID、角色生死、任务状态、未来命运队列、状态摘要、哪些条件阻断了或导致了原著事件。输出不能仅是模型编造的结局文字。

## 源码覆盖率

**目标：** core reducer + condition DSL 分支覆盖率 ≥90%，真实报告中写明统计范围及忽略文件。仅统计本地规则核心，不用跑一次 Python 资料校验来充当规则引擎覆盖率。

## 不在 P1 的正式验收范围

- PWA 手机页面、IndexedDB 真机、图片识别、语音、Safari 兼容、浏览器 API Key 安全解决方案。
- ZIP 导入器至少 10 条恶意包负例、浏览器故障恢复测试属于后续 P4；P0 需要基本数据/Schema 错误负例，但不宣称实现 P4 导入安全。

## 诚实报告

每条测试必须有源代码和实际执行结果。若无法安装依赖或者环境阻塞，标明 `BLOCKED` 而非通过。原有 `reference/architecture/qa/VALIDATION_REPORT.md` 只证明设计资料可解析。
