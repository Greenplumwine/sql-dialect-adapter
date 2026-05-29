# 数据库语法检测指南

## 概述

当不确定一段SQL代码属于哪种数据库时，通过分析SQL语句中的特征语法模式来推断数据库类型。

## 检测流程

### 1. 提取特征关键词

扫描SQL代码中是否有以下数据库特有语法：

| 特征 | 数据库 | 说明 |
|------|--------|------|
| AUTO_INCREMENT | MySQL | 自增列关键字 |
| ENGINE=InnoDB | MySQL | 存储引擎声明 |
| CHARSET=utf8mb4 | MySQL | 字符集声明 |
| LIMIT n OFFSET m | MySQL / 金仓 | 分页语法（金仓也支持） |
| IDENTITY(1,1) | 达梦 | 自增列关键字 |
| VARCHAR2 | 达梦 | 字符类型 |
| LISTAGG | 达梦 | 字符串聚合函数 |
| STRING_AGG | 金仓 | 字符串聚合函数 |
| SERIAL | 金仓 | 自增列类型 |
| BIGSERIAL | 金仓 | 大自增列类型 |
| :: 类型转换 | 金仓 | 双冒号类型转换 |
| INSERT ALL | 达梦 | 批量插入语法 |
| MERGE INTO | 达梦 | 多表更新语法 |
| SYSDATE | 达梦 | 当前日期时间 |
| DUAL | 达梦 | 虚表 |
| GROUP_CONCAT | MySQL | 字符串聚合函数 |
| IF(cond, v1, v2) | MySQL | 条件函数 |
| IFNULL | MySQL | 空值处理函数 |
| USING t2 | 金仓 | DELETE多表删除 |
| BEGIN | 金仓 | 事务开启 |
| BYTEA | 金仓 | 二进制类型 |
| JSONB | 金仓 | JSONB类型 |

### 2. 加权评分

每匹配到一个特征，对应数据库权重 +1：

```
MySQL 权重 = AUTO_INCREMENT + ENGINE + CHARSET + IF() + GROUP_CONCAT + IFNULL
达梦 权重 = IDENTITY + VARCHAR2 + LISTAGG + INSERT ALL + MERGE + SYSDATE + DUAL
金仓 权重 = SERIAL + STRING_AGG + :: + BYTEA + JSONB + BEGIN + USING
```

### 3. 确定数据库类型

- 最高权重且权重 > 1：确定为该数据库
- 最高权重 = 1 或 多数据库权重相同：标记为"不确定"，列出候选
- 所有权重 = 0：标记为"标准SQL"，可能是通用SQL或无法识别

## 手动检测清单

在不确定数据库类型时，逐项检查：

### MySQL特有语法

- [ ] 使用了 `AUTO_INCREMENT`
- [ ] 使用了 `ENGINE=InnoDB`
- [ ] 使用了 `CHARSET=utf8` 或 `utf8mb4`
- [ ] 使用了 `GROUP_CONCAT` 函数
- [ ] 使用了 `IF(cond, v1, v2)` 条件函数
- [ ] 使用了 `IFNULL(e, d)` 函数
- [ ] 使用了 `LOCATE(sub, str)` 函数
- [ ] 使用了 `` ` `` 反引号标识符
- [ ] DATE_FORMAT 使用了 `%Y-%m-%d` 格式

### 达梦特有语法

- [ ] 使用了 `IDENTITY(1,1)`
- [ ] 使用了 `VARCHAR2` 类型
- [ ] 使用了 `LISTAGG` 函数
- [ ] 使用了 `INSERT ALL ... SELECT 1 FROM dual`
- [ ] 使用了 `MERGE INTO ... WHEN MATCHED THEN UPDATE`
- [ ] 使用了 `SYSDATE`
- [ ] 使用了 `NVL` 函数
- [ ] 使用了 `INSTR(str, sub)` 函数（参数顺序与MySQL相反）
- [ ] TO_CHAR 使用了 `YYYY-MM-DD HH24:MI:SS` 格式

### 金仓特有语法

- [ ] 使用了 `SERIAL` 或 `BIGSERIAL`
- [ ] 使用了 `STRING_AGG` 函数
- [ ] 使用了 `::` 类型转换语法
- [ ] 使用了 `BYTEA` 类型
- [ ] 使用了 `JSONB` 类型
- [ ] 使用了 `EXTRACT(EPOCH FROM d)` 获取Unix时间戳
- [ ] 使用了 `d + INTERVAL '1 day'` 格式
- [ ] DELETE 使用了 `USING` 关键字

## 示例

### 示例1：检测MySQL SQL

```sql
SELECT id, name, IF(score > 60, 'pass', 'fail') AS result 
FROM users 
ORDER BY id LIMIT 10;
```

**检测结果**：
- IF() 条件函数 → MySQL (+1)
- LIMIT → MySQL/金仓 (+0)
- **结论**：MySQL SQL（权重 1）

### 示例2：检测达梦SQL

```sql
SELECT id, NVL(name, 'anonymous') AS display_name
FROM users
WHERE ROWNUM <= 50;
```

**检测结果**：
- NVL() → 达梦 (+1)
- ROWNUM → 达梦 (+1)
- **结论**：达梦 SQL（权重 2）

### 示例3：检测金仓SQL

```sql
SELECT id, name::VARCHAR(100), STRING_AGG(tag, ',')
FROM users
GROUP BY id;
```

**检测结果**：
- :: 类型转换 → 金仓 (+1)
- STRING_AGG → 金仓 (+1)
- **结论**：金仓 SQL（权重 2）

## 注意事项

1. **混合语法**：有时SQL可能包含多个数据库的特征，通常是因为之前做过转换，取最新转换的目标数据库
2. **标准SQL**：如果SQL完全使用ANSI标准语法，无法判断数据库类型，此时需进一步询问用户
3. **兼容语法**：有些语法在多个数据库中都支持（如LIMIT、CASE WHEN等），不作为区分特征
4. **版本差异**：不同数据库版本可能新增对其他数据库语法的支持（如达梦8支持LIMIT）