# macOS 与桌面包装 App 技术设计

## 目标

本文描述 macOS 原生 App 与 Tauri / Electron 桌面包装 App 的技术边界。当前只做设计，不创建应用代码。

核心目标是：桌面入口可以改进目录选择、权限授权和系统集成，但不能复制或分叉现有 Python 核心规则。

## 总体架构

长期架构应保持如下依赖方向：

```text
apps/macos               apps/desktop                apps/web
        │                         │                    │
        └─────────────── UI / native bridge ───────────┘
                                  │
                         local API / application use cases
                                  │
src/photograph_workflow/application
                                  │
src/photograph_workflow/domain
                                  │
src/photograph_workflow/models
```

约束：

- UI 层不能解析终端输出。
- UI 层不能重新实现命名模板、sidecar 匹配、冲突检测或 `.metadata.json` 写入规则。
- 文件修改必须通过 application 用例产生计划并执行。
- Python 脚本继续作为最小可靠入口和 smoke test 基准。

## 共享契约

桌面应用开始实现前，应优先稳定这些契约：

- `.metadata.json` schema。
- scan / rename / rollback / archive 计划对象。
- 错误码和错误详情结构。
- 命名模板语法。
- sidecar 匹配规则。
- 真实目录 smoke test 说明。

如果未来 Swift 侧重写部分核心规则，必须用相同 fixture 验证 Python 与 Swift 对同一输入产生一致结果。

## 桌面包装 App

桌面包装 App 复用 `apps/web/frontend`，通过 Tauri 或 Electron 提供浏览器无法提供的本地能力。

推荐优先评估 Tauri：

- 包体通常更小。
- native bridge 能力清晰。
- 适合把当前本地 Web UI 包装为桌面应用。

Electron 可以作为备选：

- 生态成熟。
- 调试工具完整。
- 如果后续需要复杂 Node 生态集成，落地成本可能更低。

### 运行模型

桌面包装 App 可以采用两种运行模型：

| 模型 | 说明 | 适用阶段 |
| --- | --- | --- |
| 本地服务模型 | 桌面壳启动本地 Python 服务，前端通过 `127.0.0.1` API 调用 | 优先推荐，复用当前 Web UI 和后端 |
| 直接调用模型 | 桌面壳通过 bridge 调用打包后的核心命令或库 | 后续优化，减少本地端口和进程管理 |

本地服务模型必须只监听 `127.0.0.1`，不能默认暴露到局域网或公网。

### Native bridge 能力

桌面壳只暴露必要的本地能力：

| Bridge 能力 | 说明 |
| --- | --- |
| `choose_directory` | 打开系统目录选择器，返回用户授权目录 |
| `get_recent_workspaces` | 返回最近工作目录 |
| `forget_workspace` | 移除最近工作目录记录 |
| `reveal_in_finder` | 在 Finder 中显示目录或文件 |
| `copy_archive_name` | 复制推荐压缩包名 |
| `open_external_app` | 后续可用于打开 Lightroom，默认不自动执行 |

扫描、重命名、回滚和归档不应直接做成 bridge 内部逻辑。它们应继续走 application 用例或本地 API。

### 权限与路径限制

桌面包装 App 必须限制文件访问范围：

- 只能处理用户通过目录选择器授权过的目录。
- 执行前再次展示 dry-run 计划。
- 不允许前端任意传入系统路径后直接修改文件。
- 最近目录记录应支持用户删除。
- 授权失效时必须重新选择目录。

如果包装 App 使用本地服务，服务端也必须校验 root 是否属于当前授权目录集合，不能只信任前端。

### 打包注意事项

桌面包装 App 不应要求普通用户预装 `uv`、Python 或 Node。

可接受方向：

- 将 Python 后端打包为独立可执行文件。
- 或随 App 内置 Python 运行时和依赖。
- ExifTool 能力随 App 管理，避免依赖用户系统全局安装。

打包后仍必须遵守当前规则：不写 RAW/DNG 元数据，只读取照片元数据并操作文件名。

## macOS 原生 App

macOS 原生 App 使用 SwiftUI 构建 UI，并在需要系统能力时使用 AppKit。

### 目录选择

目录选择使用 `NSOpenPanel`：

- 只允许选择目录。
- 允许用户授权照片项目根目录。
- 选择成功后保存 security-scoped bookmark。
- 下次启动时尝试恢复 bookmark。
- 恢复失败时提示用户重新授权。

App 内部不应把绝对路径作为唯一身份。路径可以用于展示，权限和可恢复访问应以 bookmark 为准。

### 核心逻辑集成

原生 macOS App 有两条集成路线：

| 路线 | 说明 | 约束 |
| --- | --- | --- |
| 调用本地 Python 能力 | SwiftUI 负责 UI 和权限，业务规则仍由 Python application 层执行 | 适合早期，能最大化复用现有实现 |
| Swift Workflow Core | 用 Swift Package 重写稳定规则，macOS 和 iOS 共用 | 必须通过 contracts 和 fixture 保持行为一致 |

早期不建议直接在 SwiftUI 层重写重命名规则。SwiftUI 层应调用结构化用例，并展示计划对象。

### 文件访问

原生 App 在 sandbox 场景下必须显式管理目录访问：

- 对用户选择的目录调用 security-scoped resource 访问。
- 长任务执行期间保持访问有效。
- 任务结束后释放访问。
- 文件读写失败时返回结构化错误，而不是吞掉异常。

所有文件修改仍必须先生成计划，再由用户确认。

### 元数据读取

当前技术决策中，ExifTool 是正式元数据读取后端。

macOS 原生 App 早期应通过 Python 能力或随 App 管理的 ExifTool adapter 读取元数据。未来如果 Swift 侧替换元数据读取实现，必须先验证 Sony ARW、DJI DNG 和错误 RAW 样例的行为一致性。

元数据读取失败时应返回“文件可能损坏或元数据不可读”的错误，并停止依赖 `{date}` 的重命名操作。

## 本地 API 边界

桌面入口需要 API 时，应复用现有 application 用例。

推荐 API 继续保持：

| API | 说明 |
| --- | --- |
| `GET /workspaces` | 列出最近工作目录 |
| `POST /scan` | 扫描 root |
| `POST /rename/plan` | 生成重命名计划 |
| `POST /rename/execute` | 执行已确认的重命名 |
| `POST /rollback/plan` | 生成回滚计划 |
| `POST /rollback/execute` | 执行已确认的回滚 |
| `POST /archive-name` | 生成推荐压缩包名 |
| `POST /archive/plan` | 生成归档计划 |
| `POST /archive/execute` | 执行已确认的归档 |

API 返回结构化 JSON。桌面入口和 Web UI 都不解析人类可读摘要。

## 测试策略

桌面应用实现后需要新增测试层：

- Python core：继续用 `uv run pytest` 覆盖核心规则。
- Web API：覆盖结构化请求、计划响应、错误码和授权 root 校验。
- 桌面包装 App：覆盖目录选择 bridge、最近目录、服务启动和关键页面流程。
- macOS 原生 App：覆盖 bookmark 恢复、授权失效、执行确认和错误展示。
- 真实目录 smoke test：用本地 `tmp` 副本验证 ARW/DNG 元数据读取、sidecar 同步和 `.metadata.json` 写入。

真实 RAW/DNG 不提交到仓库。

## 仓库结构建议

进入实现阶段后，可以按如下结构扩展：

```text
apps
├── web
│   └── 已存在的本地 Web UI
├── desktop
│   └── Tauri 或 Electron 包装 App
└── macos
    └── SwiftUI 原生 macOS App

contracts
└── JSON Schema、OpenAPI、fixtures

packages
└── swift-workflow-core
    └── 未来 macOS / iOS 共享核心
```

当前设计阶段不创建这些新目录。

## 风险与决策

### 规则分叉

风险：Python、Web、Tauri/Electron 和 Swift 各自实现一套命名规则。

决策：除非进入 Swift Workflow Core 阶段，否则所有入口都调用 Python application 层或共享核心。

### 权限模型不一致

风险：脚本可以访问任意路径，桌面 App 只能访问用户授权目录。

决策：桌面入口必须把授权目录作为 workspace 访问边界。API 不能只信任前端传来的路径。

### 打包体积和依赖

风险：Python、ExifTool、Web 运行时和桌面壳会增加包体。

决策：先接受桌面包装 App 的体积成本，用它验证桌面 UX；原生 SwiftUI App 等规则稳定后再建设。

### App Store 与公证

风险：macOS App 会涉及签名、公证、sandbox、ExifTool 打包和本地服务权限。

决策：早期优先面向个人本地使用和开发者签名分发；等核心能力稳定后再评估 App Store 分发。
