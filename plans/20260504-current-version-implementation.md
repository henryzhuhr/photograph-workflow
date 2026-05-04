# 当前版本实现计划

## 目标

按照现有 PRD/TDD 落地 Photograph Workflow 当前版本，让用户可以用 `uv run python scripts/*.py` 完成本地照片工作流中的扫描、重命名预览、实际重命名、回滚、归档命名、ZIP 归档和 workspace 管理。

完成后应具备：

- 递归扫描用户指定目录，识别 Sony `.arw` 与 DJI `.dng` 候选源文件。
- 通过 ExifTool JSON 输出读取 RAW/DNG 元数据，确认 DJI DNG 来源，并读取拍摄时间。
- 基于照片文件所在目录、`.metadata.json`、批量输入和命名模板生成 rename dry-run 计划。
- 同步处理与 RAW/DNG 同 stem 的 `.xmp`、`.acr`、`.jpg`、`.jpeg` sidecar。
- 执行真实 rename 前写入 pending `.metadata.json`，执行后维护可回滚的文件映射。
- 基于 `.metadata.json` 执行 rollback dry-run 和 rollback。
- 对用户传入目录整体生成 archive plan、推荐归档名和 ZIP 文件。
- 维护 `~/.local/share/photograph-workflow/workspaces.json`，支持常用工作目录管理。

当前计划不做：

- 图形界面。
- Lightroom catalog 读取或写入。
- Capture One 等其他后期软件适配。
- Lightroom 导出成片管理。
- 自动分类、图片内容识别、自动修图。

## 背景

相关文档：

- PRD 总览：`docs/prd/README.md`
- RAW 重命名需求：`docs/prd/02-raw-renaming.md`
- Lightroom 边界与归档需求：`docs/prd/03-export-archive.md`
- 产品范围与实现约束：`docs/prd/04-roadmap.md`
- TDD 总览：`docs/tdd/README.md`
- 技术架构：`docs/tdd/01-architecture.md`
- 数据契约：`docs/tdd/02-data-contracts.md`
- 扫描与元数据：`docs/tdd/03-scan-and-metadata.md`
- 重命名与回滚：`docs/tdd/04-rename-and-rollback.md`
- 归档：`docs/tdd/05-archive.md`
- 测试策略：`docs/tdd/06-testing.md`
- 扩展性设计：`docs/tdd/07-extensibility.md`

当前仓库状态：

- 项目已有 PRD、TDD、`AGENTS.md` 和 `PLANS.md`。
- `pyproject.toml` 当前仍声明 `requires-python = ">=3.14"`，TDD 要求实现前调整为 `>=3.12`，除非确认本机和 CI 都稳定使用 Python 3.14。
- 当前没有可用的 `src/photograph_workflow` 实现、脚本入口或测试。

真实数据参考：

- 用户提供了一个真实工作目录：`~/20260501-「旅游」重庆`。
- 当前只读检查结果：目录约 `9.5G`，包含 `248` 个 `.arw` 文件。
- 当前可见结构包含 `TODO` 和多个 `20260501-*` 照片子目录；计划中不记录更细的真实子目录名，避免泄露拍摄细节。
- 当前环境未在 `PATH` 中找到 `exiftool`；实现 ExifTool adapter 后，需要先解决项目环境中的 ExifTool 能力，再用该目录做真实读取验收。
- 当前实现已加入 uv 管理的 Python fallback `exifread`；当 ExifTool 二进制不存在时，仍可读取常见 TIFF-based RAW/DNG 的基础 EXIF 字段，用于当前版本的 `{date}` 命名。
- 该目录只能作为真实验收样本，不得在开发测试中直接修改、重命名或写入 `.metadata.json`。如果需要可写样本，必须复制到仓库内 `./tmp`，且复制前确认复制后系统仍至少保留 `30GB` 可用空间。

关键约束：

- 核心规则必须独立于终端交互，便于未来复用到电脑 Web 端、macOS 端和 iOS 端。
- `scripts/` 只做参数解析、确认、进度展示和摘要渲染，不承载业务规则。
- `domain` 不能直接调用 ExifTool、文件系统 rename、ZIP 写入、`input()` 或 `print()`。
- 所有外部输入、`.metadata.json`、结构化计划和错误对象使用 Pydantic `BaseModel` 校验。
- JSON 字段统一使用 `snake_case`，路径序列化为字符串。
- 不修改 RAW/DNG 内容，不写入 RAW/DNG 元数据。
- `{date}` 只能来自 RAW/DNG 元数据中的拍摄时间，不允许回退到目录日期、文件系统时间或当前时间。
- `.metadata.json.files` 采用 append-only 语义；既有条目不能被删除、重建或改写 `original_name`。
- 当前版本不支持 `{camera}`、`{seq}`、`{project_date}`。

## 决策

- 决策：当前版本使用 Python 3.12+。
  原因：TDD 明确要求不依赖 Python 3.14 独有特性。
  影响：实现时先调整 `pyproject.toml`，并避免使用 3.13/3.14 专属语法。

- 决策：核心分层采用 `models`、`domain`、`application`、`ports`、`adapters`。
  原因：后续 Web、macOS、iOS 和其他后期软件需要复用核心逻辑。
  影响：脚本入口不能直接实现扫描、命名、sidecar、metadata 或归档规则。

- 决策：ExifTool 作为优先元数据读取后端，`exifread` 作为 uv 管理的 Python fallback。
  原因：ExifTool 覆盖更完整；但当前项目需要在没有系统 ExifTool 时仍能读取 Sony `.ARW` 的基础拍摄时间。
  影响：有 ExifTool 时优先调用 ExifTool JSON；没有 ExifTool 时使用 `exifread` 读取 `FileType`、`Make`、`Model`、`DateTimeOriginal` 等当前命名所需字段。

- 决策：默认命名模板为 `{date:YYYYMMDD}-{title}-{date:HHMMSS}_{original}`。
  原因：同时保留拍摄日期、目录标题、拍摄时间和相机原始编号。
  影响：命名模板解析必须支持 `{date:<format>}` 和 `{original}` 的稳定来源。

- 决策：sidecar 只按同 stem 匹配。
  原因：`.xmp`、`.acr`、机内 JPEG 都应作为 RAW/DNG 的伴随文件，而不是独立照片。
  影响：孤立 JPEG 不处理；同 stem 多 RAW/DNG 必须报 `sidecar_ambiguous`。

- 决策：归档按用户传入目录整体打包。
  原因：用户希望自己决定归档粒度，电脑端也可能手动压缩。
  影响：archive 不主动识别导出成片或后期软件文件，只应用默认和自定义 exclude。

- 决策：workspace 使用 Linux/XDG 风格路径。
  原因：用户已确认按 XDG 习惯保存常用工作目录。
  影响：当前版本写入 `~/.local/share/photograph-workflow/workspaces.json`。

## 待确认问题

无。当前计划按现有 PRD/TDD 直接实现；如果实现过程中发现 PRD/TDD 冲突，应暂停实现并生成 review 文档。

## 实施步骤

- [ ] 脚手架与依赖
  - 调整 `pyproject.toml`：`requires-python = ">=3.12"`。
  - 添加运行依赖 `pydantic`。
  - 添加开发依赖 `pytest`。
  - 建立 `src/photograph_workflow`、`scripts`、`tests` 目录。
  - 为各层添加 `__init__.py`。

- [ ] Pydantic 模型与错误码
  - 实现 `FileRole`、`SourceFileType`、`SidecarFileType`、`DirectoryStatus`、`FileStatus`、`WorkspaceKind`。
  - 实现 `WorkspaceFile`、`WorkspaceEntry`、`WorkspaceCommandInput`。
  - 实现 `BatchInput`、`DirectoryInput`。
  - 实现 `MetadataFile`、`MetadataFileEntry`。
  - 实现 `CommonPlan`、`RenamePlanItem`、`ArchivePlan`、`ArchivePlanItem`、`ArchiveNamePlan`、`RollbackPlanItem`、`PlanIssue`。
  - 实现稳定错误码常量，覆盖 TDD 中的错误和警告。

- [ ] Ports 与 fake/mock adapter
  - 定义 `WorkspaceResolverPort`、`FileSystemPort`、`MetadataReaderPort`、`ArchiveWriterPort`、`ClockPort`、`ConfirmationPort`、`PostProcessorProfilePort`。
  - 提供 fake/mock adapter，支持测试模拟文件不存在、权限不足、磁盘空间不足、目标路径已存在、ExifTool 缺失、ExifTool 失败、metadata 写入失败、ZIP 创建失败。

- [ ] Domain 规则
  - 实现扩展名枚举和大小写不敏感匹配，重命名后保留原扩展名大小写。
  - 实现扫描分类：supported RAW/DNG、unsupported candidate、sidecar、other。
  - 实现 DJI DNG 识别：`FileType = DNG` 且 `Make` 或 `Model` 可识别为 DJI。
  - 实现 ExifTool JSON 字段解析和拍摄时间优先级。
  - 实现 `{date:<format>}` 模板解析，支持 TDD 列出的日期、时间和日期时间格式。
  - 实现 `{title}` 来源解析和目录名剥离日期逻辑。
  - 实现 `{original}` 来源：优先使用 `.metadata.json.files[].original_name`，首次纳入时记录当前真实文件名 stem。
  - 实现文件名 sanitize、非法字符检测和空文件名检测。
  - 实现 sidecar 同 stem 匹配，包含 `.xmp`、`.acr`、`.jpg`、`.jpeg`。
  - 实现 rename 冲突检测、目标存在检测、metadata deviation 检测。

- [ ] Metadata 读写与状态流转
  - 读取 `.metadata.json` 时校验 `version = 1`。
  - 缺少版本、版本非法或高于当前支持版本时报 `metadata_version_unsupported`。
  - 不存在 `.metadata.json` 时生成创建计划。
  - 实际 rename 前写入或更新 `pending` 状态。
  - 成功 rename 后更新 `current_name`、移除 `planned_name`、状态改为 `renamed`。
  - 中途失败时尽量写回真实 `current_name` 和 `failed` 状态。
  - 全目录重规划只能更新 `planned_name`，不能改写既有 `original_name`。

- [ ] Application 用例
  - `scan`：递归扫描目录，返回候选文件、支持文件和跳过原因。
  - `rename` dry-run：生成结构化 RenamePlan，包含 items、warnings、errors、metadata_changes、requires_confirmation。
  - `rename` execute：要求无错误计划和用户确认，执行文件系统 rename 并更新 metadata。
  - `rollback` dry-run/execute：根据 `.metadata.json.files` 生成和执行 `current_name -> original_name`。
  - `archive_name`：生成 `{folder}~{YYYYMMDDHHMMSS}.zip`，不创建文件。
  - `archive` dry-run/execute：按用户传入目录整体打包，应用 exclude，校验 ZIP 文件数。
  - `workspace`：list/add/set-default/remove，只操作 workspace 记录，不删除真实目录。

- [ ] Local adapters
  - `metadata_exiftool`：批量调用 ExifTool JSON 输出，捕获错误并转换为 `PlanIssue`。
  - `filesystem_local`：封装路径存在性、目录扫描、rename、metadata JSON 读写、文件大小统计。
  - `archive_zipfile`：封装 ZIP 创建和归档后校验。
  - `workspace_xdg`：读写 `~/.local/share/photograph-workflow/workspaces.json`。
  - `terminal`：渲染摘要、读取用户确认；核心层不依赖它。

- [ ] Scripts
  - `scripts/scan.py`
  - `scripts/rename.py`
  - `scripts/rollback.py`
  - `scripts/archive.py`
  - `scripts/archive_name.py`
  - `scripts/workspace.py`
  - 所有脚本都调用 application 用例，支持输出结构化 JSON 或人类摘要；实际修改前必须确认。

- [ ] 测试
  - 添加单元测试覆盖模型校验、模板解析、sidecar 匹配、DJI DNG 判断、ExifTool JSON 解析、sanitize、冲突检测、metadata 状态、archive exclude、workspace 命令。
  - 添加集成测试覆盖 fixture 项目目录扫描、rename dry-run、rename execute、rollback、archive_name、archive。
  - 用 fake/mock adapter 测试错误路径，不依赖真实照片文件。

- [ ] 验收与收尾
  - 运行 `uv run pytest`。
  - 运行 `git diff --check`。
  - 使用本地私有 Sony `.ARW` 和 DJI `.DNG` 做手工 smoke test，确认 ExifTool 可读拍摄时间；不提交真实照片文件。
  - 更新本计划的“进度记录”和“结果”。

## 验证方式

基础检查：

```text
git diff --check
uv run pytest
```

脚本 smoke test 建议：

```text
uv run python scripts/scan.py <fixture-root>
uv run python scripts/rename.py <fixture-root> --dry-run
uv run python scripts/rename.py --input <rename-input.json> --dry-run
uv run python scripts/rollback.py <fixture-photo-dir> --dry-run
uv run python scripts/archive_name.py <fixture-root>
uv run python scripts/archive.py <fixture-root> --output <tmp-archive-dir> --dry-run
uv run python scripts/workspace.py list
```

真实文件验收：

- 真实目录优先使用 `~/20260501-「旅游」重庆` 做只读扫描和元数据读取验收。
- 如果需要验证真实 rename/rollback，先从真实目录复制少量样本到 `./tmp/real-sample-*`，不要整目录直接操作；复制前先检查目录大小和磁盘可用空间，确保复制后系统仍至少保留 `30GB` 可用空间。
- 如果确实需要复制完整目录，必须先确认可用空间大于 `目录大小 + 30GB`，并明确复制目标在 `./tmp` 下；验收完成后可以删除 `./tmp` 中的副本。
- Sony `.ARW` 能读取拍摄时间。
- DJI `.DNG` 能读取拍摄时间，并能确认 DJI 来源。
- 同 stem `.xmp`、`.acr`、`.jpg`、`.jpeg` 能跟随 RAW/DNG 重命名。
- RAW/DNG 无可用拍摄时间时，rename dry-run 返回 `capture_time_missing` 并阻止执行。

## 回滚与失败处理

- 纯代码变更可通过 git revert 或丢弃未提交修改回退。
- 自动化测试不得修改真实私人照片目录。
- `~/20260501-「旅游」重庆` 只能只读使用；任何会写入、重命名、生成 `.metadata.json` 或执行 rollback/archive 的验证，都必须使用 `./tmp` 中的副本。
- 复制真实样本前必须检查磁盘空间，保证复制后仍保留至少 `30GB` 可用空间；如果不满足条件，只能使用少量文件子集或跳过真实可写验收。
- rename 执行前必须先落盘 pending `.metadata.json`，确保中途失败后仍可根据映射回滚或人工恢复。
- rollback 只依赖 `.metadata.json.files`；如果映射缺失、`current_name` 不存在或 `original_name` 冲突，dry-run 必须阻止执行。
- archive 不修改原始目录和 `.metadata.json`；失败时只清理未完成的 ZIP 产物或返回错误。
- workspace remove 只删除记录，不删除真实目录。

## 进度记录

- [x] PRD 已确认。
- [x] TDD 已确认。
- [x] 实现计划已生成。
- [x] 已记录真实数据验收目录与磁盘空间约束。
- [x] 脚手架与依赖。
- [x] Pydantic 模型与错误码。
- [x] Ports 与 fake/mock adapter。
- [x] Domain 规则。
- [x] Metadata 读写与状态流转。
- [x] Application 用例。
- [x] Local adapters。
- [x] Scripts。
- [x] 测试。
- [x] 验收与收尾。

## 结果

已完成当前版本的第一版可运行实现。

实际修改：

- 新增 `src/photograph_workflow` 包，包含 models、domain、application、ports、adapters。
- 新增 `scripts/scan.py`、`scripts/rename.py`、`scripts/rollback.py`、`scripts/archive.py`、`scripts/archive_name.py`、`scripts/workspace.py`。
- 新增 pytest 测试，覆盖模板、元数据解析、rename/rollback、archive 和 workspace。
- 调整 `pyproject.toml` 为 Python `>=3.12`，加入 `pydantic`、`pytest` 和 `exifread`。

已运行验证：

- `uv run pytest`：10 passed。
- `uv run python scripts/rename.py "$HOME/20260501-「旅游」重庆" --dry-run > /tmp/photograph-workflow-real-dryrun.json`：只读执行，生成 248 个 rename items，0 errors，0 warnings，未写入真实目录。

未覆盖项：

- 尚未执行真实 `~/20260501-「旅游」重庆` 的 ExifTool 二进制路径验收，因为当前环境 `PATH` 中未找到 `exiftool`；已通过 `exifread` fallback 完成真实 ARW 拍摄时间读取验收。
- 尚未对真实 RAW 样本执行可写 rename/rollback 验收；如需执行，必须先复制少量样本到 `./tmp` 并确认剩余空间至少 `30GB`。

后续建议：

- 安装或引入项目环境内 ExifTool 后，补真实 ARW 只读 smoke test。
- 继续增强 CLI 摘要展示，目前脚本优先输出结构化 JSON。
- 根据真实样本反馈补充 metadata repair/prune 等未来操作设计。
