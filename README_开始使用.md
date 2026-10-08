# AI Fate｜交给本地 Codex 的开发交接包

**版本：** 1.0.0 · **日期：** 2026-10-08  
**用途：** 本地 Codex 连续执行 P0 工程准备和 P1 确定性剧情引擎开发。  
**状态：** Codex-ready 交接资料 + 初始工程骨架；**不是已经完成的 P1 引擎，也不是可玩的 PWA。**

## 1. 用法（Windows / Ubuntu / macOS）

1. 把本 ZIP 完整解压到一个没有中文空格也可以正常工作的开发目录，例如 `D:\Projects\AI-Fate` 或 `~/projects/ai-fate`。不要只解压其中一个 ZIP。
2. 打开终端，进入包含 `AGENTS.md` 和 `package.json` 的根目录。
3. 执行 `node scripts/preflight.mjs`。要求 Node.js 22 LTS 或更新的受支持版本；该预检不需要安装 npm 依赖。
4. 用 **Codex App** 打开整个项目根目录，或者在该根目录启动 Codex CLI：`codex`。
5. 在 Codex 里提交这句话：`请阅读根目录 AGENTS.md 和 CODEX_START_HERE.md，按照 P0→P1 顺序连续开发，实际运行测试并交付报告。不要进入 P2。`
6. 按照 `CODEX_START_HERE.md` 的交付 Gate 检查成果，**不把资料校验通过误认为引擎已完成**。

CLI 的安装与登录由用户自行完成；包内不含模型 API Key，不需要安装酒馆。

## 2. 文件导航

| 文件/目录 | 目的 |
|---|---|
| `AGENTS.md` | 给 Codex 的持续工程约束与优先级，最先阅读 |
| `CODEX_START_HERE.md` | 一次性 P0/P1 开发任务，直接交给 Codex |
| `docs/00_PRODUCT_LOCKS.md` | 已经确定、不能擅自改变的产品原则 |
| `docs/01_P0_P1_REQUIREMENTS.md` | 两阶段交付范围与排除事项 |
| `docs/02_ENGINE_SEMANTICS.md` | 世界事实、任务、命运、时序、重放的规范 |
| `docs/03_QA_ACCEPTANCE.md` | P0/P1 验收用例与失败判定 |
| `docs/04_ADR_AND_GAPS.md` | 既有资料缺口与决策待办 |
| `docs/05_SECURITY_AND_STAGE_BOUNDARIES.md` | 信任边界、密钥、版权及后续阶段范围 |
| `fixtures/p1_scenarios.json` | 设计级测试输入，预期成功/失败/临界行为（不是运行结果） |
| `reference/architecture/` | 完整且未修改的上版架构规格、TS 契约、八类 Schema 和 QA |
| `reference/demo_storypack/` | 原创虚构 DEMO 的 8 个 JSON 文件和原始 ZIP |
| `packages/engine/` | **空白 P1 工程骨架**，由 Codex 实施 |
| `reports/` | Codex 必须填写的审计报告和 QA 结果模板 |
| `HANDOFF_MANIFEST.json` | 本交接 ZIP 所含文件的 SHA-256 检查清单 |

## 3. 验证命令

```bash
node scripts/preflight.mjs
npm install
npm run typecheck
npm run test:p1
```

- `preflight` 应当通过，说明**资料完整、JSON 可解析、交接清单一致**。
- `typecheck` 在初始骨架阶段可以通过，不代表实现完成。
- `test:p1` **初始状态故意失败**；只有 Codex 实现真实引擎并以有效的测试替换占位失败测试后，才可以通过验收。
- `npm install` 需要网络以获取开发依赖。没有网络时可以先执行预检和只阅读资料，不准伪称依赖安装及测试已通过。

## 4. 与原架构包的关系

`reference/architecture/` 来源于《AI_Fate_MVP_v1.0_Architecture_Design》，此包不修改原规格。发现矛盾时先记到 `docs/ADR.md`，必要时修正实施侧契约和样例，再记录破坏兼容性的变更与迁移，不得静默改变既定产品原则。

**首轮唯一目标：** 以可验证的世界状态、事件日志、任务判定与命运演化证明“玩家的建议可能改变、也可能无法改变原著命运”。
