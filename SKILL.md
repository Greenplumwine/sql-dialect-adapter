---
name: sql-dialect-adapter
description: "MySQL、达梦、金仓数据库SQL语法转换与适配技能。支持三种数据库之间的6种转换方向：MySQL↔达梦、MySQL↔金仓、达梦↔金仓。当需要在不同数据库间转换SQL语法、适配函数差异、处理数据类型不兼容时使用此技能。包含通用语法优先原则、详细函数差异对比、数据库语法检测和实用转换工具。"
---

# SQL方言适配技能

## 概述

本技能提供MySQL、达梦数据库、金仓数据库之间的SQL语法转换与适配能力。支持**6种转换方向**的相互转换，遵循**通用语法优先**原则，确保转换后的SQL尽可能使用标准SQL语法，仅在必要时使用目标数据库特定语法。

## 核心原则

### 通用语法优先原则

1. **优先使用标准SQL**：尽量使用ANSI SQL标准语法
2. **避免数据库特定函数**：使用标准函数替代数据库特有函数
3. **统一数据类型**：使用最通用的数据类型
4. **保持可读性**：转换后的SQL应易于理解和维护

### 转换策略优先级

```
标准SQL语法 → 目标数据库通用语法 → 目标数据库特定语法
```

## 执行流程与检查点

本 skill 在执行转换前，需经过以下检查点，防止自主跑偏：

### 检查点 1：确认转换方向（必须）

- **如果用户明确说明了源数据库和目标数据库** → 直接进入转换
- **如果用户只提供了 SQL，未说明数据库类型** → 先执行「数据库语法检测」（见下方检测章节），然后询问用户：
  > "检测到这段 SQL 可能是 **[检测结果]** 语法。请确认源数据库类型，以及目标数据库类型。"
- **如果用户只说"优化 SQL"但未提及方言转换** → 询问用户：
  > "您是否需要将这段 SQL 转换为其他数据库方言？如果是，请提供源数据库和目标数据库。"

### 检查点 2：高风险转换确认（条件触发）

当转换涉及以下情况时，**暂停并提示用户确认**：

| 风险类型 | 示例 | 提示语 |
|----------|------|--------|
| 数据类型精度变化 | `DECIMAL(19,4)` → `NUMERIC` | "数据类型可能丢失精度，请确认是否继续" |
| 函数行为不完全一致 | `GROUP_CONCAT` → `WM_CONCAT`（排序行为不同） | "目标数据库的等效函数行为可能有差异，建议转换后测试验证" |
| 分页性能差异 | `LIMIT OFFSET` → `ROWNUM` | "分页语法在目标数据库中的执行计划可能不同，建议关注性能" |
| 保留字冲突 | 表名/列名与目标数据库保留字冲突 | "以下标识符与目标数据库保留字冲突，建议添加转义符：[列表]" |

### 检查点 3：输出确认

转换完成后，提供以下信息供用户确认：
1. **变更摘要**：列出所有修改点（函数替换、类型调整、语法调整）
2. **验证建议**：建议在目标数据库中执行的测试语句
3. **风险提示**：如有 Step 2 中的高风险项，再次提醒

---

## 执行工作流

### Step 1：确认转换方向

**输入**：用户提供的 SQL 代码 + （可选）源数据库类型 + （可选）目标数据库类型

**操作**：
- 若用户已明确源数据库和目标数据库 → 直接进入 Step 2
- 若未明确 → 触发「检查点1」，检测或询问

**参考文档**：

| 源数据库 | 目标数据库 | 参考文档 |
|----------|------------|----------|
| MySQL | 达梦 | [references/mysql-to-dm.md](references/mysql-to-dm.md) |
| MySQL | 金仓 | [references/mysql-to-kingbase.md](references/mysql-to-kingbase.md) |
| 达梦 | MySQL | [references/dm-to-mysql.md](references/dm-to-mysql.md) |
| 达梦 | 金仓 | [references/dm-to-kingbase.md](references/dm-to-kingbase.md) |
| 金仓 | MySQL | [references/kingbase-to-mysql.md](references/kingbase-to-mysql.md) |
| 金仓 | 达梦 | [references/kingbase-to-dm.md](references/kingbase-to-dm.md) |

### Step 2：检测源数据库（条件执行）

**触发条件**：用户未提供源数据库类型

**操作**：
1. 使用 `scripts/detect_database.py` 分析 SQL 特征（函数名、语法关键字）
2. 将检测结果告知用户，等待确认

**输出**：确认后的源数据库类型

### Step 3：应用转换规则

**输入**：源 SQL + 确认的转换方向

**操作**：按以下优先级顺序执行转换：
1. **数据类型转换**：特有类型 → 通用/目标兼容类型
2. **函数转换**：特有函数 → 标准/目标可用函数
3. **语法转换**：调整 DDL/DML 语法差异
4. **分页查询转换**：处理分页语法差异
5. **事务控制转换**：调整事务语法

**输出**：转换后的 SQL 草稿

### Step 4：高风险确认（条件执行）

**触发条件**：涉及「检查点2」中的风险类型

**操作**：列出风险项，等待用户确认后继续

**输出**：确认后的最终转换结果

### Step 5：输出与验证

**操作**：按以下格式输出转换结果：

```markdown
## 转换结果（{源数据库} → {目标数据库}）

### 转换后的 SQL
```sql
{转换后的SQL代码}
```

### 变更摘要
| 序号 | 原语法 | 转换后 | 说明 |
|------|--------|--------|------|
| 1 | ... | ... | ... |

### 验证建议
- [ ] 在目标数据库中执行测试
- [ ] 检查数据类型兼容性
- [ ] 验证函数返回结果一致性
```

**输出**：变更摘要 + 验证清单 + 如有风险则再次提醒

## 通用转换规则

### 数据类型通用转换

| 源类型 | 通用类型 | 说明 |
|--------|----------|------|
| TINYINT | SMALLINT | 使用更通用的SMALLINT |
| MEDIUMINT | INT | 使用INT替代MEDIUMINT |
| FLOAT | REAL | 使用标准REAL类型 |
| DOUBLE | DOUBLE PRECISION | 使用标准DOUBLE PRECISION |
| DECIMAL | NUMERIC | 使用标准NUMERIC类型 |
| DATETIME | TIMESTAMP | 使用标准TIMESTAMP |
| TEXT | VARCHAR(4000) | 使用VARCHAR替代TEXT |
| CLOB | VARCHAR(4000) | 使用VARCHAR替代CLOB |
| BLOB | BYTEA | 使用标准BYTEA类型 |

### 函数通用转换

#### 条件函数

**源语法**：
```sql
IF(condition, true_value, false_value)
IFNULL(expr, default_value)
```

**通用转换**：
```sql
CASE WHEN condition THEN true_value ELSE false_value END
COALESCE(expr, default_value)
```

#### 字符串函数

**源语法**：
```sql
GROUP_CONCAT(expr SEPARATOR ',')
CONCAT(str1, str2)
```

**通用转换**：
```sql
-- 使用标准字符串连接
str1 || ', ' || str2 || ', ' || ...
-- 或使用目标数据库的聚合函数
```

#### 日期函数

**源语法**：
```sql
DATE_FORMAT(date, '%Y-%m-%d')
NOW()
```

**通用转换**：
```sql
TO_CHAR(date, 'YYYY-MM-DD')
CURRENT_TIMESTAMP
```

#### 字符串聚合函数

**源语法（MySQL）**：
```sql
GROUP_CONCAT(expr SEPARATOR ',')
```

**目标数据库映射**：

| 目标数据库 | 对应函数 | 说明 |
|-----------|---------|------|
| 达梦 | `WM_CONCAT(expr)` | 默认逗号分隔，无序 |
| 达梦 | `LISTAGG(expr, ', ') WITHIN GROUP (ORDER BY ...)` | 可指定排序 |
| 金仓 | `STRING_AGG(expr, ', ')` | PostgreSQL 兼容语法 |
| 金仓 | `GROUP_CONCAT(expr SEPARATOR ',')` | 部分版本兼容 MySQL 语法 |

#### 集合函数

**源语法（MySQL）**：
```sql
FIND_IN_SET(str, strlist)
```

**目标数据库映射**：

| 目标数据库 | 对应方案 | 示例 |
|-----------|---------|------|
| 达梦 | `INSTR(',' || strlist || ',', ',' || str || ',')` | 前后补逗号确保精确匹配 |
| 金仓 | `POSITION(',' || str || ',' IN ',' || strlist || ',')` | 同上 |
| 通用 | 正则匹配 | `strlist ~ ('(^|,)' || str || '(,|$)')` |

#### 日期运算函数

**源语法（MySQL）**：
```sql
DATE_ADD(date, INTERVAL n DAY)
DATEDIFF(date1, date2)
```

**目标数据库映射**：

| MySQL | 达梦 | 金仓 |
|-------|------|------|
| `DATE_ADD(d, INTERVAL n DAY)` | `d + n` | `d + INTERVAL 'n days'` |
| `DATEDIFF(d1, d2)` | `DATEDIFF(d1, d2)` | `d1 - d2`（返回天数） |

## 数据库语法检测

当不确定SQL代码使用的数据库类型时，使用数据库语法检测功能：

1. **检测当前数据库类型**：使用 `scripts/detect_database.py` 分析SQL代码
2. **获取转换建议**：根据检测结果选择正确的转换方向
3. **验证转换结果**：转换后再次检测确保符合目标数据库语法

具体检测方法参考 [references/database-detection.md](references/database-detection.md)

## 转换工具

```bash
# 检测数据库类型
python scripts/detect_database.py your_sql_file.sql
python scripts/detect_database.py "SELECT * FROM users"

# 转换SQL
python scripts/sql_converter.py input.sql output.sql MySQL 达梦
python scripts/sql_converter.py --string "SELECT * FROM users" MySQL 金仓
```

## 转换验证清单

转换后检查：数据类型兼容、函数可用、语法正确、分页语法、事务控制、标识符大小写、保留字冲突

## 资源文件说明

| 路径 | 用途 |
|------|------|
| `references/mysql-to-*.md` / `dm-to-*.md` / `kingbase-to-*.md` | 6种转换方向的详细规则 |
| `references/database-detection.md` | 数据库语法检测指南 |
| `references/universal-syntax.md` | 通用SQL语法参考 |
| `scripts/detect_database.py` | 数据库类型检测 |
| `scripts/sql_converter.py` | SQL语法转换 |

## 注意事项

1. **测试验证**：转换后的 SQL 必须在目标数据库中测试验证
2. **性能考虑**：通用转换可能影响性能，需评估执行计划
3. **版本差异**：不同数据库版本语法有差异，注意兼容性

## 故障排除与 Fallback

### 场景1：数据库检测失败

**触发条件**：`scripts/detect_database.py` 无法识别 SQL 方言，或返回"未知"

**Fallback 路径**：
1. 提示用户手动指定源数据库类型："未能自动检测，请确认源数据库是 MySQL / 达梦 / 金仓？"
2. 若用户也无法确定 → 按 MySQL 语法处理（兼容性最广），并在输出开头标注：
   > ⚠️ 源数据库类型未知，按 MySQL 假设处理，请确认是否符合预期
3. 若涉及敏感操作（DDL），**暂停并等待用户确认**，不要继续转换

### 场景2：函数无对应映射

**触发条件**：遇到 SKILL.md 和 references/ 中均未覆盖的函数

**Fallback 路径**：
1. 保留原函数，标注警告：
   > ⚠️ `函数名()` 未找到目标数据库对应映射，保留原样，请手动确认
2. 提供目标数据库官方文档搜索关键词建议
3. 如果该函数在多条 SQL 中重复出现，汇总列出，避免重复警告

### 场景3：转换后语法验证失败

**触发条件**：转换后的 SQL 在目标数据库执行报错

**Fallback 路径**：
1. 分析错误信息，判断是否为以下类型：
   - 保留字冲突 → 为标识符添加转义符（如 `"column"`）
   - 函数参数不匹配 → 调整参数个数或类型
   - 语法不支持的特性 → 寻找等效替代方案
2. 如果无法自动修复 → 标注错误位置，提供手动修复建议
3. 必要时回退到更通用的 SQL 语法

### 场景4：脚本执行失败

**触发条件**：`scripts/detect_database.py` 或 `scripts/sql_converter.py` 执行报错

**Fallback 路径**：
1. 检查环境：Python 版本 ≥ 3.7、文件路径正确、文件存在
2. 如果脚本不可用 → 使用 SKILL.md 内置的转换规则手动转换
3. 告知用户："自动脚本暂不可用，使用内置规则手动转换，结果供参考"

### 调试建议

1. 在目标数据库中逐步执行转换后的 SQL
2. 对比源 SQL 和目标 SQL 的执行计划
3. 使用数据库语法检测工具验证转换结果