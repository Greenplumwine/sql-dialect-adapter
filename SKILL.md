---
name: sql-dialect-adapter
description: "MySQL、达梦、金仓数据库SQL语法转换与适配。支持6种转换方向：MySQL↔达梦、MySQL↔金仓、达梦↔金仓。触发词：转SQL、SQL转换、方言转换、MySQL转达梦、达梦转MySQL、MySQL转金仓、金仓转MySQL、达梦转金仓、金仓转达梦、适配SQL、SQL迁移。"
---

# SQL 方言适配技能

## 转换方向矩阵

| 源 \ 目标 | MySQL | 达梦 | 金仓 |
|-----------|-------|------|------|
| **MySQL** | — | [mysql-to-dm](references/mysql-to-dm.md) | [mysql-to-kingbase](references/mysql-to-kingbase.md) |
| **达梦** | [dm-to-mysql](references/dm-to-mysql.md) | — | [dm-to-kingbase](references/dm-to-kingbase.md) |
| **金仓** | [kingbase-to-mysql](references/kingbase-to-mysql.md) | [kingbase-to-dm](references/kingbase-to-dm.md) | — |

**通用语法优先原则**：转换后的SQL应尽可能使用ANSI标准语法，仅在目标数据库不支持标准语法时才使用目标数据库特定语法。

优先级：`标准SQL → 目标数据库通用语法 → 目标数据库特定语法`

---

## 决策入口

根据用户输入，按以下决策树进入对应分支：

```
用户输入
  ├─ 明确指定了源数据库和目标数据库
  │   └─ → 直接进入【Step 1】
  ├─ 只提供了SQL，未说明数据库类型
  │   └─ → 执行【数据库语法检测】，然后【检查点1】
  └─ 只说"优化SQL"或"标准化SQL"
      └─ → 【检查点1】询问意图
```

### 检查点1：方向确认

| 用户状态 | 你的动作 |
|---------|---------|
| 已明确源→目标 | 直接开始转换 |
| 只给了SQL | 检测语法 → 报告结果 → 询问确认 |
| 意图模糊 | 见下方【意图模糊处理】 |

#### 意图模糊处理

当用户说"优化SQL"等未明确意图的指令时，先尝试检测数据库类型，然后提供选项引导用户：

**若检测到数据库类型**：
> 检测到这段 SQL 是 **{数据库类型}** 语法。请确认您的需求：
> 1. **方言转换**：转为其他数据库（请提供目标数据库）
> 2. **SQL 优化**：优化查询性能和写法
> 3. **标准化**：转为通用 ANSI SQL

**若未检测到数据库类型**：
> 无法确定这段 SQL 的数据库类型。请确认您的需求：
> 1. **方言转换**：请提供源数据库和目标数据库
> 2. **SQL 优化**：优化查询性能和写法
> 3. **标准化**：转为通用 ANSI SQL

### 检查点2：高风险确认

以下情况需暂停并提示用户：

| 风险类型 | 示例 | 提示语 |
|----------|------|--------|
| 数据类型精度变化 | `DECIMAL(19,4)` → `NUMERIC` | ⚠️ 数据类型可能丢失精度，请确认是否继续 |
| 函数行为差异 | `GROUP_CONCAT` → `WM_CONCAT`（排序行为不同） | ⚠️ 目标数据库的等效函数行为可能有差异，建议转换后测试验证 |
| 分页性能差异 | `LIMIT OFFSET` → `ROWNUM` | ⚠️ 分页语法在目标数据库中的执行计划可能不同，建议关注性能 |
| 保留字冲突 | 表名/列名与目标数据库保留字冲突 | ⚠️ 以下标识符与目标数据库保留字冲突，建议添加转义符：[列表] |

---

## 核心转换引擎

### Step 1：解析输入

**输入**：用户SQL + （可选）源数据库 + （可选）目标数据库

**处理**：
1. 若源/目标未明确 → 触发检查点1
2. 若已明确 → 加载对应方向的参考文档

**方向→文档映射**：

| 源→目标 | 参考文档 |
|---------|---------|
| MySQL→达梦 | [references/mysql-to-dm.md](references/mysql-to-dm.md) |
| MySQL→金仓 | [references/mysql-to-kingbase.md](references/mysql-to-kingbase.md) |
| 达梦→MySQL | [references/dm-to-mysql.md](references/dm-to-mysql.md) |
| 达梦→金仓 | [references/dm-to-kingbase.md](references/dm-to-kingbase.md) |
| 金仓→MySQL | [references/kingbase-to-mysql.md](references/kingbase-to-mysql.md) |
| 金仓→达梦 | [references/kingbase-to-dm.md](references/kingbase-to-dm.md) |

### Step 2：语法检测（条件执行）

**触发条件**：用户未提供源数据库类型

**操作**：
1. 使用 `scripts/detect_database.py` 分析SQL特征
2. 或按 [references/database-detection.md](references/database-detection.md) 手动检测
3. 将检测结果告知用户，等待确认

**检测逻辑**：
- 扫描SQL中的特征关键词（`AUTO_INCREMENT`、`IDENTITY`、`VARCHAR2`、`GROUP_CONCAT`、`LISTAGG`、`STRING_AGG`、`SYSDATE`、`::` 等）
- 加权评分，确定最可能的数据库类型
- 权重>1：直接报告；权重≤1：列出候选，请用户选择

### Step 3：模式匹配转换

**输入**：源SQL + 确认的转换方向

**按以下5种转换模式顺序执行**：

```
SQL输入
  ├─【模式A】数据类型标准化
  │   └─ 特有类型 → 通用/目标兼容类型
  ├─【模式B】函数方言替换
  │   └─ 特有函数 → 标准/目标可用函数
  ├─【模式C】语法结构重组
  │   └─ DDL/DML 语法差异调整
  ├─【模式D】分页查询适配
  │   └─ LIMIT/ROWNUM/ROW_NUMBER 转换
  └─【模式E】事务控制调整
      └─ 事务语法适配
```

**模式A — 数据类型标准化**：
- MySQL特有：`TINYINT`→`SMALLINT`、`MEDIUMINT`→`INT`、`TEXT`→`VARCHAR(4000)`
- 达梦特有：`VARCHAR2`→目标对应、`CLOB`→`VARCHAR(4000)`
- 金仓特有：`SERIAL`→目标对应、`JSONB`→目标对应

**模式B — 函数方言替换**：
- 条件函数：`IF()`→`CASE WHEN`、`IFNULL`→`COALESCE`
- 字符串聚合：`GROUP_CONCAT`→`LISTAGG`/`STRING_AGG`/`WM_CONCAT`
- 日期函数：`DATE_FORMAT`→`TO_CHAR`、`NOW()`→`CURRENT_TIMESTAMP`/`SYSDATE`
- 字符串操作：`CONCAT`→`||`、`LOCATE`→`POSITION`/`INSTR`

**模式C — 语法结构重组**：
- DDL：`AUTO_INCREMENT`→`IDENTITY`/`SERIAL`、引擎/字符集声明移除
- DML：批量插入语法、多表UPDATE/DELETE语法
- 标识符：反引号→双引号、保留字检查

**模式D — 分页查询适配**：
- MySQL：`LIMIT n OFFSET m`
- 达梦：`ROW_NUMBER() OVER` 或 `FETCH FIRST`（达梦8）
- 金仓：`LIMIT n OFFSET m`（兼容MySQL）
- 通用方案：`ROW_NUMBER() OVER` 窗口函数

**模式E — 事务控制调整**：
- MySQL：`START TRANSACTION`
- 达梦：自动开启（无需显式声明）
- 金仓：`BEGIN`

### Step 4：输出与验证

**输出格式**：

```markdown
## 转换结果（{源数据库} → {目标数据库}）

### 转换后的SQL
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

**触发检查点2的情况**：转换完成后，如涉及高风险项，再次提醒用户。

---

## 通用语法速查

当用户要求"标准化"或"通用化"SQL时，参考 [references/universal-syntax.md](references/universal-syntax.md)。

**核心规则**：
1. 数据类型：用 `SMALLINT/INT/BIGINT/VARCHAR/TIMESTAMP/NUMERIC`
2. 空值处理：用 `COALESCE` 替代 `IFNULL`/`NVL`
3. 字符串连接：用 `||` 替代 `CONCAT`
4. 日期获取：用 `CURRENT_TIMESTAMP` 替代 `NOW()`/`SYSDATE`
5. 分页：用 `ROW_NUMBER() OVER` 窗口函数
6. 标识符：小写+下划线，不使用引号包裹

---

## 故障排除与Fallback

| 场景 | 触发条件 | 处理动作 |
|------|----------|---------|
| 检测失败 | `detect_database.py` 返回"未知" | 1. 询问用户手动指定<br>2. 用户也无法确定 → 按MySQL假设处理，标注⚠️<br>3. 涉及DDL时**暂停等待确认** |
| 函数无映射 | 遇到未覆盖的函数 | 1. 保留原函数，标注⚠️<br>2. 提供官方文档搜索建议<br>3. 重复函数汇总列出 |
| 验证失败 | 转换后SQL执行报错 | 1. 分析错误类型（保留字/参数/语法）<br>2. 尝试自动修复<br>3. 无法修复则标注位置+手动建议 |
| 脚本不可用 | Python脚本执行失败 | 1. 检查环境（Python≥3.7）<br>2. 使用SKILL.md内置规则手动转换<br>3. 告知用户"自动脚本暂不可用" |

---

## 资源索引

| 路径 | 用途 |
|------|------|
| `references/mysql-to-*.md` / `dm-to-*.md` / `kingbase-to-*.md` | 6种转换方向的详细函数/类型映射表 |
| `references/database-detection.md` | 数据库语法检测指南与手动检测清单 |
| `references/universal-syntax.md` | 通用SQL语法参考与最佳实践 |
| `scripts/detect_database.py` | 自动数据库类型检测 |
| `scripts/sql_converter.py` | SQL语法批量转换工具 |

---

## 注意事项

1. **测试验证**：转换后的SQL必须在目标数据库中测试验证
2. **性能考虑**：通用转换可能影响性能，需评估执行计划
3. **版本差异**：不同数据库版本语法有差异，注意兼容性
4. **调试建议**：在目标数据库中逐步执行，对比执行计划
