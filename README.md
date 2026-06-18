# SQL Dialect Adapter

MySQL、达梦、金仓三数据库之间的 SQL 方言转换与适配技能（Claude Code Skill）。

支持 6 种转换方向：MySQL ↔ 达梦、MySQL ↔ 金仓、达梦 ↔ 金仓，并提供 SQL 优化与 ANSI 标准化能力。

## 能力

- **方言转换**：在三种数据库间互转数据类型、函数、DDL/DML 语法、分页、事务控制。
- **语法检测**：根据特征关键词加权推断 SQL 所属数据库类型。
- **SQL 优化 / 标准化**：转为通用 ANSI SQL，给出索引与执行计划建议。
- **风险检查**：通过 CHECKPOINT 机制拦截高风险变更（精度丢失、函数行为差异、保留字冲突、严格模式语义变化等）。

## 目录结构

```
skills/sql-dialect-adapter/
├── SKILL.md                          # 技能主文件：决策入口、转换引擎、检查点、黑名单
├── references/                       # 各方向详细映射规则
│   ├── mysql-to-dm.md                # MySQL → 达梦
│   ├── mysql-to-kingbase.md          # MySQL → 金仓
│   ├── dm-to-mysql.md                # 达梦 → MySQL
│   ├── dm-to-kingbase.md             # 达梦 → 金仓
│   ├── kingbase-to-mysql.md          # 金仓 → MySQL
│   ├── kingbase-to-dm.md             # 金仓 → 达梦
│   ├── universal-syntax.md           # 通用 ANSI 语法速查
│   └── database-detection.md         # 语法检测规则
└── scripts/
    ├── detect_database.py            # 数据库类型检测（特征关键词加权评分）
    └── sql_converter.py              # SQL 转换辅助脚本
```

## 转换方向矩阵

| 源 \ 目标 | MySQL | 达梦 | 金仓 |
|-----------|-------|------|------|
| **MySQL** | — | mysql-to-dm | mysql-to-kingbase |
| **达梦**  | dm-to-mysql | — | dm-to-kingbase |
| **金仓**  | kingbase-to-mysql | kingbase-to-dm | — |

**通用语法优先原则**：转换后优先使用 ANSI 标准语法，仅当目标数据库不支持时才用其特定语法。

优先级：`标准 SQL → 目标数据库通用语法 → 目标数据库特定语法`

## 转换引擎

转换按 5 种模式顺序执行：

| 模式 | 处理内容 |
|------|----------|
| A — 数据类型标准化 | 特有类型 → 通用/目标兼容类型 |
| B — 函数方言替换 | 特有函数 → 标准/目标可用函数 |
| C — 语法结构重组 | DDL/DML 语法差异、标识符转义 |
| D — 分页查询适配 | `LIMIT` / `ROWNUM` / `ROW_NUMBER` / `FETCH FIRST` |
| E — 事务控制调整 | `START TRANSACTION` / `BEGIN` / 自动开启 |

输出按变更复杂度分为简单 / 中等 / 复杂三级，复杂变更触发 CHECKPOINT 2 高风险确认与验证清单。

## 使用方式

本仓库是一个 Claude Code Skill，将 `skills/sql-dialect-adapter/` 纳入 Claude Code 的 skills 目录即可被自动调用。

触发词示例：`转SQL`、`SQL转换`、`方言转换`、`MySQL转达梦`、`达梦转MySQL`、`适配SQL`、`SQL迁移`。

### 脚本独立运行

```bash
# 检测 SQL 所属数据库类型
python3 skills/sql-dialect-adapter/scripts/detect_database.py < input.sql

# SQL 转换辅助
python3 skills/sql-dialect-adapter/scripts/sql_converter.py
```

要求 Python ≥ 3.7。

## 质量评估

通过 [darwin-skill](https://github.com/) 进行 9 维度评分与迭代优化，历史评分记录见 `results.tsv`（基线 82.7，持续演进）。

## 许可

见仓库 LICENSE（如有）。
