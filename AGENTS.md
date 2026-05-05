# AGENTS.md

This file provides context for AI coding assistants (Claude Code, Codex, GitHub Copilot, etc.) working with this repository.

## 项目背景

Photograph Workflow 是一个面向个人摄影工作流的照片文件管理项目。

当前交付目标：

- 使用 `uv` 管理的 Python 脚本。
- 提供本地 Web UI 作为开发调试和未来桌面包装的前端基础，复用 Python application 层和结构化计划对象；它不是面向用户的浏览器产品版本。
- 支持本地 RAW/DNG 扫描、元数据读取、批量重命名计划、重命名执行、回滚和归档计划。
- 当前版本以 Lightroom 工作流中的 sidecar 行为为主。
- 当前没有桌面包装 App、macOS 原生 App、iPad App 或 iPhone App，但核心设计必须为未来桌面端和移动端应用保留空间。

本项目以文档驱动开发。除非是非常明确的小型机械性修复，否则不要实现 PRD/TDD 中尚未描述的行为。

## 权威信息来源

阅读文档时按以下顺序：

1. `docs/prd/README.md`：产品概览、范围、工作流和文档索引。
2. `docs/tdd/README.md`：技术设计索引，架构、数据契约、实现边界和测试。
3. `docs/ux/README.md`：桌面 App、iPad App、iPhone App 的可视化 UX 原型、界面结构和用户流。
4. 已存在的源码和测试。

文档职责：

- PRD 描述工具要做什么、用户可见规则、产品边界和预期工作流。
- TDD 描述工具如何构建，包括架构、Pydantic 模型、端口、适配器、计划对象、错误码和测试。
- UX 描述界面如何组织信息、引导用户操作、展示状态和降低误操作风险。
- 源码必须遵守 PRD 和 TDD。如果源码需要新增文档中没有覆盖的行为，应先更新文档，或在同一次变更中同步更新文档。
- `AGENTS.md` 描述这个仓库的开发流程和协作规则。

## 开发工作流程

个人开发者从需求到落地时，使用以下流程。

### 1. 澄清需求

修改代码前，先判断请求类型：

- 产品行为变更：先更新 PRD。
- 技术设计变更：先更新 TDD。
- 实现已有文档：按照 PRD/TDD 落地。
- Bug 或不一致：先检查 PRD、TDD、代码和测试，再修改行为。

如果需求存在歧义，优先把待决策内容记录到 review 文档中，不要直接猜测。临时 review 文档可以用于记录未解决的决策；当所有条目都已解决并写入 PRD/TDD 后，应删除对应 review 文档。

### 2. 更新 PRD

当变更影响以下内容时，需要更新 PRD：

- 用户工作流。
- 命名规则。
- 元数据行为。
- sidecar 行为。
- 归档行为。
- 支持或不支持的产品范围。
- 未来产品方向。

PRD 应保持产品视角。除非是必要的产品约束，否则不要在 PRD 中写具体 Python 实现细节。新增 PRD 文档时，需要在 `docs/prd/README.md` 中加入索引。

### 3. 更新 TDD

当变更影响以下内容时，需要更新 TDD：

- 模块边界。
- Pydantic 数据契约。
- `.metadata.json` schema。
- 计划对象、警告、错误或稳定错误码。
- 端口和适配器。
- 测试策略。
- 本地 Web UI、macOS、iPad、iPhone 或其他后期软件的扩展点。

当变更影响桌面 App、iPad App 或 iPhone App 的界面结构、导航、状态展示、确认流程或响应式布局时，需要同步更新 `docs/ux/`。

TDD 必须保持既有架构方向：

- `models` 定义稳定的结构化契约。
- `domain` 负责扫描、命名、sidecar 匹配、冲突检测和工作流规则。
- `application` 编排用例，并返回结构化计划。
- `ports` 定义外部能力接口。
- `adapters` 实现本地文件系统、ExifTool、ZIP、终端和 workspace 持久化等具体细节。
- `scripts` 只负责参数解析、调用 application 用例、确认执行和摘要展示。

### 4. 检查 PRD/TDD 一致性

实现前，检查 PRD 和 TDD 是否冲突：

- PRD 是否描述了 TDD 无法支持的行为？
- TDD 是否定义了 PRD 明确排除的能力？
- 字段名、默认值、模板规则和错误行为是否一致？
- 是否仍然满足未来扩展约束？
- 是否还残留旧决策、临时 review 记录或过期命名？

如果存在未解决的问题，应记录到 review 文档中，并在实现前暂停；除非用户明确要求先做 best-effort 修复。

### 5. 小步实现

除非有明确理由，否则按以下顺序实现：

1. 项目脚手架和 `pyproject.toml`。
2. Pydantic 模型、枚举和结构化计划对象。
3. 端口和 fake adapter。
4. domain 规则。
5. application 用例。
6. 本地 adapter。
7. 脚本入口。
8. 测试和 fixture 数据。

保持变更范围清晰。不要把无关的产品决策、重构和实现工作混在一次变更里，除非它们是同一个行为落地所必需的。

### 6. 验证

纯文档变更：

- 运行 `git diff --check`。
- 阅读变更过的 PRD/TDD 段落，确认术语一致。

实现变更：

- 每次代码修改后必须运行 `uvx ruff check .`。
- 每次代码修改后必须运行 `uv run pytest`。
- 运行变更区域的聚焦测试；如果已经包含在完整 pytest 中，可以不重复运行。
- 自动化测试优先使用 fake adapter 和 fixture 目录。
- 真实 ARW/DNG 文件只用于明确的 smoke test；不要提交私人照片文件。

### 7. 提交

只有在检查过工作区后再提交。

推荐提交信息风格：

- `docs: ...` 用于 PRD/TDD/AGENTS 等纯文档变更。
- `feat: ...` 用于新增用户可见行为。
- `fix: ...` 用于 bug 修复。
- `test: ...` 用于仅测试变更。
- `refactor: ...` 用于不改变行为的代码结构调整。

除非临时 review 文件是为了记录尚未解决的决策，否则不要提交它。所有条目都已解决并写入 PRD/TDD 后，应删除对应 review 文档。

## 仓库规则

- 搜索优先使用 `rg` 或 `rg --files`。
- 手动编辑文件时使用 `apply_patch`。
- 不要编辑或提交私人照片样本。
- 不要在测试或示例中修改 RAW/DNG 文件。
- 不要依赖 Lightroom catalog 内部结构。
- 不要把 EXIF 元数据写回 RAW/DNG 文件。
- JSON 字段名统一使用 `snake_case`。
- `.metadata.json` 必须保持 append-safe：一旦记录了 `original_name`，不得重写。
- 命名模板行为必须与 PRD 对齐：默认模板是 `{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}`。
- `{date}` 只能来自照片元数据。如果无法读取拍摄时间，应报错并且不执行重命名。
- sidecar 按与 RAW/DNG 相同 stem 匹配。当前 Lightroom profile 支持 `.xmp`、`.acr`、`.jpg` 和 `.jpeg`。
- 归档应把用户指定的目录作为整体打包，只应用默认或自定义排除规则。

## 个人开发循环

日常开发使用这个轻量循环：

1. 在 PRD 中写入或调整需求。
2. 将已确认的产品行为转换为 TDD。
3. 检查 PRD/TDD 一致性。
4. 实现一个垂直切片。
5. 新增或更新聚焦测试。
6. 运行验证。
7. 提交一个内聚的变更。

这个循环刻意保持轻量。本项目面向个人开发者，不需要重流程，但需要留下足够清晰的书面上下文，保证未来 App 版本可以复用同一套核心规则。
