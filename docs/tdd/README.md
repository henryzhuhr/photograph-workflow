# Photograph Workflow TDD

## 目标

TDD 记录当前版本的技术设计契约。PRD 只描述产品边界和用户可见行为；字段、模块、流程和数据结构细节在 TDD 中维护。

当前版本交付 uv 管理的 Python 脚本，不要求安装为系统 CLI。核心逻辑必须独立于终端交互，便于未来复用到电脑 Web 端、macOS 端和 iOS 端应用。

技术设计必须为未来迭代留出空间。当前版本只交付本地 Python 脚本，但扫描、命名、校验、metadata、归档和计划生成规则不能和脚本入口、终端交互、Lightroom 或本机文件系统实现强绑定。

## 当前范围

当前版本实现这些能力：

- 递归扫描用户指定目录。
- 识别 Sony `.arw` 与 DJI `.dng` 候选源文件。
- 通过 ExifTool 读取元数据并确认 DJI DNG 来源。
- 按照片文件所在目录和命名模板生成重命名计划。
- 同步处理与 RAW/DNG 同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` sidecar。
- 维护照片目录下 `.metadata.json`。
- 支持 dry-run、实际重命名、回滚。
- 支持用户传入目录整体 ZIP 归档。
- 支持只生成带时间戳的推荐压缩包名，辅助用户手动压缩。

当前版本不实现：

- 图形界面。
- Lightroom catalog 读取或写入。
- Capture One 等其他后期软件适配。
- Lightroom 导出成片管理。
- 自动分类、图片内容识别、自动修图。

## 文档索引

| 文档 | 内容 |
| --- | --- |
| [01-architecture.md](./01-architecture.md) | 技术决策、依赖、目录结构、脚本入口 |
| [02-data-contracts.md](./02-data-contracts.md) | 枚举、Pydantic 模型、结构化计划、错误码 |
| [03-scan-and-metadata.md](./03-scan-and-metadata.md) | 文件扫描、ExifTool、RAW/DNG 识别、sidecar 匹配 |
| [04-rename-and-rollback.md](./04-rename-and-rollback.md) | 命名模板、rename 流程、rollback 流程 |
| [05-archive.md](./05-archive.md) | ZIP 归档、手动压缩命名辅助、exclude 规则 |
| [06-testing.md](./06-testing.md) | mock 后端、测试策略、实现顺序 |
| [07-extensibility.md](./07-extensibility.md) | 多端应用、多后期软件和长期演进边界 |
