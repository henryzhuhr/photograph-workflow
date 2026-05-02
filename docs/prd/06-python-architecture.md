# Python 技术架构设计

## 技术决策

项目使用 Python 实现，并用 uv 管理项目环境。当前版本交付可直接执行的 `.py` 脚本，不要求安装成系统 CLI。

原因：

- 文件系统扫描、重命名、压缩、JSON 记录都适合 Python 标准库。
- ExifTool 可以通过 `subprocess` 调用，并以 JSON 作为稳定接口。
- 需要扩展桌面界面、TUI、系统 CLI 或自动化脚本时，Python 生态更贴近本地照片工作流。

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
- `scripts/` 只做参数解析和调用业务模块。

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
│   └── archive.py
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

`scripts/scan.py`、`scripts/rename.py`、`scripts/rollback.py`、`scripts/archive.py`：

- 使用 `argparse` 解析脚本参数。
- 调用 `src/photograph_workflow/` 中的业务模块。
- 展示 dry-run、错误和执行摘要。
- 不直接写业务逻辑。

`dirs.py`：

- 定义 `PhotographDir(StrEnum)`。
- 管理本地原始照片目录和 iCloud 原始照片目录。
- 业务代码只引用枚举，不硬编码根路径。

`extensions.py`：

- 定义照片源文件、附属文件、视频类型的枚举。
- 扩展名匹配大小写不敏感。
- 只处理枚举中明确支持的类型。

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
- 只读元数据，不写 RAW/DNG。

`naming/template.py`：

- 解析命名模板。
- 展开 `{date:YYYYMMDD}`、`{date:HHMMSS}`、`{title}`、`{original}` 等 token。
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
- 检测照片目录下 `.metadata.json` 是否可写。
- 生成 dry-run 输出数据。

`planner/rollback_plan.py`：

- 读取照片目录下 `.metadata.json` 的 `files` 映射。
- 生成回滚计划。
- 检测当前文件是否存在、原始目标是否冲突。
- 支持 dry-run。

`operations/rename.py`：

- 执行已验证的重命名计划。
- 同步处理 `.xmp`、`.jpg` 等伴随文件。
- 执行成功后写入或更新照片目录下的 `.metadata.json`。
- 首次纳入工作流的文件必须写入不可变的 `original_name` 到 `renamed_name` 映射。

`operations/rollback.py`：

- 根据 `.metadata.json` 中的 `files` 映射执行回滚。
- 默认 dry-run，实际执行前要求用户确认。

`operations/archive.py`：

- 生成归档计划。
- 创建 ZIP 文件。
- 校验归档结果。

`inputs.py`：

- 使用 Pydantic `BaseModel` 读取和校验 JSON 目录列表输入。
- 校验 `root`、`directories`、`template`。
- 输入只允许指定目录，不能逐个指定照片文件。
- 后续可扩展 YAML 输入。

`mock.py`：

- 提供 mock 文件操作后端。
- 模拟文件不存在、权限不足、磁盘空间不足、目标路径已存在、ExifTool 读取失败等错误。

`records.py`：

- 读写照片目录下的 `.metadata.json`。
- 记录目录级 rename/archive 状态。
- 为后续 rollback 提供不可变原始文件映射。

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
2. 找到所有支持的 RAW/DNG。
3. 用 ExifTool 批量读取元数据。
4. 按照片文件直接父目录分组。
5. 从元数据提取拍摄日期时间，并按模板中的 `{date:<format>}` 输出。
6. 展开模板生成目标名。
7. 检测冲突。
8. dry-run 展示计划。
9. 确认照片目录下 `.metadata.json` 可写。
10. 用户确认后执行文件系统 rename。
11. 执行成功后写入或更新 `.metadata.json`。

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
- 找到伴随文件但策略未启用。
- 找到视频文件但当前版本不处理视频命名。

## 原子性与确认

重命名执行必须遵守：

1. 先生成 dry-run 计划。
2. dry-run 无错误。
3. 确认 `.metadata.json` 可写。
4. 用户确认。
5. 执行重命名。
6. 写入或更新 `.metadata.json`。

任意步骤失败都不能进入下一步。重命名执行时如果遇到错误，应停止并通过 `.metadata.json` 中已存在的文件映射支持回滚或人工恢复。

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
