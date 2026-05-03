# 测试与实现顺序

## Mock 后端

mock 后端用于测试和调试，不执行实际文件操作。

必须支持模拟：

- 文件不存在。
- 权限不足。
- 磁盘空间不足。
- 目标路径已存在。
- ExifTool 缺失。
- ExifTool 返回错误。
- `.metadata.json` 写入失败。
- ZIP 创建失败。

## 测试策略

单元测试：

- 端口 fake adapter 与 application 用例编排。
- 结构化计划 JSON 序列化。
- 扩展名枚举和大小写处理。
- sidecar stem 匹配规则。
- DJI DNG 元数据识别。
- ExifTool JSON 解析。
- `{date:<format>}` 模板解析。
- `{original}` 来源选择。
- 文件名 sanitize。
- Pydantic 输入校验。
- `.metadata.json` 版本校验。
- rename 冲突检测。
- rollback 计划生成。
- archive exclude 规则。
- archive name 生成。

集成测试：

- fixture 项目目录递归扫描。
- fake ExifTool JSON 生成 rename dry-run。
- pending metadata 写入后执行 rename。
- 中途失败后保留可回滚状态。
- rollback dry-run 和执行。
- archive dry-run 和 ZIP 文件数量校验。
- archive_name 只生成名称不创建 ZIP。

真实文件验收：

- Sony `.ARW` 读取拍摄时间。
- DJI `.DNG` 读取拍摄时间并确认 DJI 来源。
- 同 stem `.xmp`、`.acr`、`.jpg`、`.jpeg` 跟随 RAW/DNG 重命名。

## 实现顺序

推荐顺序：

1. 建立 Pydantic 模型、枚举、结构化计划和错误码。
2. 建立 `ports` 接口和 fake adapter。
3. 实现 domain 层扫描分类、sidecar 匹配、命名模板、sanitize 和冲突检测。
4. 实现 `.metadata.json` 读写和状态流转规则。
5. 实现 application 层 rename dry-run 计划。
6. 实现本地文件系统、ExifTool、zipfile 等当前版本 adapter。
7. 实现 rename 执行用例。
8. 实现 rollback plan 和 operation。
9. 实现 archive_name。
10. 实现 archive plan 和 operation。
11. 补齐脚本入口和摘要渲染。
12. 补齐测试和真实文件 smoke test。
