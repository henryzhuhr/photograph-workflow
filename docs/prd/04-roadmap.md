# 产品范围、MVP 与后续路线

## MVP 范围

MVP 应聚焦在 Lightroom 前后的文件管理自动化。

必须包含：

- 项目目录扫描。
- RAW 文件识别。
- 自定义命名模板。
- 重命名 dry-run。
- 冲突检测。
- RAW 与常见伴随文件同步重命名。
- 重命名操作记录。
- 导出目录检查。
- 归档 dry-run。
- ZIP 归档。
- 归档结果记录。

可以暂缓：

- 图形界面。
- 自动分类。
- Lightroom catalog 读取。
- 云同步。
- 图片内容识别。
- 自动修图。

## 推荐执行形态

后续实现先做 uv 管理的 Python 脚本。MVP 不要求安装成系统命令，只要能用 `uv run python ...` 直接执行即可。

示例：

```text
uv run python scripts/scan.py ./Photos/20260501-「旅游」重庆
uv run python scripts/rename.py ./Photos/20260501-「旅游」重庆 --template "{folder}-{timestamp:HHMMSS}_{original}" --dry-run
uv run python scripts/rename.py ./Photos/20260501-「旅游」重庆 --template "{folder}-{timestamp:HHMMSS}_{original}"
uv run python scripts/archive.py ./Photos/20260501-「旅游」重庆 --output /Volumes/Archive/Photos --dry-run
uv run python scripts/archive.py ./Photos/20260501-「旅游」重庆 --output /Volumes/Archive/Photos
```

如果脚本稳定后需要更顺手的入口，再考虑在 `pyproject.toml` 中增加 `project.scripts`，把脚本包装成 `photograph-workflow` 命令。

## 配置文件

建议支持项目级配置和全局配置。

项目级配置：

```text
workflow.json
```

全局配置：

```text
~/.config/photograph-workflow/config.json
```

示例：

```json
{
  "rawExtensions": [".arw", ".cr3", ".nef", ".dng"],
  "sidecarExtensions": [".xmp", ".jpg", ".jpeg"],
  "renameTemplate": "{folder}-{timestamp:HHMMSS}_{original}",
  "timestampSource": "metadata",
  "onNameConflict": "fail",
  "sequenceScope": "per-directory",
  "exportDirs": ["exports"],
  "archive": {
    "format": "zip",
    "exclude": [".DS_Store", "Thumbs.db", "*.tmp"]
  }
}
```

## 外部依赖

MVP 使用 uv 管理 Python 运行环境，并依赖 ExifTool 读取 RAW/DNG 元数据。

依赖策略：

- 脚本启动时检测 `exiftool` 可执行文件。
- `scan` 可以在缺少 ExifTool 时降级，只输出文件数量和扩展名统计。
- `rename --dry-run` 和实际重命名必须要求 ExifTool 可用，因为默认命名模板依赖拍摄时间。
- 只读调用 ExifTool，不用 ExifTool 写入 RAW/DNG。
- 重命名使用文件系统操作，不改写照片内容。
- 文档中提供 macOS、Windows、Linux 的安装说明。
- Python 依赖通过 `pyproject.toml` 和 `uv.lock` 管理。

实现上不直接依赖某个只支持 JPEG 的 EXIF 包。Python 代码应通过一个 `MetadataReader` adapter 调用 ExifTool JSON 输出，避免把第三方命令调用散落在重命名逻辑里。

Python 标准库应覆盖大部分 MVP 能力：

- `argparse`：脚本参数解析。
- `pathlib`：路径处理。
- `dataclasses`：内部计划对象。
- `json`：配置、操作记录和 ExifTool JSON 解析。
- `subprocess`：调用 ExifTool。
- `zipfile`：ZIP 归档。
- `logging`：执行日志。

MVP 默认不引入重量级运行时依赖。测试依赖可以使用 `pytest`。

## 非功能需求

可靠性：

- 文件修改操作必须尽可能原子化。
- 任何冲突都应在修改前发现。
- dry-run 和实际执行应使用同一套计划生成逻辑。

性能：

- MVP 需要支持单项目 1,000 到 5,000 张 RAW 文件。
- 扫描过程应能流式处理文件，避免一次性载入大文件内容。

可移植性：

- 文件名清洗规则需要兼容 macOS、Windows 和 Linux。
- 路径记录建议使用相对项目目录的相对路径。

可观测性：

- 每次执行应输出摘要。
- 失败时要能看到具体文件和原因。
- 操作记录应便于后续回滚、审计和排查。

## 风险与决策

### Lightroom 引用风险

如果用户已经把照片导入 Lightroom，再用工具改名，Lightroom 可能无法找到原文件。

决策：

- MVP 明确提示“请在 Lightroom 导入前重命名”。
- 如果发现目录内存在明显 Lightroom 相关文件，不自动判断安全，只提示用户确认。

### 元数据依赖风险

部分 RAW 元数据可能读取失败，或不同厂商字段不一致。

决策：

- `{date}`、`{camera}` 等元数据 token 应允许为空时回退。
- 默认模板不强依赖相机型号。
- 拍摄时间不可用时回退到原文件名排序。

### 伴随文件误匹配风险

同名 `.mov` 或 `.jpg` 可能是相关文件，也可能只是恰好同名。

决策：

- `.xmp` 默认同步。
- JPEG 和视频文件默认列入预览，执行前给出提示。
- 后续版本允许按扩展名配置同步策略。

## 后续路线

### V1

- 完成 uv 项目配置。
- 完成 `scripts/scan.py`、`scripts/rename.py`、`scripts/archive.py`。
- 完成 JSON 操作记录。
- 提供基础测试覆盖。

### V2

- 增加交互式 TUI 或简单桌面界面。
- 增加自动从目录名解析项目日期和项目名称。
- 增加归档 manifest 和 checksum。
- 增加 `scripts/rollback.py`。
- 可选增加 `project.scripts`，提供系统级命令入口。

### V3

- 支持从存储卡导入。
- 支持自动分类建议。
- 支持读取 Lightroom 导出结果并做更完整校验。
- 支持 NAS、外部硬盘和云盘归档策略。
