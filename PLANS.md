# PLANS.md

本文件定义 Photograph Workflow 项目的计划工作法。它参考 OpenAI Codex 最佳实践中的 “Plan first for difficult tasks” 原则：遇到复杂任务时，先让 Codex 形成清晰计划，再进入实现；对于长期任务，计划应当是自包含、可更新、可验证的执行文档。

参考来源：

- OpenAI Codex best practices: <https://developers.openai.com/codex/learn/best-practices#plan-first-for-difficult-tasks>
- OpenAI Cookbook ExecPlan guide: <https://developers.openai.com/cookbook/articles/codex_exec_plans>

## 什么时候需要计划

简单任务可以直接修改，例如：

- 修正文档错别字。
- 补充一个明确的小段落。
- 调整单个已确认字段名。
- 运行一次检查或提交当前修改。

以下任务必须先写计划：

- 新增或修改核心工作流行为。
- 修改 `.metadata.json`、批量输入 JSON、结构化计划或错误码。
- 新增扫描、重命名、回滚、归档、workspace 等用例。
- 修改架构边界、端口、适配器或测试策略。
- 同时影响 PRD、TDD 和实现的任务。
- 需要多步迁移、回滚策略或真实文件验收的任务。
- 存在多个可选方案，需要用户决策的任务。

## 计划文件位置

长期或复杂任务使用独立计划文件：

```text
plans/<YYYYMMDD>-<short-topic>.md
```

示例：

```text
plans/20260503-rename-core.md
plans/20260503-workspace-management.md
plans/20260503-archive-zip.md
```

如果只是当前对话内的小型计划，可以直接写在回复里，不必创建文件。

`plans/` 中的计划可以提交，但必须是仍有价值的执行记录。临时讨论、废弃决策或已完全吸收到 PRD/TDD 的 review 内容，应在完成后删除或归档说明。

## 计划与 PRD/TDD 的关系

计划不能替代 PRD/TDD。

- PRD 是产品行为的权威来源。
- TDD 是技术设计的权威来源。
- PLANS 是把一组已确认的需求和设计落地成具体工作的执行说明。

执行前的顺序：

1. 先确认 PRD 是否已经描述用户可见行为。
2. 再确认 TDD 是否已经描述数据契约、架构边界和测试策略。
3. 如果 PRD/TDD 缺失，先补文档，再写实现计划。
4. 如果 PRD/TDD 冲突，先生成 review 或决策记录，不直接实现。
5. 计划只引用已确认的 PRD/TDD 内容，不能私自新增产品行为。

## ExecPlan 格式

每个长期计划文件都应包含以下章节。

### 目标

用几句话说明完成后用户能做什么，或系统会具备什么能力。

要求：

- 面向结果，不只描述过程。
- 写清楚当前任务不做什么。
- 指向对应 PRD/TDD 文档。

### 背景

说明实现者必须知道的上下文。

应包含：

- 相关 PRD/TDD 链接。
- 当前仓库状态。
- 关键约束，例如不写 RAW/DNG 元数据、`{date}` 只来自照片元数据、`.metadata.json.original_name` 不可变。
- 与未来 Web、macOS、iOS 复用有关的边界。

### 决策

记录已经确认的决策。

写法：

```text
- 决策：归档按用户传入目录整体打包。
  原因：用户希望电脑端可手动控制归档粒度，工具不自动拆分。
  影响：archive 只应用 exclude，不主动识别导出成片。
```

如果存在未决问题，应放到“待确认问题”，不要混入已确认决策。

### 待确认问题

列出实现前必须由用户或维护者确认的问题。

每一项应写清：

- 问题是什么。
- 为什么会影响实现。
- 推荐选项是什么。
- 不确认时是否可以继续。

如果没有待确认问题，写“无”。

### 实施步骤

把任务拆成可以逐步完成的垂直切片。

建议顺序：

1. 更新或确认 PRD。
2. 更新或确认 TDD。
3. 定义模型和错误码。
4. 实现 domain 规则。
5. 实现 application 用例。
6. 实现 adapters。
7. 实现 scripts。
8. 添加测试。
9. 运行验证。

每一步都应有明确产物，例如文件路径、模型名、函数名或测试名。

### 验证方式

写清楚如何证明计划完成。

文档任务至少包含：

```text
git diff --check
```

实现任务应包含：

- 聚焦单元测试。
- 集成测试或 fixture 测试。
- 必要时的真实 ARW/DNG smoke test。
- 不提交私人照片文件的检查。

### 回滚与失败处理

说明出错时如何恢复。

必须覆盖：

- 是否会修改真实文件。
- 是否依赖 `.metadata.json` 回滚。
- 中途失败时状态如何记录。
- 用户需要如何重新 dry-run。

纯文档计划可写“只修改文档，可通过 git diff 或 revert 回退”。

### 进度记录

计划是活文档。执行时应持续更新进度，而不是完成后一次性补写。

推荐格式：

```text
- [x] PRD 已确认
- [x] TDD 已确认
- [ ] 模型实现
- [ ] domain 规则实现
- [ ] 测试补齐
```

### 结果

完成后记录：

- 实际改了什么。
- 验证命令和结果。
- 剩余风险。
- 后续任务。

## 执行规则

执行计划时遵守以下规则：

- 不要在没有更新 PRD/TDD 的情况下实现新行为。
- 不要把业务规则写进 `scripts/`。
- 不要让 UI 或脚本解析人类可读文本来理解计划结果。
- 不要把 ExifTool、文件系统、ZIP 或终端交互直接写进 domain。
- 不要修改 RAW/DNG 内容或写入 RAW/DNG 元数据。
- 不要提交真实私人照片文件。
- 不要自动删除或重建 `.metadata.json.files` 中已有条目。
- 每次实际改文件的能力都必须先支持 dry-run。

## 与 Codex 协作方式

复杂任务开始时，优先这样请求：

```text
请先阅读 PRD/TDD，生成 plans/YYYYMMDD-topic.md，不要实现。
```

确认计划后，再请求：

```text
按照 plans/YYYYMMDD-topic.md 实现，持续更新计划进度。
```

如果中途发现 PRD/TDD 冲突，Codex 应暂停实现，更新计划中的“待确认问题”或生成 review 文档，让用户先决策。

如果任务已经很明确，可以直接请求：

```text
按照现有 PRD/TDD 实现 rename dry-run 的第一步，并补测试。
```

此时 Codex 仍应在开始前快速确认涉及的 PRD/TDD 章节。

## 计划模板

复制以下模板创建新计划：

```markdown
# <计划标题>

## 目标

<完成后用户或系统获得什么能力。>

## 背景

- PRD：
- TDD：
- 当前仓库状态：
- 关键约束：

## 决策

- 决策：
  原因：
  影响：

## 待确认问题

无。

## 实施步骤

- [ ] 更新或确认 PRD。
- [ ] 更新或确认 TDD。
- [ ] 实现模型和错误码。
- [ ] 实现 domain 规则。
- [ ] 实现 application 用例。
- [ ] 实现 adapters。
- [ ] 实现 scripts。
- [ ] 添加测试。
- [ ] 运行验证。

## 验证方式

- `git diff --check`
- `<focused test command>`
- `<full test command if practical>`

## 回滚与失败处理

<说明如何撤销、如何恢复状态、是否会影响真实照片文件。>

## 进度记录

- [ ] 尚未开始。

## 结果

<完成后填写。>
```

## 当前项目进度

更新时间：2026-05-06。

当前仓库已经完成第一版 Python 核心能力、脚本入口、本地 Web UI、Tauri 桌面包装基础和桌面/iPad/iPhone UX 原型。后续开发者不需要从项目脚手架开始，应先阅读本节，再进入具体计划文件。

权威上下文：

- PRD 入口：`docs/prd/README.md`
- TDD 入口：`docs/tdd/README.md`
- UX 入口：`docs/ux/README.md`
- 当前版本实现计划：`plans/20260504-current-version-implementation.md`
- 开发协作规则：`AGENTS.md`

最近关键提交：

- `9f393df feat: redesign desktop app UX with 6-stage journey and 5 themes`
- `4185308 docs: 重构 UX 目录树预览与辅助页面`
- `e010cbe docs: add app ux journey prototype`
- `7cb3e4d feat: add Tauri desktop wrapper app with native directory picker`

### 已完成

- Python 项目使用 `uv` 管理，`pyproject.toml` 已设为 Python `>=3.12`。
- `src/photograph_workflow` 已按 TDD 分层实现：
  - `models`：Pydantic 数据契约。
  - `domain`：扫描、命名模板、sidecar、冲突、metadata、归档规则。
  - `application`：scan、rename、rollback、archive、archive_name、workspace 用例。
  - `ports`：文件系统、元数据读取、归档、确认、workspace 等外部能力接口。
  - `adapters`：本地文件系统、ExifTool/exifread、ZIP、终端、XDG workspace。
- `scripts/` 已提供当前脚本入口：
  - `scan.py`
  - `rename.py`
  - `rollback.py`
  - `archive.py`
  - `archive_name.py`
  - `workspace.py`
- 测试已覆盖核心规则：
  - `tests/test_domain.py`
  - `tests/test_rename_rollback.py`
  - `tests/test_archive_workspace.py`
- 本地 Web UI 已存在：
  - 后端：`apps/web/backend/server.py`
  - 前端：`apps/web/frontend`
  - Docker 入口：`Dockerfile`、`docker-compose.yml`
  - 默认前端访问端口：`51173`
- Tauri 桌面包装 App 已存在：
  - 入口：`apps/desktop`
  - Rust/Tauri 后端：`apps/desktop/src-tauri`
  - Vue 桌面前端：`apps/desktop/src`
  - 已包含原生目录选择器、工作流侧栏、设置页、安全中心、目录树组件和主题系统。
- UX 文档和静态原型已更新：
  - 桌面 / iPad / iPhone 三种应用形态。
  - 六阶段工作流：准备项目、检查素材、命名规则、执行重命名、Lightroom 后期、归档。
  - 桌面左下角设置和安全中心辅助入口。
  - 重命名预览按目录树展开，不使用扁平长列表。
  - 顶部可切换多套主题配色。

### 当前验证基线

代码变更后至少运行：

```text
uvx ruff check .
uv run pytest
```

UX 静态原型变更后至少运行：

```text
node --check =(sed -n '/<script>/,/<\\/script>/p' docs/ux/prototype/index.html | sed '1d;$d')
git diff --check
```

桌面前端变更后至少运行：

```text
cd apps/desktop
npm run build
```

Web 前端变更后至少运行：

```text
cd apps/web/frontend
npm run build
```

真实 RAW/DNG 验收规则：

- 真实目录 `~/20260501-「旅游」重庆` 只能用于只读 smoke test。
- 不要直接对真实目录执行 rename、rollback、archive 或写入 `.metadata.json`。
- 需要可写验收时，只复制少量样本到 `./tmp`。
- 复制前必须确认复制后系统仍至少保留 `30GB` 可用空间。
- 不提交任何私人照片、真实 RAW/DNG 或从真实照片派生出的样本文件。

### 当前未完成或需继续打磨

- 桌面 App 仍处于开发阶段，Tauri 包装和 Vue 桌面 UI 已存在，但还需要继续和 Python application 层做端到端联调。
- Web UI 是开发调试和桌面包装前端基础，不是面向用户的浏览器产品形态；不要继续把浏览器目录选择当成核心产品能力。
- UX 静态原型已经表达目标体验，但真实 `apps/desktop` UI 需要持续对齐 `docs/ux/prototype/index.html`。
- 真实 ExifTool 二进制路径仍不是强依赖；当前支持 ExifTool 优先、`exifread` fallback。后续如果要强化元数据兼容性，需要新增专门计划。
- 还没有 iPad/iPhone 原生 App 实现；当前只有 UX 设计和多平台架构预留。
- 当前只支持 Lightroom 相关 sidecar 行为；Capture One 等后期软件仍属于未来扩展。

### 下一批推荐计划

后续进入实现时，建议按以下顺序创建或更新计划：

1. `plans/<date>-desktop-python-integration.md`：把 Tauri 桌面 App 的目录选择、扫描、重命名预演、执行、回滚、归档完整接入 Python application/API 层。
2. `plans/<date>-desktop-ux-parity.md`：让 `apps/desktop` 真实界面对齐 `docs/ux/prototype/index.html`，尤其是目录树预览、设置页、安全中心、主题切换和阶段反馈。
3. `plans/<date>-api-contract-hardening.md`：稳定 Web/Tauri 调用的 API 响应模型，避免前端解析人类可读文本。
4. `plans/<date>-metadata-compatibility.md`：扩展真实 ARW/DNG 元数据 smoke test，明确 ExifTool 与 `exifread` fallback 的边界和错误提示。
5. `plans/<date>-desktop-packaging.md`：梳理 macOS `.app` 打包、Python 后端携带方式、首次启动、端口占用、日志和错误上报。
6. `plans/<date>-ios-ipad-spike.md`：只做技术 spike，验证 SwiftUI/iOS 如何复用核心规则或远期共享数据契约，不进入完整产品实现。
7. `plans/<date>-postprocessor-extension.md`：在 Lightroom 稳定后，再设计 Capture One 等后期软件 profile 扩展。

### 接手建议

接手开发时按这个顺序确认状态：

1. 运行 `git status --short`，确认是否有未提交修改。
2. 阅读 `docs/prd/README.md`、`docs/tdd/README.md`、`docs/ux/README.md`。
3. 阅读 `plans/20260504-current-version-implementation.md` 的“结果”和“未覆盖项”。
4. 根据任务类型创建新的 `plans/<date>-<topic>.md`，不要把新实现计划直接写进本文件。
5. 实现时持续更新对应计划的进度记录。
