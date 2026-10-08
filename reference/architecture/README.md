# AI 命运改写互动剧情游戏｜MVP 架构设计交付包

版本：v1.0（2026-10-08）

该 ZIP 是**技术设计、接口和数据契约样例**，不是已经实现的 PWA 游戏。所有示例人物及案例数据均为虚构 DEMO。

## 内容

- `01_MVP_技术规格_v1.0.md`：正式设计规格（模块、引擎、时序、状态机、隐私、安全、实施顺序与 QA）
- `contracts/runtime.ts`：游戏核心接口及 TypeScript DTO 设计草案
- `schemas/*.schema.json`：8 类 JSON Schema（manifest、task、world、characters、player_roles、scenes、fate、opening）
- `examples/DEMO_midnight_hospital/`：可用于数据契约评审的非成品剧情包文件样例
- `qa/ACCEPTANCE_TESTS.md`：验收流程和用例矩阵
- `qa/VALIDATION_REPORT.md`：本包 JSON/Schema 的实际验证情况

## 工程使用建议

1. 阅读规格并冻结 v1.0 版数据规范。
2. 先实现无模型 `FakeModel` 与 reducer，确保事件重放、任务判定和命运重排有确定性。
3. 再接聊天 UI 和多模态 Adapter，避免模型输出直接篡改世界。
4. 对外发布前单独解决浏览器 BYOK 认证安全问题；不要把 API Key 写在发布包或存档中。
