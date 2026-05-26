# 金仓转达梦数据库转换规则

## 基本原则

1. **通用语法优先**：能使用标准SQL语法的，优先使用标准SQL
2. **函数转换**：金仓特有函数转为达梦可用函数
3. **数据类型适配**：调整数据类型确保兼容性

---

## 1. 数据类型转换

| 金仓类型 | 达梦类型 | 通用类型 | 说明 |
|----------|----------|----------|------|
| SMALLINT | SMALLINT | SMALLINT | 一致 |
| INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | 一致 |
| FLOAT4 | FLOAT | REAL | 通用使用REAL |
| FLOAT8 | DOUBLE | DOUBLE PRECISION | 通用使用DOUBLE PRECISION |
| NUMERIC(p,s) | DECIMAL(p,s) | NUMERIC(p,s) | 通用使用NUMERIC |
| CHAR(n) | CHAR(n) | CHAR(n) | 一致 |
| VARCHAR(n) | VARCHAR2(n) | VARCHAR(n) | 达梦用VARCHAR2 |
| TEXT | CLOB | VARCHAR(4000) | 通用使用VARCHAR |
| BYTEA | BLOB | BYTEA | 通用BYTEA |
| TIMESTAMP | DATE | TIMESTAMP | 达梦DATE含时间 |
| DATE | DATE | DATE | 一致 |
| TIME | 无 | 无 | 达梦不支持纯TIME类型 |
| BOOLEAN | BIT | BOOLEAN | 达梦使用BIT |
| SERIAL | IDENTITY(1,1) | 序列+触发器 | 达梦使用IDENTITY |
| BIGSERIAL | BIGINT IDENTITY(1,1) | 序列+触发器 | 达梦使用BIGINT IDENTITY |
| JSONB | CLOB | VARCHAR2(4000) | 转换为文本存储 |

## 2. 函数转换

### 2.1 字符串函数

| 金仓 | 达梦 | 通用写法 | 示例 |
|------|------|----------|------|
| STRING_AGG(col, ',') | LISTAGG(col, ',') | 无通用语法 | `LISTAGG(name, ',')` |
| s1 \|\| s2 | CONCAT(s1, s2) | s1 \|\| s2 | `CONCAT('a', 'b')` |
| SUBSTRING(str, pos, len) | SUBSTR(str, pos, len) | SUBSTRING(str FROM pos FOR len) | `SUBSTR(name, 1, 10)` |
| LENGTH(str) | LENGTH(str) | CHAR_LENGTH(str) | 通用CHAR_LENGTH |
| CHAR_LENGTH(str) | CHAR_LENGTH(str) | CHAR_LENGTH(str) | 一致 |
| POSITION(sub IN str) | INSTR(str, sub) | POSITION(sub IN str) | `INSTR(name, 'a')` |
| REPLACE(str, from, to) | REPLACE(str, from, to) | REPLACE(str, from, to) | 一致 |
| UPPER(str) | UPPER(str) | UPPER(str) | 一致 |
| LOWER(str) | LOWER(str) | LOWER(str) | 一致 |
| TRIM(str) | TRIM(str) | TRIM(str) | 一致 |
| LPAD(str, len, pad) | LPAD(str, len, pad) | 无通用语法 | `LPAD(id, 5, '0')` |
| RPAD(str, len, pad) | RPAD(str, len, pad) | 无通用语法 | `RPAD(name, 20, ' ')` |
| REVERSE(str) | REVERSE(str) | 无通用语法 | `REVERSE('abc')` |
| LEFT(str, n) | LEFT(str, n) | SUBSTRING(str FROM 1 FOR n) | `LEFT(name, 5)` |
| RIGHT(str, n) | RIGHT(str, n) | 无通用语法 | `RIGHT(code, 4)` |

### 2.2 STRING_AGG转LISTAGG详细转换

**金仓**：
```sql
SELECT STRING_AGG(name, ', ' ORDER BY id)
FROM students 
GROUP BY class_id;
```

**达梦**：
```sql
SELECT LISTAGG(name, ', ') WITHIN GROUP (ORDER BY id)
FROM students 
GROUP BY class_id;
```

### 2.3 条件函数

| 金仓 | 达梦 | 通用写法 | 示例 |
|------|------|----------|------|
| CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | 一致 |
| COALESCE(e, d) | NVL(e, d) | COALESCE(e, d) | `NVL(name, '未知')` |
| NULLIF(e1, e2) | NULLIF(e1, e2) | NULLIF(e1, e2) | 一致 |
| COALESCE(e1, e2) | COALESCE(e1, e2) | COALESCE(e1, e2) | 一致 |

**COALESCE函数转换示例**：

金仓：
```sql
SELECT COALESCE(nickname, username) AS display_name FROM users;
```

达梦：
```sql
SELECT COALESCE(nickname, username) AS display_name FROM users;
```

### 2.4 日期时间函数

| 金仓 | 达梦 | 通用写法 | 示例 |
|------|------|----------|------|
| CURRENT_TIMESTAMP | SYSDATE | CURRENT_TIMESTAMP | `SYSDATE` |
| CURRENT_DATE | TRUNC(SYSDATE) | CURRENT_DATE | `TRUNC(SYSDATE)` |
| CURRENT_TIME | 无 | 无 | 达梦不支持纯TIME |
| TO_CHAR(d, 'YYYY-MM-DD') | TO_CHAR(d, 'YYYY-MM-DD') | 无通用语法 | `TO_CHAR(create_time, 'YYYY-MM-DD')` |
| TO_DATE(s, 'YYYY-MM-DD') | TO_DATE(s, 'YYYY-MM-DD') | TO_DATE(s, 'YYYY-MM-DD') | `TO_DATE('2024-01-01','YYYY-MM-DD')` |
| EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | `EXTRACT(YEAR FROM create_time)` |
| EXTRACT(MONTH FROM d) | EXTRACT(MONTH FROM d) | EXTRACT(MONTH FROM d) | `EXTRACT(MONTH FROM create_time)` |
| EXTRACT(DAY FROM d) | EXTRACT(DAY FROM d) | EXTRACT(DAY FROM d) | `EXTRACT(DAY FROM create_time)` |
| EXTRACT(HOUR FROM d) | EXTRACT(HOUR FROM d) | EXTRACT(HOUR FROM d) | `EXTRACT(HOUR FROM create_time)` |
| EXTRACT(MINUTE FROM d) | EXTRACT(MINUTE FROM d) | EXTRACT(MINUTE FROM d) | `EXTRACT(MINUTE FROM create_time)` |
| EXTRACT(SECOND FROM d) | EXTRACT(SECOND FROM d) | EXTRACT(SECOND FROM d) | `EXTRACT(SECOND FROM create_time)` |
| EXTRACT(DOW FROM d) | DAYOFWEEK(d) - 1 | 无通用语法 | `DAYOFWEEK(create_time) - 1` |
| EXTRACT(EPOCH FROM d) | 无 | 无 | 达梦不支持，需手动计算 |
| d + INTERVAL '1 day' | d + 1 | d + INTERVAL '1' DAY | `create_time + 1` |
| d - INTERVAL '1 month' | ADD_MONTHS(d, -1) | d - INTERVAL '1' MONTH | `ADD_MONTHS(create_time, -1)` |
| d1 - d2 | d1 - d2 | d1 - d2 | `end_date - start_date` |

**日期格式转换示例**：

金仓：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') FROM orders;
```

达梦：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') FROM orders;
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

**达梦**：
```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR2(100),
    created_at DATE DEFAULT SYSDATE
);
```

### 3.2 修改表

| 金仓 | 达梦 | 说明 |
|------|------|------|
| ALTER TABLE t ADD COLUMN c int | ALTER TABLE t ADD c int | 达梦无需COLUMN |
| ALTER TABLE t ALTER COLUMN c TYPE int | ALTER TABLE t MODIFY c int | 达梦语法不同 |
| ALTER TABLE t DROP COLUMN c | ALTER TABLE t DROP c | 达梦无需COLUMN |
| ALTER TABLE t RENAME COLUMN c1 TO c2 | ALTER TABLE t RENAME COLUMN c1 TO c2 | 一致 |
| ALTER TABLE t RENAME TO new_t | ALTER TABLE t RENAME TO new_t | 一致 |
| CREATE INDEX idx ON t(c) | 无 | 达梦无需显示创建索引 |

## 4. DML差异

### 4.1 INSERT

**金仓（批量插入）**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob');
```

**达梦**：
```sql
INSERT ALL
    INTO users (id, name) VALUES (1, 'Alice')
    INTO users (id, name) VALUES (2, 'Bob')
SELECT 1 FROM dual;
```

### 4.2 UPDATE

**金仓（多表更新）**：
```sql
UPDATE t1 SET name = t2.name FROM t2 WHERE t1.id = t2.id;
```

**达梦**：
```sql
MERGE INTO t1 USING t2 ON (t1.id = t2.id)
WHEN MATCHED THEN UPDATE SET t1.name = t2.name;
```

### 4.3 DELETE

**金仓（多表删除）**：
```sql
DELETE FROM t1 USING t2 WHERE t1.id = t2.id AND t2.status = 0;
```

**达梦**：
```sql
DELETE FROM t1 WHERE id IN (SELECT id FROM t2 WHERE status = 0);
```

## 5. 分页查询

**金仓**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

**达梦**：
```sql
-- 方式1：使用ROW_NUMBER()（推荐）
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) rn, t.* FROM users t
) WHERE rn BETWEEN 21 AND 30;

-- 方式2：使用LIMIT（达梦8支持）
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

## 6. 事务控制

| 金仓 | 达梦 | 说明 |
|------|------|------|
| BEGIN | 无需显式开启 | 达梦自动开启事务 |
| COMMIT | COMMIT | 一致 |
| ROLLBACK | ROLLBACK | 一致 |
| SET AUTOCOMMIT = OFF | SET AUTOCOMMIT OFF | 一致 |

## 7. 其他差异

### 7.1 空字符串与NULL

- **金仓**：空字符串('')和NULL是不同的值
- **达梦**：空字符串等同于NULL

转换时需注意：
```sql
-- 金仓中查询空字符串
WHERE name = ''

-- 达梦中等效查询
WHERE name IS NULL
```

### 7.2 DUAL表

| 金仓 | 达梦 |
|------|------|
| `SELECT 1;` | `SELECT 1 FROM dual;` |

达梦需要 `FROM dual`。

### 7.3 标识符大小写

- **金仓**：默认将未引用的标识符转为小写
- **达梦**：默认不区分大小写

建议：始终使用大写表名和列名，或始终使用双引号包裹以保持原始大小写。

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