"""
Created on 2025/12/31
Author: Shuijing
Description:  缺少多少天的，就会更新多少天的。几天不更新，运行一次，一次更新所有的数据
"""

import pymysql
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# MySQL数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Lhf134652',
    'database': 'stock',
    'charset': 'utf8mb4'
}

ts.set_token("0849ef1ef12463b055e298928b6a8286b2d478c365405d27ef50b629")
pro = ts.pro_api()

try:
    # 连接MySQL数据库
    conn = pymysql.connect(**DB_CONFIG)
    print("✅ MySQL数据库连接成功")

    # ======================
    # 1. 查数据库最新交易日
    # ======================
    last_date_df = pd.read_sql(
        "SELECT MAX(trade_date) AS last_date FROM daily_kline",
        conn
    )

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

        # 使用pandas的to_sql方法插入数据到MySQL
        df.to_sql(
            "daily_kline",
            conn,
            if_exists="append",
            index=False
        )

        print(f"  新增 {len(df)} 条")

    print("✅ 日线数据高速增量完成")

except pymysql.Error as e:
    print(f"❌ MySQL数据库连接失败: {e}")
    print("请检查：")
    print("1. MySQL服务是否启动")
    print("2. 数据库连接信息是否正确")
    print("3. 是否安装了pymysql库 (pip install pymysql)")

except Exception as e:
    print(f"❌ 发生未知错误: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("✅ 数据库连接已关闭")