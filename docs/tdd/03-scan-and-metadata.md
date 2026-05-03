# 扫描与元数据

## 文件扫描

扫描输入为用户指定目录。扫描器只做文件发现和候选分类，不读取大文件内容。

扫描规则：

1. 递归遍历 `root`。
2. 跳过默认排除目录和系统垃圾文件。
3. 按扩展名识别候选照片源文件：`.arw`、`.dng`。
4. 按扩展名识别候选 sidecar：`.xmp`、`.acr`、`.jpg`、`.jpeg`。
5. 孤立 JPEG 只统计为 `other`，不作为源照片处理。
6. 空目录默认跳过。
7. `TODO` 目录默认跳过，除非用户显式指定纳入处理。
8. 发现明显后期软件相关文件时，不处理该文件，并在 rename dry-run 中返回 `post_processor_reference_risk` warning。

扩展名匹配大小写不敏感，重命名后保留原始扩展名大小写。

明显后期软件相关文件包括但不限于：

- `*.lrcat`
- `*.lrdata`
- `*.lrtemplate`
- `*.cosessiondb`
- `*.cocatalogdb`

这些文件不会被 rename 修改。archive 不对它们做特殊处理；如果未命中默认或用户自定义 exclude，则随用户传入目录一起归档。

## ExifTool 集成

ExifTool 是唯一正式元数据读取后端。实现不能依赖 macOS `file` 命令，也不能使用只支持 JPEG 的轻量 EXIF 库读取 RAW。

读取字段：

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

调用要求：

- 使用 `exiftool -json`。
- 使用 `subprocess.run(..., capture_output=True, text=True, check=False)`。
- 大量文件时分批调用，避免命令行参数过长。
- ExifTool 非 0 退出码必须保留 stderr，写入结构化错误。
- 只读元数据，不写 RAW/DNG。

拍摄时间优先级：

1. `SubSecDateTimeOriginal`
2. `DateTimeOriginal`
3. `SubSecCreateDate`
4. `CreateDate`
5. `ModifyDate`

`FileCreateDate`、`FileModifyDate` 只可用于诊断展示，不能作为 `{date}` 的命名来源。

如果 RAW/DNG 无法从照片元数据读取可用拍摄时间，rename dry-run 必须阻止执行，并提示文件元数据异常，可能是文件损坏、拷贝不完整或不是当前版本支持的 RAW/DNG。不允许回退到目录日期、文件系统创建时间、文件系统修改时间或当前时间。

DJI DNG 识别：

- 候选 `.dng` 必须读取 ExifTool 元数据后再确认是否支持。
- `FileType` 必须是 `DNG`。
- `Make` 或 `Model` 必须可识别为 DJI。
- 无法确认为 DJI 来源的 `.dng` 列为不支持文件；如果目录内没有其他支持 RAW/DNG，阻止执行。

## Sidecar 匹配

Sidecar 只能跟随已确认支持的 RAW/DNG，不独立处理。

匹配规则：

- stem 大小写敏感。
- 扩展名大小写不敏感。
- `DSC00000.ARW` 匹配 `DSC00000.XMP`、`DSC00000.JPG`。
- `DSC00000.ARW` 不匹配 `dsc00000.JPG`。
- 同一个 stem 下存在多个 RAW/DNG 源文件时，dry-run 必须报错，不能猜测归属。
- `.acr` 存在时跟随同步，不存在不报错。
- `.jpg`、`.jpeg` 只有与 RAW/DNG 同 stem 时作为 sidecar。
