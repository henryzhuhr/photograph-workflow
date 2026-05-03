# 归档

## Archive 流程

当前归档单位是用户传入目录整体，不自动按照片目录拆分。archive 不关心目录里是否存在 Lightroom、Capture One、导出成片或其他后期软件相关文件；未命中默认或用户自定义 exclude 的文件会随目录一起归档。

输入：

- `source_dir`
- `output_dir`
- 可选 `archived_at`
- 可选 `overwrite`

计划阶段：

1. 校验输入目录存在。
2. 根据用户传入目录名和当前时间生成归档包名。
3. 应用预定义 exclude 规则和用户配置 exclude 规则。
4. 保证 `.metadata.json` 总是纳入归档。
5. 统计文件数量、总大小、RAW/DNG 数量、sidecar 数量、排除数量。
6. 检查输出目录可写和目标 ZIP 是否存在。
7. 如果目标 ZIP 已存在且未显式允许覆盖，返回阻塞错误。
8. 如果 `overwrite = true`，计划仍必须设置 `requires_confirmation = true`。
9. 如果存在已重命名照片但对应目录缺少 `.metadata.json`，返回非阻塞警告。
10. 返回结构化 ArchivePlan。

执行阶段：

1. 要求 dry-run 无错误。
2. 用户确认；覆盖已有 ZIP 时必须二次确认。
3. 使用 `zipfile` 创建 ZIP。
4. 保留用户传入目录下的内部层级。
5. 校验 ZIP 存在、大小大于 0、文件数量符合计划。
6. 不写回 `.metadata.json`。

预定义排除规则：

- `.DS_Store`
- `._*`
- `.Spotlight-V100`
- `.Trashes`
- `.fseventsd`
- `Thumbs.db`
- `desktop.ini`
- `*.tmp`
- `*.temp`
- `*.swp`
- `*.part`
- `*.zip`
- `*.7z`
- `*.rar`
- `*.lrdata`

## Archive Name 流程

`archive_name` 只生成推荐压缩包名称，不执行压缩。

输入：

- `source_dir`
- 可选 `output_dir`
- 可选 `archived_at`

输出：

- `archive_name`
- 可选 `archive_path`
- `archived_at`
- 如果提供 `output_dir` 且推荐 `archive_path` 已存在，返回 `archive_name_target_exists` warning，不阻止输出名称。

命名规则：

```text
{folder}~{YYYYMMDDHHMMSS}.zip
```

示例：

```text
Shanghai~20260101080001.zip
```
