# 数据契约

## 枚举契约

### FileRole

| 值 | 说明 |
| --- | --- |
| `raw` | 当前版本支持的照片源文件 |
| `sidecar` | 与 RAW/DNG 同 stem 的伴随文件 |
| `other` | 识别但不处理的其他文件 |

### SourceFileType

| 值 | 扩展名 | 当前行为 |
| --- | --- | --- |
| `sony_arw` | `.arw` | 支持 |
| `dji_dng` | `.dng` | 需要 ExifTool 确认 DJI 来源后支持 |

### SidecarFileType

| 值 | 扩展名 | 当前行为 |
| --- | --- | --- |
| `adobe_xmp` | `.xmp` | 与 RAW/DNG 同 stem 时同步 |
| `adobe_acr` | `.acr` | 与 RAW/DNG 同 stem 时同步；不存在不报错 |
| `camera_jpeg` | `.jpg`、`.jpeg` | 与 RAW/DNG 同 stem 时同步；孤立 JPEG 不处理 |

### DirectoryStatus

| 值 | 说明 |
| --- | --- |
| `configured` | 只有配置，尚未重命名 |
| `pending` | 重命名计划已经写入，文件操作尚未全部完成 |
| `renamed` | 当前目录已经按工作流命名 |
| `rolled_back` | 当前目录已执行回滚 |

### FileStatus

| 值 | 说明 |
| --- | --- |
| `pending` | 计划目标名已生成 |
| `renamed` | 文件已成功重命名 |
| `failed` | 文件操作失败，需要回滚或人工处理 |
| `rolled_back` | 文件已恢复到 `original_name` |

### WorkspaceKind

| 值 | 说明 |
| --- | --- |
| `local` | 本地工作目录 |
| `icloud` | iCloud Drive 下的工作目录 |
| `custom` | 用户自定义工作目录 |

## Pydantic 模型

所有外部输入、`.metadata.json`、结构化计划、错误对象都使用 Pydantic `BaseModel` 校验。路径字段在模型层接收字符串或 path-like 输入，业务层统一转换为 `Path`。

跨端序列化约束：

- JSON 输入和输出中的路径必须序列化为字符串。
- Python 内部可以使用 `Path`，但不得把 Python 专用对象泄露到计划 JSON。
- 错误、警告、计划条目必须使用稳定字段名，避免 UI 依赖文本解析。
- 字段命名统一使用 snake_case。
- 新增字段优先设计为可选字段，避免破坏旧版本客户端。

### WorkspaceFile

对应当前版本的用户级 workspace 配置文件：

```text
~/.local/share/photograph-workflow/workspaces.json
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `version` | int | 是 | 当前只支持 `1` |
| `workspaces` | list[`WorkspaceEntry`] | 是 | 用户保存过的工作目录 |
| `default_workspace_id` | string | 否 | 默认工作目录 id |
| `created_at` | datetime | 否 | 文件创建时间 |
| `updated_at` | datetime | 否 | 最近更新时间 |

### WorkspaceEntry

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 是 | 稳定唯一 id |
| `name` | string | 是 | 展示名称 |
| `path` | path | 是 | 工作目录路径 |
| `kind` | WorkspaceKind | 是 | `local`、`icloud` 或 `custom` |
| `created_at` | datetime | 否 | 创建时间 |
| `updated_at` | datetime | 否 | 最近更新时间 |

约束：

- 显式传入 `root` 时，不要求必须命中已保存 workspace。
- 未传入 `root` 时，可以从 `default_workspace_id` 或用户选择的 workspace 解析项目目录。
- 当前版本不引入通用全局配置文件，workspace 文件只保存用户选择过的目录。

### WorkspaceCommandInput

用于 `scripts/workspace.py`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation` | string | 是 | `list`、`add`、`set_default` 或 `remove` |
| `path` | path | 否 | `add` 时必填，表示要保存的工作目录 |
| `name` | string | 否 | `add` 时可选，默认使用目录名 |
| `kind` | WorkspaceKind | 否 | `add` 时可选，默认 `custom` |
| `workspace_id` | string | 否 | `set_default`、`remove` 时必填 |

校验规则：

- `add` 的 `path` 必须存在且是目录。
- `name` 存在时不能为空字符串。
- `set_default` 和 `remove` 的 `workspace_id` 必须命中已有 workspace。
- `remove` 只删除 workspace 记录，不删除文件系统目录。

### BatchInput

用于 `--input` JSON。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `root` | path | 是 | 项目根目录 |
| `directories` | list[`DirectoryInput`] | 是 | 待处理目录，至少 1 项 |
| `template` | string | 否 | 根级默认模板 |
| `strict` | boolean | 否 | 默认 `false`，控制空目录或无支持源文件目录是否阻止执行 |

校验规则：

- `root` 必须存在且是目录。
- `directories` 不能为空。
- `directories[].path` 必须是相对路径，不能包含 `..` 逃逸 `root`。
- `root / directories[].path` 必须存在且是目录。
- 输入只允许指定目录，不允许逐个指定照片文件。
- 当目录没有支持的 RAW/DNG 时，`strict = false` 返回 warning；`strict = true` 返回 error。

### DirectoryInput

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `path` | path | 是 | 相对 `root` 的目录 |
| `title` | string | 否 | 覆盖目录标题 |
| `template` | string | 否 | 覆盖该目录模板 |

校验规则：

- `title` 存在时不能为空字符串。
- `path` 指向分类容器且自身不含照片文件时，不允许设置 `title`。

### MetadataFile

对应照片目录下 `.metadata.json`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `version` | int | 是 | 当前只支持 `1` |
| `title` | string | 否 | 目录显示标题 |
| `template` | string | 否 | 目录专用模板 |
| `status` | DirectoryStatus | 否 | 默认 `configured` |
| `created_at` | datetime | 否 | 创建时间 |
| `updated_at` | datetime | 否 | 最近更新时间 |
| `files` | list[`MetadataFileEntry`] | 否 | 文件映射 |

版本策略：

- 当前版本只写入 `version = 1`。
- 缺少 `version`、版本不是整数、版本大于当前支持版本时，dry-run 必须报错并阻止执行。
- 当前版本不做自动迁移。

### MetadataFileEntry

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `original_name` | string | 是 | 首次纳入工作流时的原始文件名，不可变 |
| `current_name` | string | 是 | 文件系统当前真实文件名 |
| `planned_name` | string | 否 | pending 状态下目标文件名 |
| `role` | FileRole | 是 | `raw` 或 `sidecar` |
| `status` | FileStatus | 是 | 文件级状态 |

约束：

- `original_name` 一旦写入，不得被重规划修改。
- `current_name` 只能表示真实存在的当前文件名。
- `planned_name` 只能表示 pending 目标名，成功后必须移除。
- `files` 映射采用 append-only 原则；既有条目不能被自动删除、重建或改写 `original_name`。
- 新发现的 RAW/DNG 或 sidecar 只能追加新条目。
- `.metadata.json.files` 中存在但当前文件系统找不到的条目必须报告 `metadata_deviation`，默认阻止 rename。

## 结构化计划契约

业务模块必须返回结构化计划对象，脚本层只负责把计划渲染成终端摘要。dry-run、rename、rollback、archive、archive_name 都必须使用结构化计划，避免未来多端应用解析终端文本。

### Common Plan

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation` | string | 是 | `rename`、`rollback`、`archive` 或 `archive_name` |
| `root` | path | 是 | 本次操作的输入目录 |
| `dry_run` | boolean | 是 | 是否为 dry-run |
| `items` | list[object] | 是 | 计划条目列表 |
| `warnings` | list[`PlanIssue`] | 是 | 非阻塞警告 |
| `errors` | list[`PlanIssue`] | 是 | 阻塞错误 |
| `metadata_changes` | list[object] | 否 | `.metadata.json` 创建或更新计划 |
| `requires_confirmation` | boolean | 是 | 实际执行前是否需要用户确认 |

### RenamePlanItem

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_path` | path | 是 | 当前源路径 |
| `target_path` | path | 是 | 计划目标路径 |
| `role` | FileRole | 是 | `raw` 或 `sidecar` |
| `raw_source_path` | path | 否 | sidecar 归属 RAW/DNG；RAW/DNG 自身为空 |
| `original_name` | string | 是 | 首次纳入工作流时记录的原始文件名 |
| `current_name` | string | 是 | 文件系统当前真实文件名 |
| `planned_name` | string | 否 | pending 状态下计划目标文件名 |
| `status` | FileStatus | 是 | 文件级状态 |

### ArchivePlan

ArchivePlan 继承 Common Plan，并补充归档级字段。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_dir` | path | 是 | 用户选择的归档目录 |
| `archive_path` | path | 是 | 目标压缩包路径 |
| `archived_at` | datetime | 是 | 用于命名的归档时间 |
| `overwrite` | boolean | 是 | 是否允许覆盖已有归档包 |
| `total_size_bytes` | integer | 是 | 计划纳入归档的总大小 |
| `included_count` | integer | 是 | 计划纳入归档的文件数量 |
| `excluded_count` | integer | 是 | 被排除的文件数量 |
| `raw_count` | integer | 是 | RAW/DNG 文件数量 |
| `sidecar_count` | integer | 是 | sidecar 文件数量 |

### ArchivePlanItem

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_path` | path | 是 | 将检查或纳入归档的源路径 |
| `archive_path` | path | 是 | 目标压缩包路径 |
| `size_bytes` | integer | 否 | 文件大小 |
| `included` | boolean | 是 | 是否纳入归档 |
| `exclude_reason` | string | 否 | 被排除时的原因 |

### ArchiveNamePlan

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_dir` | path | 是 | 用户选择的目录 |
| `archive_name` | string | 是 | 推荐压缩包文件名 |
| `archive_path` | path | 否 | 如果提供输出目录，则返回完整目标路径 |
| `archived_at` | datetime | 是 | 用于命名的归档时间 |

### RollbackPlanItem

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `current_path` | path | 是 | 当前真实文件路径 |
| `target_original_path` | path | 是 | 回滚目标路径 |
| `role` | FileRole | 是 | `raw` 或 `sidecar` |
| `status` | FileStatus | 是 | 回滚计划状态 |

### PlanIssue

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `code` | string | 是 | 稳定错误码或警告码 |
| `message` | string | 是 | 面向用户的说明 |
| `path` | path | 否 | 关联文件或目录 |
| `details` | object | 否 | 结构化调试信息 |

## 错误码

建议错误码：

| code | 级别 | 说明 |
| --- | --- | --- |
| `exiftool_missing` | error | rename 需要 ExifTool，但未找到 |
| `metadata_read_failed` | error | ExifTool 读取失败 |
| `capture_time_missing` | error | RAW/DNG 无可用拍摄时间 |
| `unsupported_dng_source` | error/warning | DNG 无法确认为 DJI 来源 |
| `target_conflict` | error | 多个文件生成同一目标路径 |
| `target_exists` | error | 目标路径已存在且不是计划内文件 |
| `invalid_filename` | error | 生成文件名非法 |
| `metadata_version_unsupported` | error | `.metadata.json` 版本不支持 |
| `metadata_write_failed` | error | `.metadata.json` 不可写或写入失败 |
| `directory_no_supported_sources` | warning/error | 指定目录没有支持的 RAW/DNG；级别由 `strict` 决定 |
| `workspace_not_found` | error | 指定 workspace 不存在 |
| `workspace_path_invalid` | error | workspace 路径不存在或不是目录 |
| `sidecar_ambiguous` | error | 同 stem 多 RAW/DNG，sidecar 归属不明确 |
| `archive_target_exists` | error | 目标 ZIP 已存在 |
| `archive_name_target_exists` | warning | `archive_name` 推荐目标已存在 |
| `archive_missing_metadata` | warning | 存在已重命名照片但对应目录缺少 `.metadata.json` |
| `metadata_deviation` | error | 文件系统状态与 `.metadata.json` 映射不一致 |
| `post_processor_reference_risk` | warning | 发现后期软件相关文件，重命名可能导致引用丢失 |
