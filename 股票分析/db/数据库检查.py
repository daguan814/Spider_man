import pandas as pd
from sqlalchemy import create_engine

# ======================
# MySQL数据库连接配置
# ======================
DB_CONFIG = {
    'user': 'root',
    'password': 'Lhf134652',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'stock',
    'charset': 'utf8mb4'
}

# SQLAlchemy连接字符串
DB_URI = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
)

try:
    # 创建SQLAlchemy引擎
    engine = create_engine(DB_URI)
    print("✅ MySQL数据库连接成功 (SQLAlchemy)")

    print("========== 1. 数据库中的表 ==========")
    tables = pd.read_sql("SHOW TABLES;", engine)
    print(tables)

    print("\n========== 2. daily_kline 表结构 ==========")
    columns = pd.read_sql("DESCRIBE daily_kline;", engine)
    print(columns)

    print("\n========== 2b. stock_basic 表结构 ==========")
    stock_basic_columns = pd.read_sql("DESCRIBE stock_basic;", engine)
    print(stock_basic_columns)

    print("\n========== 3. 日线总记录数 ==========")
    total_rows = pd.read_sql("SELECT COUNT(*) AS 记录数 FROM daily_kline;", engine)
    print(total_rows)

    print("\n========== 3b. stock_basic 总记录数 ==========")
    stock_basic_rows = pd.read_sql("SELECT COUNT(*) AS 记录数 FROM stock_basic;", engine)
    print(stock_basic_rows)

    print("\n========== 4. 股票数量 ==========")
    stock_cnt = pd.read_sql("SELECT COUNT(DISTINCT ts_code) AS 股票数 FROM daily_kline;", engine)
    print(stock_cnt)

    print("\n========== 5. 覆盖的交易日 ==========")
    date_range = pd.read_sql(
        """
        SELECT 
            MIN(trade_date) AS 最早日期,
            MAX(trade_date) AS 最晚日期,
            COUNT(DISTINCT trade_date) AS 交易日数量
        FROM daily_kline;
        """,
        engine
    )
    print(date_range)

    print("\n========== 6. 每只股票的数据天数分布 ==========")
    days_per_stock = pd.read_sql(
        """
        SELECT 
            ts_code,
            COUNT(*) AS 天数
        FROM daily_kline
        GROUP BY ts_code
        ORDER BY 天数;
        """,
        engine
    )

    print("最少数据的股票：")
    print(days_per_stock.head(10))

    print("--- 天数分布统计 ---")
    print(days_per_stock["天数"].value_counts().sort_index())

    print("\n========== 7. JOIN 股票名称抽样 ==========")
    # 强制 COLLATE 避免字符集冲突
    sample = pd.read_sql(
        """
        SELECT 
            d.ts_code,
            b.name AS 股票名称,
            d.trade_date,
            d.close
        FROM daily_kline d
        LEFT JOIN stock_basic b
            ON d.ts_code COLLATE utf8mb4_unicode_ci = b.ts_code COLLATE utf8mb4_unicode_ci
        ORDER BY d.trade_date DESC
        LIMIT 10;
        """,
        engine
    )
    print(sample)

    print("\n========== 8. 数据库基本信息 ==========")
    db_info = pd.read_sql("SELECT VERSION() AS mysql_version, DATABASE() AS current_database;", engine)
    print(db_info)

except Exception as e:
    print(f"❌ 发生错误: {e}")
