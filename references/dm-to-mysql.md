# 达梦转MySQL数据库转换规则

## 基本原则

1. **通用语法优先**：能使用标准SQL语法的，优先使用标准SQL
2. **函数转换**：达梦特有函数转为MySQL可用函数
3. **数据类型适配**：调整数据类型确保兼容性

---

## 1. 数据类型转换

| 达梦类型 | MySQL类型 | 通用类型 | 说明 |
|----------|-----------|----------|------|
| TINYINT | TINYINT | SMALLINT | 通用使用SMALLINT |
| SMALLINT | SMALLINT | SMALLINT | 一致 |
| INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | 一致 |
| FLOAT | FLOAT | REAL | 通用使用REAL |
| DOUBLE | DOUBLE | DOUBLE PRECISION | 通用使用DOUBLE PRECISION |
| DECIMAL(p,s) | DECIMAL(p,s) | NUMERIC(p,s) | 通用使用NUMERIC |
| CHAR(n) | CHAR(n) | CHAR(n) | 一致 |
| VARCHAR2(n) | VARCHAR(n) | VARCHAR(n) | MySQL用VARCHAR |
| CLOB | LONGTEXT | VARCHAR(4000) | 通用使用VARCHAR |
| BLOB | LONGBLOB | BYTEA | 通用BYTEA |
| DATE | DATETIME | TIMESTAMP | 达梦DATE含时间，MySQL DATETIME对应 |
| TIMESTAMP | TIMESTAMP | TIMESTAMP | 一致 |
| BIT | TINYINT(1) | BOOLEAN | 通用使用BOOLEAN |
| IDENTITY(1,1) | AUTO_INCREMENT | 序列+触发器 | MySQL使用AUTO_INCREMENT |

**注意事项**：
- 达梦的 `DATE` 类型包含日期和时间信息，相当于MySQL的 `DATETIME`
- 达梦的 `VARCHAR2` 直接对应MySQL的 `VARCHAR`
- 达梦的 `CLOB` 对应MySQL的 `LONGTEXT`
- 达梦的 `IDENTITY` 自增列转换为MySQL的 `AUTO_INCREMENT`

## 2. 函数转换

### 2.1 字符串函数

| 达梦 | MySQL | 通用写法 | 示例 |
|------|-------|----------|------|
| LISTAGG(col, ',') | GROUP_CONCAT(col SEPARATOR ',') | 无通用语法 | `GROUP_CONCAT(name SEPARATOR ',')` |
| CONCAT(s1, s2) | CONCAT(s1, s2) | s1 \|\| s2 | 一致 |
| SUBSTR(str, pos, len) | SUBSTRING(str, pos, len) | SUBSTRING(str FROM pos FOR len) | `SUBSTRING(name, 1, 10)` |
| LENGTH(str) | LENGTH(str) | CHAR_LENGTH(str) | 通用CHAR_LENGTH |
| CHAR_LENGTH(str) | CHAR_LENGTH(str) | CHAR_LENGTH(str) | 一致 |
| INSTR(str, sub) | LOCATE(sub, str) | POSITION(sub IN str) | `LOCATE('a', name)` |
| REPLACE(str, from, to) | REPLACE(str, from, to) | REPLACE(str, from, to) | 一致 |
| UPPER(str) | UPPER(str) | UPPER(str) | 一致 |
| LOWER(str) | LOWER(str) | LOWER(str) | 一致 |
| TRIM(str) | TRIM(str) | TRIM(str) | 一致 |
| LPAD(str, len, pad) | LPAD(str, len, pad) | 无通用语法 | `LPAD(id, 5, '0')` |
| RPAD(str, len, pad) | RPAD(str, len, pad) | 无通用语法 | `RPAD(name, 20, ' ')` |
| REVERSE(str) | REVERSE(str) | 无通用语法 | `REVERSE('abc')` |
| LEFT(str, n) | LEFT(str, n) | SUBSTRING(str FROM 1 FOR n) | `LEFT(name, 5)` |
| RIGHT(str, n) | RIGHT(str, n) | 无通用语法 | `RIGHT(code, 4)` |

### 2.2 LISTAGG转GROUP_CONCAT详细转换

**达梦**：
```sql
SELECT LISTAGG(name, ', ') WITHIN GROUP (ORDER BY id)
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

| 达梦 | MySQL | 通用写法 | 示例 |
|------|-------|----------|------|
| CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | 一致 |
| NVL(e, d) | IFNULL(e, d) | COALESCE(e, d) | `COALESCE(name, '未知')` |
| NULLIF(e1, e2) | NULLIF(e1, e2) | NULLIF(e1, e2) | 一致 |
| COALESCE(e1, e2) | COALESCE(e1, e2) | COALESCE(e1, e2) | 一致 |

**NVL函数转换示例**：

达梦：
```sql
SELECT NVL(nickname, username) AS display_name FROM users;
```

MySQL（通用语法）：
```sql
SELECT COALESCE(nickname, username) AS display_name FROM users;
```

**注意**：达梦的 `NVL` 仅支持两个参数，`COALESCE` 支持多个参数。

### 2.4 日期时间函数

| 达梦 | MySQL | 通用写法 | 示例 |
|------|-------|----------|------|
| SYSDATE | NOW() | CURRENT_TIMESTAMP | `CURRENT_TIMESTAMP` |
| TRUNC(SYSDATE) | CURDATE() | CURRENT_DATE | `CURRENT_DATE` |
| TO_CHAR(d, 'YYYY-MM-DD') | DATE_FORMAT(d, '%Y-%m-%d') | 无通用语法 | `DATE_FORMAT(create_time, '%Y-%m-%d')` |
| TO_DATE(s, 'YYYY-MM-DD') | STR_TO_DATE(s, '%Y-%m-%d') | TO_DATE(s, 'YYYY-MM-DD') | `STR_TO_DATE('2024-01-01','%Y-%m-%d')` |
| EXTRACT(YEAR FROM d) | YEAR(d) | EXTRACT(YEAR FROM d) | `YEAR(create_time)` |
| EXTRACT(MONTH FROM d) | MONTH(d) | EXTRACT(MONTH FROM d) | `MONTH(create_time)` |
| EXTRACT(DAY FROM d) | DAY(d) | EXTRACT(DAY FROM d) | `DAY(create_time)` |
| EXTRACT(HOUR FROM d) | HOUR(d) | EXTRACT(HOUR FROM d) | `HOUR(create_time)` |
| EXTRACT(MINUTE FROM d) | MINUTE(d) | EXTRACT(MINUTE FROM d) | `MINUTE(create_time)` |
| EXTRACT(SECOND FROM d) | SECOND(d) | EXTRACT(SECOND FROM d) | `SECOND(create_time)` |
| DAYOFWEEK(d) | DAYOFWEEK(d) | 无通用语法 | `DAYOFWEEK(create_time)` |
| ADD_MONTHS(d, n) | DATE_ADD(d, INTERVAL n MONTH) | d + INTERVAL 'n' MONTH | `DATE_ADD(create_time, INTERVAL 3 MONTH)` |
| d + 1 | DATE_ADD(d, INTERVAL 1 DAY) | d + INTERVAL '1' DAY | `DATE_ADD(create_time, INTERVAL 1 DAY)` |
| d1 - d2 | DATEDIFF(d1, d2) | d1 - d2 | `DATEDIFF(end_date, start_date)` |
| LAST_DAY(d) | LAST_DAY(d) | 无通用语法 | `LAST_DAY(date_field)` |

**日期格式转换示例**：

达梦：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') FROM orders;
```

MySQL：
```sql
SELECT DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s') FROM orders;
```

**TO_DATE示例**：

达梦：
```sql
SELECT TO_DATE('2024-01-01', 'YYYY-MM-DD') FROM dual;
```

MySQL：
```sql
SELECT STR_TO_DATE('2024-01-01', '%Y-%m-%d') FROM dual;
```

### 2.5 数值函数

| 达梦 | MySQL | 通用语法 | 说明 |
|------|-------|----------|------|
| ABS(x) | ABS(x) | ABS(x) | 一致 |
| CEIL(x) | CEIL(x) | CEIL(x) | 一致 |
| FLOOR(x) | FLOOR(x) | FLOOR(x) | 一致 |
| ROUND(x, d) | ROUND(x, d) | ROUND(x, d) | 一致 |
| TRUNC(x, d) | TRUNCATE(x, d) | TRUNC(x, d) | MySQL使用TRUNCATE |
| MOD(n, m) | MOD(n, m) | MOD(n, m) | 一致 |
| RAND() | RAND() | 无通用语法 | 一致 |
| GREATEST(a, b) | GREATEST(a, b) | GREATEST(a, b) | 一致 |
| LEAST(a, b) | LEAST(a, b) | LEAST(a, b) | 一致 |

### 2.6 聚合函数

| 达梦 | MySQL | 说明 |
|------|-------|------|
| COUNT(DISTINCT col) | COUNT(DISTINCT col) | 一致 |
| LISTAGG | GROUP_CONCAT | 见2.2节 |

### 2.7 类型转换

| 达梦 | MySQL | 通用语法 | 示例 |
|------|-------|----------|------|
| CAST(e AS type) | CAST(e AS type) | CAST(e AS type) | 一致 |
| CONVERT(type, e) | CONVERT(e, type) | CAST(e AS type) | `CAST(123 AS CHAR(10))` |

## 3. DDL差异

### 3.1 创建表

**达梦**：
```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR2(100),
    created_at DATE DEFAULT SYSDATE
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

| 达梦 | MySQL | 说明 |
|------|-------|------|
| ALTER TABLE t ADD c int | ALTER TABLE t ADD COLUMN c int | MySQL需COLUMN |
| ALTER TABLE t MODIFY c int | ALTER TABLE t MODIFY c int | 一致 |
| ALTER TABLE t DROP c | ALTER TABLE t DROP COLUMN c | MySQL需COLUMN |
| ALTER TABLE t RENAME COLUMN c1 TO c2 | ALTER TABLE t CHANGE c1 c2 int | MySQL语法不同 |
| ALTER TABLE t RENAME TO new_t | ALTER TABLE t RENAME TO new_t | 一致 |

## 4. DML差异

### 4.1 INSERT

**达梦（批量插入）**：
```sql
INSERT ALL
    INTO users (id, name) VALUES (1, 'Alice')
    INTO users (id, name) VALUES (2, 'Bob')
SELECT 1 FROM dual;
```

**MySQL**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

### 4.2 UPDATE

**达梦（多表更新）**：
```sql
MERGE INTO t1 USING t2 ON (t1.id = t2.id)
WHEN MATCHED THEN UPDATE SET t1.name = t2.name;
```

**MySQL**：
```sql
UPDATE t1, t2 SET t1.name = t2.name WHERE t1.id = t2.id;
```

### 4.3 DELETE

**达梦（多表删除）**：
```sql
DELETE FROM t1 WHERE id IN (SELECT id FROM t2 WHERE status = 0);
```

**MySQL**：
```sql
DELETE t1 FROM t1, t2 WHERE t1.id = t2.id AND t2.status = 0;
```

## 5. 分页查询

**达梦（ROW_NUMBER方式）**：
```sql
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) rn, t.* FROM users t
) WHERE rn BETWEEN 21 AND 30;
```

**MySQL**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

## 6. 事务控制

| 达梦 | MySQL | 说明 |
|------|-------|------|
| 无需显式开启 | START TRANSACTION | MySQL需显式开启 |
| COMMIT | COMMIT | 一致 |
| ROLLBACK | ROLLBACK | 一致 |
| SET AUTOCOMMIT OFF | SET autocommit = 0 | 一致 |

## 7. 其他差异

### 7.1 空字符串与NULL

- **达梦**：空字符串('')等同于NULL
- **MySQL**：空字符串('')和NULL是不同的值

转换时需注意：
```sql
-- 达梦中查询空字符串
WHERE name IS NULL

-- MySQL中等效查询
WHERE name = ''
```

达梦转MySQL时，如果查询条件中有 `IS NULL`，需要确认原始场景是真正的NULL还是空字符串。

### 7.2 DUAL表

| 达梦 | MySQL |
|------|-------|
| `SELECT 1 FROM dual;` | `SELECT 1 FROM dual;` 或 `SELECT 1;` |

两种写法在MySQL中均可使用。

### 7.3 ROWNUM

达梦中可使用 `ROWNUM` 进行分页，MySQL中不支持 `ROWNUM`，需使用 `LIMIT` + `OFFSET`。

## 8. 完整转换示例

### 示例1：复杂查询转换

**达梦**：
```sql
SELECT 
    c.name AS class_name,
    COUNT(s.id) AS student_count,
    LISTAGG(s.name, ', ') WITHIN GROUP (ORDER BY s.score DESC) AS top_students,
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

**达梦**：
```sql
CREATE TABLE orders (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    order_no VARCHAR2(50) NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) DEFAULT 0.00,
    status TINYINT DEFAULT 0,
    remark CLOB,
    created_at DATE DEFAULT SYSDATE,
    updated_at DATE DEFAULT SYSDATE
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

CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_status ON orders(status);
```
