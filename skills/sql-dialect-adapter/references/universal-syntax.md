# 通用SQL语法参考

## 概述

本指南提供MySQL、达梦、金仓三种数据库的通用SQL语法建议，遵循"通用语法优先"原则，确保SQL在三种数据库中都可用。

## 通用数据类型

| 通用类型 | MySQL | 达梦 | 金仓 | 说明 |
|----------|-------|------|------|------|
| SMALLINT | SMALLINT | SMALLINT | SMALLINT | 一致 |
| INT | INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | BIGINT | 一致 |
| REAL | FLOAT | FLOAT | FLOAT4 | 单精度浮点 |
| DOUBLE PRECISION | DOUBLE | DOUBLE | FLOAT8 | 双精度浮点 |
| NUMERIC(p,s) | DECIMAL(p,s) | DECIMAL(p,s) | NUMERIC(p,s) | 精确数值 |
| CHAR(n) | CHAR(n) | CHAR(n) | CHAR(n) | 定长字符串 |
| VARCHAR(n) | VARCHAR(n) | VARCHAR2(n) | VARCHAR(n) | 变长字符串 |
| VARCHAR(4000) | TEXT | CLOB | TEXT | 大文本通用方案 |
| BYTEA | LONGBLOB | BLOB | BYTEA | 二进制数据 |
| TIMESTAMP | DATETIME | DATE | TIMESTAMP | 日期时间 |
| DATE | DATE | DATE | DATE | 日期 |
| BOOLEAN | TINYINT(1) | BIT | BOOLEAN | 布尔值 |

**自增列通用方案**：
```sql
-- 通用方案：使用序列+触发器
CREATE SEQUENCE seq_users_id START WITH 1 INCREMENT BY 1;

CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

-- 各数据库具体实现不同，此为通用概念
```

## 通用函数

### 条件判断

**通用语法**：
```sql
CASE WHEN condition THEN value1 ELSE value2 END
```

**替代方案**：
- MySQL特有：`IF(condition, value1, value2)`
- 达梦特有：`CASE WHEN condition THEN value1 ELSE value2 END`（与通用一致）
- 金仓特有：`CASE WHEN condition THEN value1 ELSE value2 END`（与通用一致）

### 空值处理

**通用语法**：
```sql
COALESCE(expression, default_value)
```

**替代方案**：
- MySQL特有：`IFNULL(expression, default_value)`
- 达梦特有：`NVL(expression, default_value)`
- 金仓特有：`COALESCE(expression, default_value)`（与通用一致）

### 字符串连接

**通用语法**：
```sql
'string1' || 'string2'
```

**替代方案**：
- MySQL特有：`CONCAT('string1', 'string2')`
- 达梦特有：`CONCAT('string1', 'string2')` 或 `'string1' || 'string2'`
- 金仓特有：`'string1' || 'string2'`（与通用一致）

### 字符串提取

**通用语法**：
```sql
SUBSTRING(string FROM start FOR length)
```

**替代方案**：
- MySQL特有：`SUBSTRING(string, start, length)`
- 达梦特有：`SUBSTR(string, start, length)`
- 金仓特有：`SUBSTRING(string, start, length)`（与通用一致）

### 字符串位置查找

**通用语法**：
```sql
POSITION(substring IN string)
```

**替代方案**：
- MySQL特有：`LOCATE(substring, string)`
- 达梦特有：`INSTR(string, substring)`（参数顺序相反）
- 金仓特有：`POSITION(substring IN string)`（与通用一致）

### 当前日期时间

**通用语法**：
```sql
CURRENT_TIMESTAMP
```

**替代方案**：
- MySQL特有：`NOW()`
- 达梦特有：`SYSDATE`
- 金仓特有：`CURRENT_TIMESTAMP`（与通用一致）

### 日期格式化

**通用语法**：无通用语法，需使用数据库特有函数

**各数据库语法**：
- MySQL：`DATE_FORMAT(date, '%Y-%m-%d')`
- 达梦：`TO_CHAR(date, 'YYYY-MM-DD')`
- 金仓：`TO_CHAR(date, 'YYYY-MM-DD')`

**建议**：在应用层处理日期格式化，或为每个数据库编写适配函数。

## 通用DML语法

### SELECT

**通用语法**：
```sql
SELECT column1, column2
FROM table1 t1
INNER JOIN table2 t2 ON t1.id = t2.id
WHERE condition
GROUP BY column1
HAVING aggregate_condition
ORDER BY column1
```

**分页查询通用方案**：
```sql
-- 使用ROW_NUMBER()实现通用分页
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS rn, t.*
    FROM table t
) AS numbered
WHERE rn BETWEEN start_row AND end_row;
```

### INSERT

**通用语法**：
```sql
INSERT INTO table (col1, col2) VALUES (val1, val2);
```

**批量插入通用方案**：
```sql
-- 多次执行单条插入
INSERT INTO table (col1, col2) VALUES (val1, val2);
INSERT INTO table (col1, col2) VALUES (val3, val4);
```

### UPDATE

**通用语法**：
```sql
UPDATE table SET col1 = value1 WHERE condition;
```

**多表更新通用方案**：
```sql
-- 使用子查询
UPDATE table1 
SET col1 = (SELECT col2 FROM table2 WHERE table2.id = table1.id)
WHERE EXISTS (SELECT 1 FROM table2 WHERE table2.id = table1.id);
```

### DELETE

**通用语法**：
```sql
DELETE FROM table WHERE condition;
```

**多表删除通用方案**：
```sql
-- 使用子查询
DELETE FROM table1 
WHERE id IN (SELECT id FROM table2 WHERE condition);
```

## 通用DDL语法

### 创建表

**通用语法**：
```sql
CREATE TABLE table_name (
    column1 data_type [NOT NULL],
    column2 data_type [DEFAULT default_value],
    PRIMARY KEY (column1)
);
```

**自增列通用方案**：
```sql
-- 不使用数据库特有自增语法，在应用层控制
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
```

### 修改表

**通用语法**：
```sql
ALTER TABLE table_name ADD column_name data_type;
ALTER TABLE table_name DROP COLUMN column_name;
ALTER TABLE table_name RENAME TO new_table_name;
```

### 创建索引

**通用语法**：
```sql
CREATE INDEX index_name ON table_name (column_name);
```

## 事务控制

**通用语法**：
```sql
-- 开始事务（各数据库实现不同）
-- MySQL: START TRANSACTION
-- 达梦: 自动开始
-- 金仓: BEGIN

-- 提交事务
COMMIT;

-- 回滚事务
ROLLBACK;
```

**建议**：在应用层使用事务管理框架，避免直接使用数据库特有的事务语法。

## 标识符命名规范

### 通用规则

1. **使用小写**：表名、列名、索引名等全部使用小写
2. **使用下划线分隔**：`user_account` 而不是 `userAccount` 或 `UserAccount`
3. **避免保留字**：不使用 `user`, `order`, `group`, `limit`, `offset` 等保留字
4. **不使用特殊字符**：仅使用字母、数字、下划线
5. **长度适中**：不超过30个字符

### 标识符引用

**通用方案**：不使用任何引号包裹标识符

**各数据库差异**：
- MySQL：反引号 `` `column_name` ``
- 达梦：双引号 `"column_name"`
- 金仓：双引号 `"column_name"`

**建议**：遵循命名规范，避免使用需要引号的标识符。

## 最佳实践

### 1. 避免数据库特有函数

**不推荐**：
```sql
-- MySQL特有
SELECT IFNULL(name, 'unknown') FROM users;

-- 达梦特有
SELECT NVL(name, 'unknown') FROM users;
```

**推荐**：
```sql
-- 通用语法
SELECT COALESCE(name, 'unknown') FROM users;
```

### 2. 使用标准数据类型

**不推荐**：
```sql
-- MySQL特有
TINYINT, MEDIUMINT, YEAR, ENUM

-- 达梦特有
VARCHAR2, CLOB

-- 金仓特有
SERIAL, BIGSERIAL, JSONB
```

**推荐**：
```sql
-- 通用类型
SMALLINT, INT, BIGINT, VARCHAR, TEXT, NUMERIC, TIMESTAMP
```

### 3. 分页查询通用化

**不推荐**：
```sql
-- MySQL/金仓特有
SELECT * FROM users LIMIT 10 OFFSET 20;

-- 达梦特有
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) rn, t.* FROM users t
) WHERE rn BETWEEN 21 AND 30;
```

**推荐**：
```sql
-- 通用分页
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS rn, t.*
    FROM users t
) AS numbered
WHERE rn BETWEEN 21 AND 30;
```

### 4. 日期时间处理

**不推荐**：
```sql
-- MySQL特有
SELECT DATE_FORMAT(create_time, '%Y-%m-%d') FROM orders;

-- 达梦/金仓特有
SELECT TO_CHAR(create_time, 'YYYY-MM-DD') FROM orders;
```

**推荐**：
```sql
-- 在应用层格式化，或使用数据库适配层
SELECT create_time FROM orders;
```

## 兼容性检查清单

完成SQL编写后，检查以下项目：

1. ✅ **数据类型兼容**：所有数据类型在三种数据库中都可用
2. ✅ **函数兼容**：所有函数在三种数据库中都支持
3. ✅ **语法兼容**：DDL/DML语法符合三种数据库规范
4. ✅ **标识符兼容**：标识符命名无需引号包裹
5. ✅ **保留字检查**：未使用任何数据库的保留字
6. ✅ **分页兼容**：分页查询使用通用方案
7. ✅ **事务兼容**：事务控制使用应用层管理
8. ✅ **字符集兼容**：使用UTF-8字符集