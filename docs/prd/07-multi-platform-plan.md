# 多端应用规划

## 目标

本项目长期希望同时支持这些使用入口：

- Python 脚本：面向当前个人工作流，作为最直接、最稳定的自动化入口。
- 本地 Web UI：作为开发调试入口和桌面包装 App 的前端基础，不作为面向用户的浏览器产品版本。
- 桌面 / macOS App：面向桌面端目录授权、Finder 集成和打包分发场景，包含 Tauri / Electron 包装和 SwiftUI 原生路线。
- iPad App：面向触摸屏、双栏工作台和外部存储访问场景。
- iPhone App：面向单列向导、现场检查和移动端轻量操作场景。

当前可交付版本以 Python 核心和脚本入口为权威实现，并已提供本地 Web UI。桌面包装 App、macOS 原生 App、iPad App 和 iPhone App 仍处于设计阶段，不在当前代码实现范围内。

## 产品路线

推荐路线：

```text
第一步：继续稳定 Python 核心逻辑和脚本入口
        ↓
第二步：增加本地 Web UI，复用 Python application 层（已具备本地版本）
        ↓
第三步：将 Web UI 或本地服务包装为桌面 App / macOS App
        ↓
第四步：在规则稳定后建设原生 SwiftUI iPad / iPhone App
```

这条路线的核心判断是：先把扫描、命名、校验、sidecar、回滚、归档和错误处理稳定下来，再扩展 UI。UI 不应该重新定义业务规则。

## 当前脚本入口

当前脚本入口继续保留，并作为后续所有图形界面的行为基准。

脚本入口需要持续满足：

- 能直接处理本地照片目录。
- 所有危险操作都先支持 dry-run。
- 输出结构化计划对象。
- 不依赖本地 Web UI、macOS、iPad 或 iPhone UI。
- 不把交互提示、终端文本或命令行参数作为核心业务规则。

即使未来有桌面、iPad 和 iPhone App，脚本仍然应该可用，方便批处理、排障和真实目录 smoke test。

## 本地 Web UI

本地 Web UI 是当前已存在的可视化实现基础，但不是面向用户的浏览器产品版本。

本地 Web UI 的职责是：

- 复用 Python application 层，验证结构化计划和错误展示。
- 为桌面包装 App 提供可复用前端基础。
- 用于开发调试、内部验证和本地 smoke test 辅助。
- 在 Docker 或普通浏览器环境下不承诺完整本地目录选择体验。

Web UI 不应该解析脚本输出，而应该直接调用 Python application 层，或通过本地 API 获取结构化计划。

## macOS App

macOS App 作为第二阶段建设目标。

可接受的路线有两种：

- 先将 Web UI 与 Python 本地服务包装成 macOS App。
- 后续如有必要，再建设更原生的 SwiftUI macOS App。

macOS App 的重点不在于重新实现业务规则，而在于改善这些体验：

- 文件夹选择。
- 最近工作目录。
- 本地权限授权。
- 执行前确认。
- 长任务进度。
- 错误展示。
- 手动压缩包命名辅助。

macOS App 必须遵守当前核心规则：不写 RAW/DNG 元数据，不绕过 dry-run，不破坏 `.metadata.json.original_name` 的不可变性。

macOS 原生 App 与 Tauri / Electron 桌面包装 App 的详细产品设计见 [08-macos-desktop-app-design.md](./08-macos-desktop-app-design.md)。

## iPad / iPhone App

iPad App 和 iPhone App 是长期方向，建议在核心规则和数据契约稳定后再实现。

iPad / iPhone App 应使用原生 SwiftUI。它可以和 Python 项目放在同一个仓库中，但不应假设能直接复用 Python 运行时。

iPad / iPhone 端需要单独处理：

- 文件访问权限。
- 外部存储或 Files App 目录授权。
- RAW/DNG 元数据读取能力。
- sidecar 文件同目录匹配。
- 长任务进度和取消。
- iPad 双栏工作台和 iPhone 单列向导上的计划预览与错误展示。

未来 iPad / iPhone App 优先复用这些跨端契约：

- `.metadata.json` schema。
- 批量输入 JSON schema。
- dry-run 计划结构。
- 稳定错误码。
- 命名模板语法。
- sidecar 匹配规则。

如果 iPad / iPhone 端不能直接复用 Python 核心逻辑，应在 Swift 侧重写核心规则，并通过共享契约和测试用例保持行为一致。

## 建议仓库结构

长期可以按 monorepo 组织：

```text
.
├── src/photograph_workflow
│   └── Python 核心逻辑
├── scripts
│   └── Python 脚本入口
├── apps
│   ├── web
│   │   └── Web UI
│   ├── desktop
│   │   └── Tauri / Electron 桌面包装 App
│   ├── macos
│   │   └── SwiftUI 原生 macOS App
│   └── ios
│       └── SwiftUI iPad / iPhone App
├── contracts
│   └── JSON Schema、OpenAPI、示例计划和跨端 fixture
└── packages
    └── swift-workflow-core
        └── 未来 Swift Package，承载 iPad/iPhone/macOS 端可复用规则
```

当前阶段不需要一次性创建这些目录。只有当对应入口开始实现时，才新增目录和构建配置。

## 跨端一致性原则

无论入口是脚本、本地 Web UI、桌面包装 App、macOS 原生 App、iPad App 还是 iPhone App，都必须保持一致：

- `{date}` 只能来自照片元数据，读取失败必须报错，不生成依赖日期的目标文件名。
- 默认命名模板保持 `{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}`。
- `.metadata.json` 使用 snake_case 字段名。
- `.metadata.json.files[].original_name` 一旦记录，不得因后续重命名而改变。
- RAW/DNG 与同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` sidecar 同步处理。
- 只处理照片文件所在目录，不要求顶层分类目录有照片文件。
- 实际重命名、回滚和归档必须先生成可预览计划。
- 核心逻辑不得写 RAW/DNG 元数据。

## 不做什么

当前桌面 / macOS / iPad / iPhone 计划阶段不做：

- 不打包 macOS App。
- 不实现 Tauri / Electron 桌面包装 App。
- 不实现 iPad App。
- 不实现 iPhone App。
- 不接入 Capture One。
- 不把 Python 核心逻辑迁移到 Swift。
- 不改变当前脚本使用方式。
