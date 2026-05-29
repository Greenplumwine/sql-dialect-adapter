# 金仓转MySQL数据库转换规则

## 基本原则

1. **通用语法优先**：能使用标准SQL语法的，优先使用标准SQL
2. **函数转换**：金仓特有函数转为MySQL可用函数
3. **数据类型适配**：调整数据类型确保兼容性

---

## 1. 数据类型转换

| 金仓类型 | MySQL类型 | 通用类型 | 说明 |
|----------|-----------|----------|------|
| SMALLINT | SMALLINT | SMALLINT | 一致 |
| INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | 一致 |
| FLOAT4 | FLOAT | REAL | 通用使用REAL |
| FLOAT8 | DOUBLE | DOUBLE PRECISION | 通用使用DOUBLE PRECISION |
| NUMERIC(p,s) | DECIMAL(p,s) | NUMERIC(p,s) | 通用使用NUMERIC |
| CHAR(n) | CHAR(n) | CHAR(n) | 一致 |
| VARCHAR(n) | VARCHAR(n) | VARCHAR(n) | 一致 |
| TEXT | LONGTEXT | VARCHAR(4000) | 通用使用VARCHAR |
| BYTEA | LONGBLOB | BYTEA | 通用BYTEA |
| TIMESTAMP | DATETIME | TIMESTAMP | MySQL DATETIME对应金仓TIMESTAMP |
| DATE | DATE | DATE | 一致 |
| TIME | TIME | TIME | 一致 |
| BOOLEAN | TINYINT(1) | BOOLEAN | MySQL使用TINYINT(1) |
| SERIAL | INT AUTO_INCREMENT | 序列+触发器 | MySQL使用AUTO_INCREMENT |
| BIGSERIAL | BIGINT AUTO_INCREMENT | 序列+触发器 | MySQL使用BIGINT AUTO_INCREMENT |
| JSONB | JSON | JSON | MySQL支持JSON类型 |

## 2. 函数转换

### 2.1 字符串函数

| 金仓 | MySQL | 通用写法 | 示例 |
|------|-------|----------|------|
| STRING_AGG(col, ',') | GROUP_CONCAT(col SEPARATOR ',') | 无通用语法 | `GROUP_CONCAT(name SEPARATOR ',')` |
| s1 \|\| s2 | CONCAT(s1, s2) | s1 \|\| s2 | `CONCAT('a', 'b')` |
| SUBSTRING(str, pos, len) | SUBSTRING(str, pos, len) | SUBSTRING(str FROM pos FOR len) | `SUBSTRING(name, 1, 10)` |
| LENGTH(str) | LENGTH(str) | CHAR_LENGTH(str) | 通用CHAR_LENGTH |
| CHAR_LENGTH(str) | CHAR_LENGTH(str) | CHAR_LENGTH(str) | 一致 |
| POSITION(sub IN str) | LOCATE(sub, str) | POSITION(sub IN str) | `LOCATE('a', name)` |
| REPLACE(str, from, to) | REPLACE(str, from, to) | REPLACE(str, from, to) | 一致 |
| UPPER(str) | UPPER(str) | UPPER(str) | 一致 |
| LOWER(str) | LOWER(str) | LOWER(str) | 一致 |
| TRIM(str) | TRIM(str) | TRIM(str) | 一致 |
| LPAD(str, len, pad) | LPAD(str, len, pad) | 无通用语法 | `LPAD(id, 5, '0')` |
| RPAD(str, len, pad) | RPAD(str, len, pad) | 无通用语法 | `RPAD(name, 20, ' ')` |
| REVERSE(str) | REVERSE(str) | 无通用语法 | `REVERSE('abc')` |
| LEFT(str, n) | LEFT(str, n) | SUBSTRING(str FROM 1 FOR n) | `LEFT(name, 5)` |
| RIGHT(str, n) | RIGHT(str, n) | 无通用语法 | `RIGHT(code, 4)` |

### 2.2 STRING_AGG转GROUP_CONCAT详细转换

**金仓**：
```sql
SELECT STRING_AGG(name, ', ' ORDER BY id)
FROM students 
GROUP BY class_id;
```

**MySQL**：
```sql
SELECT GROUP_CONCAT(name ORDER BY id SEPARATOR ', ')
FROM students 
GROUP BY class_id;
```

### 2.3 条件函数

| 金仓 | MySQL | 通用写法 | 示例 |
|------|-------|----------|------|
| CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | 一致 |
| COALESCE(e, d) | COALESCE(e, d) | COALESCE(e, d) | `COALESCE(name, '未知')` |
| NULLIF(e1, e2) | NULLIF(e1, e2) | NULLIF(e1, e2) | 一致 |
| COALESCE(e1, e2) | COALESCE(e1, e2) | COALESCE(e1, e2) | 一致 |

### 2.4 日期时间函数

| 金仓 | MySQL | 通用写法 | 示例 |
|------|-------|----------|------|
| CURRENT_TIMESTAMP | NOW() | CURRENT_TIMESTAMP | `NOW()` |
| CURRENT_DATE | CURDATE() | CURRENT_DATE | `CURDATE()` |
| CURRENT_TIME | CURTIME() | CURRENT_TIME | `CURTIME()` |
| TO_CHAR(d, 'YYYY-MM-DD') | DATE_FORMAT(d, '%Y-%m-%d') | 无通用语法 | `DATE_FORMAT(create_time, '%Y-%m-%d')` |
| TO_DATE(s, 'YYYY-MM-DD') | STR_TO_DATE(s, '%Y-%m-%d') | TO_DATE(s, 'YYYY-MM-DD') | `STR_TO_DATE('2024-01-01','%Y-%m-%d')` |
| EXTRACT(YEAR FROM d) | YEAR(d) | EXTRACT(YEAR FROM d) | `YEAR(create_time)` |
| EXTRACT(MONTH FROM d) | MONTH(d) | EXTRACT(MONTH FROM d) | `MONTH(create_time)` |
| EXTRACT(DAY FROM d) | DAY(d) | EXTRACT(DAY FROM d) | `DAY(create_time)` |
| EXTRACT(HOUR FROM d) | HOUR(d) | EXTRACT(HOUR FROM d) | `HOUR(create_time)` |
| EXTRACT(MINUTE FROM d) | MINUTE(d) | EXTRACT(MINUTE FROM d) | `MINUTE(create_time)` |
| EXTRACT(SECOND FROM d) | SECOND(d) | EXTRACT(SECOND FROM d) | `SECOND(create_time)` |
| EXTRACT(DOW FROM d) | DAYOFWEEK(d) - 1 | 无通用语法 | `DAYOFWEEK(create_time) - 1` |
| EXTRACT(EPOCH FROM d) | UNIX_TIMESTAMP(d) | EXTRACT(EPOCH FROM d) | `UNIX_TIMESTAMP(create_time)` |
| d + INTERVAL '1 day' | DATE_ADD(d, INTERVAL 1 DAY) | d + INTERVAL '1' DAY | `DATE_ADD(create_time, INTERVAL 1 DAY)` |
| d - INTERVAL '1 month' | DATE_SUB(d, INTERVAL 1 MONTH) | d - INTERVAL '1' MONTH | `DATE_SUB(create_time, INTERVAL 1 MONTH)` |
| d1 - d2 | DATEDIFF(d1, d2) | d1 - d2 | `DATEDIFF(end_date, start_date)` |

**日期格式转换示例**：

金仓：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') FROM orders;
```

MySQL：
```sql
SELECT DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s') FROM orders;
```

## 3. DDL差异

### 3.1 创建表

**金仓**：
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**MySQL**：
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 3.2 修改表

| 金仓 | MySQL | 说明 |
|------|-------|------|
| ALTER TABLE t ADD COLUMN c int | ALTER TABLE t ADD COLUMN c int | 一致 |
| ALTER TABLE t ALTER COLUMN c TYPE int | ALTER TABLE t MODIFY c int | MySQL语法不同 |
| ALTER TABLE t DROP COLUMN c | ALTER TABLE t DROP COLUMN c | 一致 |
| ALTER TABLE t RENAME COLUMN c1 TO c2 | ALTER TABLE t CHANGE c1 c2 int | MySQL语法不同 |
| ALTER TABLE t RENAME TO new_t | ALTER TABLE t RENAME TO new_t | 一致 |
| CREATE INDEX idx ON t(c) | ALTER TABLE t ADD INDEX idx(c) | MySQL语法不同 |

## 4. DML差异

### 4.1 INSERT

**金仓**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

**MySQL**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

### 4.2 UPDATE

**金仓**：
```sql
UPDATE t1 SET name = t2.name FROM t2 WHERE t1.id = t2.id;
```

**MySQL**：
```sql
UPDATE t1, t2 SET t1.name = t2.name WHERE t1.id = t2.id;
```

### 4.3 DELETE

**金仓**：
```sql
DELETE FROM t1 USING t2 WHERE t1.id = t2.id AND t2.status = 0;
```

**MySQL**：
```sql
DELETE t1 FROM t1, t2 WHERE t1.id = t2.id AND t2.status = 0;
```

## 5. 分页查询

**金仓**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

**MySQL**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

## 6. 事务控制

| 金仓 | MySQL | 说明 |
|------|-------|------|
| BEGIN | START TRANSACTION | MySQL使用START TRANSACTION |
| COMMIT | COMMIT | 一致 |
| ROLLBACK | ROLLBACK | 一致 |
| SET AUTOCOMMIT = OFF | SET autocommit = 0 | 一致 |

## 7. 其他差异

### 7.1 双引号语义

| 场景 | 金仓 | MySQL |
|------|------|-------|
| `"column_name"` | 带引号的标识符 | 字符串字面量（严格模式下报错） |
| `'column_name'` | 字符串字面量 | 字符串字面量 |
| `` `column_name` `` | 无效语法 | 标识符 |

**转换时需注意**：金仓中双引号用于标识符，MySQL中双引号在非ANSI模式下为字符串，在严格模式下会报错。建议将所有双引号标识符转为反引号。

**转换示例**：
金仓：
```sql
SELECT "user_name" FROM "users";
```

MySQL：
```sql
SELECT `user_name` FROM `users`;
```

### 7.2 保留字差异

金仓数据库的保留字比MySQL更多，需注意以下常用词是否为保留字：

| 关键字 | 金仓 | MySQL | 处理方式 |
|--------|------|-------|----------|
| LIMIT | 保留字 | 非保留字 | 金仓中需注意 |
| OFFSET | 保留字 | 非保留字 | 金仓中需注意 |
| TYPE | 保留字 | 非保留字 | 金仓中需注意 |
| WINDOW | 保留字 | 保留字 | 使用反引号包裹 |
| USER | 保留字 | 保留字 | 使用反引号包裹 |

### 7.3 标识符大小写

- **金仓**：默认将未引用的标识符转为小写
- **MySQL**：默认大小写敏感取决于操作系统

建议：始终使用小写表名和列名，或始终使用反引号包裹以保持原始大小写。

## 8. 完整转换示例

### 示例1：复杂查询转换

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

**MySQL**：
```sql
SELECT 
    c.name AS class_name,
    COUNT(s.id) AS student_count,
    GROUP_CONCAT(s.name ORDER BY s.score DESC SEPARATOR ', ') AS top_students,
    CASE WHEN AVG(s.score) >= 60 THEN '达标' ELSE '未达标' END AS status,
    DATE_FORMAT(MAX(s.created_at), '%Y-%m-%d') AS last_updated
FROM classes c
LEFT JOIN students s ON c.id = s.class_id
WHERE c.status = 'active'
GROUP BY c.id, c.name
HAVING COUNT(s.id) > 10
ORDER BY student_count DESC
LIMIT 5;
```

### 示例2：建表语句转换

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
```

**MySQL**：
```sql
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) DEFAULT 0.00,
    status TINYINT DEFAULT 0 COMMENT '0-待支付 1-已支付',
    remark LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```