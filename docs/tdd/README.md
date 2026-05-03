# Photograph Workflow TDD

## 目标

本文档记录当前版本的技术设计契约。PRD 只描述产品边界和用户可见行为；字段、模块和数据结构细节在 TDD 中维护。

## 结构化计划契约

业务模块必须返回结构化计划对象，脚本层只负责把计划渲染成终端摘要。dry-run、rename、rollback、archive 都必须使用结构化计划，避免未来电脑 Web 端、macOS 端和 iOS 端重复解析终端文本。

通用计划字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `operation` | string | 是 | `rename`、`rollback`、`archive` 或 `archive_name` |
| `root` | path | 是 | 本次操作的输入目录 |
| `dry_run` | boolean | 是 | 是否为 dry-run |
| `items` | list[object] | 是 | 计划条目列表 |
| `warnings` | list[object] | 是 | 非阻塞警告 |
| `errors` | list[object] | 是 | 阻塞错误 |
| `metadata_changes` | list[object] | 否 | `.metadata.json` 创建或更新计划 |
| `requires_confirmation` | boolean | 是 | 实际执行前是否需要用户确认 |

## Rename Plan

rename 条目至少包含：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_path` | path | 是 | 当前源路径 |
| `target_path` | path | 是 | 计划目标路径 |
| `role` | string | 是 | `raw` 或 `sidecar` |
| `raw_source_path` | path | 否 | sidecar 归属的 RAW/DNG 路径；RAW/DNG 自身可为空 |
| `original_name` | string | 是 | 首次纳入工作流时记录的原始文件名 |
| `current_name` | string | 是 | 文件系统当前真实文件名 |
| `planned_name` | string | 否 | pending 状态下计划目标文件名 |
| `status` | string | 是 | `pending`、`renamed`、`failed`、`rolled_back` 等 |

## Archive Plan

archive 条目至少包含：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_path` | path | 是 | 将检查或纳入归档的源路径 |
| `archive_path` | path | 是 | 目标压缩包路径 |
| `size_bytes` | integer | 否 | 文件大小 |
| `included` | boolean | 是 | 是否纳入归档 |
| `exclude_reason` | string | 否 | 被排除时的原因 |

## Archive Name Plan

手动压缩辅助只生成推荐压缩包名称，不执行压缩。

字段至少包含：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_dir` | path | 是 | 用户选择的目录 |
| `archive_name` | string | 是 | 推荐压缩包文件名 |
| `archive_path` | path | 否 | 如果提供输出目录，则返回完整目标路径 |
| `archived_at` | datetime | 是 | 用于命名的归档时间 |

## Rollback Plan

rollback 条目至少包含：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `current_path` | path | 是 | 当前真实文件路径 |
| `target_original_path` | path | 是 | 回滚目标路径 |
| `role` | string | 是 | `raw` 或 `sidecar` |
| `status` | string | 是 | 回滚计划状态 |
