# Lightroom 边界与原始素材归档需求

## 目标

明确 Lightroom 导出后的成片不由工具管理，同时对 RAW/DNG 原始素材目录提供可重复、可验证的压缩归档能力。

## Lightroom 阶段边界

当前版本不直接控制 Lightroom，也不读取 Lightroom catalog。

工具负责：

- 提醒用户在重命名完成后再导入 Lightroom。
- 管理 RAW/DNG 及其附属文件的命名一致性。
- 可选地归档原始素材目录。

工具不负责：

- 自动套用 Lightroom 预设。
- 自动评级、筛选或修图。
- 直接写入 Lightroom catalog。
- 指定 Lightroom 导出目录。
- 检查 Lightroom 导出结果。
- 移动、重命名、归档 Lightroom 导出后的成片。
- 管理导入 Apple Photos 系统相册后的文件。

## 导出边界

Lightroom 导出后的文件由用户自行处理。典型流程是：

```text
.
└── Lightroom 导出成片
    └── 用户直接导入 Apple Photos 系统相册
```

产品决策：

- 不提供导出目录配置。
- 不要求项目目录内存在 `exports/`。
- 不把导出成片纳入归档包。
- 不校验导出文件数量。

## 归档输入

默认纳入归档：

- RAW/DNG 原始照片文件。
- 同名附属文件，例如 `.xmp`、`.acr`、机内直出 JPEG。
- 每个照片目录下的 `.metadata.json`。
- 用户手写的说明文件，例如 `README.md`、`notes.md`。

默认排除：

- `.DS_Store`
- `Thumbs.db`
- 临时文件。
- 系统缓存文件。
- 已存在的历史压缩包。
- 可重新生成的预览缓存。

## 归档包命名

默认模板：

```text
{project_date}-{project_name}-{archived_date}.zip
```

示例：

```text
20260101-Shanghai_Oriental_Pearl-20260101.zip
```

推荐 token：

| Token | 含义 | 示例 |
| --- | --- | --- |
| `{project_date}` | 项目日期 | `20260101` |
| `{project_name}` | 项目名称 | `Shanghai_Oriental_Pearl` |
| `{folder}` | 项目目录名 | `20260101-Shanghai_Oriental_Pearl` |
| `{archived_date}` | 归档日期 | `20260101` |

## 归档位置

当前版本支持两类位置：

- 项目目录内的 `archive/`。
- 用户指定的外部归档目录，例如移动硬盘或 NAS 挂载路径。

如果目标归档包已存在，默认行为是阻止覆盖。用户可以显式选择：

- 生成带序号的新文件名。
- 覆盖旧归档包。

覆盖行为必须二次确认。

## 归档前检查

归档前需要展示预览：

- 项目目录路径。
- 归档输出路径。
- 将纳入归档的文件数量。
- 将纳入归档的总大小。
- 被排除的文件数量。
- RAW 文件数量。
- 附属文件数量。

阻塞条件：

- 项目目录不存在。
- 输出目录不可写。
- 归档包目标路径已存在且用户未确认覆盖。
- 没有找到任何 RAW 文件。

警告条件：

- 存在已重命名照片但对应目录缺少 `.metadata.json`。
- 项目状态不是 `renamed` 或 `editing`。

## 归档后校验

归档完成后至少校验：

- 压缩包文件存在。
- 压缩包大小大于 0。
- 压缩包内文件数与预览计划一致。

可选增强：

- 写入 SHA-256 校验和。
- 生成归档 manifest。
- 对压缩包执行完整解包测试。

## 操作记录

归档完成后更新相关照片目录下的 `.metadata.json`。

建议结构：

```json
{
  "status": "archived",
  "archive": {
    "created_at": "2026-01-01T08:00:01+08:00",
    "path": "archive/20260101-Shanghai_Oriental_Pearl-20260101.zip",
    "format": "zip",
    "file_count": 245,
    "size_bytes": 4294967296
  }
}
```

## 验收标准

- 用户可以指定项目目录和归档输出位置。
- 工具可以在压缩前展示归档计划。
- 默认不会覆盖已有压缩包。
- 压缩完成后可以确认归档包存在且内容数量符合计划。
- `.metadata.json` 会记录归档结果。
- 工具不会读取、检查或归档 Lightroom 导出后的成片。
