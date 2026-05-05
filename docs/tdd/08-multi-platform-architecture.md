# 多端应用技术路线

## 目标

本文件描述脚本、Web UI、macOS App 和 iOS App 共存时的技术路线。它不改变当前版本范围；当前权威业务实现仍是 uv 管理的 Python 核心和脚本入口，本地 Web UI 作为可视化入口复用这些能力。

长期目标是让不同入口共享同一套规则和数据契约，避免形成互相不一致的脚本版、Web 版和移动版。

## 推荐阶段

### 1. Python core 与 scripts

当前阶段继续以 Python 核心逻辑为权威实现。

要求：

- `models`、`domain`、`application`、`ports`、`adapters` 的边界保持稳定。
- `scripts/` 只做参数解析、调用 application 用例、用户确认和结果展示。
- 所有计划对象、错误码和 `.metadata.json` 行为先在 Python 侧稳定。
- 脚本入口持续作为真实目录 smoke test 和批处理入口。

### 2. 本地 Web UI

Web UI 是第一个推荐实现且当前已具备本地版本的图形界面。

推荐技术边界：

- Python 后端复用现有 `application` 层。
- Web API 返回现有 Pydantic 计划对象或等价 JSON。
- 前端只负责目录选择、计划展示、确认、进度和错误呈现。
- Web UI 不解析脚本输出，不复制命名模板、sidecar 匹配或冲突检测规则。

可选目录结构：

```text
apps/web
├── backend
│   └── 调用 photograph_workflow.application
└── frontend
    └── 页面、样式和交互
```

如果采用轻量实现，也可以先把后端和页面放在同一个 `apps/web` 中，等复杂度上升后再拆分。

### 3. 桌面包装 App 与 macOS App

桌面端可以先把 Web UI 包装为 Tauri / Electron 应用，再在规则稳定后建设更原生的 SwiftUI macOS App。

推荐策略：

- 第一阶段优先复用本地 Web UI 或本地 Python 服务。
- 桌面层负责文件夹选择、权限授权、窗口、菜单、通知和应用打包。
- 核心扫描、命名、sidecar、回滚和归档规则仍由 Python core 或共享核心提供。

macOS 原生 SwiftUI 可以作为后续选项，但不应在核心规则尚未稳定时提前重写全部逻辑。

macOS 原生 App 与 Tauri / Electron 桌面包装 App 的详细技术设计见 [09-macos-desktop-app-architecture.md](./09-macos-desktop-app-architecture.md)。

### 4. iOS SwiftUI App

iOS App 应作为长期独立入口规划。

推荐策略：

- UI 使用 SwiftUI。
- 核心规则可以通过 Swift Package 逐步重写。
- 行为一致性依赖共享契约、fixture 和跨语言测试，而不是依赖 Python 运行时。

可选目录结构：

```text
apps/ios
└── PhotographWorkflowApp

packages/swift-workflow-core
└── Sources
```

iOS 侧需要替换的 adapter：

| 能力 | iOS 方向 |
| --- | --- |
| 文件访问 | Files App、document picker、security scoped resource |
| 元数据读取 | iOS 可用的 metadata API 或专门的 RAW metadata reader |
| 用户确认 | SwiftUI confirmation dialog |
| 计划展示 | SwiftUI list/table/detail |
| 长任务 | async task、进度、取消 |
| workspace | iOS 可访问目录授权记录 |

## 共享契约

为了让 Python、Web 和 SwiftUI 保持一致，需要逐步建立 `contracts/`。

建议内容：

```text
contracts
├── metadata.schema.json
├── batch-input.schema.json
├── plan.schema.json
├── errors.md
└── fixtures
    ├── rename-plan-basic.json
    ├── rename-plan-sidecar.json
    └── archive-plan-basic.json
```

当前阶段可以先不生成这些文件，但后续实现桌面包装 App、macOS 原生 App 或 SwiftUI iOS App 前应补齐。

共享契约必须覆盖：

- `.metadata.json`。
- 批量输入 JSON。
- scan、rename、rollback、archive 的计划输出。
- 稳定错误码。
- 命名模板语法。
- sidecar 匹配规则。

## API 边界

Web UI 或 macOS 包装需要 API 时，API 应以 application 用例为边界。

推荐 API 形态：

| API | 对应用例 | 说明 |
| --- | --- | --- |
| `GET /workspaces` | workspace list | 列出已保存工作目录 |
| `POST /scan` | scan | 递归扫描指定 root |
| `POST /rename/plan` | rename dry-run | 只生成重命名计划 |
| `POST /rename/execute` | rename execute | 基于用户确认执行 |
| `POST /rollback/plan` | rollback dry-run | 只生成回滚计划 |
| `POST /rollback/execute` | rollback execute | 基于用户确认执行 |
| `POST /archive-name` | archive_name | 生成推荐压缩包名 |
| `POST /archive/plan` | archive dry-run | 只生成归档计划 |
| `POST /archive/execute` | archive execute | 基于用户确认执行 |

API 不应暴露内部 adapter 细节。路径、错误和计划都通过结构化模型表达。

## 跨端测试策略

多端实现后，测试应分层：

- Python core：继续用 pytest 覆盖 domain、application 和 adapter 行为。
- Web UI：用 API 测试验证结构化响应，用浏览器测试覆盖关键交互。
- macOS App：覆盖目录选择、权限授权和执行确认。
- iOS App：覆盖 Swift core 的命名模板、sidecar 匹配、metadata 读取失败处理和计划展示。
- contracts：用共享 JSON fixture 验证 Python 与 Swift 对同一输入产生一致结果。

真实 RAW/DNG 仍只用于 smoke test，不提交到仓库。

## 风险

### 多套业务规则分叉

如果 Web UI 或 iOS App 复制 Python 逻辑，很容易出现同一目录在不同入口生成不同文件名。

决策：

- Web UI 优先调用 Python application 层。
- iOS 如需重写核心规则，必须基于共享契约和 fixture 验证一致性。

### iOS 文件权限差异

iOS 不能按桌面脚本假设任意读写用户目录。

决策：

- iOS App 作为长期独立入口规划。
- iOS adapter 必须显式处理目录授权、可访问范围和长期访问记录。
- 不把桌面绝对路径作为跨端唯一身份。

### macOS 打包复杂度

macOS App 会引入签名、公证、权限和沙盒问题。

决策：

- 先以本地 Web UI 或 Python 服务包装为主。
- 原生 SwiftUI macOS App 作为后续体验优化，不作为第一阶段目标。

## 当前不实施

当前阶段不实施：

- `apps/macos` 目录。
- `apps/desktop` 目录。
- `apps/ios` 目录。
- `contracts` 目录。
- Swift Package。
- macOS 打包。
- iOS 文件访问。

这些内容只有在进入对应实现计划时再创建。
