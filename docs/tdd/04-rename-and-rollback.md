# 重命名与回滚

## 命名模板

默认模板：

```text
{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}
```

支持 token：

| Token | 说明 |
| --- | --- |
| `{folder}` | 当前照片文件所在目录名 |
| `{title}` | 目录显示标题 |
| `{parent}` | 父目录名 |
| `{relative_dir}` | 相对项目根目录路径 |
| `{date}` | 默认 `YYYYMMDD` |
| `{date:<format>}` | 显式日期时间格式 |
| `{original}` | `.metadata.json` 首次记录的原始文件名，不含扩展名 |
| `{camera}` | 相机型号 |

日期格式：

- `YYYYMMDD`
- `YYYY-MM-DD`
- `YYMMDD`
- `HHMMSS`
- `HH:mm:ss`
- `YYYYMMDDTHHMMSS`
- `YYYY-MM-DDTHH:mm:ss`

模板解析失败、未知 token、非法日期格式、生成空文件名、生成非法文件名时，dry-run 必须报错并阻止执行。

`{date}` 只来自 RAW/DNG 元数据中的拍摄时间。不允许回退到目录日期、文件系统创建时间、文件系统修改时间或当前时间。当前版本不支持 `{project_date}`、`{seq}`、`{seq:04}`。

配置优先级从高到低：

1. 命令行显式参数。
2. 批量输入中该目录的 `title` / `template`。
3. 目录内 `.metadata.json`。
4. 批量输入根级 `template`。
5. 默认模板和从目录名剥离日期得到的标题。

如果命令行或批量输入覆盖已有 `.metadata.json` 中的 `title` / `template`，rename 计划必须展示覆盖内容，并在实际执行成功后写回 `.metadata.json`。

## Rename 流程

rename 分为计划阶段和执行阶段。

计划阶段：

1. 扫描项目根目录。
2. 按扩展名找到候选照片源文件。
3. 用 ExifTool 批量读取候选文件元数据。
4. 确认当前版本支持的 RAW/DNG。
5. 按已确认 RAW/DNG 的 stem 匹配 sidecar。
6. 按照片文件直接父目录分组。
7. 读取或创建目录级 `.metadata.json` 计划。
8. 计算 `title`、`template`、`original_name`。
9. 展开目标文件名。
10. 检测既有 `.metadata.json` 映射与当前文件系统是否一致。
11. 检测冲突、非法文件名、目标路径存在、metadata 可写性。
12. 发现明显后期软件相关文件时，加入 `post_processor_reference_risk` warning。
13. 返回结构化 RenamePlan。

如果发现同一目录内存在已由工作流接管、但不符合当前 `.metadata.json` 规范的文件，dry-run 必须报告偏差并默认阻止继续执行，直到用户修正文件或显式执行回滚/重新规划。

如果命令行或批量输入显式覆盖已有 `.metadata.json` 中的 `title` / `template`，必须对该照片目录执行全目录重规划。重规划只更新 `planned_name`，不得删除既有条目，不得改写既有 `original_name`。

如果扫描发现新增 RAW/DNG 或新增同 stem sidecar，只能追加新的 `.metadata.json.files` 条目。当前版本不提供自动清理失效条目的能力；未来如需清理，应单独设计 metadata repair/prune 操作。

执行阶段：

1. 要求已有无错误 dry-run 计划。
2. 用户确认，或显式传入 `--yes`。
3. 写入或更新 `.metadata.json` 为 `pending`。
4. 在 `files` 中写入 `original_name`、真实 `current_name`、目标 `planned_name`。
5. 执行文件系统 rename。
6. 成功条目更新 `current_name`，移除 `planned_name`，状态改为 `renamed`。
7. 全部成功后目录状态改为 `renamed`。
8. 中途失败时，尽量写回真实 `current_name` 和 `failed` 状态，供回滚或人工恢复。

## Rollback 流程

rollback 只依赖 `.metadata.json`。

计划阶段：

1. 读取照片目录 `.metadata.json`。
2. 校验 `version` 和 `files`。
3. 对每个条目生成 `current_name -> original_name` 的回滚计划。
4. 如果存在 `planned_name` 且 `current_name == original_name`，只清理 `planned_name` 和状态。
5. 检查 `current_name` 是否存在。
6. 检查 `original_name` 目标是否冲突。
7. 返回结构化 RollbackPlan。

执行阶段：

1. 要求 dry-run 无错误。
2. 用户确认。
3. 执行文件 rename。
4. 更新 `current_name`、文件级 `status`、目录级 `status`、`updated_at`。
5. 不删除 `.metadata.json`。
