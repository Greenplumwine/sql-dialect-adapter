# MySQL转金仓数据库转换规则

## 基本原则

1. **通用语法优先**：能使用标准SQL语法的，优先使用标准SQL
2. **函数转换**：MySQL特有函数转为金仓可用函数
3. **数据类型适配**：调整数据类型确保兼容性

---

## 1. 数据类型转换

| MySQL类型 | 金仓类型 | 通用类型 | 说明 |
|-----------|----------|----------|------|
| TINYINT | SMALLINT | SMALLINT | 金仓无TINYINT |
| SMALLINT | SMALLINT | SMALLINT | 一致 |
| MEDIUMINT | INT | INT | 金仓无MEDIUMINT |
| INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | 一致 |
| FLOAT | FLOAT4 | REAL | 通用使用REAL |
| DOUBLE | FLOAT8 | DOUBLE PRECISION | 通用使用DOUBLE PRECISION |
| DECIMAL(p,s) | NUMERIC(p,s) | NUMERIC(p,s) | 一致 |
| CHAR(n) | CHAR(n) | CHAR(n) | 一致 |
| VARCHAR(n) | VARCHAR(n) | VARCHAR(n) | 一致 |
| TEXT | TEXT | VARCHAR(4000) | 通用使用VARCHAR |
| MEDIUMTEXT | TEXT | VARCHAR(4000) | 同上 |
| LONGTEXT | TEXT | TEXT | 金仓TEXT支持大文本 |
| BLOB | BYTEA | BYTEA | 一致 |
| DATETIME | TIMESTAMP | TIMESTAMP | 金仓使用TIMESTAMP |
| DATE | DATE | DATE | 一致 |
| TIMESTAMP | TIMESTAMP | TIMESTAMP | 一致 |
| TIME | TIME | TIME | 一致 |
| YEAR | CHAR(4) | CHAR(4) | 金仓无YEAR类型 |
| ENUM('a','b') | VARCHAR(10) | VARCHAR(10) | 使用VARCHAR存储 |
| SET | VARCHAR(100) | VARCHAR(100) | 使用VARCHAR存储 |
| JSON | JSONB | JSONB | 金仓支持JSONB类型 |
| BOOLEAN | BOOLEAN | BOOLEAN | 一致 |
| AUTO_INCREMENT | SERIAL | 序列+触发器 | 金仓使用SERIAL |

## 2. 函数转换

### 2.1 字符串函数

| MySQL | 金仓 | 通用写法 | 示例 |
|-------|------|----------|------|
| GROUP_CONCAT(col SEPARATOR ',') | STRING_AGG(col, ',') | 无通用语法 | `STRING_AGG(name, ',')` |
| CONCAT(s1, s2) | s1 \|\| s2 | s1 \|\| s2 | `'a' \|\| 'b'` |
| CONCAT_WS(',', a, b) | a \|\| ',' \|\| b | a \|\| ',' \|\| b | `col1 \|\| ',' \|\| col2` |
| SUBSTRING(str, pos, len) | SUBSTRING(str, pos, len) | SUBSTRING(str FROM pos FOR len) | `SUBSTRING(name, 1, 10)` |
| LENGTH(str) | LENGTH(str) | CHAR_LENGTH(str) | 通用CHAR_LENGTH |
| CHAR_LENGTH(str) | CHAR_LENGTH(str) | CHAR_LENGTH(str) | 一致 |
| LOCATE(sub, str) | POSITION(sub IN str) | POSITION(sub IN str) | `POSITION('a' IN name)` |
| REPLACE(str, from, to) | REPLACE(str, from, to) | REPLACE(str, from, to) | 一致 |
| UPPER(str) | UPPER(str) | UPPER(str) | 一致 |
| LOWER(str) | LOWER(str) | LOWER(str) | 一致 |
| TRIM(str) | TRIM(str) | TRIM(str) | 一致 |
| LPAD(str, len, pad) | LPAD(str, len, pad) | 无通用语法 | `LPAD(id, 5, '0')` |
| RPAD(str, len, pad) | RPAD(str, len, pad) | 无通用语法 | `RPAD(name, 20, ' ')` |
| REVERSE(str) | REVERSE(str) | 无通用语法 | `REVERSE('abc')` |
| LEFT(str, n) | LEFT(str, n) | SUBSTRING(str FROM 1 FOR n) | `LEFT(name, 5)` |
| RIGHT(str, n) | RIGHT(str, n) | 无通用语法 | `RIGHT(code, 4)` |

### 2.2 GROUP_CONCAT详细转换

**MySQL**：
```sql
SELECT GROUP_CONCAT(name ORDER BY id SEPARATOR ', ')
FROM students 
GROUP BY class_id;
```

**金仓**：
```sql
SELECT STRING_AGG(name, ', ' ORDER BY id)
FROM students 
GROUP BY class_id;
```

### 2.3 条件函数

| MySQL | 金仓 | 通用写法 | 示例 |
|-------|------|----------|------|
| IF(cond, v1, v2) | CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | `CASE WHEN score>=60 THEN '及格' ELSE '不及格' END` |
| IFNULL(e, d) | COALESCE(e, d) | COALESCE(e, d) | `COALESCE(name, '未知')` |
| NULLIF(e1, e2) | NULLIF(e1, e2) | NULLIF(e1, e2) | 一致 |
| COALESCE(e1, e2) | COALESCE(e1, e2) | COALESCE(e1, e2) | 一致 |

**IF函数转换示例**：

MySQL：
```sql
SELECT IF(score >= 60, '及格', '不及格') AS result FROM students;
```

金仓：
```sql
SELECT CASE WHEN score >= 60 THEN '及格' ELSE '不及格' END AS result FROM students;
```

**IFNULL函数转换示例**：

MySQL：
```sql
SELECT IFNULL(nickname, username) AS display_name FROM users;
```

金仓：
```sql
SELECT COALESCE(nickname, username) AS display_name FROM users;
```

### 2.4 日期时间函数

| MySQL | 金仓 | 通用写法 | 示例 |
|-------|------|----------|------|
| NOW() | CURRENT_TIMESTAMP | CURRENT_TIMESTAMP | `CURRENT_TIMESTAMP` |
| CURDATE() | CURRENT_DATE | CURRENT_DATE | `CURRENT_DATE` |
| CURTIME() | CURRENT_TIME | CURRENT_TIME | `CURRENT_TIME` |
| DATE_FORMAT(d, '%Y-%m-%d') | TO_CHAR(d, 'YYYY-MM-DD') | 无通用语法 | `TO_CHAR(create_time, 'YYYY-MM-DD')` |
| STR_TO_DATE(s, '%Y-%m-%d') | TO_DATE(s, 'YYYY-MM-DD') | TO_DATE(s, 'YYYY-MM-DD') | `TO_DATE('2024-01-01','YYYY-MM-DD')` |
| YEAR(d) | EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | `EXTRACT(YEAR FROM create_time)` |
| MONTH(d) | EXTRACT(MONTH FROM d) | EXTRACT(MONTH FROM d) | `EXTRACT(MONTH FROM create_time)` |
| DAY(d) | EXTRACT(DAY FROM d) | EXTRACT(DAY FROM d) | `EXTRACT(DAY FROM create_time)` |
| HOUR(d) | EXTRACT(HOUR FROM d) | EXTRACT(HOUR FROM d) | `EXTRACT(HOUR FROM create_time)` |
| MINUTE(d) | EXTRACT(MINUTE FROM d) | EXTRACT(MINUTE FROM d) | `EXTRACT(MINUTE FROM create_time)` |
| SECOND(d) | EXTRACT(SECOND FROM d) | EXTRACT(SECOND FROM d) | `EXTRACT(SECOND FROM create_time)` |
| WEEKDAY(d) | EXTRACT(DOW FROM d) - 1 | 无通用语法 | `EXTRACT(DOW FROM create_time) - 1` |
| DAYOFWEEK(d) | EXTRACT(DOW FROM d) | 无通用语法 | `EXTRACT(DOW FROM create_time)` |
| UNIX_TIMESTAMP(d) | EXTRACT(EPOCH FROM d) | EXTRACT(EPOCH FROM d) | `EXTRACT(EPOCH FROM create_time)` |
| DATE_ADD(d, INTERVAL 1 DAY) | d + INTERVAL '1 day' | d + INTERVAL '1' DAY | `create_time + INTERVAL '1 day'` |
| DATE_SUB(d, INTERVAL 1 MONTH) | d - INTERVAL '1 month' | d - INTERVAL '1' MONTH | `create_time - INTERVAL '1 month'` |
| DATEDIFF(d1, d2) | d1 - d2 | d1 - d2 | `end_date - start_date` |
| TIMESTAMPDIFF(unit, d1, d2) | 根据unit使用EXTRACT计算 | 无通用语法 | 根据unit手动计算 |
| LAST_DAY(d) | (DATE_TRUNC('month', d) + INTERVAL '1 month' - INTERVAL '1 day')::DATE | 无通用语法 | `(DATE_TRUNC('month', create_time) + INTERVAL '1 month' - INTERVAL '1 day')::DATE` |

**日期格式转换示例**：

MySQL：
```sql
SELECT DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s') FROM orders;
```

金仓：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') FROM orders;
```

**STR_TO_DATE示例**：

MySQL：
```sql
SELECT STR_TO_DATE('2024-01-01', '%Y-%m-%d') FROM dual;
```

金仓：
```sql
SELECT TO_DATE('2024-01-01', 'YYYY-MM-DD') FROM dual;
```

### 2.5 数值函数

| MySQL | 金仓 | 通用语法 | 说明 |
|-------|------|----------|------|
| ABS(x) | ABS(x) | ABS(x) | 一致 |
| CEIL(x) | CEIL(x) | CEIL(x) | 一致 |
| FLOOR(x) | FLOOR(x) | FLOOR(x) | 一致 |
| ROUND(x, d) | ROUND(x, d) | ROUND(x, d) | 一致 |
| TRUNCATE(x, d) | TRUNC(x, d) | TRUNC(x, d) | 一致 |
| MOD(n, m) | MOD(n, m) | MOD(n, m) | 一致 |
| RAND() | RANDOM() | 无通用语法 | 金仓使用RANDOM() |
| FORMAT(x, d) | TO_CHAR(x, 'FM9999999990.00') | 无通用语法 | 需要手动格式化 |
| GREATEST(a, b) | GREATEST(a, b) | GREATEST(a, b) | 一致 |
| LEAST(a, b) | LEAST(a, b) | LEAST(a, b) | 一致 |

### 2.6 聚合函数

| MySQL | 金仓 | 说明 |
|-------|------|------|
| COUNT(DISTINCT col) | COUNT(DISTINCT col) | 一致 |
| GROUP_CONCAT | STRING_AGG | 见2.2节 |
| BIT_AND | BIT_AND | 一致 |
| BIT_OR | BIT_OR | 一致 |
| JSON_OBJECTAGG | JSON_OBJECTAGG | 金仓支持 |

### 2.7 类型转换

| MySQL | 金仓 | 通用语法 | 示例 |
|-------|------|----------|------|
| CAST(e AS type) | CAST(e AS type) | CAST(e AS type) | 一致 |
| CONVERT(e, type) | CAST(e AS type) | CAST(e AS type) | `CAST(123 AS VARCHAR(10))` |

## 3. DDL差异

### 3.1 创建表

**MySQL**：
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**金仓**：
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 修改表

| MySQL | 金仓 | 说明 |
|-------|------|------|
| ALTER TABLE t ADD COLUMN c int | ALTER TABLE t ADD COLUMN c int | 一致 |
| ALTER TABLE t MODIFY c int | ALTER TABLE t ALTER COLUMN c TYPE int | 金仓语法不同 |
| ALTER TABLE t DROP COLUMN c | ALTER TABLE t DROP COLUMN c | 一致 |
| ALTER TABLE t CHANGE c1 c2 int | ALTER TABLE t RENAME COLUMN c1 TO c2 | 金仓语法不同 |
| ALTER TABLE t RENAME TO new_t | ALTER TABLE t RENAME TO new_t | 一致 |
| ALTER TABLE t ADD INDEX idx(c) | CREATE INDEX idx ON t(c) | 金仓使用CREATE INDEX |

## 4. DML差异

### 4.1 INSERT

**MySQL（批量插入）**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

**金仓**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

**通用写法（兼容所有数据库）**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice');
INSERT INTO users (id, name) VALUES (2, 'Bob');
```

### 4.2 UPDATE

**MySQL（多表更新）**：
```sql
UPDATE t1, t2 SET t1.name = t2.name WHERE t1.id = t2.id;
```

**金仓**：
```sql
UPDATE t1 SET name = t2.name FROM t2 WHERE t1.id = t2.id;
```

### 4.3 DELETE

**MySQL（多表删除）**：
```sql
DELETE t1 FROM t1, t2 WHERE t1.id = t2.id AND t2.status = 0;
```

**金仓**：
```sql
DELETE FROM t1 USING t2 WHERE t1.id = t2.id AND t2.status = 0;
```

## 5. 分页查询

**MySQL**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

**金仓**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

## 6. 事务控制

| MySQL | 金仓 | 说明 |
|-------|------|------|
| START TRANSACTION | BEGIN | 金仓使用BEGIN |
| COMMIT | COMMIT | 一致 |
| ROLLBACK | ROLLBACK | 一致 |
| SET autocommit = 0 | SET AUTOCOMMIT = OFF | 设置自动提交 |

## 7. 其他差异

### 7.1 空字符串与NULL

- **MySQL**：空字符串('')和NULL是不同的值
- **金仓**：空字符串('')和NULL是不同的值

与达梦不同，金仓和MySQL一样区分空字符串和NULL，不存在此兼容问题。

### 7.2 保留字差异

金仓数据库的保留字比MySQL更多，需注意以下常用词是否为保留字：

| 关键字 | MySQL | 金仓 | 处理方式 |
|--------|-------|------|----------|
| USER | 保留字 | 保留字 | 使用双引号包裹 |
| ORDER | 保留字 | 保留字 | 使用双引号包裹 |
| GROUP | 保留字 | 保留字 | 使用双引号包裹 |
| LIMIT | 非保留字 | 保留字 | 金仓中需注意 |
| OFFSET | 非保留字 | 保留字 | 金仓中需注意 |
| WINDOW | 保留字 | 保留字 | 使用双引号包裹 |
| TYPE | 非保留字 | 保留字 | 金仓中需注意 |

### 7.3 标识符大小写

- **MySQL**：默认大小写敏感取决于操作系统（Linux下敏感，Windows下不敏感）
- **金仓**：默认将未引用的标识符转为小写

建议：始终使用小写表名和列名，或始终使用双引号包裹以保持原始大小写。

### 7.4 双引号语义

| 场景 | MySQL | 金仓 |
|------|-------|------|
| `"column_name"` | 字符串字面量 | 带引号的标识符 |
| `'column_name'` | 字符串字面量 | 字符串字面量 |
| `` `column_name` `` | 标识符 | 无效语法 |

**转换时需注意**：MySQL中双引号用于字符串在严格模式下会报错，金仓中双引号仅用于标识符。如有MySQL使用双引号做字符串的场景，需转换为单引号。

## 8. 完整转换示例

### 示例1：复杂查询转换

**MySQL**：
```sql
SELECT 
    c.name AS class_name,
    COUNT(s.id) AS student_count,
    GROUP_CONCAT(s.name ORDER BY s.score DESC SEPARATOR ', ') AS top_students,
    IF(AVG(s.score) >= 60, '达标', '未达标') AS status,
    DATE_FORMAT(MAX(s.created_at), '%Y-%m-%d') AS last_updated
FROM classes c
LEFT JOIN students s ON c.id = s.class_id
WHERE c.status = 'active'
GROUP BY c.id
HAVING student_count > 10
ORDER BY student_count DESC
LIMIT 5;
```

**金仓**：
```sql
SELECT 
    c.name AS class_name,
    COUNT(s.id) AS student_count,
    STRING_AGG(s.name, ', ' ORDER BY s.score DESC) AS top_students,
    CASE WHEN AVG(s.score) >= 60 THEN '达标' ELSE '未达标' END AS status,
    TO_CHAR(MAX(s.created_at), 'YYYY-MM-DD') AS last_updated
FROM classes c
LEFT JOIN students s ON c.id = s.class_id
WHERE c.status = 'active'
GROUP BY c.id, c.name
HAVING COUNT(s.id) > 10
ORDER BY student_count DESC
LIMIT 5;
```

### 示例2：建表语句转换

**MySQL**：
```sql
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) DEFAULT 0.00,
    status TINYINT DEFAULT 0 COMMENT '0-待支付 1-已支付',
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```

**金仓**：
```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(50) NOT NULL,
    user_id BIGINT NOT NULL,
    amount NUMERIC(10,2) DEFAULT 0.00,
    status SMALLINT DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_status ON orders(status);
```
