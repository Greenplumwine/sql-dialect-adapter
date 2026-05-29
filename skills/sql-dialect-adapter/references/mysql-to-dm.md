# MySQL转达梦数据库转换规则

## 基本原则

1. **通用语法优先**：能使用标准SQL语法的，优先使用标准SQL
2. **函数转换**：MySQL特有函数转为达梦可用函数
3. **数据类型适配**：调整数据类型确保兼容性

---

## 1. 数据类型转换

| MySQL类型 | 达梦类型 | 通用类型 | 说明 |
|-----------|----------|----------|------|
| TINYINT | TINYINT | SMALLINT | 达梦支持TINYINT，通用用SMALLINT |
| SMALLINT | SMALLINT | SMALLINT | 一致 |
| MEDIUMINT | INT | INT | 达梦无MEDIUMINT |
| INT | INT | INT | 一致 |
| BIGINT | BIGINT | BIGINT | 一致 |
| FLOAT | FLOAT | REAL | 通用使用REAL |
| DOUBLE | DOUBLE | DOUBLE PRECISION | 通用使用DOUBLE PRECISION |
| DECIMAL(p,s) | DECIMAL(p,s) | NUMERIC(p,s) | 通用使用NUMERIC |
| CHAR(n) | CHAR(n) | CHAR(n) | 一致 |
| VARCHAR(n) | VARCHAR2(n) | VARCHAR(n) | 达梦用VARCHAR2 |
| TEXT | CLOB | VARCHAR2(4000) | 达梦CLOB |
| MEDIUMTEXT | CLOB | VARCHAR2(4000) | 同上 |
| LONGTEXT | CLOB | CLOB | 达梦CLOB |
| BLOB | BLOB | BYTEA | 通用BYTEA |
| DATETIME | DATE | TIMESTAMP | 达梦DATE含时间 |
| DATE | DATE | DATE | 一致 |
| TIMESTAMP | TIMESTAMP | TIMESTAMP | 一致 |
| TIME | TIME | 无 | 达梦不支持纯TIME类型 |
| YEAR | CHAR(4) | CHAR(4) | 达梦无YEAR类型 |
| ENUM('a','b') | VARCHAR2(10) | VARCHAR(10) | 使用VARCHAR存储 |
| SET | VARCHAR2(100) | VARCHAR(100) | 使用VARCHAR存储 |
| JSON | CLOB | VARCHAR2(4000) | 转换为文本存储 |
| BOOLEAN | BIT | BOOLEAN | 通用使用BOOLEAN |
| AUTO_INCREMENT | IDENTITY(1,1) | 序列+触发器 | 达梦使用IDENTITY |

## 2. 函数转换

### 2.1 字符串函数

| MySQL | 达梦 | 通用写法 | 示例 |
|-------|------|----------|------|
| GROUP_CONCAT(col SEPARATOR ',') | LISTAGG(col, ',') | 无通用语法，使用达梦函数 | `LISTAGG(name, ',')` |
| CONCAT(s1, s2) | CONCAT(s1, s2) 或 \|\| | s1 \|\| s2 | `'a' \|\| 'b'` |
| CONCAT_WS(',', a, b) | 自定义组合 | a \|\| ',' \|\| b | `col1 \|\| ',' \|\| col2` |
| SUBSTRING(str, pos, len) | SUBSTR(str, pos, len) | SUBSTRING(str FROM pos FOR len) | `SUBSTR(name, 1, 10)` |
| LENGTH(str) | LENGTH(str) | CHAR_LENGTH(str) | 通用CHAR_LENGTH |
| CHAR_LENGTH(str) | CHAR_LENGTH(str) | CHAR_LENGTH(str) | 一致 |
| LOCATE(sub, str) | INSTR(str, sub) | POSITION(sub IN str) | `POSITION('a' IN name)` |
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

**达梦**：
```sql
SELECT LISTAGG(name, ', ') WITHIN GROUP (ORDER BY id)
FROM students 
GROUP BY class_id;
```

### 2.3 条件函数

| MySQL | 达梦 | 通用写法 | 示例 |
|-------|------|----------|------|
| IF(cond, v1, v2) | CASE WHEN cond THEN v1 ELSE v2 END | CASE WHEN cond THEN v1 ELSE v2 END | `CASE WHEN score>=60 THEN '及格' ELSE '不及格' END` |
| IFNULL(e, d) | NVL(e, d) | COALESCE(e, d) | `COALESCE(name, '未知')` |
| NULLIF(e1, e2) | NULLIF(e1, e2) | NULLIF(e1, e2) | 一致 |
| COALESCE(e1, e2) | COALESCE(e1, e2) | COALESCE(e1, e2) | 一致 |

**IF函数转换示例**：

MySQL：
```sql
SELECT IF(score >= 60, '及格', '不及格') AS result FROM students;
```

达梦：
```sql
SELECT CASE WHEN score >= 60 THEN '及格' ELSE '不及格' END AS result FROM students;
```

**IFNULL函数转换示例**：

MySQL：
```sql
SELECT IFNULL(nickname, username) AS display_name FROM users;
```

达梦（通用语法）：
```sql
SELECT COALESCE(nickname, username) AS display_name FROM users;
```

### 2.4 日期时间函数

| MySQL | 达梦 | 通用写法 | 示例 |
|-------|------|----------|------|
| NOW() | SYSDATE | CURRENT_TIMESTAMP | `CURRENT_TIMESTAMP` |
| CURDATE() | TRUNC(SYSDATE) | CURRENT_DATE | `CURRENT_DATE` |
| CURTIME() | 不直接支持 | CAST(SYSDATE AS TIME) | `SYSDATE` |
| DATE_FORMAT(d, '%Y-%m-%d') | TO_CHAR(d, 'YYYY-MM-DD') | 无通用语法 | `TO_CHAR(create_time, 'YYYY-MM-DD')` |
| STR_TO_DATE(s, '%Y-%m-%d') | TO_DATE(s, 'YYYY-MM-DD') | TO_DATE(s, 'YYYY-MM-DD') | `TO_DATE('2024-01-01','YYYY-MM-DD')` |
| YEAR(d) | EXTRACT(YEAR FROM d) | EXTRACT(YEAR FROM d) | `EXTRACT(YEAR FROM create_time)` |
| MONTH(d) | EXTRACT(MONTH FROM d) | EXTRACT(MONTH FROM d) | `EXTRACT(MONTH FROM create_time)` |
| DAY(d) | EXTRACT(DAY FROM d) | EXTRACT(DAY FROM d) | `EXTRACT(DAY FROM create_time)` |
| HOUR(d) | EXTRACT(HOUR FROM d) | EXTRACT(HOUR FROM d) | `EXTRACT(HOUR FROM create_time)` |
| MINUTE(d) | EXTRACT(MINUTE FROM d) | EXTRACT(MINUTE FROM d) | `EXTRACT(MINUTE FROM create_time)` |
| SECOND(d) | EXTRACT(SECOND FROM d) | EXTRACT(SECOND FROM d) | `EXTRACT(SECOND FROM create_time)` |
| WEEKDAY(d) | DAYOFWEEK(d) - 1 | 无通用语法 | `DAYOFWEEK(create_time) - 1` |
| DAYOFWEEK(d) | DAYOFWEEK(d) | 无通用语法 | `DAYOFWEEK(create_time)` |
| UNIX_TIMESTAMP(d) | 无 | 无通用语法 | 需要自行计算 |
| DATE_ADD(d, INTERVAL 1 DAY) | d + 1 | d + INTERVAL '1' DAY | `create_time + 1` |
| DATE_SUB(d, INTERVAL 1 MONTH) | ADD_MONTHS(d, -1) | d - INTERVAL '1' MONTH | `ADD_MONTHS(create_time, -1)` |
| DATEDIFF(d1, d2) | d1 - d2 | d1 - d2 | `end_date - start_date` |
| TIMESTAMPDIFF(unit, d1, d2) | 需要计算 | 无通用语法 | 根据unit手动计算 |
| LAST_DAY(d) | LAST_DAY(d) | 无通用语法 | `LAST_DAY(date_field)` |

**日期格式转换示例**：

MySQL：
```sql
SELECT DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s') FROM orders;
```

达梦：
```sql
SELECT TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') FROM orders;
```

**STR_TO_DATE示例**：

MySQL：
```sql
SELECT STR_TO_DATE('2024-01-01', '%Y-%m-%d') FROM dual;
```

达梦：
```sql
SELECT TO_DATE('2024-01-01', 'YYYY-MM-DD') FROM dual;
```

### 2.5 数值函数

| MySQL | 达梦 | 通用语法 | 说明 |
|-------|------|----------|------|
| ABS(x) | ABS(x) | ABS(x) | 一致 |
| CEIL(x) | CEIL(x) | CEIL(x) | 一致 |
| FLOOR(x) | FLOOR(x) | FLOOR(x) | 一致 |
| ROUND(x, d) | ROUND(x, d) | ROUND(x, d) | 一致 |
| TRUNCATE(x, d) | TRUNC(x, d) | TRUNC(x, d) | 一致 |
| MOD(n, m) | MOD(n, m) | MOD(n, m) | 一致 |
| RAND() | RAND() | 无通用语法 | 达梦支持 |
| FORMAT(x, d) | 无 | 无通用语法 | 需要手动格式化 |
| GREATEST(a, b) | GREATEST(a, b) | GREATEST(a, b) | 一致 |
| LEAST(a, b) | LEAST(a, b) | LEAST(a, b) | 一致 |

### 2.6 聚合函数

| MySQL | 达梦 | 说明 |
|-------|------|------|
| COUNT(DISTINCT col) | COUNT(DISTINCT col) | 一致 |
| GROUP_CONCAT | LISTAGG | 见2.2节 |
| BIT_AND | 无 | 需自定义 |
| BIT_OR | 无 | 需自定义 |
| JSON_OBJECTAGG | 无 | 需自定义 |

### 2.7 类型转换

| MySQL | 达梦 | 通用语法 | 示例 |
|-------|------|----------|------|
| CAST(e AS type) | CAST(e AS type) | CAST(e AS type) | 一致 |
| CONVERT(e, type) | CONVERT(type, e) | CAST(e AS type) | `CAST(123 AS VARCHAR2(10))` |

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

**达梦**：
```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR2(100),
    created_at DATE DEFAULT SYSDATE
);
```

### 3.2 修改表

| MySQL | 达梦 | 说明 |
|-------|------|------|
| ALTER TABLE t ADD COLUMN c int | ALTER TABLE t ADD c int | 无需COLUMN关键字 |
| ALTER TABLE t MODIFY c int | ALTER TABLE t MODIFY c int | 一致 |
| ALTER TABLE t DROP COLUMN c | ALTER TABLE t DROP c | 无需COLUMN关键字 |
| ALTER TABLE t CHANGE c1 c2 int | ALTER TABLE t RENAME COLUMN c1 TO c2 | 达梦语法不同 |
| ALTER TABLE t RENAME TO new_t | ALTER TABLE t RENAME TO new_t | 一致 |
| ALTER TABLE t ADD INDEX idx(c) | 无 | 达梦无需显示创建索引 |

## 4. DML差异

### 4.1 INSERT

**MySQL（批量插入）**：
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

**通用写法**：
```sql
INSERT INTO users (id, name) VALUES (1, 'Alice');
INSERT INTO users (id, name) VALUES (2, 'Bob');
```

### 4.2 UPDATE

**MySQL（多表更新）**：
```sql
UPDATE t1, t2 SET t1.name = t2.name WHERE t1.id = t2.id;
```

**达梦**：
```sql
MERGE INTO t1 USING t2 ON (t1.id = t2.id)
WHEN MATCHED THEN UPDATE SET t1.name = t2.name;
```

### 4.3 DELETE

**MySQL（多表删除）**：
```sql
DELETE t1 FROM t1, t2 WHERE t1.id = t2.id AND t2.status = 0;
```

**达梦**：
```sql
DELETE FROM t1 WHERE id IN (SELECT id FROM t2 WHERE status = 0);
```

## 5. 分页查询

**MySQL**：
```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

**达梦**：
```sql
-- 方式1：使用ROWNUM（不推荐）
SELECT * FROM (SELECT ROWNUM rn, t.* FROM (SELECT * FROM users ORDER BY id) t) WHERE rn BETWEEN 21 AND 30;

-- 方式2：使用ROW_NUMBER()（推荐）
SELECT * FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY id) rn, t.* FROM users t
) WHERE rn BETWEEN 21 AND 30;

-- 方式3：使用LIMIT（达梦8支持）
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

## 6. 事务控制

| MySQL | 达梦 | 说明 |
|-------|------|------|
| START TRANSACTION | 无需显式开启 | 达梦自动开启事务 |
| COMMIT | COMMIT | 一致 |
| ROLLBACK | ROLLBACK | 一致 |
| SET autocommit = 0 | SET AUTOCOMMIT OFF | 设置自动提交 |

## 7. 其他差异

### 7.1 空字符串与NULL

- **MySQL**：空字符串('')和NULL是不同的值
- **达梦**：空字符串等同于NULL

转换时需注意：
```sql
-- MySQL中查询空字符串
WHERE name = ''

-- 达梦中等效查询
WHERE name IS NULL
```

### 7.2 表别名

**MySQL**：
```sql
SELECT * FROM users u;
```

**达梦**：
```sql
SELECT * FROM users u;  -- 达梦支持AS别名的隐式写法
SELECT * FROM users AS u;  -- 但推荐使用AS
```

### 7.3 LIMIT语法

**MySQL**：
```sql
SELECT * FROM users LIMIT 10;
```

**达梦**：
```sql
SELECT * FROM users FETCH FIRST 10 ROWS ONLY;
-- 或
SELECT * FROM users WHERE ROWNUM <= 10;
```

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