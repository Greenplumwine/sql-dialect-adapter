#!/usr/bin/env python3
"""
SQL语法转换脚本
支持MySQL、达梦、金仓三种数据库之间的SQL语法转换
"""

import sys
import os
import re


def convert_group_concat_to_listagg(sql):
    """将 GROUP_CONCAT 转换为达梦 LISTAGG，正确处理无 ORDER BY 的情况"""
    pattern = r'GROUP_CONCAT\s*\(\s*(.+?)\s*(?:ORDER\s+BY\s+(.+?))?\s*(?:SEPARATOR\s+\'(.+?)\')?\s*\)'

    def replacer(match):
        expr = match.group(1).strip()
        order_by = match.group(2)
        separator = match.group(3) or ','

        if order_by:
            return f"LISTAGG({expr}, '{separator}') WITHIN GROUP (ORDER BY {order_by.strip()})"
        else:
            return f"LISTAGG({expr}, '{separator}')"

    return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)


def convert_group_concat_to_string_agg(sql):
    """将 GROUP_CONCAT 转换为金仓 STRING_AGG，正确处理无 ORDER BY 的情况"""
    pattern = r'GROUP_CONCAT\s*\(\s*(.+?)\s*(?:ORDER\s+BY\s+(.+?))?\s*(?:SEPARATOR\s+\'(.+?)\')?\s*\)'

    def replacer(match):
        expr = match.group(1).strip()
        order_by = match.group(2)
        separator = match.group(3) or ','

        if order_by:
            return f"STRING_AGG({expr}, '{separator}' ORDER BY {order_by.strip()})"
        else:
            return f"STRING_AGG({expr}, '{separator}')"

    return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)


def convert_string_agg_to_group_concat(sql):
    """将金仓 STRING_AGG 转换为 MySQL GROUP_CONCAT"""
    pattern = r'STRING_AGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*(?:ORDER\s+BY\s+(.+?))?\s*\)'

    def replacer(match):
        expr = match.group(1).strip()
        separator = match.group(2).strip()
        order_by = match.group(3)

        if order_by:
            return f"GROUP_CONCAT({expr} ORDER BY {order_by.strip()} SEPARATOR '{separator}')"
        else:
            return f"GROUP_CONCAT({expr} SEPARATOR '{separator}')"

    return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)


def convert_listagg_to_group_concat(sql):
    """将达梦 LISTAGG 转换为 MySQL GROUP_CONCAT"""
    pattern = r'LISTAGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*\)\s*(?:WITHIN\s+GROUP\s*\(\s*ORDER\s+BY\s+(.+?)\s*\))?'

    def replacer(match):
        expr = match.group(1).strip()
        separator = match.group(2).strip()
        order_by = match.group(3)

        if order_by:
            return f"GROUP_CONCAT({expr} ORDER BY {order_by.strip()} SEPARATOR '{separator}')"
        else:
            return f"GROUP_CONCAT({expr} SEPARATOR '{separator}')"

    return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)


def convert_listagg_to_string_agg(sql):
    """将达梦 LISTAGG 转换为金仓 STRING_AGG"""
    pattern = r'LISTAGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*\)\s*(?:WITHIN\s+GROUP\s*\(\s*ORDER\s+BY\s+(.+?)\s*\))?'

    def replacer(match):
        expr = match.group(1).strip()
        separator = match.group(2).strip()
        order_by = match.group(3)

        if order_by:
            return f"STRING_AGG({expr}, '{separator}' ORDER BY {order_by.strip()})"
        else:
            return f"STRING_AGG({expr}, '{separator}')"

    return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)


def convert_limit_offset(sql, source_db, target_db):
    """
    将 LIMIT OFFSET 转换为目标数据库的分页语法。
    生成可直接使用的 ROW_NUMBER() 方案（达梦）或保留 LIMIT（金仓）。
    """
    s = source_db.lower()
    t = target_db.lower()

    # 只有 MySQL/Kingbase -> DM 需要转换；Kingbase 兼容 LIMIT
    if not (s in ['mysql', 'kingbase'] and t == 'dm'):
        return sql

    def _build_row_number_pagination(sql_text, limit, offset):
        """构建 ROW_NUMBER() 分页查询"""
        start = offset + 1
        end = offset + limit
        before_limit = sql_text.strip()

        # 查找末尾的 ORDER BY（在 LIMIT 之前）
        order_match = re.search(r'\bORDER\s+BY\s+(.+?)$', before_limit, re.IGNORECASE | re.DOTALL)
        if order_match:
            order_by = order_match.group(1).strip()
            inner = before_limit[:order_match.start()].strip()
        else:
            order_by = '1'
            inner = before_limit

        return (f"SELECT * FROM (\n"
                f"    SELECT ROW_NUMBER() OVER (ORDER BY {order_by}) AS rn, t.*\n"
                f"    FROM ({inner}) t\n"
                f") WHERE rn BETWEEN {start} AND {end}")

    # 匹配 LIMIT n OFFSET m
    match1 = re.search(r'\bLIMIT\s+(\d+)\s+OFFSET\s+(\d+)\b', sql, re.IGNORECASE)
    if match1:
        limit = int(match1.group(1))
        offset = int(match1.group(2))
        return _build_row_number_pagination(sql[:match1.start()], limit, offset)

    # 匹配 LIMIT m, n
    match2 = re.search(r'\bLIMIT\s+(\d+)\s*,\s*(\d+)\b', sql, re.IGNORECASE)
    if match2:
        offset = int(match2.group(1))
        limit = int(match2.group(2))
        return _build_row_number_pagination(sql[:match2.start()], limit, offset)

    # 匹配 LIMIT n
    match3 = re.search(r'\bLIMIT\s+(\d+)\b', sql, re.IGNORECASE)
    if match3:
        limit = int(match3.group(1))
        before_limit = sql[:match3.start()].strip()
        return f"{before_limit}\nFETCH FIRST {limit} ROWS ONLY"

    return sql


# 转换规则映射（纯文本替换，不含 GROUP_CONCAT / LIMIT / STRING_AGG / LISTAGG）
CONVERSION_RULES = {
    # MySQL -> 达梦
    'mysql_to_dm': {
        'AUTO_INCREMENT': 'IDENTITY(1,1)',
        r'VARCHAR\s*\(\s*(\d+)\s*\)': r'VARCHAR2(\1)',
        'TEXT': 'CLOB',
        'DATETIME': 'DATE',
        r'\bIF\s*\(\s*([^,]+)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)': r'CASE WHEN \1 THEN \2 ELSE \3 END',
        r'\bIFNULL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        r"DATE_FORMAT\s*\(\s*(.+?)\s*,\s*'%Y-%m-%d\s*%H:%i:%s'\s*\)": r"TO_CHAR(\1, 'YYYY-MM-DD HH24:MI:SS')",
        r"DATE_FORMAT\s*\(\s*(.+?)\s*,\s*'%Y-%m-%d'\s*\)": r"TO_CHAR(\1, 'YYYY-MM-DD')",
        r'DATE_SUB\s*\(\s*(.+?)\s*,\s*INTERVAL\s+(\d+)\s+DAY\s*\)': r'\1 - \2',
        r'DATE_ADD\s*\(\s*(.+?)\s*,\s*INTERVAL\s+(\d+)\s+DAY\s*\)': r'\1 + \2',
    },
    # 达梦 -> MySQL
    'dm_to_mysql': {
        r'IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)': 'AUTO_INCREMENT',
        r'VARCHAR2\s*\(\s*(\d+)\s*\)': r'VARCHAR(\1)',
        'CLOB': 'LONGTEXT',
        r'DATE\s+AS\s+TIMESTAMP': 'DATETIME',
        r'\bSYSDATE\b': 'NOW()',
        r'\bNVL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        r"TO_CHAR\s*\(\s*(.+?)\s*,\s*'YYYY-MM-DD\s+HH24:MI:SS'\s*\)": r"DATE_FORMAT(\1, '%Y-%m-%d %H:%i:%s')",
        r"TO_CHAR\s*\(\s*(.+?)\s*,\s*'YYYY-MM-DD'\s*\)": r"DATE_FORMAT(\1, '%Y-%m-%d')",
    },
    # MySQL -> 金仓
    'mysql_to_kingbase': {
        'AUTO_INCREMENT': 'SERIAL',
        'TINYINT': 'SMALLINT',
        'MEDIUMINT': 'INT',
        'DATETIME': 'TIMESTAMP',
        r'\bIF\s*\(\s*([^,]+)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)': r'CASE WHEN \1 THEN \2 ELSE \3 END',
        r'\bIFNULL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        r"DATE_FORMAT\s*\(\s*(.+?)\s*,\s*'%Y-%m-%d\s*%H:%i:%s'\s*\)": r"TO_CHAR(\1, 'YYYY-MM-DD HH24:MI:SS')",
        r"DATE_FORMAT\s*\(\s*(.+?)\s*,\s*'%Y-%m-%d'\s*\)": r"TO_CHAR(\1, 'YYYY-MM-DD')",
        'BLOB': 'BYTEA',
        'JSON': 'JSONB',
    },
    # 金仓 -> MySQL
    'kingbase_to_mysql': {
        r'\bSERIAL\b(?!\s*\()': 'AUTO_INCREMENT',
        'BIGSERIAL': 'BIGINT AUTO_INCREMENT',
        r"TO_CHAR\s*\(\s*(.+?)\s*,\s*'YYYY-MM-DD\s+HH24:MI:SS'\s*\)": r"DATE_FORMAT(\1, '%Y-%m-%d %H:%i:%s')",
        'BYTEA': 'LONGBLOB',
        'JSONB': 'JSON',
        r'::\s*(\w+)': r'CAST(AS \1)',  # 简化处理
        r'\bBEGIN\b(?!\s*(TRANSACTION|WORK))': 'START TRANSACTION',
    },
    # 达梦 -> 金仓
    'dm_to_kingbase': {
        r'IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)': 'SERIAL',
        r'VARCHAR2\s*\(\s*(\d+)\s*\)': r'VARCHAR(\1)',
        'CLOB': 'TEXT',
        r'\bDATE\b(?=\s+DEFAULT|\s+\,)': 'TIMESTAMP',
        r'\bSYSDATE\b': 'CURRENT_TIMESTAMP',
        r'\bNVL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        r"TO_DATE\s*\(\s*(.+?)\s*,\s*'YYYY-MM-DD'\s*\)": r"TO_DATE(\1, 'YYYY-MM-DD')",
    },
    # 金仓 -> 达梦
    'kingbase_to_dm': {
        r'\bSERIAL\b(?!\s*\()': 'IDENTITY(1,1)',
        'BIGSERIAL': 'BIGINT IDENTITY(1,1)',
        'TIMESTAMP': 'DATE',
        'CURRENT_TIMESTAMP': 'SYSDATE',
        'BYTEA': 'BLOB',
        'JSONB': 'CLOB',
        r'::\s*(\w+)': r'CAST(AS \1)',  # 简化处理
    },
}


def convert_sql(sql_text, source_db, target_db):
    """
    转换SQL语法
    """
    if source_db == target_db:
        return sql_text, ["源数据库和目标数据库相同，无需转换"]

    conversion_key = f"{source_db.lower()}_to_{target_db.lower()}"
    if conversion_key not in CONVERSION_RULES:
        return sql_text, [f"不支持从 {source_db} 转换到 {target_db}"]

    converted = sql_text
    applied_rules = []

    # 1. 特殊处理：GROUP_CONCAT / STRING_AGG / LISTAGG 转换
    if conversion_key == 'mysql_to_dm':
        converted = convert_group_concat_to_listagg(converted)
        applied_rules.append("特殊处理: GROUP_CONCAT -> LISTAGG")
    elif conversion_key == 'mysql_to_kingbase':
        converted = convert_group_concat_to_string_agg(converted)
        applied_rules.append("特殊处理: GROUP_CONCAT -> STRING_AGG")
    elif conversion_key == 'kingbase_to_mysql':
        converted = convert_string_agg_to_group_concat(converted)
        applied_rules.append("特殊处理: STRING_AGG -> GROUP_CONCAT")
    elif conversion_key == 'dm_to_mysql':
        converted = convert_listagg_to_group_concat(converted)
        applied_rules.append("特殊处理: LISTAGG -> GROUP_CONCAT")
    elif conversion_key == 'dm_to_kingbase':
        converted = convert_listagg_to_string_agg(converted)
        applied_rules.append("特殊处理: LISTAGG -> STRING_AGG")
    elif conversion_key == 'kingbase_to_dm':
        converted = convert_string_agg_to_group_concat(converted)
        applied_rules.append("特殊处理: STRING_AGG -> LISTAGG (via GROUP_CONCAT)")

    # 2. 特殊处理：LIMIT OFFSET 分页转换
    if conversion_key in ['mysql_to_dm', 'kingbase_to_dm']:
        original = converted
        converted = convert_limit_offset(converted, source_db, target_db)
        if converted != original:
            applied_rules.append("特殊处理: LIMIT OFFSET -> ROW_NUMBER() 分页")

    # 3. 纯文本正则替换
    rules = CONVERSION_RULES[conversion_key]
    for pattern, replacement in rules.items():
        try:
            new_text, count = re.subn(pattern, replacement, converted, flags=re.IGNORECASE)
            if count > 0:
                converted = new_text
                applied_rules.append(f"应用规则: {pattern} -> {replacement} (替换 {count} 处)")
        except Exception as e:
            applied_rules.append(f"规则应用失败: {pattern} -> {replacement} (错误: {e})")

    return converted, applied_rules


def main():
    if len(sys.argv) < 4:
        print("用法: python sql_converter.py <输入文件> <输出文件> <源数据库> <目标数据库>")
        print("      python sql_converter.py --string \"SQL语句\" <源数据库> <目标数据库>")
        print("")
        print("支持的数据库类型: mysql, dm, kingbase")
        print("示例:")
        print("  python sql_converter.py input.sql output.sql mysql dm")
        print("  python sql_converter.py --string \"SELECT * FROM users\" mysql kingbase")
        sys.exit(1)

    if sys.argv[1] == '--string':
        sql_text = sys.argv[2]
        source_db = sys.argv[3].lower()
        target_db = sys.argv[4].lower()
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        source_db = sys.argv[3].lower()
        target_db = sys.argv[4].lower()

        if not os.path.exists(input_file):
            print(f"错误: 输入文件 '{input_file}' 不存在")
            sys.exit(1)

        with open(input_file, 'r', encoding='utf-8') as f:
            sql_text = f.read()

    # 数据库类型映射
    db_map = {
        'mysql': 'MySQL',
        'dm': '达梦',
        'kingbase': '金仓'
    }

    if source_db not in db_map or target_db not in db_map:
        print(f"错误: 不支持的数据库类型。支持: {', '.join(db_map.keys())}")
        sys.exit(1)

    source_db_name = db_map[source_db]
    target_db_name = db_map[target_db]

    print(f"转换: {source_db_name} -> {target_db_name}")
    print(f"源SQL长度: {len(sql_text)} 字符")

    converted_sql, applied_rules = convert_sql(sql_text, source_db, target_db)

    if sys.argv[1] == '--string':
        print("\n转换后的SQL:")
        print(converted_sql)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_sql)
        print(f"已写入输出文件: {output_file}")
        print(f"输出SQL长度: {len(converted_sql)} 字符")

    if applied_rules:
        print(f"\n应用的转换规则 ({len(applied_rules)} 条):")
        for rule in applied_rules:
            print(f"  - {rule}")
    else:
        print("\n未应用任何转换规则")

    print("\n注意:")
    print("1. 自动转换可能不完整，请人工验证转换结果")
    print("2. 复杂SQL可能需要手动调整")
    print("3. 建议在目标数据库中测试转换后的SQL")


if __name__ == '__main__':
    main()
