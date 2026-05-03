# PRD 审阅记录

审阅时间：2026-05-03

审阅范围：`docs/prd/README.md`、`01-workflow.md`、`02-raw-renaming.md`、`03-export-archive.md`、`04-roadmap.md`、`05-standard-directory.md`、`06-python-architecture.md`。

## 当前结论

当前 PRD 的主线已经一致：当前版本交付 uv 管理的 Python 脚本，聚焦 Lightroom 导入前的 RAW/DNG 重命名、Adobe sidecar 同步、目录级 `.metadata.json` 和原始素材 ZIP 归档。当前版本不实现图形界面、不支持 Capture One 等其他后期软件、不管理 Lightroom 导出后的成片。

以下是本次审阅后仍建议决策或补充的事项。

## 发现项

### P1：`pending` 状态下的 `current_name` 与回滚规则存在冲突

位置：`02-raw-renaming.md` 的目录级 dotfile、回滚要求；`06-python-architecture.md` 的原子性与确认。

问题：PRD 要求执行 rename 前先写入 `pending` 状态的 `.metadata.json`，并把 `original_name` 到 `current_name` 的计划映射落盘。但回滚规则又要求把 `current_name` 恢复为 `original_name`。如果实际执行中途失败，部分文件已经改名，部分文件仍保持原名，`current_name` 可能只是计划目标名而不是文件系统中的真实当前名，回滚 dry-run 会因为 `current_name` 不存在而失败。

建议决策：把 `current_name` 定义为文件系统中的真实当前文件名，新增 `planned_name` 表示 pending 目标名；或者为每个 `files` 条目增加文件级状态，明确 `pending`、`renamed`、`failed` 时如何恢复。

### P1：归档粒度仍不够明确

位置：`01-workflow.md` 的原始素材归档；`03-export-archive.md` 的归档输入、归档包命名。

问题：PRD 同时使用“项目目录”和“照片目录”描述归档对象。示例 ZIP 名看起来是单个照片目录，例如 `20260101-Shanghai_Oriental_Pearl~20260101080001.zip`；但命令示例又可能传入 `Photograph-Raw/Travel/Shanghai` 这类包含多个照片目录的分类容器。不同粒度会影响 ZIP 命名、归档内容、是否包含多个 `.metadata.json`、以及归档后如何查找。

建议决策：明确当前版本归档单位是“用户传入的目录整体”还是“每个照片目录单独归档”。如果两者都支持，需要定义默认行为和 ZIP 命名规则。

### P1：RAW+JPEG 或其他同目录素材的处理边界需要更明确

位置：`01-workflow.md` 的导入素材；`02-raw-renaming.md` 的 Adobe sidecar 策略；`03-export-archive.md` 的归档输入。

问题：当前版本明确同步 `.xmp`、`.acr`，并说明机内直出 JPEG 可识别但不作为默认 sidecar 同步要求。但如果用户拍摄 RAW+JPEG，JPEG 是留在原名、只归档不重命名，还是默认完全忽略，PRD 还不够明确。这个决策会直接影响目录整洁度和归档完整性。

建议决策：为机内 JPEG 定义单独角色，例如 `camera_jpeg`，并明确当前版本是忽略、只统计、纳入归档，还是允许通过配置同步重命名。

### P2：`.metadata.json` 版本迁移策略缺失

位置：`02-raw-renaming.md` 的 `.metadata.json` 模型契约；`06-python-architecture.md` 的多端扩展架构原则。

问题：PRD 已经有 `version` 字段，也要求未来支持电脑 Web、macOS、iOS 等多端复用，但没有定义旧版本 metadata 的读取、迁移、拒绝执行或备份策略。多端应用出现后，旧脚本和新应用可能同时遇到不同 schema。

建议决策：定义 schema 兼容策略，例如只读兼容旧版本、写入前自动迁移、无法识别版本时阻止执行，并在 dry-run 中展示迁移计划。

### P2：Adobe sidecar 匹配规则需要精确化

位置：`02-raw-renaming.md` 的 Adobe sidecar 策略；`06-python-architecture.md` 的 `extensions.py` 和 `operations/rename.py`。

问题：PRD 说明 `.xmp`、`.acr` 默认同步，但没有明确大小写、basename 匹配、多个同名候选、RAW 与 DNG 同 basename 共存时的冲突策略。照片目录中可能同时存在 `DSC00000.ARW`、`DSC00000.DNG`、`DSC00000.XMP`，此时 sidecar 归属不应靠猜测。

建议决策：定义 sidecar 只按完整 stem 一对一匹配；大小写匹配不敏感但保留原扩展名；同 stem 多个 RAW 源文件时阻止执行并要求用户手动处理。

### P2：dry-run 结构化输出契约还没有落到 PRD

位置：`04-roadmap.md` 的多端扩展约束；`06-python-architecture.md` 的多端扩展架构原则。

问题：PRD 已要求 dry-run 计划、错误、冲突、metadata 更新计划都要结构化，但没有定义最小输出模型。当前脚本可以先用文本展示，但未来电脑 Web、macOS、iOS 应用会依赖结构化计划来渲染 UI 和确认操作。

建议决策：在后续 TDD 中定义 `RenamePlan`、`ArchivePlan`、`RollbackPlan` 的字段边界，至少包括 `items`、`warnings`、`errors`、`metadata_changes`、`sidecar_changes`、`requires_confirmation`。

### P2：状态流转是产品状态还是持久化状态需要区分

位置：`01-workflow.md` 的状态流转；`02-raw-renaming.md` 的 `.metadata.json` 状态；`03-export-archive.md` 的操作记录。

问题：整体流程写了 `imported -> classified -> renamed -> editing -> archived`，但 `.metadata.json` 主要记录 rename 状态，归档又明确不写回 `.metadata.json`。这会让 `editing`、`archived` 看起来像可持久化状态，但当前版本没有持久化位置。

建议决策：明确该状态流转只是用户工作流说明，不等同于 `.metadata.json.status`；或者引入单独的项目级状态记录，但这会扩大当前版本范围。

### P3：DJI DNG 的识别依据需要补充

位置：`02-raw-renaming.md` 的支持文件类型；`05-standard-directory.md` 的递归扫描模型。

问题：PRD 说当前版本支持 DJI `.DNG`，遇到无法确认来源的 DNG 应警告或阻止，但没有定义如何确认 DJI 来源。实现时需要知道依赖 ExifTool 的 `Make`、`Model`、`FileType` 还是其他字段。

建议决策：当前版本可以先用 ExifTool 的 `Make` / `Model` 包含 DJI 作为识别依据；无法识别来源的 `.dng` 默认在 dry-run 中警告或阻止，由配置决定。

### P3：归档排除规则和隐藏文件策略需要更具体

位置：`03-export-archive.md` 的默认排除；`04-roadmap.md` 的全局配置示例。

问题：当前只列出 `.DS_Store`、`Thumbs.db`、临时文件、缓存、历史压缩包等类型，但没有说明隐藏 dotfile 的默认策略。`.metadata.json` 必须纳入归档，而其他 dotfile 可能是系统文件、编辑器配置或用户说明。

建议决策：默认排除明确系统垃圾文件，但不要按“所有 dotfile”整体排除；`.metadata.json` 必须始终保留。

## 已确认一致的内容

- 当前版本只支持 Lightroom 工作流，不支持 Capture One 等其他后期软件。
- 当前版本支持 Adobe sidecar 同步，默认扩展名为 `.xmp`、`.acr`。
- 当前版本源照片默认只处理 Sony `.ARW` 和 DJI `.DNG`。
- 命名模板使用 `{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}`，`{date}` 来自照片元数据，`{title}` 来自 `.metadata.json`、批量输入或目录名解析。
- `.metadata.json` 使用 snake_case 字段，包含 `created_at`、`updated_at`、`original_name`、`current_name`。
- `{original}` 以 `.metadata.json` 首次记录的 `original_name` 为准，不依赖 RAW 内部是否保存原始文件名。
