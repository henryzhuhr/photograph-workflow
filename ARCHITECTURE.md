# ARCHITECTURE

## 技术栈

### 核心后端

| 技术 | 用途 |
|---|---|
| **Python 3.12+** | 核心业务逻辑 |
| **uv** | 包管理器 |
| **FastAPI** | REST API 框架 |
| **Uvicorn** | ASGI 服务器 |
| **Pydantic 2.x** | 数据校验与结构化模型 |
| **exiftool** (系统级) / **exifread** | EXIF 元数据读取 |
| **Ruff** | Linter |
| **pytest** | 测试框架 |

### Web 前端

| 技术 | 用途 |
|---|---|
| **Vue 3** | UI 框架 |
| **TypeScript 5.7** | 类型安全 |
| **Vite 6** | 构建工具与开发服务器 |
| **vue-i18n** | 国际化（中/英） |

### 桌面 App

| 技术 | 用途 |
|---|---|
| **Tauri 2** | 桌面应用框架 |
| **Rust** (edition 2021) | Tauri 原生后端（文件对话框、剪贴板、工作区持久化） |
| **@tauri-apps/api 2** | JS ↔ Rust 桥接 |
| **tauri-plugin-dialog** | 原生目录选择器 |
| **tauri-plugin-clipboard-manager** | 系统剪贴板 |

### 基础设施

| 技术 | 用途 |
|---|---|
| **Docker** (node:22 + python:3.12-slim) | 多阶段构建 |
| **Docker Compose** | 单服务编排 (127.0.0.1:51173) |

---

## 架构模式：六边形架构（Ports & Adapters）

```
┌─────────────────────────────────────────────┐
│                   scripts                    │  CLI 入口（argparse）
├─────────────────────────────────────────────┤
│                application                   │  用例编排（scan / rename / rollback / archive）
├─────────────────────────────────────────────┤
│                  domain                      │  核心规则（命名模板、冲突检测、sidecar 匹配）
├─────────────────────────────────────────────┤
│                  models                      │  Pydantic 结构化契约（Photo / Plan / Metadata）
├─────────────────────────────────────────────┤
│          ports          │                    │  抽象接口（Filesystem / MetadataReader / ArchiveWriter）
├──────────────────────────┤                   │
│        adapters          │                   │  具体实现（exiftool / local fs / ZIP / XDG / terminal）
└──────────────────────────┴───────────────────┘
```

- `models/` — 稳定的 Pydantic 数据契约，不依赖任何外部实现
- `domain/` — 扫描、命名、sidecar 匹配、冲突检测、归档规则
- `application/` — 编排用例，返回结构化计划对象（scan plan / rename plan / rollback plan / archive plan）
- `ports/` — 定义外部能力接口（filesystem、metadata_reader、archive_writer、workspace_resolver、post_processor）
- `adapters/` — 对接本地文件系统、ExifTool、ZIP 压缩、XDG 目录、终端 I/O
- `scripts/` — 解析 CLI 参数 → 调用 application 用例 → 确认执行 → 输出摘要

核心原则：**domain 和 application 不依赖任何具体 UI 或文件系统实现**，便于未来复用到桌面端、iPad 端和 iPhone 端。

---

## 桌面 App 运行时架构

```
┌───────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Tauri (Rust) │────▶│  Vue 3 前端      │────▶│  FastAPI 后端    │
│  原生能力      │     │  (WebView)       │     │  (uvicorn :8000) │
│  • 目录选择   │     │  • 工作区面板    │     │  • /api/* 路由   │
│  • 剪贴板     │     │  • 扫描/重命名   │     │  • application   │
│  • 工作区持久化│     │  • 回滚/归档     │     │  • domain        │
│  • Finder 打开 │     │  • i18n          │     │  • adapters      │
└───────────────┘     └──────────────────┘     └─────────────────┘
       ▲                        │                        │
       │  Tauri IPC             │  HTTP fetch            │  uv 子进程
       └────────────────────────┘                        │
                                                         │
  Tauri 启动时 spawn uv run uvicorn，关闭窗口时 kill 子进程
```

- 桌面 App 代码位于 `apps/desktop/`，复用 `apps/web/frontend/` 的 Vue 组件
- 平台检测 (`platform.ts`) 判断运行环境：Tauri（`window.__TAURI_INTERNALS__`）或浏览器
- 开发时 Vite dev server 在 `:5173`，代理 `/api` 到后端 `:8000`

---

## 源码目录

```
photograph-workflow/
├── src/photograph_workflow/     # Python 核心
│   ├── models/                  # Pydantic 数据模型
│   ├── domain/                  # 核心业务规则
│   ├── application/             # 用例编排
│   ├── ports/                   # 抽象接口
│   └── adapters/                # 具体实现
├── apps/
│   ├── web/frontend/            # Vue 3 Web 前端
│   └── desktop/                 # Tauri 桌面 App（复用 web 前端）
├── scripts/                     # CLI 脚本入口
├── tests/                       # pytest 测试
├── docs/
│   ├── prd/                     # 产品需求文档
│   ├── tdd/                     # 技术设计文档
│   └── ux/                      # UX 原型
└── pyproject.toml               # Python 项目配置
```
