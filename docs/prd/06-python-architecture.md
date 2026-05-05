# Python 技术架构设计

## 定位

当前版本使用 Python 实现，并用 uv 管理项目环境。交付形态以可直接执行的 `.py` 脚本和本地 Web UI 为主，不要求安装成系统 CLI。

这份 PRD 文档只描述产品层面的技术边界。具体模块、接口、数据模型和执行流程以 [TDD 文档](../tdd/README.md) 为准。

## 长期扩展原则

长期方向上，这套工作流可能扩展为桌面包装 App、macOS 原生 App 和 iOS App，也可能扩展到 Capture One 等其他后期软件。当前版本不实现桌面包装 App、macOS 原生 App 或 iOS App，也不支持 Lightroom 之外的后期软件；但产品设计、数据契约和核心逻辑边界必须避免和单一脚本入口强绑定，保证后续可以复用同一套扫描、命名、校验和归档规则。

因此当前 Python 实现必须满足：

- 脚本入口只做参数解析、用户确认、摘要展示和调用业务模块。
- 扫描、命名、校验、回滚和归档规则必须放在可复用核心模块。
- dry-run 计划、错误列表、metadata 更新计划和归档计划都必须是结构化数据。
- 终端文本输出只是展示层，不能成为 Web/macOS/iOS 未来集成的解析依据。
- 文件系统访问、ExifTool 调用、归档写入、用户确认和后期软件策略必须有可替换边界。
- `.metadata.json` 是跨端共享的数据契约，字段命名、状态流转和版本兼容策略必须稳定。
- 用户选择过的工作目录保存为 workspace 数据，便于脚本和未来 App 自动加载。

## 分层边界

推荐架构以 TDD 为准，核心分为：

| 层 | 职责 |
| --- | --- |
| `models` | Pydantic 数据契约、枚举、计划对象、错误对象 |
| `domain` | 扫描分类、sidecar 匹配、命名模板、冲突校验、状态流转规则 |
| `application` | 编排 scan、rename、rollback、archive 用例，返回结构化计划 |
| `ports` | 工作区解析、文件系统、元数据读取、归档、时钟、确认、后期软件策略接口 |
| `adapters` | ExifTool、本地文件系统、zipfile、终端脚本等具体实现 |

依赖方向只能从外层指向内层。`domain` 不能依赖 `adapters`，脚本入口也不能承载业务规则。

## uv 项目管理

项目使用 uv 管理 Python 版本、依赖和执行环境。

推荐执行方式：

```text
uv run python scripts/scan.py <project-dir>
uv run python scripts/rename.py <project-dir> --dry-run
uv run python scripts/archive.py <project-dir> --dry-run
```

原则：

- 当前版本不要求 `pip install -e .` 后生成系统命令。
- 脚本可以直接执行，便于用户按本地工作流调用。
- 公共逻辑仍放在 `src/photograph_workflow/`，避免脚本之间复制代码。
- 未来如果增加桌面包装、macOS 原生或 iOS 入口，应复用 application/domain/models 层或共享契约，而不是重新实现命名规则。

## 当前版本技术边界

当前版本：

- 使用 ExifTool JSON 输出读取 RAW/DNG 元数据。
- 只读调用 ExifTool，不写 RAW/DNG。
- 支持 Sony `.arw` 和可确认为 DJI 来源的 `.dng`。
- 支持 Lightroom 工作流中的 `.xmp`、`.acr` 和同 stem 机内 JPEG sidecar。
- 使用 `.metadata.json` 保存目录级配置、状态和原始文件映射。
- 使用 `~/.local/share/photograph-workflow/workspaces.json` 保存用户选择过的工作目录。
- 支持 dry-run、实际重命名、回滚、ZIP 归档和归档命名辅助。

当前版本不实现：

- macOS 原生 App。
- 桌面包装 App。
- 移动端界面。
- Capture One profile。
- Lightroom catalog 读写。
- 导出成片管理。

## 详细设计索引

- [技术架构](../tdd/01-architecture.md)
- [数据契约](../tdd/02-data-contracts.md)
- [扫描与元数据](../tdd/03-scan-and-metadata.md)
- [重命名与回滚](../tdd/04-rename-and-rollback.md)
- [归档](../tdd/05-archive.md)
- [测试与实现顺序](../tdd/06-testing.md)
- [扩展性设计](../tdd/07-extensibility.md)
