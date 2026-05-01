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

## 推荐命令形态

后续实现可以先做 CLI。

示例：

```text
photograph-workflow scan ./Photos/2026-04-30_Tokyo-Street
photograph-workflow rename ./Photos/2026-04-30_Tokyo-Street --template "{project_date}_{folder}_{seq:04}" --dry-run
photograph-workflow rename ./Photos/2026-04-30_Tokyo-Street --template "{project_date}_{folder}_{seq:04}"
photograph-workflow archive ./Photos/2026-04-30_Tokyo-Street --output /Volumes/Archive/Photos --dry-run
photograph-workflow archive ./Photos/2026-04-30_Tokyo-Street --output /Volumes/Archive/Photos
```

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
  "renameTemplate": "{project_date}_{folder}_{seq:04}",
  "sequenceScope": "per-directory",
  "exportDirs": ["exports"],
  "archive": {
    "format": "zip",
    "exclude": [".DS_Store", "Thumbs.db", "*.tmp"]
  }
}
```

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

- 完成 CLI。
- 完成 scan、rename、archive 三个命令。
- 完成 JSON 操作记录。
- 提供基础测试覆盖。

### V2

- 增加交互式 TUI 或简单桌面界面。
- 增加自动从目录名解析项目日期和项目名称。
- 增加归档 manifest 和 checksum。
- 增加 rollback 命令。

### V3

- 支持从存储卡导入。
- 支持自动分类建议。
- 支持读取 Lightroom 导出结果并做更完整校验。
- 支持 NAS、外部硬盘和云盘归档策略。

