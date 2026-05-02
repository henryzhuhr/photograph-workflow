# 产品范围与实现约束

## 当前版本范围

当前版本聚焦在 Lightroom 导入前的 RAW/DNG 文件管理自动化，以及原始素材归档。不管理 Lightroom 导出后的成片。

产品能力：

- 项目目录扫描。
- RAW/DNG 文件识别。
- 支持扩展名枚举和目录枚举。
- 自定义命名模板。
- 重命名 dry-run。
- 实际执行前用户确认。
- 冲突检测。
- RAW/DNG 与常见伴随文件同步重命名。
- 目录级 `.metadata.json` 操作记录。
- `.metadata.json` 原始文件映射。
- rollback 脚本。
- mock 模式。
- JSON 目录列表输入。
- 归档 dry-run。
- ZIP 归档。
- 归档结果记录。

## 推荐执行形态

当前版本使用 uv 管理的 Python 脚本，不要求安装成系统命令，只要能用 `uv run python ...` 直接执行即可。

示例：

```text
uv run python scripts/scan.py ./Photograph-Raw/Travel/Shanghai
uv run python scripts/rename.py ./Photograph-Raw/Travel/Shanghai --template "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}" --dry-run
uv run python scripts/rename.py ./Photograph-Raw/Travel/Shanghai --template "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}"
uv run python scripts/rename.py --input ./rename-input.json --dry-run
uv run python scripts/rollback.py ./Photograph-Raw/Travel/Shanghai/20260101-上海东方明珠 --dry-run
uv run python scripts/archive.py ./Photograph-Raw/Travel/Shanghai --output /Volumes/Archive/Photos --dry-run
uv run python scripts/archive.py ./Photograph-Raw/Travel/Shanghai --output /Volumes/Archive/Photos
```

如果脚本稳定后需要更顺手的入口，再考虑在 `pyproject.toml` 中增加 `project.scripts`，把脚本包装成 `photograph-workflow` 命令。

## 配置文件

建议支持项目级配置和全局配置。

项目级配置：

```text
照片目录下的 .metadata.json
```

全局配置：

```text
~/.config/photograph-workflow/config.json
```

示例：

```json
{
  "raw_extensions": [".arw", ".cr3", ".nef", ".dng"],
  "sidecar_extensions": [".xmp", ".jpg", ".jpeg"],
  "rename_template": "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}",
  "timestamp_source": "metadata",
  "on_name_conflict": "fail",
  "require_dry_run_before_apply": true,
  "require_confirmation": true,
  "sequence_scope": "per-directory",
  "archive": {
    "format": "zip",
    "exclude": [".DS_Store", "Thumbs.db", "*.tmp"]
  }
}
```

## 外部依赖

当前版本使用 uv 管理 Python 运行环境，并在项目环境中管理 ExifTool 能力来读取 RAW/DNG 元数据。

依赖策略：

- 脚本启动时检测项目环境中的 `exiftool` 能力。
- `scan` 可以在缺少 ExifTool 时降级，只输出文件数量和扩展名统计。
- `rename --dry-run` 和实际重命名必须要求 ExifTool 可用，因为默认命名模板依赖拍摄时间。
- 只读调用 ExifTool，不用 ExifTool 写入 RAW/DNG。
- 重命名使用文件系统操作，不改写照片内容。
- 不要求用户把 ExifTool 安装到系统目录；如果需要二进制，应安装在项目虚拟环境或项目工具目录。
- Python 依赖通过 `pyproject.toml` 和 `uv.lock` 管理。

实现上不直接依赖某个只支持 JPEG 的 EXIF 包。Python 代码应通过一个 `MetadataReader` adapter 调用 ExifTool JSON 输出，避免把第三方命令调用散落在重命名逻辑里。

Python 标准库应覆盖大部分当前版本能力：

- `argparse`：脚本参数解析。
- `pathlib`：路径处理。
- `enum.StrEnum`：目录、扩展名、文件角色枚举。
- `dataclasses`：内部计划对象。
- `json`：配置、操作记录和 ExifTool JSON 解析。
- `subprocess`：调用 ExifTool。
- `zipfile`：ZIP 归档。
- `logging`：执行日志。

当前版本默认不引入重量级运行时依赖。测试依赖可以使用 `pytest`。

## 非功能需求

可靠性：

- 文件修改操作必须尽可能原子化。
- 实际执行前必须先通过 dry-run 生成可执行计划。
- 任何冲突都应在修改前发现。
- dry-run 和实际执行应使用同一套计划生成逻辑。
- 任意错误都会阻止整个批次执行。
- 执行前确认每个照片目录的 `.metadata.json` 可写，并在执行成功后写入不可变原始文件映射。

性能：

- 当前版本需要支持单项目 1,000 到 5,000 张 RAW 文件。
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

- 明确提示“请在 Lightroom 导入前重命名”。
- 如果发现目录内存在明显 Lightroom 相关文件，不自动判断安全，只提示用户确认。

### 元数据依赖风险

部分 RAW 元数据可能读取失败，或不同厂商字段不一致。

决策：

- `{date}`、`{camera}` 等元数据 token 应允许为空时回退。
- 默认模板不强依赖相机型号。
- 拍摄时间不可用时回退到原文件名排序。

### 伴随文件误匹配风险

同名 `.jpg`、`.jpeg`、`.xmp`、`.acr` 可能是相关文件，也可能只是恰好同名。

决策：

- `.xmp` 默认同步。
- `.acr` 默认同步。
- 机内直出 JPEG 默认识别并纳入计划。
- 视频文件不参与当前版本命名，但架构保留视频管理能力。
- 允许按扩展名配置同步策略。

## 不包含的能力

当前版本不包含：

- 图形界面。
- 自动分类。
- Lightroom catalog 读取。
- 云同步。
- 图片内容识别。
- 自动修图。
- Lightroom 导出成片管理。
