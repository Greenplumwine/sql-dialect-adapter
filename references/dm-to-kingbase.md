# 达梦转金仓数据库转换规则

## 基本原则

1. **通用语法优先**：能使用标准SQL语法的，优先使用标准SQL
2. **函数转换**：达梦特有函数转为金仓可用函数
3. **数据类型适配**：调整数据类型确保兼容性

---

## 1. 数据类型转换

| 达梦类型 | 金仓类型 | 通用类型 | 说明 |
|----------|----------|----------|------|
| TINYINT | SMALLINT | SMALLINT | 金仓无TINYINT |
| SMALLINT | SMALLINT | SMALLINT | 一致 |
| INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | 一致 |
| FLOAT | FLOAT4 | REAL | 通用使用REAL |
| DOUBLE | FLOAT8 | DOUBLE PRECISION | 通用使用DOUBLE PRECISION |
| DECIMAL(p,s) | NUMERIC(p,s) | NUMERIC(p,s) | 一致 |
| CHAR(n) | CHAR(n) | CHAR(n) | 一致 |
| VARCHAR2(n) | VARCHAR(n) | VARCHAR(n) | 金仓用VARCHAR |
| CLOB | TEXT | VARCHAR(4000) | 通用使用VARCHAR |
| BLOB | BYTEA | BYTEA | 一致 |
| DATE | TIMESTAMP | TIMESTAMP | 达梦DATE含时间，金仓用TIMESTAMP |
| TIMESTAMP | TIMESTAMP | TIMESTAMP | 一致 |
| BIT | BOOLEAN | BOOLEAN | 通用使用BOOLEAN |
| IDENTITY(1,1) | SERIAL | 序列+触发器 | 金仓使用SERIAL |

## 2. 函数转换

### 2.1 字符串函数

| 达梦 | 金仓 | 通用写法 | 示例 |
|------|------|----------|------|
| LISTAGG(col, ',') | STRING_AGG(col, ',') | 无通用语法 | `STRING_AGG(name, ',')` |
| CONCAT(s1, s2) | s1 \|\| s2 | s1 \|\| s2 | `'a' \|\| 'b'` |
| SUBSTR(str, pos, len) | SUBSTRING(str, pos, len) | SUBSTRING(str FROM pos FOR len) | `SUBSTRING(name, 1, 10)` |
| LENGTH(str) | LENGTH(str) | CHAR_LENGTH(str) | 通用CHAR_LENGTH |
| CHAR_LENGTH(str) | CHAR_LENGTH(str) | CHAR_LENGTH(str) | 一致 |
| INSTR(str, sub) | POSITION(sub IN str) | POSITION(sub IN str) | `POSITION('a' IN name)` |
| REPLACE(str, from, to) | REPLACE(str, from, to) | REPLACE(str, from, to) | 一致 |
| UPPER(str) | UPPER(str) | UPPER(str) | 一致 |
| LOWER(str) | LOWER(str) | LOWER(str) | 一致 |
| TRIM(str) | TRIM(str) | TRIM(str) | 一致 |
| LPAD(str, len, pad) | LPAD(str, len, pad) | 无通用语法 | `LPAD(id, 5, '0')` |
| RPAD(str, len, pad) | RPAD(str, len, pad) | 无通用语法 | `RPAD(name, 20, ' ')` |
| REVERSE(str) | REVERSE(str) | 无通用语法 | `REVERSE('abc')` |
| LEFT(str, n) | LEFT(str, n) | SUBSTRING(str FROM 1 FOR n) | `LEFT(name, 5)` |
| RIGHT(str, n) | RIGHT(str, n) | 无通用语法 | `RIGHT(code, 4)` |

### 2.2 LISTAGG转STRING_AGG详细转换

**达梦**：
```sql
SELECT LISTAGG(name, ', ') WITHIN GROUP (ORDER BY id)
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

| 达梦 | 金仓 | 通用写法 | 示例 |
|------|------|----------|------|
| CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | 一致 |
| NVL(e, d) | COALESCE(e, d) | COALESCE(e, d) | `COALESCE(name, '未知')` |
| NULLIF(e1, e2) | NULLIF(e1, e2) | NULLIF(e1, e2) | 一致 |
| COALESCE(e1, e2) | COALESCE(e1, e2) | COALESCE(e1, e2) | 一致 |

**NVL函数转换示例**：

达梦：
```sql
SELECT NVL(nickname, username) AS display_name FROM users;
```

金仓：
```sql
SELECT COALESCE(nickname, username) AS display_name FROM users;
```

### 2.4 日期时间函数

| 达梦 | 金仓 | 通用写法 | 示例 |
|------|------|----------|------|
| SYSDATE | CURRENT_TIMESTAMP | CURRENT_TIMESTAMP | `CURRENT_TIMESTAMP` |
| TRUNC(SYSDATE) | CURRENT_DATE | CURRENT_DATE | `CURRENT_DATE` |
| TO_CHAR(d, 'YYYY-MM-DD') | TO_CHAR(d, 'YYYY-MM-DD') | 无通用语法 | `TO_CHAR(create_time, 'YYYY-MM-DD')` |
| TO_DATE(s, 'YYYY-MM-DD') | TO_DATE(s, 'YYYY-MM-DD') | TO_DATE(s, 'YYYY-MM-DD') | `TO_DATE('2024-01-01','YYYY-MM-DD')` |
| EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | `EXTRACT(YEAR FROM create_time)` |
| EXTRACT(MONTH FROM d) | EXTRACT(MONTH FROM d) | EXTRACT(MONTH FROM d) | `EXTRACT(MONTH FROM create_time)` |
| EXTRACT(DAY FROM d) | EXTRACT(DAY FROM d) | EXTRACT(DAY FROM d) | `EXTRACT(DAY FROM create_time)` |
| EXTRACT(HOUR FROM d) | EXTRACT(HOUR FROM d) | EXTRACT(HOUR FROM d) | `EXTRACT(HOUR FROM create_time)` |
| EXTRACT(MINUTE FROM d) | EXTRACT(MINUTE FROM d) | EXTRACT(MINUTE FROM d) | `EXTRACT(MINUTE FROM create_time)` |
| EXTRACT(SECOND FROM d) | EXTRACT(SECOND FROM d) | EXTRACT(SECOND FROM d) | `EXTRACT(SECOND FROM create_time)` |
| DAYOFWEEK(d) | EXTRACT(DOW FROM d) + 1 | 无通用语法 | `EXTRACT(DOW FROM create_time) + 1` |
| ADD_MONTHS(d, n) | d + INTERVAL 'n month' | d + INTERVAL 'n' MONTH | `create_time + INTERVAL '3 month'` |
| d + 1 | d + INTERVAL '1 day' | d + INTERVAL '1' DAY | `create_time + INTERVAL '1 day'` |
| d1 - d2 | d1 - d2 | d1 - d2 | `end_date - start_date` |
| LAST_DAY(d) | (DATE_TRUNC('month', d) + INTERVAL '1 month' - INTERVAL '1 day')::DATE | 无通用语法 | 需手动计算 |

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

**金仓**：
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 修改表

| 达梦 | 金仓 | 说明 |
|------|------|------|
| ALTER TABLE t ADD c int | ALTER TABLE t ADD COLUMN c int | 金仓需COLUMN |
| ALTER TABLE t MODIFY c int | ALTER TABLE t ALTER COLUMN c TYPE int | 金仓语法不同 |
| ALTER TABLE t DROP c | ALTER TABLE t DROP COLUMN c | 金仓需COLUMN |
| ALTER TABLE t RENAME COLUMN c1 TO c2 | ALTER TABLE t RENAME COLUMN c1 TO c2 | 一致 |
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

**金仓**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

### 4.2 UPDATE

**达梦（多表更新）**：
```sql
MERGE INTO t1 USING t2 ON (t1.id = t2.id)
WHEN MATCHED THEN UPDATE SET t1.name = t2.name;
```

**金仓**：
```sql
UPDATE t1 SET name = t2.name FROM t2 WHERE t1.id = t2.id;
```

### 4.3 DELETE

**达梦**：
```sql
DELETE FROM t1 WHERE id IN (SELECT id FROM t2 WHERE status = 0);
```

**金仓**：
```sql
DELETE FROM t1 USING t2 WHERE t1.id = t2.id AND t2.status = 0;
```

## 5. 分页查询

**达梦（ROW_NUMBER方式）**：
```sql
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) rn, t.* FROM users t
) WHERE rn BETWEEN 21 AND 30;
```

**金仓**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

## 6. 事务控制

| 达梦 | 金仓 | 说明 |
|------|------|------|
| 无需显式开启 | BEGIN | 金仓使用BEGIN |
| COMMIT | COMMIT | 一致 |
| ROLLBACK | ROLLBACK | 一致 |
| SET AUTOCOMMIT OFF | SET AUTOCOMMIT = OFF | 一致 |

## 7. 其他差异

### 7.1 空字符串与NULL

- **达梦**：空字符串('')等同于NULL
- **金仓**：空字符串('')和NULL是不同的值

转换时需注意：
```sql
-- 达梦中查询空字符串
WHERE name IS NULL

-- 金仓中等效查询
WHERE name = ''
```

达梦转金仓时，若原始达梦代码用 `IS NULL` 判断空字符串，需确认业务意图后决定是否改为 `= ''`。

### 7.2 DUAL表

| 达梦 | 金仓 |
|------|------|
| `SELECT 1 FROM dual;` | `SELECT 1;` |

金仓中可省略 `FROM dual`。

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