"""
Created on 2025/12/31
Author: Shuijing
Description:  缺少多少天的，就会更新多少天的。几天不更新，运行一次，一次更新所有的数据
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# ======================
# MySQL数据库配置 (SQLAlchemy)
# ======================
DB_CONFIG = {
    'user': 'root',
    'password': 'Lhf134652',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'stock',
    'charset': 'utf8mb4'
}

DB_URI = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
)

# ======================
# Tushare 初始化
# ======================
ts.set_token("0849ef1ef12463b055e298928b6a8286b2d478c365405d27ef50b629")
pro = ts.pro_api()

try:
    # 创建SQLAlchemy引擎
    engine = create_engine(DB_URI)
    print("✅ MySQL数据库连接成功 (SQLAlchemy)")

    # ======================
    # 1. 查数据库最新交易日
    # ======================
    last_date_df = pd.read_sql("SELECT MAX(trade_date) AS last_date FROM daily_kline", engine)
    last_date = last_date_df.loc[0, "last_date"]

    if last_date is None:
        start_date = "19900101"
    else:
        dt = datetime.strptime(last_date, "%Y%m%d") + timedelta(days=1)
        start_date = dt.strftime("%Y%m%d")

    today = datetime.now().strftime("%Y%m%d")

    print("数据库最新日期：", last_date)
    print("开始更新日期：", start_date)
    print("结束日期：", today)

    # ======================
    # 2. 拉交易日列表
    # ======================
    trade_days = pro.trade_cal(
        exchange="",
        start_date=start_date,
        end_date=today,
        is_open=1
    )["cal_date"].tolist()

    print(f"需要更新 {len(trade_days)} 个交易日")

    # ======================
    # 3. 按【交易日】批量更新
    # ======================
    for trade_date in trade_days:
        print(f"更新 {trade_date} ...")

        df = pro.daily(trade_date=trade_date)

        if df.empty:
            continue

        df = df[
            [
                "ts_code", "trade_date",
                "open", "high", "low", "close",
                "pre_close", "change", "pct_chg",
                "vol", "amount"
            ]
        ]

        # 使用 SQLAlchemy engine 插入数据
        df.to_sql(
            "daily_kline",
            engine,
            if_exists="append",
            index=False
        )

        print(f"  新增 {len(df)} 条")

    print("✅ 日线数据高速增量完成")

except Exception as e:
    print(f"❌ 发生错误: {e}")

finally:
    # SQLAlchemy engine 不需要像 pymysql 一样手动关闭连接
    print("✅ 数据库操作完成")
