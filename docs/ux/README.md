# App UX Prototype

本目录记录 Photograph Workflow 的 App UX 原型，覆盖桌面端、iPad 端和 iPhone 端。这里不维护纯 Markdown 线框稿；设计必须优先以可打开、可评审的静态原型呈现。

当前 UX 不设计面向用户的浏览器产品版本。原因是照片工作流需要稳定的本地目录选择、长期目录授权、Finder / Files 集成和本地文件写入确认，这些能力不应该建立在浏览器安全模型上。

UX 文档不仅描述基础界面，还必须描述用户旅程、可点击交互、状态反馈和危险操作确认。完整旅程见 [用户旅程与交互设计](./01-user-journey.md)，注解规范见 [UX 注解说明](./02-ux-annotations.md)。

## 查看方式

直接打开静态 HTML 查看：

```text
docs/ux/prototype/index.html
```

这个原型是静态 HTML/CSS，不连接后端，不执行真实文件操作。浏览器只是查看原型的工具，不代表产品形态是浏览器 Web App。

原型右上角提供 Desktop / iPad / iPhone 视图切换，点击后会平滑滚动到对应 App UX。

原型顶部包含 UX 注解区，用来说明完整用户旅程、关键反馈、安全门槛和异常分支。注解区是评审辅助，不代表最终 App 必须展示同样的说明文字。

当前原型支持轻量点击交互：

- 切换 Desktop / iPad / iPhone 视图。
- 切换配色方案。
- 在 Desktop 视图点击左侧工作流阶段，查看对应用户旅程说明。
- 在 iPad 视图点击左侧工作流阶段，切换触摸工作台的当前流程。
- 在 iPhone 视图点击横向流程胶囊，明确当前阶段并跳到指定流程。
- 点击 Desktop、iPad 或 iPhone 的主按钮模拟进入下一阶段。

原型仍然不连接后端，不读取或修改本地文件。

## 配色方案

原型顶部提供主题切换器，当前包含：

| 主题 | 方向 |
| --- | --- |
| Neutral Graphite + Soft Cobalt | 推荐默认；中性文件工作台，蓝色只做操作点缀 |
| Cool Mono + Cyan Accent | 更冷静、技术感更强 |
| Warm Paper + Sage | 更接近摄影工作室和纸质档案 |
| Silver Olive | 克制、低饱和，适合长时间管理文件 |
| Low-light Darkroom | 低光环境使用，不作为默认主题 |

原型会用 `localStorage` 记住上一次选择。未来如果落到应用里，主题应成为 App 的用户偏好设置，并复用同一组设计 token。

### 主题 Token

| 主题 | 背景 | 表面 | 文本 | 主色 | 主色弱背景 | 成功 | 警告 | 危险 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Neutral Graphite + Soft Cobalt | `#f5f6f8` | `#ffffff` | `#17202a` | `#3a63d8` | `#e9eeff` | `#16865a` | `#a66300` | `#c0392b` |
| Cool Mono + Cyan Accent | `#f2f7f8` | `#ffffff` | `#14262d` | `#0f7285` | `#e4f3f6` | `#127450` | `#9b610f` | `#ba3a2e` |
| Warm Paper + Sage | `#f7f4ed` | `#fffdf8` | `#252019` | `#4f6f52` | `#e8efe5` | `#3f7a4b` | `#9a6500` | `#a83b2f` |
| Silver Olive | `#f3f5f2` | `#ffffff` | `#1f2a24` | `#557245` | `#e9f1e4` | `#20714f` | `#99640e` | `#b33a2f` |
| Low-light Darkroom | `#15171b` | `#20242b` | `#f4f6f8` | `#7ba7ff` | `#1f2d4a` | `#6fd39a` | `#e5ae57` | `#ff877e` |

配色语义：

- 当前阶段、已完成阶段和主操作使用当前主题的主色。
- `success` 绿色只用于真实成功状态，例如重命名完成、Ready、无阻塞错误。
- `warning` 和 `danger` 只用于需要用户注意或会阻止执行的风险。

## 当前方向

这版 UX 完全重构旧 Web UI 的信息架构，但产品形态按桌面端、iPad 端和 iPhone 端 App 设计：

- 从“功能 Tab”改成“项目工作台”。
- 把 `Workspace` 收进项目选择器，不作为主流程步骤。
- 把 `Rollback` 收进安全中心，不作为日常主流程步骤。
- 主流程聚焦：准备项目、检查素材、命名规则、执行重命名、Lightroom 后期、归档。
- 桌面 App 负责系统目录选择、最近项目、Reveal in Finder、目录授权恢复和本地文件写入确认。
- iPad App 保留项目工作台结构，但用触摸友好的卡片、双栏和可收起检查面板承载流程。
- iPhone App 使用单列向导，每次聚焦一个阶段，底部固定主操作，危险操作进入确认页或 sheet。
- 浏览器 Web UI 只能作为开发、调试或桌面包装前端基础，不作为目标用户的浏览器产品版本。

## 设计约束

- 所有危险操作必须先生成 dry-run 计划，再确认执行。
- 文件明细默认折叠，先展示目录级状态。
- `{date}` 只来自照片元数据，读取失败必须阻止依赖日期的重命名。
- `.metadata.json.original_name` 不可变。
- RAW/DNG 与同 stem sidecar 同步处理。
- 桌面包装 App、macOS 原生 App、iPad App 和 iPhone App 必须复用相同结构化计划和错误语义。
