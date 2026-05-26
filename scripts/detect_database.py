#!/usr/bin/env python3
"""
数据库语法检测脚本
分析SQL代码，推断其所属的数据库类型（MySQL / 达梦 / 金仓）
"""

import sys
import re

def detect_database(sql):
    """
    检测SQL代码使用的数据库类型。
    返回 (database_type, confidence, features)
    """
    scores = {
        'MySQL': 0,
        '达梦': 0,
        '金仓': 0
    }
    features = {
        'MySQL': [],
        '达梦': [],
        '金仓': []
    }

    # MySQL 特征检测
    mysql_patterns = [
        (r'AUTO_INCREMENT', 'AUTO_INCREMENT'),
        (r'ENGINE\s*=\s*InnoDB', 'ENGINE=InnoDB'),
        (r"CHARSET\s*=\s*utf8(mb4)?", 'CHARSET=utf8mb4'),
        (r'\bIF\s*\([^,]+,', 'IF() 函数'),
        (r'\bGROUP_CONCAT\s*\(', 'GROUP_CONCAT()'),
        (r'\bIFNULL\s*\(', 'IFNULL()'),
        (r'\bLOCATE\s*\(', 'LOCATE()'),
        (r"DATE_FORMAT\s*\(.*'%[YymdHis]'", 'DATE_FORMAT()'),
        (r'\bENUM\s*\(', 'ENUM类型'),
        (r'\bMEDIUMINT\b', 'MEDIUMINT类型'),
        (r'\bYEAR\b', 'YEAR类型'),
        (r'`\w+`', '反引号标识符'),
    ]
    for pattern, name in mysql_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            scores['MySQL'] += 1
            features['MySQL'].append(name)

    # 达梦特征检测
    dm_patterns = [
        (r'\bIDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)', 'IDENTITY()'),
        (r'\bVARCHAR2\b', 'VARCHAR2类型'),
        (r'\bLISTAGG\s*\(', 'LISTAGG()'),
        (r'INSERT\s+ALL\b', 'INSERT ALL'),
        (r'WHEN\s+MATCHED\s+THEN\s+UPDATE', 'MERGE INTO'),
        (r'\bSYSDATE\b', 'SYSDATE'),
        (r'\bNVL\s*\(', 'NVL()'),
        (r'\bINSTR\s*\(', 'INSTR()'),
        (r'\bROWNUM\b', 'ROWNUM'),
        (r"TO_CHAR\s*\(.*'YYYY-MM-DD", 'TO_CHAR() 达梦格式'),
        (r'FROM\s+dual\b', 'FROM dual'),
    ]
    for pattern, name in dm_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            scores['达梦'] += 1
            features['达梦'].append(name)

    # 金仓特征检测
    kingbase_patterns = [
        (r'\bSERIAL\b(?!\s*\()', 'SERIAL类型'),
        (r'\bBIGSERIAL\b', 'BIGSERIAL类型'),
        (r'\bSTRING_AGG\s*\(', 'STRING_AGG()'),
        (r'\w+\s*::\s*\w+', ':: 类型转换'),
        (r'\bBYTEA\b', 'BYTEA类型'),
        (r'\bJSONB\b', 'JSONB类型'),
        (r"EXTRACT\s*\(\s*EPOCH\s+FROM", 'EXTRACT(EPOCH FROM)'),
        (r"INTERVAL\s+'(\d+)\s+(day|month|year)'", "INTERVAL 'n unit'"),
        (r'DELETE\s+FROM\s+\w+\s+USING\b', 'DELETE USING'),
        (r'\bBEGIN\b(?!\s*(TRANSACTION|WORK))', 'BEGIN 事务'),
        (r'\bRANDOM\s*\(\s*\)', 'RANDOM()'),
    ]
    for pattern, name in kingbase_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            scores['金仓'] += 1
            features['金仓'].append(name)

    # 确定数据库类型
    max_score = max(scores.values())
    candidates = [db for db, score in scores.items() if score == max_score]

    if max_score == 0:
        return '标准SQL', 0, features
    elif len(candidates) == 1:
        return candidates[0], max_score, features
    else:
        return f"不确定 ({', '.join(candidates)})", max_score, features


def main():
    if len(sys.argv) < 2:
        print("用法: python detect_database.py <sql字符串>")
        print("      python detect_database.py --file <sql文件路径>")
        sys.exit(1)

    if sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("错误: 请提供SQL文件路径")
            sys.exit(1)
        file_path = sys.argv[2]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
        except FileNotFoundError:
            print(f"错误: 文件 '{file_path}' 不存在")
            sys.exit(1)
        except Exception as e:
            print(f"错误: 读取文件失败 - {e}")
            sys.exit(1)
    else:
        sql = ' '.join(sys.argv[1:])

    db_type, confidence, features = detect_database(sql)

    print(f"检测结果: {db_type}")
    print(f"置信度: {confidence}")
    print(f"匹配到的特征:")
    for db_name in ['MySQL', '达梦', '金仓']:
        if features[db_name]:
            print(f"  {db_name}: {', '.join(features[db_name])}")

    if '不确定' in db_type:
        print("\n建议: 请手动指定源数据库类型")
    elif db_type == '标准SQL':
        print("\n注意: 代码使用标准SQL语法，可在三种数据库中使用")


if __name__ == '__main__':
    main()