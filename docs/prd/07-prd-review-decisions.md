# PRD 全量审阅与待决策问题

审阅日期：2026-05-02

## 结论

当前 PRD 主线是清晰的：以 Python 和 uv 实现本地照片工作流，核心围绕递归扫描、RAW/DNG 重命名、目录级 `.metadata.json`、Lightroom 导入前稳定命名、原始素材归档。

但文档中仍有几处产品语义冲突或实现前必须明确的决策点。基于这些问题，当前不建议直接提交为最终 PRD 版本，应先完成以下决策。

## 待决策问题

### 1. `.metadata.json` 的写入时机与原子性冲突

相关文档：

- `docs/prd/02-raw-renaming.md`
- `docs/prd/04-roadmap.md`
- `docs/prd/06-python-architecture.md`

当前冲突：

- PRD 要求 `.metadata.json` 保存首次执行时的不可变 `original_name` 到 `renamed_name` 映射。
- 架构流程又写成“先执行重命名，再写入或更新 `.metadata.json`”。
- 如果第一次执行时文件已经被重命名，但 `.metadata.json` 写入失败，就会丢失 `{original}` 的唯一可靠来源，也无法稳定回滚。

需要决策：

- 是否采用“两阶段写入”：先写入 pending 状态的 `.metadata.json` 或临时元数据文件，确认映射已经落盘后再执行文件 rename，最后更新为 renamed 状态。
- 或者接受失败后人工恢复，但这会削弱 `.metadata.json` 作为回滚依据的设计目标。

建议：

- 采用两阶段写入，并要求 `.metadata.json` 的映射在任何文件 rename 之前已经可恢复。

### 2. `.metadata.json` 与命令行、批量输入的优先级冲突

相关文档：

- `docs/prd/02-raw-renaming.md`

当前冲突：

- 目录级规则写到：如果 `.metadata.json` 存在且合法，目录命名配置以该文件为准。
- 配置优先级又写到：命令行显式参数、批量输入目录级 `title` / `template` 高于 `.metadata.json`。
- 这会导致一个目录已经建立了不可变映射后，外部输入仍可能覆盖 `title` 或 `template`，从而让新增文件和既有文件处于不同命名规范。

需要决策：

- `.metadata.json` 存在后是否应该成为目录的唯一权威配置。
- 如果允许外部覆盖，是否必须把覆盖结果写回 `.metadata.json`，并对既有文件执行整体重新规划。

建议：

- `.metadata.json` 存在后默认最高优先级。
- 外部 `title` / `template` 只能在 `.metadata.json` 不存在时初始化目录配置。
- 如果用户要修改既有目录规范，应设计显式的“更新目录元数据/重新规划”动作，而不是普通 rename 自动覆盖。

### 3. 递归目录输入与目录级 `title` 的作用范围不明确

相关文档：

- `docs/prd/02-raw-renaming.md`
- `docs/prd/05-standard-directory.md`

当前冲突：

- 批量输入中 `directories[].path` 会递归扫描。
- `directories[].title` 又表示“目录内照片使用的显示标题”。
- 如果输入的是一个上层分类目录，里面包含多个照片子目录，那么这个 `title` 应该只应用到输入目录本身，还是递归应用到所有子目录，目前没有明确。

需要决策：

- `directories[].title` 是否只对 `path` 指向的那个照片目录生效。
- 当 `path` 是分类容器时，是否禁止设置 `title`。
- 是否支持类似继承配置，但默认不继承到子目录。

建议：

- `directories[].title` 只对实际包含照片文件的目标目录生效。
- 如果 `path` 目录本身没有照片、只是分类容器，则不允许设置 `title`，由子目录自己的 `.metadata.json` 或目录名解析决定。

### 4. 默认 `{title}` 解析规则与样例存在不一致

相关文档：

- `docs/prd/02-raw-renaming.md`
- `docs/prd/05-standard-directory.md`

当前冲突：

- 标准目录文档前半部分说，照片应以 `20260501-重庆人民大礼堂` 作为命名前缀。
- 后续默认模板示例又使用 `大礼堂` 作为 `{title}`，生成 `20260501-大礼堂-184126_DSC09907.ARW`。
- 如果没有 `.metadata.json` 或批量输入 `title`，工具到底应该解析出 `重庆人民大礼堂`，还是进一步简化成 `大礼堂`，目前没有规则。

需要决策：

- 默认解析是否只剥离日期，得到 `重庆人民大礼堂`。
- 像 `大礼堂` 这种短标题是否必须由 `.metadata.json` 或批量输入显式提供。

建议：

- 默认只剥离日期，不做地点或语义压缩。
- `大礼堂` 这类短标题必须来自 `.metadata.json` 或批量输入，避免工具猜测地点语义。

### 5. 归档状态记录放在目录 `.metadata.json` 里会重复且语义不清

相关文档：

- `docs/prd/01-workflow.md`
- `docs/prd/03-export-archive.md`

当前冲突：

- 归档对象是项目目录，可能包含多个照片目录。
- 归档结果现在要求写入“相关照片目录下的 `.metadata.json`”。
- 如果一个 ZIP 包覆盖多个照片目录，那么每个目录都写同一个 archive 结果会重复；如果只写部分目录，又无法表达项目归档整体状态。

需要决策：

- 是否引入项目级归档 manifest，例如 archive manifest，只记录归档包路径、文件数量、校验和。
- 或者把 `.metadata.json` 的 archive 字段定义为“该目录已被哪个归档包包含”，而不是项目级归档状态。

建议：

- 保留目录级 `.metadata.json` 管理照片命名和文件映射。
- 归档结果单独生成 manifest，避免把项目级状态塞进每个照片目录。

### 6. “项目级配置”与 `.metadata.json` 的概念混淆

相关文档：

- `docs/prd/04-roadmap.md`

当前冲突：

- 文档说“建议支持项目级配置和全局配置”。
- 但项目级配置示例写的是“照片目录下的 `.metadata.json`”。
- `.metadata.json` 是目录元数据，不是项目级配置；二者职责不同。

需要决策：

- 当前版本是否需要项目级配置文件。
- 如果需要，应该单独定义文件名和字段；如果不需要，应删除“项目级配置”的说法。

建议：

- 当前版本只保留全局配置和目录级 `.metadata.json`。
- 项目级配置暂不定义，避免和目录元数据混淆。

### 7. Pydantic 是必需依赖，但“默认不引入重量级运行时依赖”表述冲突

相关文档：

- `docs/prd/02-raw-renaming.md`
- `docs/prd/04-roadmap.md`

当前冲突：

- 批量输入要求必须用 Pydantic `BaseModel` 强制校验。
- 范围文档又写“当前版本默认不引入重量级运行时依赖”。
- Pydantic 虽然合理，但它是明确的第三方运行时依赖。

需要决策：

- 是否把 Pydantic 明确列为当前版本必需依赖。
- 或者只在批量输入能力启用时引入。

建议：

- 明确 Pydantic 是当前版本必需依赖，因为批量输入格式校验已经是核心需求。

### 8. 日期格式“国际标准”表述需要落成明确语法

相关文档：

- `docs/prd/02-raw-renaming.md`

当前风险：

- 文档现在使用 `YYYYMMDD`、`YYMMDD`、`HHMMSS` 这种模板语法。
- ExifTool 和 Python 常见日期格式实际更接近 strftime 的 `%Y%m%d`、`%y%m%d`、`%H%M%S`。
- 如果只说“参考通用日期时间格式标准”，实现时容易出现不同解释。

需要决策：

- 项目模板是否继续使用用户友好的 `YYYYMMDD` 语法，并由项目解析器映射到底层日期格式。
- 是否允许 strftime 原生格式。

建议：

- 当前版本只支持项目自定义的紧凑格式枚举：`YYYYMMDD`、`YYMMDD`、`YYDDMM`、`YYYYDDMM`、`HHMMSS`。
- 不声明其为完整国际标准，避免误导。

### 9. PRD 里仍包含具体 Python 代码片段

相关文档：

- `docs/prd/02-raw-renaming.md`

当前冲突：

- 用户已要求“不要有代码的具体实现”。
- `工作目录枚举` 章节仍包含 `PhotographDir` 的 Python 代码示例。

需要决策：

- 是否把代码块改成字段/枚举契约描述。

建议：

- 删除具体 Python 代码，只保留目录枚举的产品契约和路径含义。

## 外部依据备注

关于 RAW 文件是否可靠保存原始文件名：

- ExifTool 的 [Writing FileName and Directory tags](https://exiftool.org/filename.html) 说明 `FileName`、`Directory` 用于通过 ExifTool 重命名或移动文件，语义是文件系统路径/文件名。
- ExifTool 的 [Extra Tags](https://exiftool.org/TagNames/Extra.html) 文档也把 `FileName` 归类为 System tag。
- 因此 `{original}` 不能依赖 RAW 内部元数据恢复，当前版本应继续以 `.metadata.json` 中首次写入的 `original_name` 作为唯一可靠来源。

## 建议处理顺序

1. 先确认 `.metadata.json` 的权威性和两阶段写入策略。
2. 再确认目录 title 的默认解析规则。
3. 决定归档结果是否引入独立 manifest。
4. 清理项目级配置、Pydantic 依赖、日期格式和代码片段表述。

这些决策完成后，再统一修改 PRD 并提交。
