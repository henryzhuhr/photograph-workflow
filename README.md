# Photograph Workflow

Photograph Workflow 是一个本地照片文件管理脚本项目，用于在 Lightroom 导入前整理 RAW/DNG 文件名，并在后期完成后辅助归档原始素材目录。

当前版本支持：

- 递归扫描照片目录。
- 读取 Sony `.ARW` 和 DJI `.DNG` 的拍摄时间。
- 按目录标题批量生成重命名计划。
- 同步处理同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` sidecar。
- 写入照片目录下的 `.metadata.json`，记录原始文件名和当前文件名映射。
- 根据 `.metadata.json` 回滚重命名。
- 生成推荐压缩包名称，或把用户指定目录整体打成 ZIP。
- 保存常用 workspace。
- 提供 Tauri/Desktop App 桌面入口。

## 安装

项目使用 `uv` 管理依赖：

```bash
uv sync
```

元数据读取优先使用系统或项目环境中的 `exiftool`。如果当前环境没有 `exiftool`，脚本会自动 fallback 到 Python 依赖 `exifread`，用于读取当前命名所需的基础 EXIF 字段。

## 当前可交付入口

当前可交付入口包括：

1. uv 管理的 Python 脚本。
2. Tauri/Desktop App 桌面应用。

Python 脚本入口：

- `scripts/scan.py`
- `scripts/rename.py`
- `scripts/rollback.py`
- `scripts/archive_name.py`
- `scripts/archive.py`
- `scripts/workspace.py`

当前没有 Web UI 版本，也没有面向用户的浏览器产品版本。后续 iPad 端和 iPhone 端的界面方向以 `docs/ux/` 中的静态原型和说明为准；这些原型只用于设计验证，不执行真实文件操作。

## Tauri/Desktop App

Tauri/Desktop App 是当前可交付的桌面入口，提供原生窗口、本地目录选择器、Finder 集成和最近目录记录。桌面入口复用 Python application 层和结构化计划对象；它不是浏览器 Web UI 版本。

### 前置条件

桌面 App 需要 Node.js、npm、Rust 工具链和项目 Python 依赖。

安装 Python 依赖：

```bash
uv sync
```

安装 Rust 工具链：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

重启 shell 后验证：

```bash
rustc --version
cargo --version
```

### 开发启动

```bash
cd apps/desktop
npm install
npm run tauri dev
```

Tauri 会自动：

1. 启动 Vite 前端开发服务器（端口 `5173`）。
2. 启动 Python 后端（端口 `8000`）。
3. 打开原生 macOS 窗口加载桌面应用。

### 生产构建

```bash
cd apps/desktop
npm install
npm run tauri build
```

构建产物在 `apps/desktop/src-tauri/target/release/bundle/` 下。macOS 构建会生成 `.app` 包。

当前桌面 App 启动时会调用 `uv run uvicorn apps.web.backend.server:app` 拉起本地 Python 后端，因此运行环境仍需要能执行项目 Python 依赖。后续如要做独立分发，需要补齐 Python 后端打包或 sidecar 方案。

## 推荐工作流

1. 把相机存储卡里的 RAW 文件复制到电脑。
2. 手动整理目录，把照片放到分类好的照片目录中。
3. 在 Lightroom 导入前执行 rename dry-run。
4. 确认重命名计划无误后执行 rename。
5. 把稳定命名后的目录导入 Lightroom 修图。
6. 后期完成后按需要生成归档名或压缩 ZIP。

不要在 Lightroom 已经导入并引用这些 RAW 文件后再重命名，否则 Lightroom 可能找不到原文件。

## 目录命名建议

照片文件应放在真正的照片目录中，工具会递归扫描：

```text
Photograph-Raw/
└── Travel/
    └── Shanghai/
        ├── 20260101-上海东方明珠/
        │   ├── DSC00000.ARW
        │   └── DSC00000.XMP
        └── 20260101-武康路/
            └── DSC00001.ARW
```

默认命名模板：

```text
{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}
```

示例输出：

```text
20260101-上海东方明珠-080001_DSC00000.ARW
20260101-上海东方明珠-080001_DSC00000.XMP
```

其中：

- `{date:YYYYMMDD}` 和 `{date:HHMMSS}` 来自 RAW/DNG 元数据中的拍摄时间。
- `{title}` 默认来自照片目录名，例如 `20260101-上海东方明珠` 会得到 `上海东方明珠`。
- `{original}` 来自首次纳入工作流时记录的原始文件名，不含扩展名。

## 扫描目录

只扫描目录，不修改任何文件：

```bash
uv run python scripts/scan.py ~/Photograph-Raw/Travel/Shanghai
```

输出是结构化 JSON，包含每个文件的角色：

- `raw`
- `sidecar`
- `other`

## 重命名预览

强烈建议每次先 dry-run：

```bash
uv run python scripts/rename.py ~/Photograph-Raw/Travel/Shanghai --dry-run
```

如果你使用真实照片目录，也应该先只读预览：

```bash
uv run python scripts/rename.py "$HOME/20260501-「旅游」重庆" --dry-run
```

dry-run 会输出：

- 将被重命名的 RAW/DNG。
- 将跟随重命名的 sidecar。
- 目标文件名。
- 将创建或更新的 `.metadata.json`。
- `warnings` 和 `errors`。

如果 `errors` 非空，不要执行真实重命名。

## 执行重命名

确认 dry-run 输出无误后再执行：

```bash
uv run python scripts/rename.py ~/Photograph-Raw/Travel/Shanghai
```

脚本会再次要求确认。确认后才会修改文件。

如果你明确要跳过交互确认：

```bash
uv run python scripts/rename.py ~/Photograph-Raw/Travel/Shanghai --yes
```

执行前，工具会先在照片目录中写入 `.metadata.json` 的 pending 状态，记录：

- `original_name`
- `current_name`
- `planned_name`
- 文件角色
- 文件状态

执行成功后，`.metadata.json` 会更新为 `renamed` 状态，并保留可回滚映射。

## 批量输入

可以用 JSON 指定多个待处理目录：

```json
{
  "root": "/Users/example/Photograph-Raw/Travel/Shanghai",
  "directories": [
    {
      "path": "20260101-上海东方明珠",
      "title": "上海东方明珠"
    },
    {
      "path": "20260101-HongKong_Victoria_Peak",
      "title": "Victoria_Peak"
    }
  ],
  "template": "{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}",
  "strict": false
}
```

运行：

```bash
uv run python scripts/rename.py --input rename-input.json --dry-run
```

注意：

- `directories[].path` 必须是相对 `root` 的目录。
- 不支持逐个列出照片文件。
- `title` 只对该目录内的照片生效，不递归继承给子照片目录。

## 回滚

如果已经执行过重命名，可以根据照片目录里的 `.metadata.json` 回滚：

```bash
uv run python scripts/rollback.py ~/Photograph-Raw/Travel/Shanghai/20260101-上海东方明珠 --dry-run
```

确认无误后执行：

```bash
uv run python scripts/rollback.py ~/Photograph-Raw/Travel/Shanghai/20260101-上海东方明珠
```

回滚不会删除 `.metadata.json`，只会把 `current_name` 恢复为 `original_name`，并更新状态。

## 归档命名

如果你更喜欢用 Finder、系统压缩或 Keka 手动压缩，可以只生成推荐压缩包名：

```bash
uv run python scripts/archive_name.py ~/Photograph-Raw/Travel/Shanghai
```

示例：

```text
Shanghai~20260101080001.zip
```

## ZIP 归档

先预览：

```bash
uv run python scripts/archive.py ~/Photograph-Raw/Travel/Shanghai --output /Volumes/Archive/Photos --dry-run
```

确认后执行：

```bash
uv run python scripts/archive.py ~/Photograph-Raw/Travel/Shanghai --output /Volumes/Archive/Photos
```

归档规则：

- 按用户传入目录整体打包。
- 不自动按照片目录拆分。
- 不主动识别 Lightroom 导出成片。
- 未命中 exclude 的文件都会进入 ZIP。
- `.metadata.json` 总是保留。
- 默认不覆盖已有 ZIP。

默认排除：

- `.DS_Store`
- `._*`
- `.Spotlight-V100`
- `.Trashes`
- `.fseventsd`
- `Thumbs.db`
- `desktop.ini`
- `*.tmp`
- `*.temp`
- `*.swp`
- `*.part`
- `*.zip`
- `*.7z`
- `*.rar`
- `*.lrdata`

## Workspace

保存常用照片工作目录：

```bash
uv run python scripts/workspace.py add ~/Photograph-Raw --name Photograph-Raw --kind local
```

查看：

```bash
uv run python scripts/workspace.py list
```

设置默认：

```bash
uv run python scripts/workspace.py set-default <workspace-id>
```

移除记录：

```bash
uv run python scripts/workspace.py remove <workspace-id>
```

`remove` 只删除 workspace 记录，不删除真实目录。

Workspace 文件位置：

```text
~/.local/share/photograph-workflow/workspaces.json
```

## 真实照片目录安全规则

真实照片目录默认只读验证。

如果要对真实照片做可写测试：

1. 不要直接操作原目录。
2. 先复制少量样本到仓库的 `./tmp` 下。
3. 复制前检查磁盘空间，确保复制后系统仍至少保留 `30GB` 可用空间。
4. 在 `./tmp` 的副本上执行 rename、rollback 或 archive。

仓库的 `.gitignore` 已忽略 `tmp/`。

## 当前限制

- 当前只明确支持 Sony `.arw` 和 DJI `.dng`。
- 当前不支持 `{camera}`、`{seq}`、`{project_date}`。
- 当前不读取或修改 Lightroom catalog。
- 当前不管理 Lightroom 导出成片。
- 当前不写入 RAW/DNG 元数据。
- 当前没有 Web UI、macOS 原生 App、iPad App 或 iPhone App 的可交付版本。
- 当前 CLI 主要输出结构化 JSON，后续可以继续优化人类可读摘要。
