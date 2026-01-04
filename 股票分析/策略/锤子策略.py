from sqlalchemy import create_engine
import pandas as pd


class HammerStrategy:
    """锤子线策略：前五天连续下跌 + 今日锤子线形态（SQLAlchemy版）"""

    def __init__(self, db_url=None):
        """
        db_url 示例：
        'mysql+pymysql://root:密码@127.0.0.1:3306/stock?charset=utf8mb4'
        """
        if db_url is None:
            self.db_url = "mysql+pymysql://root:Lhf134652@127.0.0.1:3306/stock?charset=utf8mb4"
        else:
            self.db_url = db_url

        self.name = "锤子线策略"
        self.description = "筛选前五天连续下跌且今日出现锤子线形态的股票"

    def execute(self):
        """执行策略分析"""
        try:
            # 创建 SQLAlchemy engine
            engine = create_engine(self.db_url)
            print("✅ 数据库连接成功（SQLAlchemy）")

            # =========================
            # 1. 获取最近 6 个交易日
            # =========================
            dates = pd.read_sql(
                "SELECT DISTINCT trade_date FROM daily_kline ORDER BY trade_date DESC LIMIT 6",
                engine
            )["trade_date"].tolist()

            today = dates[0]
            prev_5_days = dates[1:]  # 不含今天

            print("今日：", today)
            print("前五交易日：", prev_5_days)

            # =========================
            # 2. 前五天连续下跌
            # =========================
            down_5_df = pd.read_sql(
                f"""
                SELECT ts_code
                FROM daily_kline
                WHERE trade_date IN ({','.join("'" + d + "'" for d in prev_5_days)})
                  AND close < pre_close
                GROUP BY ts_code
                HAVING COUNT(*) = 5
                """,
                engine
            )
            down_5_codes = set(down_5_df["ts_code"])
            print(f"\n前五天连续下跌股票数：{len(down_5_codes)}")

            # =========================
            # 3. 今日 K 线数据
            # =========================
            today_df = pd.read_sql(
                f"""
                SELECT ts_code, open, high, low, close
                FROM daily_kline
                WHERE trade_date = '{today}'
                """,
                engine
            )

            # 计算锤子线特征
            today_df["body"] = (today_df["close"] - today_df["open"]).abs()
            today_df["lower_shadow"] = today_df[["open", "close"]].min(axis=1) - today_df["low"]
            today_df["upper_shadow"] = today_df["high"] - today_df[["open", "close"]].max(axis=1)

            # 锤子线判定（宽松版）
            hammer_df = today_df[
                (today_df["lower_shadow"] >= 2 * today_df["body"]) &
                (today_df["upper_shadow"] <= today_df["body"])
                ]
            hammer_codes = set(hammer_df["ts_code"])
            print(f"今日锤子线股票数：{len(hammer_codes)}")

            # =========================
            # 4. 同时满足两个条件
            # =========================
            target_codes = down_5_codes & hammer_codes
            print(f"\n🔥 前五天跌 + 今日锤子线：{len(target_codes)} 只")

            if not target_codes:
                print("暂无符合条件的股票")
                return []

            # =========================
            # 5. 查询股票名称 + 今日 K 线
            # =========================
            result = pd.read_sql(
                f"""
                SELECT d.ts_code, b.name AS 股票名称, d.open, d.high, d.low, d.close
                FROM daily_kline d
                JOIN stock_basic b ON d.ts_code = b.ts_code
                WHERE d.trade_date = '{today}'
                  AND d.ts_code IN ({','.join("'" + c + "'" for c in target_codes)})
                ORDER BY b.name
                """,
                engine
            )

            print("\n====== 结果股票 ======")
            print(result)
            return result.to_dict('records')

        except Exception as e:
            print(f"❌ 策略执行过程中出错: {e}")
            return []


# 保留独立运行功能
if __name__ == "__main__":
    strategy = HammerStrategy()
    strategy.execute()
