# 扩展性设计

## 设计目标

当前版本只实现本地 Python 脚本，但技术设计必须支持长期演进：

- 电脑 Web 端。
- macOS 端。
- iOS 端。
- Capture One 等 Lightroom 之外的后期软件。
- 更复杂的归档、同步和审计能力。

当前版本不实现这些形态，但不能把核心规则写死在脚本、终端文本、Lightroom 术语或本地文件系统细节里。

脚本、Web UI、macOS App 和 iOS App 的具体技术路线见 [08-multi-platform-architecture.md](./08-multi-platform-architecture.md)。

## 稳定核心

以下规则属于长期稳定核心：

- 递归扫描和文件角色分类。
- RAW/DNG 支持判断。
- sidecar 同 stem 匹配。
- `.metadata.json` schema、版本和状态流转。
- 命名模板解析。
- `{original}` 的不可变来源。
- rename dry-run 和实际执行的两阶段模型。
- rollback 基于 `.metadata.json`。
- archive 计划、exclude、命名和结果校验。
- 结构化计划对象和稳定错误码。

这些规则必须放在 `domain`、`application` 和 `models` 层，不能只存在于脚本入口。

## 可替换边界

以下能力必须通过端口或策略隔离：

| 能力 | 当前实现 | 未来扩展 |
| --- | --- | --- |
| 文件访问 | 本地文件系统 | macOS sandbox、iOS document picker、Web 后端存储 |
| 元数据读取 | ExifTool | 平台 metadata API、云端 metadata worker |
| 后期软件策略 | Lightroom sidecar 策略 | Capture One sidecar、软件专用目录规则 |
| 归档执行 | Python ZIP | Keka、系统压缩服务、NAS 或云端归档 |
| 用户确认 | 终端交互 | Web modal、桌面弹窗、移动端确认页 |
| 计划展示 | 终端摘要 | Web 表格、桌面列表、移动端预览 |

核心用例只依赖端口接口，不依赖具体 adapter。

## 多端应用约束

为了未来支持 Web、macOS 和 iOS，当前实现必须满足：

- 业务函数返回 Pydantic 模型或可序列化 dict，不返回仅适合终端阅读的字符串。
- 所有路径在 JSON 输出中使用字符串；Python 内部可以使用 `Path`，但序列化边界不能暴露 Python 专用对象。
- 操作必须支持 dry-run 先行，实际执行必须可以由外部 UI 控制确认。
- 错误必须使用稳定 `code`，UI 可以根据 `code` 做本地化、筛选和高亮。
- 进度、日志、确认、取消不能写死在核心逻辑中。
- 执行操作应预留取消和重试边界，即使当前脚本暂不实现可视化取消。

## 后期软件扩展

当前版本只支持 Lightroom 相关 sidecar 行为，但技术设计不应把后期软件写死为 Lightroom。

建议抽象为 `PostProcessorProfile`：

| 字段 | 说明 |
| --- | --- |
| `name` | 策略名称，例如 `lightroom` |
| `sidecar_extensions` | 当前策略识别的 sidecar 扩展名 |
| `same_stem_required` | sidecar 是否必须与 RAW/DNG 同 stem |
| `required_sidecars` | 是否有必须存在的 sidecar |
| `optional_sidecars` | 可存在但不强制的 sidecar |
| `export_handling` | 导出成片是否纳入当前工具管理 |

当前 `lightroom` profile：

- `sidecar_extensions`: `.xmp`、`.acr`、`.jpg`、`.jpeg`
- `same_stem_required`: true
- `required_sidecars`: 空
- `optional_sidecars`: `.xmp`、`.acr`、`.jpg`、`.jpeg`
- `export_handling`: 当前版本不管理导出成片

未来支持 Capture One 时，应新增 profile，而不是改写 rename 核心流程。

## Schema 演进

`.metadata.json` 是跨端共享数据契约，必须稳定演进：

- 当前只写入 `version = 1`。
- 读取到更高版本必须阻止执行，不能尝试猜测。
- 后续 schema 迁移必须先通过 dry-run 展示迁移计划。
- 实际迁移前必须有用户确认。
- 迁移必须保留回滚依据，尤其不能改写既有 `original_name`。

新增字段优先使用可选字段，避免破坏旧版本读取。字段命名统一使用 snake_case。

## 实现约束

实现时必须避免：

- 在 `scripts/` 中实现命名、扫描、sidecar 或归档规则。
- 在 `domain` 中调用 `subprocess`、`zipfile`、`input()`、`print()`。
- 让错误只存在于文本消息，没有稳定错误码。
- 让 UI 通过解析终端输出理解 dry-run 结果。
- 把 Lightroom 作为模型或模块的唯一上层概念。
- 把本地绝对路径作为跨端数据模型的唯一身份依据。

当前版本可以只提供本地 adapter，但接口边界要先留好。
