# RAW 文件重命名需求

## 目标

根据已经分类好的目录，批量重命名目录下的 RAW 文件，并支持用户自定义命名格式。这个功能是整个工作流的核心，因为它决定了后续 Lightroom、导出文件和归档包的可追踪性。

## 支持的文件类型

MVP 建议支持常见 RAW 扩展名：

```text
.arw
.cr2
.cr3
.nef
.nrw
.raf
.orf
.rw2
.dng
.raw
```

扩展名匹配应大小写不敏感，但保留原扩展名大小写。

## 元数据读取方案

正式实现应使用 ExifTool 作为第一优先级的元数据读取后端，而不是依赖 macOS `file` 命令或只支持 JPEG 的轻量 EXIF 库。

选择 ExifTool 的原因：

- 官方支持 Sony `.ARW`、DJI `.DNG` 以及常见 RAW 格式。
- 能读取 EXIF、XMP、MakerNotes 等多类元数据。
- 支持 JSON 输出，适合 CLI 稳定解析。
- 支持批量处理目录或文件列表，避免逐文件启动进程带来的性能损耗。
- 跨 macOS、Windows、Linux，可作为外部依赖安装。

实现要求：

- 启动时检测 `exiftool` 是否可用。
- 如果缺少 `exiftool`，`scan` 可以降级为只统计文件，但 `rename` 必须阻止执行并提示安装。
- 读取元数据时使用 JSON 输出，不解析人类可读文本。
- 只使用 ExifTool 读取元数据，不使用 ExifTool 写入或修改 RAW/DNG 元数据。
- 文件重命名只通过文件系统 rename 完成，不改写照片文件内容。
- 对大量文件使用批量调用，优先使用参数文件或批处理模式，避免每个文件启动一次 `exiftool`。
- 元数据读取层应封装为独立 adapter，后续可以替换或增加其他后端。

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

拍摄时间优先级：

1. `SubSecDateTimeOriginal`
2. `DateTimeOriginal`
3. `SubSecCreateDate`
4. `CreateDate`
5. `ModifyDate`
6. `FileCreateDate`
7. `FileModifyDate`

命名中的 `{timestamp:HHMMSS}` 默认使用相机记录的本地时间，不做时区转换。`OffsetTimeOriginal` 只作为后续跨时区校正能力的依据。

验收要求：

- 用真实 Sony `.ARW` 文件验证可以读出拍摄时间。
- 用真实 DJI `.DNG` 文件验证可以读出拍摄时间。
- 如果某个文件无法读出拍摄时间，dry-run 必须列出该文件，并阻止默认重命名。

## 命名模板

模板由 token 组成。

推荐 MVP token：

| Token | 含义 | 示例 |
| --- | --- | --- |
| `{folder}` | 当前照片文件所在目录名 | `20260501-重庆人民大礼堂` |
| `{parent}` | 当前照片文件所在目录的上一级目录名 | `20260501-「旅游」重庆` |
| `{relative_dir}` | 当前照片目录相对项目根目录的路径 | `day1/20260501-重庆人民大礼堂` |
| `{date}` | 拍摄日期或用户指定日期 | `20260430` |
| `{project_date}` | 项目日期，通常来自目录名或配置 | `20260430` |
| `{timestamp:HHMMSS}` | 拍摄时间，精确到时分秒 | `184126` |
| `{seq}` | 序号 | `1` |
| `{seq:04}` | 固定位数序号 | `0001` |
| `{original}` | 原始文件名，不含扩展名 | `DSC01234` |
| `{camera}` | 相机型号，来自元数据 | `ILCE-7M4` |

默认模板建议：

```text
{folder}-{timestamp:HHMMSS}_{original}
```

示例：

```text
20260501-重庆人民大礼堂-184126_DSC09907.ARW
```

这个模板对应三段式命名：`{日期}-{标题}-{其他}`。其中 `{folder}` 通常已经包含 `{日期}-{标题}`，`{timestamp:HHMMSS}_{original}` 是其他信息，既保留拍摄时间，也保留相机原始编号。

如果同一目录内存在同一秒拍摄的多张照片，`{original}` 可以避免单纯时间戳导致的撞名。工具仍必须在 dry-run 中做最终冲突检测，避免多机位、重复导入或异常文件造成目标名冲突。

## 序号规则

序号需要稳定、可重复。

MVP 排序规则：

1. 优先按拍摄时间排序。
2. 如果拍摄时间不可用，按原始文件名自然排序。
3. 如果仍然冲突，按完整路径排序。

原因：部分相机文件号会从 `DSC09999` 回绕到 `DSC00001`。如果只按文件名排序，同一次拍摄中回绕后的照片会排到前面，导致序号不符合真实拍摄顺序。

序号作用范围可配置：

- `per-directory`：每个目录从 1 开始，推荐默认值。
- `per-project`：整个项目目录共用一组序号。

当默认模板不使用 `{seq}` 时，序号只作为可选的冲突解决策略使用。默认不应自动添加序号，因为 `{original}` 已经提供了较好的可追踪性。

## dry-run 预览

执行前必须提供预览。

预览内容：

```text
DSC09907.ARW -> 20260501-重庆人民大礼堂-184126_DSC09907.ARW
DSC09908.ARW -> 20260501-重庆人民大礼堂-184127_DSC09908.ARW
```

预览还需要展示：

- 扫描到的 RAW 数量。
- 扫描到的照片目录数量。
- 将被同步重命名的伴随文件数量。
- 冲突文件列表。
- 无法读取元数据的文件列表。
- 最终输出目录。

## 冲突检测

以下情况必须阻止执行：

- 两个源文件生成同一个目标名。
- 目标文件已经存在且不是本次重命名计划的一部分。
- 模板展开后文件名为空。
- 文件名包含当前操作系统不允许的字符。

以下情况应给出警告：

- 元数据缺失导致 `{date}` 或 `{camera}` 为空。
- 目录名包含空格、特殊符号或过长。
- 文件扩展名不在支持列表里，但疑似 RAW 文件。

## 伴随文件策略

RAW 文件可能存在同名伴随文件。

示例：

```text
DSC01234.ARW
DSC01234.XMP
DSC01234.JPG
```

当 RAW 被重命名为：

```text
20260501-重庆人民大礼堂-184126_DSC09907.ARW
```

伴随文件应同步变为：

```text
20260501-重庆人民大礼堂-184126_DSC09907.XMP
20260501-重庆人民大礼堂-184126_DSC09907.JPG
```

MVP 同步扩展名：

```text
.xmp
.jpg
.jpeg
.mov
.mp4
.wav
```

如果存在同名视频文件，需要提示用户确认，因为视频不一定是 RAW 的伴随文件。

## 操作记录

每次实际执行重命名后，应写入一份记录文件。

建议路径：

```text
workflow.json
```

建议内容：

```json
{
  "version": 1,
  "projectStatus": "renamed",
  "renameTemplate": "{folder}-{timestamp:HHMMSS}_{original}",
  "renamedAt": "2026-04-30T20:30:00+08:00",
  "operations": [
    {
      "from": "20260501-重庆人民大礼堂/DSC09907.ARW",
      "to": "20260501-重庆人民大礼堂/20260501-重庆人民大礼堂-184126_DSC09907.ARW",
      "sidecars": [
        {
          "from": "20260501-重庆人民大礼堂/DSC09907.XMP",
          "to": "20260501-重庆人民大礼堂/20260501-重庆人民大礼堂-184126_DSC09907.XMP"
        }
      ]
    }
  ]
}
```

## 回滚要求

MVP 可以不提供自动回滚命令，但必须保留足够记录让用户或后续功能完成回滚。

后续版本可提供：

```text
photograph-workflow rename --rollback workflow.json
```

## 验收标准

- 用户可以指定项目目录和命名模板。
- 工具可以递归扫描多层子目录中的 RAW 文件。
- 工具以照片文件所在目录名作为 `{folder}`，而不是解析项目根目录中的旅游类型或地点。
- 工具可以 dry-run 输出完整重命名计划。
- 发生命名冲突时，不修改任何文件。
- 执行成功后，RAW 和已识别伴随文件都完成重命名。
- 执行成功后，项目目录写入操作记录。
