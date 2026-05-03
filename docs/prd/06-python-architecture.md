# Python 技术架构设计

## 技术决策

项目使用 Python 实现，并用 uv 管理项目环境。当前版本交付可直接执行的 `.py` 脚本，不要求安装成系统 CLI。

原因：

- 文件系统扫描、重命名、压缩、JSON 记录都适合 Python 标准库。
- ExifTool 可以通过 `subprocess` 调用，并以 JSON 作为稳定接口。
- 需要扩展桌面界面、TUI、系统 CLI 或自动化脚本时，Python 生态更贴近本地照片工作流。

长期方向上，当前脚本能力可能被电脑 Web 端、macOS 端和 iOS 端应用复用。因此当前实现必须把业务核心和脚本入口分离，避免把核心能力写成只能在终端交互中工作的流程。

## 多端扩展架构原则

当前版本只交付 Python 脚本，但核心模块需要满足以下原则：

- 核心模块只接收结构化输入并返回结构化结果，脚本文本输出只是其中一种展示方式。
- dry-run 计划、错误列表、冲突列表、metadata 更新计划和归档计划都应有可序列化的数据结构。
- 扫描、命名、校验、回滚和归档逻辑不能直接依赖 `argparse`、终端输入或终端颜色。
- 文件系统访问、ExifTool 调用、用户确认、进度展示和日志输出应有清晰边界，便于未来替换为 Web、macOS 或 iOS 的实现。
- `.metadata.json` 是跨端共享的数据契约，字段命名、状态流转和兼容策略必须稳定。
- 当前版本不实现网络服务、桌面窗口或移动端界面；只保留可扩展边界。

## uv 项目管理

项目使用 uv 管理 Python 版本、依赖和执行环境。

仓库应以 `pyproject.toml` 和 `uv.lock` 作为 Python 项目管理入口。现有 `package.json` 不作为当前版本的项目管理依据；如果没有前端或 Node 工具链需求，可以删除或标记为历史遗留。

推荐执行方式：

```text
uv run python scripts/scan.py <project-dir>
uv run python scripts/rename.py <project-dir> --dry-run
uv run python scripts/archive.py <project-dir> --dry-run
```

原则：

- 当前版本不要求 `pip install -e .` 后生成系统命令。
- 脚本可以直接执行，便于用户按本地工作流调用。
- 公共逻辑仍放在 `src/photograph_workflow/`，避免脚本之间复制代码。
- `scripts/` 只做参数解析、用户确认、摘要展示和调用业务模块。

## Python 版本

仓库当前 `pyproject.toml` 已声明 Python 项目。

建议版本策略：

- 当前版本代码优先兼容 Python 3.12+。
- 如果继续保留 `requires-python = ">=3.14"`，需要确认用户本机和 CI 都有 Python 3.14。
- 不依赖 Python 3.14 独有特性，避免后续使用门槛过高。

## 包结构

建议源码结构：

```text
.
├── scripts
│   ├── scan.py
│   ├── rename.py
│   ├── rollback.py
│   ├── archive.py
│   └── archive_name.py
├── src
│   └── photograph_workflow
│       ├── __init__.py
│       ├── config.py
│       ├── dirs.py
│       ├── scanner.py
│       ├── extensions.py
│       ├── metadata
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── exiftool.py
│       ├── naming
│       │   ├── __init__.py
│       │   ├── template.py
│       │   └── sanitize.py
│       ├── planner
│       │   ├── __init__.py
│       │   ├── rename_plan.py
│       │   ├── archive_plan.py
│       │   └── rollback_plan.py
│       ├── operations
│       │   ├── __init__.py
│       │   ├── rename.py
│       │   ├── rollback.py
│       │   └── archive.py
│       ├── inputs.py
│       ├── mock.py
│       └── records.py
└── tests
```

## 模块职责

`scripts/scan.py`、`scripts/rename.py`、`scripts/rollback.py`、`scripts/archive.py`、`scripts/archive_name.py`：

- 使用 `argparse` 解析脚本参数。
- 调用 `src/photograph_workflow/` 中的业务模块。
- 展示 dry-run、错误和执行摘要。
- 不直接写业务逻辑。

`dirs.py`：

- 管理本地原始照片目录和 iCloud 原始照片目录的目录契约。
- 业务代码引用统一目录契约，不硬编码根路径。

`extensions.py`：

- 定义照片源文件、sidecar、其他素材和视频类型的枚举。
- 扩展名匹配大小写不敏感。
- 只处理枚举中明确支持的类型。
- sidecar 匹配基于文件 stem，stem 大小写敏感，扩展名匹配大小写不敏感但重命名后保留原扩展名大小写。
- 如果同一 stem 下存在多个 RAW/DNG 源文件，阻止执行并要求用户手工处理。

`scanner.py`：

- 递归扫描项目目录。
- 识别支持的 RAW/DNG 文件。
- 跳过 `.DS_Store`、空目录、默认排除目录。

`metadata/base.py`：

- 定义 `MetadataReader` 协议或抽象基类。
- 返回统一的 `PhotoMetadata` 数据结构。

`metadata/exiftool.py`：

- 检测项目环境中的 ExifTool 能力是否可用。
- 批量调用 `exiftool -json`。
- 解析拍摄时间、相机型号、文件类型等字段。
- 对 `.dng` 读取 `FileType`、`Make`、`Model`，用于确认 DJI DNG 来源。
- 只读元数据，不写 RAW/DNG。

`naming/template.py`：

- 解析命名模板。
- 展开 `{date:YYYYMMDD}`、`{date:HHMMSS}`、`{title}`、`{original}` 等 token。
- `{date:<format>}` 按 ISO 8601 的 basic 和 extended 表示形式输出；文件名默认使用不含冒号的 basic 格式。
- `{original}` 必须优先来自 `.metadata.json` 首次记录的 `original_name`；ExifTool 的 `FileName` 只能作为首次接管前的当前文件名输入，不能作为已重命名文件的原始名依据。
- 返回目标文件名，不执行文件操作。

`naming/sanitize.py`：

- 清理跨平台非法字符。
- 检查文件名长度。
- 保留中文、数字、英文字母、横杠和下划线。

`planner/rename_plan.py`：

- 根据扫描结果、元数据和模板生成重命名计划。
- 检测目标名冲突。
- 检测目标文件是否已存在。
- 检测 sidecar 与 RAW/DNG 的同 stem 归属关系。
- 检测未知来源 DNG 和同 stem 多 RAW/DNG 冲突。
- 检测照片目录下 `.metadata.json` 是否可写。
- 生成 dry-run 输出数据。

`planner/rollback_plan.py`：

- 读取照片目录下 `.metadata.json` 的 `files` 映射。
- 生成回滚计划。
- 检测 `current_name` 是否存在、`original_name` 目标是否冲突。
- 对仍处于 `pending` 且尚未实际重命名的条目，只生成清理 `planned_name` 和状态更新的计划。
- 支持 dry-run。

`operations/rename.py`：

- 执行已验证的重命名计划。
- 同步处理与 RAW/DNG 同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` 等 sidecar 文件。
- 执行文件 rename 前，先写入或更新照片目录下 `pending` 状态的 `.metadata.json`。
- 文件 rename 成功后，再把 `.metadata.json` 更新为 `renamed` 状态。
- 首次纳入工作流的文件必须写入不可变的 `original_name`、表示真实当前文件名的 `current_name`，以及 `pending` 状态下的 `planned_name`。
- 文件 rename 成功后，必须把 `current_name` 更新为目标文件名，并移除对应条目的 `planned_name`。
- 如果实际执行中途失败，必须尽量把已经成功 rename 的条目更新为真实 `current_name`，并把失败条目标记为 `failed`。

`operations/rollback.py`：

- 根据 `.metadata.json` 中的 `files` 映射执行回滚。
- 默认 dry-run，实际执行前要求用户确认。

`operations/archive.py`：

- 生成归档计划。
- 按用户传入的目录整体创建单个 ZIP，不自动按照片目录拆分。
- ZIP 内保留用户传入目录下的内部层级。
- 创建 ZIP 文件，文件名使用用户传入目录名加 `~YYYYMMDDHHMMSS` 归档时间后缀。
- 支持只生成推荐归档包名称，不执行压缩，用于用户手动压缩。
- 校验归档结果。
- 不生成额外归档记录文件，不把归档结果写回 `.metadata.json`。

`inputs.py`：

- 读取和结构化校验 JSON 目录列表输入。
- 校验 `root`、`directories`、`template`。
- 输入只允许指定目录，不能逐个指定照片文件。
- 后续可扩展 YAML 输入。

`mock.py`：

- 提供 mock 文件操作后端。
- 模拟文件不存在、权限不足、磁盘空间不足、目标路径已存在、ExifTool 读取失败等错误。

`records.py`：

- 读写照片目录下的 `.metadata.json`。
- 记录目录级 rename 状态。
- 为后续 rollback 提供不可变原始文件映射。
- 校验 `.metadata.json` 的 `version`，当前只支持 `version = 1`。
- 遇到缺失版本、未知版本或未来版本时，dry-run 必须报错并阻止执行。

## 结构化计划契约

业务模块必须返回结构化计划对象，脚本层只负责把计划渲染成终端摘要。字段契约属于 TDD 范围，详见 `docs/tdd/README.md`。

## ExifTool 集成

ExifTool 是元数据读取后端。Python 侧可以使用 wrapper 或直接调用二进制，但必须通过 uv 和项目环境管理，不要求用户安装到系统目录。

调用方式：

```text
exiftool -json -FileName -Directory -FileType -Make -Model -DateTimeOriginal -CreateDate -ModifyDate -SubSecDateTimeOriginal -SubSecCreateDate -OffsetTimeOriginal -FileCreateDate -FileModifyDate <files...>
```

实现要求：

- 优先检查项目虚拟环境或项目工具目录中的 ExifTool 能力。
- 不把 ExifTool 安装到用户系统目录作为默认要求。
- 如果使用 Python wrapper，依赖写入 `pyproject.toml`。
- 使用 `subprocess.run(..., capture_output=True, text=True, check=False)` 调用。
- 解析 stdout JSON。
- 如果 ExifTool 返回非 0 exit code，保留 stderr 并在 dry-run 中展示。
- 大量文件时分批调用，避免命令行参数过长。

## 默认重命名策略

默认模板：

```text
{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}
```

示例：

```text
DSC00000.ARW -> 20260101-上海东方明珠-080001_DSC00000.ARW
```

处理流程：

1. 扫描项目根目录。
2. 按扩展名找到候选照片源文件，例如 `.arw`、`.dng`。
3. 用 ExifTool 批量读取候选文件元数据。
4. 确认当前版本支持的 RAW/DNG：Sony `.arw` 作为支持源文件，`.dng` 必须确认 `FileType = DNG` 且 `Make` 或 `Model` 可识别为 DJI。
5. 根据已确认支持的 RAW/DNG 按 stem 匹配 sidecar。
6. 按照片文件直接父目录分组。
7. 从元数据提取拍摄日期时间，并按模板中的 `{date:<format>}` 输出。
8. 展开模板生成目标名。
9. 检测冲突。
10. dry-run 展示计划。
11. 确认照片目录下 `.metadata.json` 可写。
12. 用户确认。
13. 写入或更新 `pending` 状态的 `.metadata.json`，其中 `current_name` 是真实当前文件名，`planned_name` 是目标文件名。
14. 执行文件系统 rename。
15. 执行成功后更新 `.metadata.json` 为 `renamed` 状态，将 `planned_name` 落到 `current_name` 并移除 `planned_name`。

## 错误处理

阻止执行：

- 缺少 ExifTool 且命名模板依赖元数据。
- 任意照片缺少可用拍摄时间。
- 目标文件名冲突。
- 目标路径已存在。
- 文件名非法或过长。
- `.metadata.json` 无法写入。
- 用户未确认实际执行。

允许警告：

- 非照片文件被跳过。
- 空目录被跳过。
- 找到 sidecar 但策略未启用。
- 找到视频文件但当前版本不处理视频命名。

## 原子性与确认

重命名执行必须遵守：

1. 先生成 dry-run 计划。
2. dry-run 无错误。
3. 确认 `.metadata.json` 可写。
4. 用户确认。
5. 写入或更新 `pending` 状态的 `.metadata.json`。
6. 执行重命名。
7. 更新 `.metadata.json` 为 `renamed` 状态。

任意步骤失败都不能进入下一步。重命名执行时如果遇到错误，应停止并通过 `.metadata.json` 中已存在的 `original_name`、`current_name`、`planned_name` 和文件级 `status` 支持回滚或人工恢复。

## 测试策略

单元测试：

- 模板展开。
- 文件名清洗。
- 重命名计划冲突检测。
- ExifTool JSON 解析。
- `.metadata.json` 读写。
- JSON 目录列表输入。
- 回滚计划生成。
- mock 文件操作错误模拟。

集成测试：

- 使用 fixture 模拟项目目录。
- 用假的 ExifTool JSON 输出测试 rename dry-run。
- 用 mock 模式测试权限不足、目标存在、磁盘空间不足。
- 可选地在本机有 ExifTool 时跑真实 ARW/DNG smoke test。

真实文件验收：

- Sony `.ARW`：确认可以读取拍摄时间。
- DJI `.DNG`：确认可以读取拍摄时间。
- 当前脱敏样例目录：按默认模板 dry-run 后目标名冲突数为 0。
