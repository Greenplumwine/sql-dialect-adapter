# CLAUDE.local.md

个人偏好，与 CLAUDE.md 一起在每次会话自动加载。

## 关于我

- 角色：全栈独立开发，独自负责这个项目的设计、编写、测试与优化。
- 熟悉度：非常熟悉 DM / Kingbase / MySQL 方言差异及本 skill 结构，无需背景科普，直接进入正题。

## 沟通偏好

- **简洁**：直接给结论和代码，少铺垫。
- **解释取舍**：改动时说明为什么这么选、放弃了什么。
- **先提计划**：实现前先给方案/计划待确认，再动手。

## 项目背景

- 本仓库核心是 `skills/sql-dialect-adapter`：一个 SQL 方言适配 skill，含 `references/`（各方言对照规则）与 `scripts/`（sql_converter.py、detect_database.py）。
- 通过 `darwin-skill` 持续评分优化，历史记录见 `results.tsv`（基线 82.7，迭代演进中）。
