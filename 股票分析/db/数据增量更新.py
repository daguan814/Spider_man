import sqlite3
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "stock.db"

ts.set_token("0849ef1ef12463b055e298928b6a8286b2d478c365405d27ef50b629")
pro = ts.pro_api()

conn = sqlite3.connect(DB_PATH)

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

    df.to_sql(
        "daily_kline",
        conn,
        if_exists="append",
        index=False
    )

    print(f"  新增 {len(df)} 条")

conn.close()
print("✅ 日线数据高速增量完成")
