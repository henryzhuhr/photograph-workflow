# RAW 文件重命名需求

## 目标

根据已经分类好的目录，批量重命名目录下的 RAW/DNG 文件，并支持用户自定义命名格式。这个功能是整个工作流的核心，因为它决定了后续 Lightroom 引用、sidecar 和原始素材归档包的可追踪性。

## 工作目录契约

工作目录分为本地目录和 iCloud 目录两类。实现时需要用统一的目录契约管理根路径，不在业务逻辑里散落硬编码路径。

建议目录契约：

| 目录 | 含义 | 示例 |
| --- | --- | --- |
| 本地根目录 | 用户本机可访问的基础目录 | `$HOME` |
| iCloud 根目录 | iCloud Drive 在本机的同步目录 | `$HOME/Library/Mobile Documents/com~apple~CloudDocs` |
| 本地原始照片目录 | 本地 RAW/DNG 工作区 | `$HOME/Photograph-Raw` |
| iCloud 原始照片目录 | iCloud RAW/DNG 工作区 | `iCloud Drive/Photograph/Photograph-Raw` |

## 支持的文件类型

支持的照片源文件扩展名必须写入枚举。当前版本只处理枚举中列出的类型，不做“猜测式支持”。

建议定义：

| 枚举值 | 扩展名 | 归属/用途 | 当前版本行为 |
| --- | --- | --- | --- |
| `SONY_ARW` | `.arw` | Sony Alpha RAW | 支持 |
| `DJI_DNG` | `.dng` | DJI DNG | 支持 |

不默认处理的类型：

| 枚举值 | 扩展名 | 归属/用途 | 当前版本行为 |
| --- | --- | --- | --- |
| `CANON_CR2` | `.cr2` | Canon RAW | 不处理 |
| `CANON_CR3` | `.cr3` | Canon RAW | 不处理 |
| `NIKON_NEF` | `.nef` | Nikon RAW | 不处理 |
| `FUJI_RAF` | `.raf` | Fujifilm RAW | 不处理 |
| `OLYMPUS_ORF` | `.orf` | Olympus RAW | 不处理 |
| `PANASONIC_RW2` | `.rw2` | Panasonic RAW | 不处理 |

扩展名匹配必须大小写不敏感，但重命名后保留原扩展名大小写。

`.dng` 不能简单视为统一类型。DJI DNG 和 Adobe DNG 可能有不同来源、元数据结构和命名规则。当前版本只明确支持 DJI DNG。

DJI DNG 识别依据：

- ExifTool 的 `FileType` 应为 `DNG`。
- ExifTool 的 `Make` 或 `Model` 应能识别为 DJI。
- 如果 `.dng` 无法确认为 DJI 来源，当前版本默认不处理，并在 dry-run 中列为不支持文件；如果本次目录没有其他支持的 RAW/DNG，则阻止执行。

## 元数据读取方案

正式实现应使用项目环境管理的 ExifTool 能力作为第一优先级的元数据读取后端，而不是依赖 macOS `file` 命令或只支持 JPEG 的轻量 EXIF 库。

选择 ExifTool 的原因：

- 官方支持 Sony `.ARW`、DJI `.DNG` 以及常见 RAW 格式。
- 能读取 EXIF、XMP、MakerNotes 等多类元数据。
- 支持 JSON 输出，适合 CLI 稳定解析。
- 支持批量处理目录扫描出的文件集合，避免逐文件启动进程带来的性能损耗。
- 跨 macOS、Windows、Linux，可作为项目依赖或项目内二进制能力管理。

实现要求：

- 通过 `pyproject.toml` 和 uv 管理 Python 侧依赖。
- 如果使用 Python wrapper 调用 ExifTool，该 wrapper 必须写入 `pyproject.toml`。
- 如果必须使用 ExifTool 二进制，不要求用户安装到系统目录；应安装或定位在项目虚拟环境或项目工具目录中。
- 脚本启动时先检测项目环境中的 `exiftool` 能力。
- 如果缺少 ExifTool 能力，`scan` 可以降级为只统计文件，但 `rename` 必须阻止执行并提示项目内安装方式。
- 读取元数据时使用 JSON 输出，不解析人类可读文本。
- 只使用 ExifTool 读取元数据，不使用 ExifTool 写入或修改 RAW/DNG 元数据。
- 文件重命名只通过文件系统 rename 完成，不改写照片文件内容。
- 对大量文件使用批量调用，优先使用参数文件或批处理模式，避免每个文件启动一次 `exiftool`。
- 元数据读取层应封装为独立 adapter，便于替换或增加其他后端。

建议读取字段：

```text
FileName
Directory
FileType
Make
Model
DateTimeOriginal
CreateDate
ModifyDate
SubSecDateTimeOriginal
SubSecCreateDate
OffsetTimeOriginal
FileCreateDate
FileModifyDate
```

`FileCreateDate`、`FileModifyDate` 只可用于诊断展示，不能作为 `{date}` 的命名来源。

拍摄时间优先级：

1. `SubSecDateTimeOriginal`
2. `DateTimeOriginal`
3. `SubSecCreateDate`
4. `CreateDate`
5. `ModifyDate`

命名中的 `{date}` 只使用相机写入 RAW/DNG 元数据中的拍摄时间，不做时区转换。`OffsetTimeOriginal` 只作为后续跨时区校正能力的依据。

不允许把目录日期、文件系统创建时间、文件系统修改时间或当前时间作为 `{date}` 的自动回退来源。如果 RAW/DNG 无法读出可用拍摄时间，dry-run 必须报错并阻止处理。

验收要求：

- 用真实 Sony `.ARW` 文件验证可以读出拍摄时间。
- 用真实 DJI `.DNG` 文件验证可以读出拍摄时间。
- 如果 RAW/DNG 无法读出拍摄时间，dry-run 必须列出该文件并阻止默认重命名。错误信息需要明确提示该文件元数据异常，可能是文件损坏、拷贝不完整或不是当前版本支持的 RAW/DNG。

## 命名模板

模板由 token 组成。

推荐 token：

| Token | 含义 | 示例 |
| --- | --- | --- |
| `{folder}` | 当前照片文件所在目录名 | `20260101-上海东方明珠` |
| `{title}` | 目录显示标题，来自 dotfile、批量输入或目录名解析 | `上海东方明珠` |
| `{parent}` | 当前照片文件所在目录的上一级目录名 | `Shanghai` |
| `{relative_dir}` | 当前照片目录相对项目根目录的路径 | `Travel/Shanghai/20260101-上海东方明珠` |
| `{date}` | 拍摄日期时间，支持默认格式和显式格式 | `20260101` |
| `{date:YYYYMMDD}` | 按指定格式输出拍摄日期 | `20260101` |
| `{date:YYMMDD}` | 按指定格式输出拍摄日期 | `260101` |
| `{date:HHMMSS}` | 按指定格式输出拍摄时间 | `080001` |
| `{original}` | 原始文件名，不含扩展名 | `DSC00000` |
| `{camera}` | 相机型号，来自元数据 | `ILCE-7M4` |

默认模板建议：

```text
{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}
```

示例：

```text
20260101-上海东方明珠-080001_DSC00000.ARW
```

这个模板对应三段式命名：`{日期}-{标题}-{其他}`。第一段 `{date:YYYYMMDD}` 来自照片元数据，第二段 `{title}` 来自 dotfile、批量输入或目录名解析，第三段 `{date:HHMMSS}_{original}` 既保留拍摄时间，也保留相机原始编号。

`{date}` 格式规则：

- `{date}` 不带格式时使用默认格式 `YYYYMMDD`。
- `{date:<format>}` 使用显式格式输出日期时间，格式语义按 ISO 8601 的 basic 和 extended 表示形式设计。
- 当前支持的日期格式包括 `YYYYMMDD`、`YYYY-MM-DD`、`YYMMDD`。
- 当前支持的时间格式包括 `HHMMSS`、`HH:mm:ss`。
- 当前支持的日期时间格式包括 `YYYYMMDDTHHMMSS`、`YYYY-MM-DDTHH:mm:ss`。
- 默认文件名模板必须使用不含冒号的 basic 格式，避免跨平台非法字符。
- 当前不支持自然语言月份、星期、时区等格式。
- 如果格式无法解析，或者格式中包含不支持的符号，dry-run 必须报错并阻止执行。
- `{date:HHMMSS}` 取拍摄时间中的时分秒；不再单独提供 `{timestamp}` token。
- 当前版本不支持 `{project_date}`、`{seq}`、`{seq:04}`。

如果同一目录内存在同一秒拍摄的多张照片，`{original}` 可以避免单纯时间戳导致的撞名。工具仍必须在 dry-run 中做最终冲突检测，避免多机位、重复导入或异常文件造成目标名冲突。

## dry-run 预览

执行前必须提供预览。

预览内容：

```text
DSC00000.ARW -> 20260101-上海东方明珠-080001_DSC00000.ARW
DSC00001.ARW -> 20260101-上海东方明珠-080002_DSC00001.ARW
```

预览还需要展示：

- 扫描到的 RAW 数量。
- 扫描到的照片目录数量。
- 将被同步重命名的 sidecar 数量。
- 冲突文件列表。
- 无法读取元数据的文件列表。
- 最终输出目录。
- 将创建或更新的 `.metadata.json` 路径。
- 是否启用 mock 模式。

实际执行前必须先完成一次 dry-run。dry-run 发现任何错误时，实际执行必须停止，用户修正错误后才能重新执行。

实际执行还必须二次确认。脚本需要展示摘要并要求用户输入确认；只有用户明确确认后才能修改文件。`--yes` 可以作为显式跳过交互确认的高级参数，但不能跳过 dry-run 计划校验。

dry-run 必须同时提供结构化计划和面向人的摘要。结构化计划用于未来电脑 Web 端、macOS 端和 iOS 端复用。

结构化计划字段契约属于 TDD 范围，详见 `docs/tdd/README.md`。

## 冲突检测

以下情况必须阻止执行：

- 两个源文件生成同一个目标名。
- 目标文件已经存在且不是本次重命名计划的一部分。
- 模板展开后文件名为空。
- 文件名包含当前操作系统不允许的字符。
- 任何文件缺少命名模板必需的元数据。
- 枚举外扩展名被请求重命名。
- `.metadata.json` 无法写入。

以下情况应给出警告：

- 可选元数据 token 缺失且模板允许空值或回退。
- 目录名包含空格、特殊符号或过长。
- 文件扩展名不在支持列表里，但疑似 RAW 文件。

## Sidecar 策略

RAW/DNG 文件可能存在同 stem 的 sidecar 文件。当前版本以 Lightroom 工作流为目标，必须支持 `.xmp`、`.acr`，以及与 RAW/DNG 同 stem 的机内 JPEG 同步重命名。

示例：

```text
DSC00000.ARW
DSC00000.XMP
DSC00000.JPG
```

当 RAW 被重命名为：

```text
20260101-上海东方明珠-080001_DSC00000.ARW
```

Sidecar 应同步变为：

```text
20260101-上海东方明珠-080001_DSC00000.XMP
20260101-上海东方明珠-080001_DSC00000.JPG
```

默认同步扩展名：

```text
.xmp
.acr
.jpg
.jpeg
```

Sidecar 扩展名也需要写入枚举，并标注用途：

| 枚举值 | 扩展名 | 用途 | 当前版本行为 |
| --- | --- | --- | --- |
| `ADOBE_XMP` | `.xmp` | Adobe sidecar | 自动同步 |
| `ADOBE_ACR` | `.acr` | Adobe Camera Raw sidecar，新版本 Adobe 工作流可能稳定产生 | 存在且与 RAW/DNG 同 stem 时自动同步；不要求每张照片都存在 |
| `CAMERA_JPEG` | `.jpg` / `.jpeg` | 机内 JPEG sidecar | 与 RAW/DNG 同 stem 时自动同步；孤立 JPEG 不独立处理 |

匹配规则：

- Sidecar 只按文件 stem 与 RAW/DNG 匹配，例如 `DSC00000.ARW` 匹配 `DSC00000.XMP`、`DSC00000.JPG`。
- 扩展名匹配大小写不敏感，但 stem 匹配大小写敏感；例如 `DSC00000.ARW` 不匹配 `dsc00000.JPG`。
- 重命名后保留原扩展名大小写。
- `.acr` 是新版本 Adobe 工作流可能产生的 sidecar，存在时必须跟随 RAW/DNG 同步；不存在不视为错误。
- `.jpg`、`.jpeg` 只有在与已支持 RAW/DNG 同 stem 时才作为 sidecar；不匹配 RAW/DNG 的 JPEG 不参与当前版本重命名。
- 如果同一个 stem 下存在多个 RAW/DNG 源文件，dry-run 必须报错并要求用户手工处理，不能猜测 sidecar 归属。

视频文件不定义命名规则，不参与自动重命名。架构保留视频文件管理能力，视频应以独立规则处理 `.mov`、`.mp4`、`.wav` 等文件。

## 批量输入

当需要处理的目录较多时，除了直接传入一个项目根目录，还应支持通过规范的 JSON 或 YAML 文件输入待处理目录列表。

当前版本必须支持 JSON 输入；YAML 不作为必需能力，除非项目已经引入 YAML 解析依赖。

输入文件必须先做结构化格式校验，再进入目录扫描、元数据读取和重命名计划生成。具体校验库不在 PRD 中规定，后续技术设计或 TDD 再定义。

输入模型契约：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `root` | path | 是 | 无 | 项目根目录，可以是绝对路径 |
| `directories` | list[object] | 是 | 无 | 待处理目录配置列表，至少 1 项 |
| `template` | string | 否 | `{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}` | 重命名模板 |
| `strict` | boolean | 否 | `false` | 没有支持 RAW/DNG 的目录是否阻止执行 |

`directories` 每一项的模型契约：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `path` | path | 是 | 无 | 相对 `root` 的待处理目录 |
| `title` | string | 否 | 无 | 目录内照片使用的显示标题，例如 `上海东方明珠` |
| `template` | string | 否 | 无 | 该目录专用重命名模板 |

建议 JSON 格式：

```json
{
  "root": "/Users/example/Photograph-Raw/Travel/Shanghai",
  "directories": [
    {
      "path": "20260101-上海东方明珠",
      "title": "上海东方明珠"
    },
    {
      "path": "20260101-HongKong_Victoria_Peak"
    }
  ],
  "template": "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}"
}
```

输入文件语义：

- `root` 是项目根目录，可以是绝对路径。
- `directories` 是要处理的分类目录配置列表。
- `directories[].path` 必须是相对 `root` 的相对路径。
- `directories[].title` 用于覆盖目录名中的标题部分。例如目录名是 `20260101-HongKong_Victoria_Peak`，但用户希望文件名使用 `Victoria_Peak`，则该目录的 `title` 设置为 `Victoria_Peak`。
- 工具对 `root / directory.path` 进行递归扫描，找到目录下所有支持枚举中的 RAW/DNG 文件。
- 不支持在输入文件中逐个列出照片文件。照片文件必须由工具基于目录扫描得到。
- 根级 `template` 可选，缺省使用默认模板。
- 目录级 `template` 可选，优先级高于根级 `template`。
- `directories[].title` 只对 `path` 指向且直接包含照片文件的目录生效，不递归继承到子照片目录。
- 如果 `path` 是分类容器且目录本身没有照片文件，则该项不允许设置 `title`；dry-run 必须报错并阻止执行。子目录由自己的 `.metadata.json`、批量输入配置或目录名默认解析决定。
- 如果模板使用 `{title}`，但目录配置和 `.metadata.json` 都没有提供 `title`，工具默认从目录名中剥离前缀日期得到标题。例如 `20260101-HongKong_Victoria_Peak` 得到 `HongKong_Victoria_Peak`，不做语义压缩。

校验要求：

- `root` 必须存在且必须是目录。
- `directories` 不能为空。
- `directories[].path` 必须是相对路径，不能包含 `..` 逃逸 `root`。
- `root / directories[].path` 必须存在且必须是目录。
- `directories[].title` 如果存在，不能为空字符串。
- 如果某个目录下没有支持的照片源文件，dry-run 需要给出警告；是否阻止执行由 `strict` 配置决定，当前版本默认警告但不阻止。

## 目录级 dotfile

每个照片目录可以包含一个由本工作流管理的 `.metadata.json`，用于保存当前目录的命名配置、处理状态和原始文件映射。该文件用于简化长期管理：批量输入只需要指定目录，目录自己的命名偏好跟随目录保存。

`.metadata.json` 是目录级元数据规范。同一个目录下的所有照片源文件和 sidecar 必须严格遵守同一套配置，不允许对单个文件设置例外规则。

建议文件名：

```text
.metadata.json
```

目录结构示例：

```text
.
└── 20260101-上海东方明珠
    ├── .metadata.json
    ├── DSC00000.ARW
    └── DSC00001.ARW
```

`.metadata.json` 模型契约：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `version` | integer | 是 | `1` | 元数据格式版本 |
| `title` | string | 否 | 无 | 该目录照片使用的显示标题 |
| `template` | string | 否 | 无 | 该目录专用重命名模板 |
| `status` | string | 否 | `configured` | 目录处理状态，例如 `configured`、`pending`、`renamed`、`rolled_back` |
| `created_at` | datetime | 否 | 无 | 元数据文件创建时间 |
| `updated_at` | datetime | 否 | 无 | 最近一次由工具更新的时间 |
| `files` | list[object] | 否 | `[]` | 原始文件名、当前真实文件名和 pending 目标名的映射 |

版本兼容策略：

- 当前版本只写入 `version = 1`。
- 读取 `.metadata.json` 时必须校验 `version`。
- 缺少 `version`、版本不是整数、版本大于当前支持版本、或版本格式无法识别时，dry-run 必须报错并阻止执行。
- 当前版本不做自动迁移，因为尚未存在历史 schema。
- 后续如果引入 schema 迁移，必须先在 dry-run 中展示迁移计划，实际写入前要求用户确认，并保留回滚依据。

`files` 每一项的模型契约：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `original_name` | string | 是 | 无 | 第一次执行时记录的原始文件名 |
| `current_name` | string | 是 | 无 | 文件系统中当前真实存在的文件名 |
| `planned_name` | string | 否 | 无 | `pending` 状态下计划重命名的目标文件名，执行成功后移除 |
| `role` | string | 是 | 无 | 文件角色，例如 `raw`、`sidecar` |
| `status` | string | 是 | 无 | 文件处理状态，例如 `pending`、`renamed`、`failed`、`rolled_back` |

示例：

```json
{
  "version": 1,
  "title": "上海东方明珠",
  "template": "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}",
  "status": "pending",
  "created_at": "2026-01-01T08:00:01+08:00",
  "updated_at": "2026-01-01T08:00:01+08:00",
  "files": [
    {
      "original_name": "DSC00000.ARW",
      "current_name": "DSC00000.ARW",
      "planned_name": "20260101-上海东方明珠-080001_DSC00000.ARW",
      "role": "raw",
      "status": "pending"
    },
    {
      "original_name": "DSC00000.XMP",
      "current_name": "DSC00000.XMP",
      "planned_name": "20260101-上海东方明珠-080001_DSC00000.XMP",
      "role": "sidecar",
      "status": "pending"
    },
    {
      "original_name": "DSC00000.JPG",
      "current_name": "DSC00000.JPG",
      "planned_name": "20260101-上海东方明珠-080001_DSC00000.JPG",
      "role": "sidecar",
      "status": "pending"
    }
  ]
}
```

处理规则：

- 如果目录内存在 `.metadata.json`，工具必须优先读取该文件，并做结构化格式校验。
- 如果 `.metadata.json` 存在且合法，目录命名配置默认以该文件为准。
- 命令行或批量输入中的目录级 `title` / `template` 可以显式覆盖 `.metadata.json`；覆盖必须在 dry-run 中展示，并在实际执行成功后写回 `.metadata.json`。
- 显式覆盖已有 `title` / `template` 时，工具必须对该目录执行全目录重新规划，不能只影响新增文件。
- 如果 `.metadata.json` 不存在，工具按批量输入或默认规则生成重命名计划，并在 dry-run 中展示将创建该文件。
- 实际重命名前，工具必须先写入或更新 `.metadata.json` 为 `pending` 状态，并保证 `original_name`、`current_name`、`planned_name` 的计划映射已经落盘。
- `current_name` 必须始终表示文件系统中当前真实存在的文件名，不能用来表达未来目标名。
- `planned_name` 只表示 `pending` 状态下的目标文件名；文件 rename 成功后，工具必须把 `current_name` 更新为目标文件名，并移除该条目的 `planned_name`。
- 文件 rename 成功后，工具再把 `.metadata.json` 的目录状态更新为 `renamed`，并把相关文件条目的 `status` 更新为 `renamed`。
- 如果实际执行中途失败，已经成功 rename 的文件条目必须尽量更新 `current_name` 和 `status`；失败条目保留当前真实文件名，并标记为 `failed`，以支持回滚或人工恢复。
- `.metadata.json` 由本工作流产生和维护，用户可以手工编辑，但格式错误会阻止执行。
- `.metadata.json` 不记录单个文件的命名规则，不允许出现 per-file 配置。
- 同一目录内的 RAW/DNG 及其同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` 必须使用同一个 `title`、`template` 和日期格式规则。
- 如果工具发现同一目录内存在不符合 `.metadata.json` 规范的已命名文件，dry-run 必须报告偏差；默认阻止继续执行，直到用户修正文件或显式执行回滚/重新规划。
- `files` 映射在文件第一次纳入工作流时写入。`original_name` 必须表示该文件第一次被工作流接管时的真实原始文件名，不能随着后续重命名而改变。
- 后续全目录重规划允许在 `pending` 状态更新既有条目的 `planned_name`，并在执行成功后更新 `current_name`，但不得修改既有条目的 `original_name`。
- 后续如果发现新增照片，只能追加新的 `files` 条目，不能删除或重建已有条目。
- 回滚必须使用 `.metadata.json` 中的 `files` 映射，将 `current_name` 恢复为 `original_name`。

## 原始文件名来源

`{original}` 必须来自 `.metadata.json` 中首次记录的 `original_name`，不能从当前文件名反推，也不能依赖 RAW/DNG 内部元数据自动恢复。

设计依据：

- ExifTool 的 `FileName`、`Directory` 属于文件系统伪标签，表示当前路径和当前文件名，不是 RAW/DNG 内部稳定保存的原始文件名。
- XMP 中存在类似 `PreservedFileName` 的字段，但不是相机 RAW 文件一定写入的通用标准，也不应作为当前版本的可靠前提。
- 本工作流不写入 RAW/DNG 内容，因此不会把原始文件名嵌入照片文件。
- 即使后续支持把原始文件名写入 XMP sidecar，也只能作为冗余信息；当前版本的真实来源仍然是 `.metadata.json` 中的不可变映射。
- 如果一个文件已经被工作流重命名过，后续再次执行时必须继续使用 `.metadata.json` 中的 `original_name` 展开 `{original}`，避免 `{original}` 变成上一次重命名后的文件名。

配置优先级从高到低：

1. 命令行显式参数。
2. 批量输入中该目录的 `title` / `template`。
3. 目录内 `.metadata.json`。
4. 批量输入根级 `template`。
5. 默认模板和从目录名剥离日期得到的标题。

如果第 1 或第 2 项覆盖了已有 `.metadata.json` 中的 `title` / `template`，工具必须把覆盖结果写回 `.metadata.json`，并执行全目录重规划。

## 操作记录

每次实际执行重命名后，应更新照片目录下的 `.metadata.json`。

记录位置：

```text
.metadata.json
```

建议内容：

```json
{
  "version": 1,
  "title": "上海东方明珠",
  "template": "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}",
  "status": "renamed",
  "created_at": "2026-01-01T08:00:01+08:00",
  "updated_at": "2026-01-01T08:00:02+08:00",
  "files": [
    {
      "original_name": "DSC00000.ARW",
      "current_name": "20260101-上海东方明珠-080001_DSC00000.ARW",
      "role": "raw",
      "status": "renamed"
    },
    {
      "original_name": "DSC00000.XMP",
      "current_name": "20260101-上海东方明珠-080001_DSC00000.XMP",
      "role": "sidecar",
      "status": "renamed"
    },
    {
      "original_name": "DSC00000.JPG",
      "current_name": "20260101-上海东方明珠-080001_DSC00000.JPG",
      "role": "sidecar",
      "status": "renamed"
    }
  ]
}
```

## 回滚要求

当前版本必须支持回滚。回滚不依赖额外的备份文件，而是依赖每个照片目录下 `.metadata.json` 中的 `files` 映射。

回滚规则：

- 回滚脚本读取指定目录的 `.metadata.json`。
- 对每个 `files` 条目，将 `current_name` 恢复为 `original_name`。
- 如果存在 `planned_name` 但 `current_name` 仍等于 `original_name`，说明该文件尚未实际重命名，回滚时只清理 `planned_name` 并更新状态。
- 如果 `files` 映射缺失，禁止回滚。
- 如果 `current_name` 不存在，或 `original_name` 已存在且不是当前映射的一部分，dry-run 必须报错并阻止执行。
- 回滚不会删除 `.metadata.json`；回滚完成后更新目录级 `status`、文件级 `status`、`current_name` 和 `updated_at`。

回滚执行方式：

```text
uv run python scripts/rollback.py ./20260101-上海东方明珠 --dry-run
```

## Mock 模式

必须支持 mock 模式，便于测试和调试。

mock 模式要求：

- 不执行任何实际文件操作。
- 输出完整计划，包括重命名、sidecar 同步、`.metadata.json` 创建或更新。
- 支持模拟错误，例如文件不存在、权限不足、磁盘空间不足、目标路径已存在、ExifTool 读取失败。
- mock 模式可以与 dry-run 同时使用；mock 主要用于模拟环境和错误，dry-run 主要用于展示真实计划。

## 验收标准

- 用户可以指定项目目录和命名模板。
- 工具可以递归扫描多层子目录中的 RAW 文件。
- 工具以照片文件所在目录名作为 `{folder}`，而不是解析项目根目录中的旅游类型或地点。
- 工具可以 dry-run 输出完整重命名计划。
- 工具实际执行前必须已经完成 dry-run 校验，并获得用户确认。
- 发生命名冲突时，不修改任何文件。
- dry-run 阶段发现任意错误都会阻止整个批次执行；实际执行中如果出现文件系统错误，必须保留 `.metadata.json` 映射用于回滚或人工恢复。
- 执行成功后，RAW/DNG 和已识别 sidecar 都完成重命名。
- 执行成功后，照片目录写入或更新 `.metadata.json`。
- 执行成功后，目录下 `.metadata.json` 包含可用于回滚的文件映射，其中 `original_name` 不可变，`current_name` 表示真实当前文件名。
