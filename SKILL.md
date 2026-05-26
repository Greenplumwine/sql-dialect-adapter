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

## 快速开始

### 1. 确定转换方向

| 源数据库 | 目标数据库 | 参考文档 |
|----------|------------|----------|
| MySQL | 达梦 | [references/mysql-to-dm.md](references/mysql-to-dm.md) |
| MySQL | 金仓 | [references/mysql-to-kingbase.md](references/mysql-to-kingbase.md) |
| 达梦 | MySQL | [references/dm-to-mysql.md](references/dm-to-mysql.md) |
| 达梦 | 金仓 | [references/dm-to-kingbase.md](references/dm-to-kingbase.md) |
| 金仓 | MySQL | [references/kingbase-to-mysql.md](references/kingbase-to-mysql.md) |
| 金仓 | 达梦 | [references/kingbase-to-dm.md](references/kingbase-to-dm.md) |

### 2. 应用转换规则

根据转换方向参考相应的文档，按照以下顺序应用转换规则：

1. **数据类型转换**：将源数据库特有类型转换为目标数据库兼容类型
2. **函数转换**：将源数据库特有函数转换为目标数据库可用函数
3. **语法转换**：调整DDL/DML语法差异
4. **分页查询转换**：处理分页查询语法差异
5. **事务控制转换**：调整事务语法

### 3. 验证转换结果

使用数据库语法检测工具验证转换后的SQL是否符合目标数据库语法。

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

## 数据库语法检测

当不确定SQL代码使用的数据库类型时，使用数据库语法检测功能：

1. **检测当前数据库类型**：使用 `scripts/detect_database.py` 分析SQL代码
2. **获取转换建议**：根据检测结果选择正确的转换方向
3. **验证转换结果**：转换后再次检测确保符合目标数据库语法

具体检测方法参考 [references/database-detection.md](references/database-detection.md)

## 转换工具

### 自动检测脚本

```bash
# 检测SQL文件使用的数据库类型
python scripts/detect_database.py your_sql_file.sql

# 检测SQL字符串
python scripts/detect_database.py "SELECT IFNULL(name, '未知') FROM users"
```

### 语法转换脚本

```bash
# 转换SQL文件
python scripts/sql_converter.py input.sql output.sql MySQL 达梦

# 转换SQL字符串
python scripts/sql_converter.py --string "SELECT * FROM users" MySQL 金仓
```

## 常见场景转换示例

### 场景1：条件函数转换

**源SQL（MySQL）**：
```sql
SELECT IF(score >= 60, '及格', '不及格'), 
       IFNULL(name, '未知'),
       GROUP_CONCAT(name SEPARATOR ', ')
FROM students 
GROUP BY class_id;
```

**通用转换**：
```sql
SELECT CASE WHEN score >= 60 THEN '及格' ELSE '不及格' END,
       COALESCE(name, '未知'),
       -- 使用目标数据库的字符串聚合函数
FROM students 
GROUP BY class_id;
```

### 场景2：分页查询转换

**源SQL（MySQL）**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

**通用转换**：
```sql
-- 使用标准LIMIT/OFFSET语法
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

### 场景3：日期函数转换

**源SQL（MySQL）**：
```sql
SELECT DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s'),
       UNIX_TIMESTAMP(create_time)
FROM orders;
```

**通用转换**：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS'),
       EXTRACT(EPOCH FROM create_time)
FROM orders;
```

## 转换验证清单

完成SQL转换后，检查以下项目：

1. ✅ **数据类型兼容**：所有数据类型在目标数据库中可用
2. ✅ **函数可用**：所有函数在目标数据库中支持
3. ✅ **语法正确**：DDL/DML语法符合目标数据库规范
4. ✅ **分页查询**：分页语法正确转换
5. ✅ **事务控制**：事务语法正确
6. ✅ **标识符大小写**：表名、列名大小写正确处理
7. ✅ **保留字冲突**：避免使用目标数据库保留字

## 资源文件说明

- `references/mysql-to-dm.md` - MySQL转达梦详细转换规则
- `references/mysql-to-kingbase.md` - MySQL转金仓详细转换规则
- `references/dm-to-mysql.md` - 达梦转MySQL详细转换规则
- `references/dm-to-kingbase.md` - 达梦转金仓详细转换规则
- `references/kingbase-to-mysql.md` - 金仓转MySQL详细转换规则
- `references/kingbase-to-dm.md` - 金仓转达梦详细转换规则
- `references/database-detection.md` - 数据库语法检测指南
- `references/universal-syntax.md` - 通用SQL语法参考
- `scripts/detect_database.py` - 数据库类型检测脚本
- `scripts/sql_converter.py` - SQL语法转换脚本

## 注意事项

1. **测试验证**：转换后的SQL必须在目标数据库中测试验证
2. **性能考虑**：某些通用转换可能影响性能，需评估
3. **功能完整性**：确保转换后的SQL功能与原始SQL一致
4. **错误处理**：转换过程中可能遇到无法自动转换的语法，需要手动处理
5. **版本差异**：不同数据库版本可能有语法差异，需注意版本兼容性

## 故障排除

### 常见问题

1. **函数不存在**：检查函数是否在目标数据库中支持，参考函数差异文档
2. **语法错误**：仔细对比源SQL和目标SQL的语法差异
3. **数据类型不兼容**：使用通用数据类型或目标数据库兼容类型
4. **分页查询失败**：检查分页语法是否正确转换

### 调试建议

1. 在目标数据库中逐步执行转换后的SQL
2. 使用数据库客户端工具查看详细错误信息
3. 对比源SQL和目标SQL的执行计划
4. 使用数据库语法检测工具验证转换结果