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

## 命名模板

模板由 token 组成。

推荐 MVP token：

| Token | 含义 | 示例 |
| --- | --- | --- |
| `{folder}` | 当前 RAW 所在目录名 | `Tokyo-Street` |
| `{parent}` | 上一级目录名 | `Japan` |
| `{date}` | 拍摄日期或用户指定日期 | `20260430` |
| `{project_date}` | 项目日期，通常来自目录名或配置 | `20260430` |
| `{seq}` | 序号 | `1` |
| `{seq:04}` | 固定位数序号 | `0001` |
| `{original}` | 原始文件名，不含扩展名 | `DSC01234` |
| `{camera}` | 相机型号，来自元数据 | `ILCE-7M4` |

默认模板建议：

```text
{project_date}_{folder}_{seq:04}
```

## 序号规则

序号需要稳定、可重复。

MVP 排序规则：

1. 优先按拍摄时间排序。
2. 如果拍摄时间不可用，按原始文件名自然排序。
3. 如果仍然冲突，按完整路径排序。

序号作用范围可配置：

- `per-directory`：每个目录从 1 开始，推荐默认值。
- `per-project`：整个项目目录共用一组序号。

## dry-run 预览

执行前必须提供预览。

预览内容：

```text
DSC01234.ARW -> 20260430_Tokyo-Street_0001.ARW
DSC01235.ARW -> 20260430_Tokyo-Street_0002.ARW
```

预览还需要展示：

- 扫描到的 RAW 数量。
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
20260430_Tokyo-Street_0001.ARW
```

伴随文件应同步变为：

```text
20260430_Tokyo-Street_0001.XMP
20260430_Tokyo-Street_0001.JPG
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
  "renameTemplate": "{project_date}_{folder}_{seq:04}",
  "renamedAt": "2026-04-30T20:30:00+08:00",
  "operations": [
    {
      "from": "raw/DSC01234.ARW",
      "to": "raw/20260430_Tokyo-Street_0001.ARW",
      "sidecars": [
        {
          "from": "raw/DSC01234.XMP",
          "to": "raw/20260430_Tokyo-Street_0001.XMP"
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
- 工具可以扫描多层子目录中的 RAW 文件。
- 工具可以 dry-run 输出完整重命名计划。
- 发生命名冲突时，不修改任何文件。
- 执行成功后，RAW 和已识别伴随文件都完成重命名。
- 执行成功后，项目目录写入操作记录。

