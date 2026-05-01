# Python 技术架构设计

## 技术决策

项目使用 Python 实现，并用 uv 管理项目环境。第一阶段交付可直接执行的 `.py` 脚本，不要求安装成系统 CLI。

原因：

- 文件系统扫描、重命名、压缩、JSON 记录都适合 Python 标准库。
- ExifTool 可以通过 `subprocess` 调用，并以 JSON 作为稳定接口。
- 后续扩展桌面界面、TUI、系统 CLI 或自动化脚本时，Python 生态更贴近本地照片工作流。

## uv 项目管理

项目使用 uv 管理 Python 版本、依赖和执行环境。

仓库应以 `pyproject.toml` 和 `uv.lock` 作为 Python 项目管理入口。现有 `package.json` 不作为 MVP 的项目管理依据；如果没有前端或 Node 工具链需求，后续可以删除或标记为历史遗留。

推荐执行方式：

```text
uv run python scripts/scan.py <project-dir>
uv run python scripts/rename.py <project-dir> --dry-run
uv run python scripts/archive.py <project-dir> --dry-run
```

原则：

- MVP 不要求 `pip install -e .` 后生成系统命令。
- 脚本可以直接执行，便于用户按本地工作流调用。
- 公共逻辑仍放在 `src/photograph_workflow/`，避免脚本之间复制代码。
- `scripts/` 只做参数解析和调用业务模块。

## Python 版本

仓库当前 `pyproject.toml` 已声明 Python 项目。

建议版本策略：

- MVP 代码优先兼容 Python 3.12+。
- 如果继续保留 `requires-python = ">=3.14"`，需要确认用户本机和 CI 都有 Python 3.14。
- 不依赖 Python 3.14 独有特性，避免后续使用门槛过高。

## 包结构

建议源码结构：

```text
scripts/
  scan.py
  rename.py
  archive.py
src/
  photograph_workflow/
    __init__.py
    config.py
    scanner.py
    metadata/
      __init__.py
      base.py
      exiftool.py
    naming/
      __init__.py
      template.py
      sanitize.py
    planner/
      __init__.py
      rename_plan.py
      archive_plan.py
    operations/
      __init__.py
      rename.py
      archive.py
    records.py
tests/
```

## 模块职责

`scripts/scan.py`、`scripts/rename.py`、`scripts/archive.py`：

- 使用 `argparse` 解析脚本参数。
- 调用 `src/photograph_workflow/` 中的业务模块。
- 展示 dry-run、错误和执行摘要。
- 不直接写业务逻辑。

`scanner.py`：

- 递归扫描项目目录。
- 识别支持的 RAW/DNG 文件。
- 跳过 `.DS_Store`、空目录、默认排除目录。

`metadata/base.py`：

- 定义 `MetadataReader` 协议或抽象基类。
- 返回统一的 `PhotoMetadata` 数据结构。

`metadata/exiftool.py`：

- 检测 `exiftool` 是否可用。
- 批量调用 `exiftool -json`。
- 解析拍摄时间、相机型号、文件类型等字段。
- 只读元数据，不写 RAW/DNG。

`naming/template.py`：

- 解析命名模板。
- 展开 `{folder}`、`{timestamp:HHMMSS}`、`{original}` 等 token。
- 返回目标文件名，不执行文件操作。

`naming/sanitize.py`：

- 清理跨平台非法字符。
- 检查文件名长度。
- 保留中文、数字、英文字母、横杠和下划线。

`planner/rename_plan.py`：

- 根据扫描结果、元数据和模板生成重命名计划。
- 检测目标名冲突。
- 检测目标文件是否已存在。
- 生成 dry-run 输出数据。

`operations/rename.py`：

- 执行已验证的重命名计划。
- 同步处理 `.xmp`、`.jpg` 等伴随文件。
- 写入操作记录。

`operations/archive.py`：

- 生成归档计划。
- 创建 ZIP 文件。
- 校验归档结果。

`records.py`：

- 读写 `workflow.json`。
- 记录 rename/archive 操作。
- 为后续 rollback 提供数据基础。

## ExifTool 集成

ExifTool 是元数据读取后端，不是 Python 包。

调用方式：

```text
exiftool -json -FileName -Directory -FileType -Make -Model -DateTimeOriginal -CreateDate -ModifyDate -SubSecDateTimeOriginal -SubSecCreateDate -OffsetTimeOriginal -FileCreateDate -FileModifyDate <files...>
```

实现要求：

- 使用 `shutil.which("exiftool")` 检查依赖。
- 使用 `subprocess.run(..., capture_output=True, text=True, check=False)` 调用。
- 解析 stdout JSON。
- 如果 ExifTool 返回非 0 exit code，保留 stderr 并在 dry-run 中展示。
- 大量文件时分批调用，避免命令行参数过长。

## 默认重命名策略

默认模板：

```text
{folder}-{timestamp:HHMMSS}_{original}
```

示例：

```text
DSC09907.ARW -> 20260501-重庆人民大礼堂-184126_DSC09907.ARW
```

处理流程：

1. 扫描项目根目录。
2. 找到所有支持的 RAW/DNG。
3. 用 ExifTool 批量读取元数据。
4. 按照片文件直接父目录分组。
5. 从元数据提取 `HHMMSS`。
6. 展开模板生成目标名。
7. 检测冲突。
8. dry-run 展示计划。
9. 用户确认后执行文件系统 rename。

## 错误处理

阻止执行：

- 缺少 ExifTool 且命名模板依赖元数据。
- 任意照片缺少可用拍摄时间。
- 目标文件名冲突。
- 目标路径已存在。
- 文件名非法或过长。

允许警告：

- 非照片文件被跳过。
- 空目录被跳过。
- 找到伴随文件但策略未启用。

## 测试策略

单元测试：

- 模板展开。
- 文件名清洗。
- 重命名计划冲突检测。
- ExifTool JSON 解析。
- `workflow.json` 读写。

集成测试：

- 使用 fixture 模拟项目目录。
- 用假的 ExifTool JSON 输出测试 rename dry-run。
- 可选地在本机有 ExifTool 时跑真实 ARW/DNG smoke test。

真实文件验收：

- Sony `.ARW`：确认可以读取拍摄时间。
- DJI `.DNG`：确认可以读取拍摄时间。
- 当前重庆样例目录：按默认模板 dry-run 后目标名冲突数为 0。
