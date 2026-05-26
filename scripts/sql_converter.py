#!/usr/bin/env python3
"""
SQL语法转换脚本
支持MySQL、达梦、金仓三种数据库之间的SQL语法转换
"""

import sys
import os
import re

# 转换规则映射
CONVERSION_RULES = {
    # MySQL -> 达梦
    'mysql_to_dm': {
        'AUTO_INCREMENT': 'IDENTITY(1,1)',
        'VARCHAR\s*\(\s*(\d+)\s*\)': r'VARCHAR2(\1)',
        'TEXT': 'CLOB',
        'DATETIME': 'DATE',
        'IF\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)': r'CASE WHEN \1 THEN \2 ELSE \3 END',
        'IFNULL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        'GROUP_CONCAT\s*\(\s*(.+?)\s*(?:ORDER\s+BY\s+(.+?))?\s*(?:SEPARATOR\s+\'(.+?)\')?\s*\)': 
            r'LISTAGG(\1, \'\3\') WITHIN GROUP (ORDER BY \2)',
        'DATE_FORMAT\s*\(\s*(.+?)\s*,\s*\'%Y-%m-%d\s*%H:%i:%s\'\s*\)': r'TO_CHAR(\1, \'YYYY-MM-DD HH24:MI:SS\')',
        r'LIMIT\s+(\d+)\s+OFFSET\s+(\d+)': r'-- 分页查询需手动转换\n-- 原始: LIMIT \1 OFFSET \2\n-- 达梦: 使用ROW_NUMBER()或LIMIT(达梦8支持)',
    },
    # 达梦 -> MySQL
    'dm_to_mysql': {
        'IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)': 'AUTO_INCREMENT',
        'VARCHAR2\s*\(\s*(\d+)\s*\)': r'VARCHAR(\1)',
        'CLOB': 'LONGTEXT',
        'DATE\s+AS\s+TIMESTAMP': 'DATETIME',
        'SYSDATE': 'NOW()',
        'NVL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        'LISTAGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*\)\s+WITHIN\s+GROUP\s*\(\s*ORDER\s+BY\s+(.+?)\s*\)':
            r'GROUP_CONCAT(\1 ORDER BY \3 SEPARATOR \'\2\')',
        'TO_CHAR\s*\(\s*(.+?)\s*,\s*\'YYYY-MM-DD\s+HH24:MI:SS\'\s*\)': r'DATE_FORMAT(\1, \'%Y-%m-%d %H:%i:%s\')',
    },
    # MySQL -> 金仓
    'mysql_to_kingbase': {
        'AUTO_INCREMENT': 'SERIAL',
        'TINYINT': 'SMALLINT',
        'MEDIUMINT': 'INT',
        'DATETIME': 'TIMESTAMP',
        'IF\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)': r'CASE WHEN \1 THEN \2 ELSE \3 END',
        'IFNULL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        'GROUP_CONCAT\s*\(\s*(.+?)\s*(?:ORDER\s+BY\s+(.+?))?\s*(?:SEPARATOR\s+\'(.+?)\')?\s*\)': 
            r'STRING_AGG(\1, \'\3\') ORDER BY \2',
        'DATE_FORMAT\s*\(\s*(.+?)\s*,\s*\'%Y-%m-%d\s*%H:%i:%s\'\s*\)': r'TO_CHAR(\1, \'YYYY-MM-DD HH24:MI:SS\')',
        'BLOB': 'BYTEA',
        'JSON': 'JSONB',
    },
    # 金仓 -> MySQL
    'kingbase_to_mysql': {
        'SERIAL': 'AUTO_INCREMENT',
        'BIGSERIAL': 'BIGINT AUTO_INCREMENT',
        'STRING_AGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*(?:ORDER\s+BY\s+(.+?))?\s*\)':
            r'GROUP_CONCAT(\1 ORDER BY \3 SEPARATOR \'\2\')',
        'TO_CHAR\s*\(\s*(.+?)\s*,\s*\'YYYY-MM-DD\s+HH24:MI:SS\'\s*\)': r'DATE_FORMAT(\1, \'%Y-%m-%d %H:%i:%s\')',
        'BYTEA': 'LONGBLOB',
        'JSONB': 'JSON',
        '::\s*(\w+)': r'CAST(AS \1)',  # 简化处理
        'BEGIN': 'START TRANSACTION',
    },
    # 达梦 -> 金仓
    'dm_to_kingbase': {
        'IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)': 'SERIAL',
        'VARCHAR2\s*\(\s*(\d+)\s*\)': r'VARCHAR(\1)',
        'CLOB': 'TEXT',
        'DATE': 'TIMESTAMP',
        'SYSDATE': 'CURRENT_TIMESTAMP',
        'NVL\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)': r'COALESCE(\1, \2)',
        'LISTAGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*\)\s+WITHIN\s+GROUP\s*\(\s*ORDER\s+BY\s+(.+?)\s*\)':
            r'STRING_AGG(\1, \'\2\') ORDER BY \3',
        'TO_DATE\s*\(\s*(.+?)\s*,\s*\'YYYY-MM-DD\'\s*\)': r'TO_DATE(\1, \'YYYY-MM-DD\')',  # 一致
    },
    # 金仓 -> 达梦
    'kingbase_to_dm': {
        'SERIAL': 'IDENTITY(1,1)',
        'BIGSERIAL': 'BIGINT IDENTITY(1,1)',
        'STRING_AGG\s*\(\s*(.+?)\s*,\s*\'\s*(.+?)\s*\'\s*(?:ORDER\s+BY\s+(.+?))?\s*\)':
            r'LISTAGG(\1, \'\2\') WITHIN GROUP (ORDER BY \3)',
        'TIMESTAMP': 'DATE',
        'CURRENT_TIMESTAMP': 'SYSDATE',
        'BYTEA': 'BLOB',
        'JSONB': 'CLOB',
        '::\s*(\w+)': r'CAST(AS \1)',  # 简化处理
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

    rules = CONVERSION_RULES[conversion_key]
    converted = sql_text
    applied_rules = []

    for pattern, replacement in rules.items():
        try:
            # 使用正则表达式进行替换
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

    converted_sql, applied_rules = convert_sql(sql_text, source_db_name, target_db_name)

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