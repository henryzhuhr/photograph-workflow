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

## 当前项目的推荐首批计划

后续进入实现时，建议按以下顺序创建计划：

1. `plans/<date>-project-scaffold.md`：建立 uv/Python 项目结构、依赖和测试框架。
2. `plans/<date>-data-contracts.md`：实现 Pydantic 模型、枚举、计划对象和错误码。
3. `plans/<date>-scan-metadata.md`：实现扫描、ExifTool adapter、RAW/DNG 识别和 sidecar 匹配。
4. `plans/<date>-rename-dry-run.md`：实现模板解析、metadata 计划和冲突检测。
5. `plans/<date>-rename-execute-rollback.md`：实现真实 rename 和 rollback。
6. `plans/<date>-archive.md`：实现 archive_name、archive plan 和 ZIP 执行。
7. `plans/<date>-workspace.md`：实现 workspace 持久化和 `scripts/workspace.py`。
