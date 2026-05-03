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
- RAW/DNG 与 sidecar 同步重命名。
- 目录级 `.metadata.json` 操作记录。
- `.metadata.json` 原始文件映射。
- rollback 脚本。
- mock 模式。
- JSON 目录列表输入。
- 归档 dry-run。
- ZIP 归档。
- 带归档时间的 ZIP 文件命名。

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

## 多端扩展约束

当前版本不实现电脑 Web 端、macOS 端或 iOS 端应用，但所有产品和技术设计必须保留多端扩展空间。

约束：

- 核心能力不能只服务命令行交互，必须能被未来 GUI、Web API 或移动端操作流复用。
- `.metadata.json`、批量输入 JSON 和 dry-run 计划输出必须保持结构化，不能依赖只适合终端阅读的文本。
- 文件扫描、命名模板、元数据读取、冲突检测、两阶段 metadata 写入和归档命名应作为平台无关的核心规则。
- 脚本只负责参数解析、用户确认和摘要展示，不承载不可复用的业务逻辑。
- 后续多端应用可以复用同一套核心模块，并按平台替换文件选择、权限授权、进度展示和错误呈现方式。

## 配置文件

当前版本不定义项目级配置文件。目录级配置和状态由每个照片目录下的 `.metadata.json` 管理；跨项目默认值可由全局配置管理。

全局配置建议路径：

```text
~/.config/photograph-workflow/config.json
```

示例：

```json
{
  "raw_extensions": [".arw", ".dng"],
  "sidecar_extensions": [".xmp", ".acr", ".jpg", ".jpeg"],
  "rename_template": "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}",
  "timestamp_source": "metadata",
  "on_name_conflict": "fail",
  "require_dry_run_before_apply": true,
  "require_confirmation": true,
  "sequence_scope": "per-directory",
  "archive": {
    "format": "zip",
    "exclude": [
      ".DS_Store",
      "._*",
      ".Spotlight-V100",
      ".Trashes",
      ".fseventsd",
      "Thumbs.db",
      "desktop.ini",
      "*.tmp",
      "*.temp",
      "*.swp",
      "*.part",
      "*.zip",
      "*.7z",
      "*.rar",
      "*.lrdata"
    ],
    "include_dotfiles_by_default": true,
    "always_include": [".metadata.json"]
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
- `enum`：目录、扩展名、文件角色枚举。
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
- dry-run 阶段的任意错误都会阻止整个批次执行。
- 实际执行中如果发生文件系统错误，必须留下足够的 `.metadata.json` 映射信息用于回滚或人工恢复。
- 执行文件重命名前写入 `pending` 状态的 `.metadata.json`，确保 `original_name`、`current_name`、`planned_name` 映射已经落盘。

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

结构化输出：

- dry-run、rename、rollback、archive 都必须返回结构化计划对象。
- 脚本可以把结构化计划渲染为终端摘要，但业务模块不能只返回文本。
- 结构化计划必须包含 `items`、`warnings`、`errors`、`requires_confirmation`。
- 涉及 `.metadata.json` 的操作必须包含 `metadata_changes`。
- 涉及 sidecar 的操作必须能在计划中表达 sidecar 与 RAW/DNG 的归属关系。

## 风险与决策

### Lightroom 引用风险

如果用户已经把照片导入 Lightroom，再用工具改名，Lightroom 可能无法找到原文件。

决策：

- 明确提示“请在 Lightroom 导入前重命名”。
- 如果发现目录内存在明显 Lightroom 相关文件，不自动判断安全，只提示用户确认。

### 元数据依赖风险

部分 RAW 元数据可能读取失败，或不同厂商字段不一致。

决策：

- 默认模板依赖 `{date}`，如果无法读取可用拍摄时间，dry-run 必须报错并阻止执行。
- 后续可选 token 允许定义各自的空值或回退策略，但不能影响默认模板的安全性。
- 默认模板不强依赖相机型号。
- 拍摄时间不可用时只能回退展示排序，不能生成依赖 `{date}` 的目标文件名。

### Sidecar 误匹配风险

同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` 可能是相关文件，也可能只是恰好同名。

决策：

- `.xmp` 默认同步。
- `.acr` 默认同步；它是新版本 Adobe 工作流可能稳定产生的 sidecar，但不要求每张照片都存在。
- 与 RAW/DNG 同 stem 的 `.jpg`、`.jpeg` 作为机内 JPEG sidecar 默认同步。
- 不匹配 RAW/DNG stem 的 JPEG 不参与当前版本重命名。
- 视频文件不参与当前版本命名，但架构保留视频管理能力。
- 允许按扩展名配置同步策略。

## 不包含的能力

当前版本不包含：

- 图形界面。
- 自动分类。
- Lightroom catalog 读取。
- Capture One 等其他后期软件适配。
- 云同步。
- 图片内容识别。
- 自动修图。
- Lightroom 导出成片管理。
- 电脑 Web 端、macOS 端和 iOS 端应用界面。
