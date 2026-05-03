# PRD/TDD Review

## 结论

当前 PRD 和 TDD 已经覆盖了主流程、metadata、sidecar、归档和未来扩展方向，但仍存在几处需要修正或补齐的设计问题。因此当前不应提交并推送，建议先对齐以下事项。

## 问题列表

### 1. 工作目录契约在 TDD 中缺失

- 级别：P1
- 位置：`docs/prd/01-workflow.md:11`、`docs/prd/01-workflow.md:26`、`docs/prd/01-workflow.md:27`、`docs/tdd/01-architecture.md:60`

PRD 要求工作目录分为本地目录和 iCloud 目录两类，并支持从本地原始照片目录和 iCloud 原始照片目录中选择项目目录。但 TDD 当前只保留了 `config.py` 和通用 `FileSystemPort`，没有定义目录根枚举、目录解析策略或跨平台目录定位接口。

建议：

- 在 TDD 中补充 `WorkspaceRoot` / `DirectoryRoot` 之类的数据契约。
- 在 `ports` 中增加目录定位或工作区解析端口，例如 `WorkspaceResolverPort`。
- 明确本地根目录、iCloud 根目录、本地原始照片目录、iCloud 原始照片目录的配置来源和优先级。

### 2. 批量输入的 `strict` 行为没有进入 TDD

- 级别：P1
- 位置：`docs/prd/02-raw-renaming.md:320`、`docs/prd/02-raw-renaming.md:327`、`docs/tdd/02-data-contracts.md:58`

PRD 明确：如果某个目录下没有支持的照片源文件，dry-run 默认给出警告，不阻止；是否阻止由 `strict` 配置决定。TDD 的 `BatchInput` 只定义了 `root`、`directories`、`template`，没有 `strict` 或等价的执行策略字段，也没有对应错误码/警告码。

建议：

- 在 `BatchInput` 或 operation options 中增加 `strict`，默认 `false`。
- 增加 `directory_no_supported_sources` 之类的 `PlanIssue` code。
- 明确 `strict=false` 是 warning，`strict=true` 是 error。

### 3. `.metadata.json` 的追加与重规划规则在 TDD 中不完整

- 级别：P1
- 位置：`docs/prd/02-raw-renaming.md:421`、`docs/prd/02-raw-renaming.md:422`、`docs/prd/02-raw-renaming.md:433`、`docs/prd/02-raw-renaming.md:435`、`docs/tdd/02-data-contracts.md:119`、`docs/tdd/04-rename-and-rollback.md:47`

PRD 要求显式覆盖 `title` / `template` 时必须执行全目录重新规划；新增照片只能追加新的 `files` 条目，不能删除或重建已有条目。TDD 目前只写了 `original_name` 不可变、`current_name` 表示真实文件、`planned_name` 成功后移除，没有把“全目录重规划”和“追加而非重建”的规则写清楚。

建议：

- 在 TDD 的 MetadataFileEntry 约束中补充 append-only 语义。
- 在 rename 计划流程中明确：覆盖目录配置时必须全目录重规划。
- 明确已有条目匹配策略：优先基于 `.metadata.json.files`，新增文件追加，不能重写既有 `original_name`。

### 4. `{seq}` token 的排序和作用域没有定义

- 级别：P1
- 位置：`docs/prd/05-standard-directory.md:142`、`docs/prd/05-standard-directory.md:148`、`docs/prd/05-standard-directory.md:181`、`docs/prd/05-standard-directory.md:183`、`docs/tdd/04-rename-and-rollback.md:22`

TDD 已经声明支持 `{seq}` 和 `{seq:04}`，但没有定义序号作用域、排序规则、同一秒照片如何排序、文件号回绕如何处理。PRD 中已有排序要求：需要序号或展示顺序时，必须按拍摄时间排序，而不能按文件名字典序排序。

建议：

- 在 TDD 中定义 `sequence_scope`，默认建议 `per-directory`。
- 明确 `{seq}` 只在模板显式使用时启用，不默认追加。
- 明确排序优先级：拍摄时间、文件系统创建/修改时间、相机文件号回绕感知排序、原始完整路径。
- 明确拍摄时间不可用时不能生成依赖 `{date}` 的文件名，但可以用于展示排序回退。

### 5. `{date}` 来源在 PRD 内部存在歧义

- 级别：P2
- 位置：`docs/prd/05-standard-directory.md:113`、`docs/prd/05-standard-directory.md:164`、`docs/tdd/03-scan-and-metadata.md:55`

`docs/prd/05-standard-directory.md` 写到 `{date:YYYYMMDD}` 是“拍摄日期或目录日期”，但其他 PRD 和 TDD 都要求默认模板中的 `{date}` 来自照片元数据；RAW/DNG 读不到拍摄时间时，dry-run 必须阻止执行。这里的“或目录日期”容易让实现误以为可以自动回退目录日期。

建议：

- 将 `{date:YYYYMMDD}` 改为“拍摄日期”。
- 目录日期统一使用 `{project_date}`，并在 TDD 中定义 `{project_date}` 的解析来源和失败行为。

### 6. 全局配置在 PRD 中出现，但 TDD 没有数据契约

- 级别：P2
- 位置：`docs/prd/04-roadmap.md:56`、`docs/prd/04-roadmap.md:60`、`docs/prd/04-roadmap.md:68`、`docs/tdd/01-architecture.md:72`

PRD 给出了全局配置建议路径和示例字段，包括扩展名、默认模板、冲突策略、确认策略、归档 exclude 等。TDD 只在目录结构里保留 `config.py`，没有定义全局配置是否属于当前版本，也没有定义加载顺序、字段模型或与 `.metadata.json` / 批量输入的优先级关系。

建议二选一：

- 如果当前版本要支持全局配置，在 TDD 中增加 `GlobalConfig` Pydantic 模型和配置优先级。
- 如果当前版本不实现全局配置，把 PRD 中的全局配置明确标为后续能力，避免实现时误判范围。

### 7. 归档覆盖和手动命名辅助的目标存在行为不完整

- 级别：P2
- 位置：`docs/prd/03-export-archive.md:148`、`docs/prd/03-export-archive.md:136`、`docs/tdd/05-archive.md:22`、`docs/tdd/05-archive.md:55`

PRD 要求归档目标已存在时默认阻止覆盖，用户显式覆盖时必须二次确认；`archive_name` 如果目标文件名已存在，应生成错误或提示重新生成时间戳。TDD 只有 `overwrite` 和目标存在阻塞规则，没有写覆盖二次确认，也没有写 `archive_name` 的目标存在处理。

建议：

- 在 TDD 中补充 `overwrite=true` 仍需要 confirmation 的规则。
- 为 `archive_name` 增加目标存在检查规则和错误码，例如 `archive_name_target_exists`。

### 8. Lightroom 已导入风险没有进入 TDD 的计划/错误模型

- 级别：P2
- 位置：`docs/prd/01-workflow.md:61`、`docs/prd/01-workflow.md:143`、`docs/prd/04-roadmap.md:170`、`docs/tdd/02-data-contracts.md:211`

PRD 多处强调重命名必须发生在 Lightroom 导入前；如果已经导入或存在明显 Lightroom 相关文件，只能提示风险。TDD 当前没有对应的扫描规则、warning code 或 plan issue。

建议：

- 增加非阻塞 warning code，例如 `lightroom_reference_risk`。
- 在扫描或 rename plan 中定义“明显 Lightroom 相关文件”的保守检测范围。
- 明确该能力不读取 Lightroom catalog，只做风险提示。

