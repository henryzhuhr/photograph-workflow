# 技术架构

## 技术决策

| 项 | 决策 |
| --- | --- |
| 项目管理 | uv |
| 运行语言 | Python |
| Python 版本 | 优先兼容 Python 3.12+；不依赖 Python 3.14 独有特性 |
| 结构化模型 | Pydantic `BaseModel` |
| 元数据读取 | ExifTool JSON 输出 |
| 文件操作 | Python 标准库 `pathlib`、`os`、`shutil`、`zipfile` |
| 测试框架 | pytest |

`pyproject.toml` 当前声明 `requires-python = ">=3.14"`。实现前应调整为项目实际可用版本，例如 `>=3.12`，除非确认本机和 CI 都稳定使用 Python 3.14。

## 架构原则

当前版本是 Python 脚本项目，但实现必须按可复用核心设计：

- 核心规则不依赖 `argparse`、终端输入、终端颜色、桌面通知或具体 UI。
- 核心规则不直接调用 ExifTool、文件系统 rename、ZIP 写入或 Lightroom 相关能力。
- 脚本入口只做参数解析、确认、进度展示和摘要渲染。
- dry-run、rename、rollback、archive、archive_name 都返回结构化计划对象。
- Web、macOS、iOS 或后续桌面端应该复用同一套计划对象和错误码，而不是解析命令行输出。
- 当前版本只支持 Lightroom 工作流，但核心模型不得命名为 Lightroom 专用概念；`.xmp`、`.acr`、机内 JPEG 等规则应通过 sidecar 策略表达。
- 用户选择过的工作目录需要以稳定契约保存，当前版本采用 Linux/XDG 风格路径，未来 App 复用同一契约。

## 分层边界

推荐分为 5 层：

| 层 | 职责 | 允许依赖 |
| --- | --- | --- |
| `models` | Pydantic 数据契约、枚举、计划对象、错误对象 | 标准库、Pydantic |
| `domain` | 扫描分类、sidecar 匹配、命名模板、冲突校验、状态流转规则 | `models` |
| `application` | 编排 scan、rename、rollback、archive 用例，返回结构化计划 | `models`、`domain`、`ports` |
| `ports` | 工作区解析、文件系统、元数据读取、归档、时钟、确认、后期软件策略接口 | `models` |
| `adapters` | ExifTool、本地文件系统、zipfile、终端脚本等具体实现 | `ports`、标准库、外部工具 |

依赖方向只能从外层指向内层。`domain` 不能反向依赖 `adapters`，否则未来做 Web/macOS/iOS 时会被本地脚本实现锁死。

## 依赖策略

运行依赖建议：

- `pydantic`：批量输入、metadata、计划对象、错误对象的结构化校验。

开发依赖建议：

- `pytest`：单元测试和集成测试。

ExifTool 作为外部能力管理：

- Python 代码通过 adapter 调用 ExifTool。
- 不要求用户把 ExifTool 安装到系统目录。
- 可以优先查找项目工具目录、虚拟环境可执行路径，再查找 `PATH`。
- 缺少 ExifTool 时，`scan` 可以降级为扩展名统计；`rename` 必须阻止执行。

## 推荐目录结构

```text
.
├── scripts
│   ├── scan.py
│   ├── rename.py
│   ├── rollback.py
│   ├── archive.py
│   └── archive_name.py
├── src
│   └── photograph_workflow
│       ├── __init__.py
│       ├── config.py
│       ├── errors.py
│       ├── application
│       │   ├── __init__.py
│       │   ├── scan.py
│       │   ├── rename.py
│       │   ├── rollback.py
│       │   ├── archive.py
│       │   └── archive_name.py
│       ├── domain
│       │   ├── __init__.py
│       │   ├── scanner.py
│       │   ├── sidecar.py
│       │   ├── naming_template.py
│       │   ├── sanitize.py
│       │   ├── workflow_state.py
│       │   ├── metadata_record.py
│       │   ├── conflicts.py
│       │   └── extensions.py
│       ├── ports
│       │   ├── __init__.py
│       │   ├── workspace_resolver.py
│       │   ├── filesystem.py
│       │   ├── metadata_reader.py
│       │   ├── archive_writer.py
│       │   ├── clock.py
│       │   ├── confirmation.py
│       │   └── post_processor.py
│       ├── adapters
│       │   ├── __init__.py
│       │   ├── workspace_xdg.py
│       │   ├── filesystem_local.py
│       │   ├── metadata_exiftool.py
│       │   ├── archive_zipfile.py
│       │   └── terminal.py
│       ├── mock.py
│       └── models
│           ├── __init__.py
│           ├── input.py
│           ├── metadata.py
│           ├── plan.py
│           └── photo.py
└── tests
```

## 脚本入口

脚本只负责参数解析、调用业务模块、输出摘要和用户确认，不承载业务规则。

| 脚本 | 作用 |
| --- | --- |
| `scripts/scan.py` | 扫描目录，输出候选文件、支持文件和跳过原因 |
| `scripts/rename.py` | 生成或执行重命名计划 |
| `scripts/rollback.py` | 根据 `.metadata.json` 生成或执行回滚计划 |
| `scripts/archive.py` | 生成或执行 ZIP 归档计划 |
| `scripts/archive_name.py` | 只生成推荐压缩包名称，不执行压缩 |

推荐命令：

```text
uv run python scripts/scan.py <root>
uv run python scripts/rename.py <root> --dry-run
uv run python scripts/rename.py <root>
uv run python scripts/rename.py --input rename-input.json --dry-run
uv run python scripts/rollback.py <photo-dir> --dry-run
uv run python scripts/archive.py <root> --output <archive-dir> --dry-run
uv run python scripts/archive_name.py <root>
```

脚本入口调用 `application` 层用例。用例返回结构化计划后，脚本再决定如何展示文本、是否请求用户确认、是否执行实际操作。

## Workspace 持久化

当前版本支持用户显式传入任意可访问的 `root` 路径，也支持保存用户选择过的常用工作目录。显式传入的 `root` 永远优先。

工作目录配置使用 Linux/XDG 风格用户级数据目录：

```text
~/.local/share/photograph-workflow/workspaces.json
```

当前本地 adapter 负责读写这个文件。未来 Web、macOS、iOS 入口可以复用相同数据契约，但替换目录选择、权限授权和持久化 adapter。

## 端口设计

核心用例通过端口访问外部能力：

| 端口 | 当前适配器 | 未来替换方向 |
| --- | --- | --- |
| `WorkspaceResolverPort` | XDG workspace 文件 | macOS 安全书签、iOS document picker、Web 用户空间 |
| `FileSystemPort` | 本地文件系统 | macOS sandbox 文件访问、安全书签、Web 后端存储 |
| `MetadataReaderPort` | ExifTool JSON | 平台原生 metadata API、服务端 metadata worker |
| `ArchiveWriterPort` | Python `zipfile` | Keka 集成、系统压缩服务、远端归档任务 |
| `ClockPort` | 系统时间 | 测试固定时间、平台统一时间源 |
| `ConfirmationPort` | 终端确认 | Web modal、macOS/iOS native dialog |
| `PostProcessorProfilePort` | Lightroom sidecar 策略 | Capture One、Adobe Bridge、其他后期软件策略 |

端口返回的数据必须转换为 `models` 中的结构化对象。adapter 捕获的异常不能直接向上抛出给脚本层，而应转换为稳定错误码和 `PlanIssue`。

## 扩展策略

新增平台或后期软件时，优先新增 adapter 或 profile：

- 新增 Web/macOS/iOS 入口时，只新增 UI 层和必要 adapter，不复制 `domain` 规则。
- 新增 Capture One 支持时，只新增 `PostProcessorProfile` 和必要 sidecar 策略，不改写 rename 主流程。
- 新增归档后端时，只新增 `ArchiveWriterPort` 的 adapter，不改变 archive 计划契约。
- 新增 metadata 后端时，只新增 `MetadataReaderPort` 的 adapter，不改变拍摄时间选择规则。

更多长期演进约束见 [07-extensibility.md](./07-extensibility.md)。
