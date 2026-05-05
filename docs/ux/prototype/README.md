# UX 原型说明

本目录保存可直接打开评审的静态 UX 原型：

```text
docs/ux/prototype/index.html
```

这个原型不是只展示基础界面。它需要表达用户旅程和关键交互，但不连接后端、不执行真实文件操作。

当前交互层级：

- 可以切换桌面 / iPad / iPhone 视图。
- 可以切换主题配色。
- 可以点击桌面视图左侧工作流阶段，查看该阶段的用户意图、系统反馈和下一步动作。
- 可以点击 iPad 左侧工作流阶段，切换触摸工作台的当前流程。
- 可以点击 iPhone 横向流程胶囊，明确当前阶段并跳到指定流程。
- 可以点击桌面、iPad 和 iPhone 主按钮，模拟从当前阶段进入下一阶段。
- 可以展开桌面重命名预览里的目录树，查看每个目录和子目录中的文件映射。
- 可以点击桌面左下角 `设置`，进入设置页面查看语言、主题、默认值和安全规则。
- 可以点击桌面左下角 `安全中心`，进入安全中心查看预演、元数据不可变和可追踪性规则。

详细用户旅程见 `docs/ux/01-user-journey.md`。

注解规范见 `docs/ux/02-ux-annotations.md`。原型顶部的 UX 注解区用于评审完整旅程、安全门槛和异常路径，不代表最终应用内必须展示同样的说明文案。

## 视图切换器

右上角的 `桌面 / iPad / iPhone` 是应用视图切换器，不使用浏览器默认锚点跳转体验。

实现方式：

- HTML 中每个入口保留 `href="#desktop-app"` 这类锚点，保证没有 JavaScript 时仍可访问。
- 同时给入口增加 `data-view-link`，用于 JavaScript 查找目标区块。
- 点击时调用 `event.preventDefault()` 阻止默认瞬间跳转。
- 根据 `data-view-link` 找到对应区块后，调用 `scrollIntoView({ behavior: "smooth", block: "start" })` 平滑滚动。
- 用 `history.replaceState(null, "", "#...")` 更新地址 hash，避免产生多条浏览历史记录。
- 用 `setActiveView()` 同步当前入口高亮。
- 用 `IntersectionObserver` 监听 `#desktop-app`、`#ipad-app`、`#iphone-app`，用户手动滚动时也能同步高亮当前视图。
- `.section` 设置 `scroll-margin-top`，避免滚动后标题贴住窗口顶部。

这个交互的目标是保留锚点可分享、可刷新定位的优点，同时让点击切换更接近应用内导航，而不是网页目录跳转。

## 主题切换器

配色方案使用 `data-theme-option` 标记主题卡片。

实现方式：

- 点击主题卡片后，将 `document.documentElement.dataset.theme` 设置为对应主题名。
- CSS 通过 `:root[data-theme="..."]` 切换设计 token。
- 当前主题保存到 `localStorage` 的 `photograph-workflow-theme`，下次打开原型时自动恢复。
- 当前选中的主题卡片增加 `is-selected`，并同步 `aria-pressed`。

## 工作流阶段交互

桌面和 iPad 视图左侧流程阶段使用 `data-journey-step` 标记。

实现方式：

- 每个阶段保留 `role="button"` 和 `tabindex="0"`，鼠标和键盘都能触发。
- 点击或按 `Enter` / `Space` 时调用 `setJourneyStep()`。
- `setJourneyStep()` 更新桌面、iPad 和 iPhone 的阶段高亮、顶部状态、主标题、主说明、主按钮、用户旅程卡片和右侧下一步提示。
- `data-journey-next` 标记桌面、iPad 和 iPhone 的主按钮，点击后进入下一个阶段，用于模拟真实应用的连续操作路径。
- iPhone 使用 `data-phone-progress-dot` 同步顶部进度点，并用横向滚动的 `phone-step` 胶囊替代完整侧边栏。
- 重命名预览使用原生 `details` / `summary` 表达目录树，默认展示目录摘要，展开后展示 RAW/DNG 和同名附属文件的原名到目标名映射。
- 这只是 UX 层模拟，不调用后端、不生成真实计划、不修改文件。

## 辅助页面

桌面左下角 `设置` 和 `安全中心` 是辅助旅程入口，不属于六阶段主流程。

实现方式：

- 左下角入口使用 `data-utility-page` 标记，主内容区页面使用 `data-desktop-content` 标记。
- 点击 `设置` 或 `安全中心` 时，`setDesktopContent()` 切换主内容区页面，并同步入口的 `active` 和 `aria-pressed` 状态。
- 点击任意桌面工作流阶段时，原型会回到 `workflow` 页面，并保留当前阶段高亮。
- 设置内容分为通用、工作流默认值、归档、安全；语言选择归入设置的通用区域。
- 安全中心展示预演优先、阻塞错误、原始文件名不可变和附属文件同步等规则。
- 安全中的预演和 `original_name` 不可变规则展示为已锁定 / 始终开启，表示它们不是普通偏好，不能被用户关闭。
- 辅助页面不展示当前项目的扫描结果、预演计划或执行确认；这些内容仍然属于主旅程对应阶段。
