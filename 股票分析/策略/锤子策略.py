import pymysql
import pandas as pd

class HammerStrategy:
    """锤子线策略：前五天连续下跌 + 今日锤子线形态"""
    
    def __init__(self, db_config=None):
        # MySQL数据库连接配置
        if db_config is None:
            self.db_config = {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': 'Lhf134652',
                'database': 'stock',
                'charset': 'utf8mb4'
            }
        else:
            self.db_config = db_config
            
        self.name = "锤子线策略"
        self.description = "筛选前五天连续下跌且今日出现锤子线形态的股票"
    
    def execute(self):
        """执行策略分析"""
        try:
            # 连接MySQL数据库
            conn = pymysql.connect(**self.db_config)
            print("✅ MySQL数据库连接成功")
            
            # =========================
            # 1. 取最近 6 个交易日
            # =========================
            dates = pd.read_sql(
                """
                SELECT DISTINCT trade_date
                FROM daily_kline
                ORDER BY trade_date DESC
                LIMIT 6;
                """,
                conn
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
                conn
            )

            down_5_codes = set(down_5_df["ts_code"])
            print(f"\n前五天连续下跌股票数：{len(down_5_codes)}")

            # =========================
            # 3. 今天的 K 线数据
            # =========================
            today_df = pd.read_sql(
                f"""
                SELECT
                    ts_code,
                    open,
                    high,
                    low,
                    close
                FROM daily_kline
                WHERE trade_date = '{today}'
                """,
                conn
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

            result = pd.read_sql(
                f"""
                SELECT
                    d.ts_code,
                    b.name AS 股票名称,
                    d.open,
                    d.high,
                    d.low,
                    d.close
                FROM daily_kline d
                JOIN stock_basic b
                    ON d.ts_code = b.ts_code
                WHERE d.trade_date = '{today}'
                  AND d.ts_code IN ({','.join("'" + c + "'" for c in target_codes)})
                ORDER BY b.name;
                """,
                conn
            )

            print("\n====== 结果股票 ======")
            print(result)
            
            return result.to_dict('records')
            
        except pymysql.Error as e:
            print(f"❌ MySQL数据库连接失败: {e}")
            print("请检查：")
            print("1. MySQL服务是否启动")
            print("2. 数据库连接信息是否正确")
            print("3. 是否安装了pymysql库 (pip install pymysql)")
            return []
        except Exception as e:
            print(f"❌ 策略执行过程中出错: {e}")
            return []
        finally:
            if 'conn' in locals() and conn:
                conn.close()
                print("✅ 数据库连接已关闭")

# 保留原有的独立运行功能
if __name__ == "__main__":
    strategy = HammerStrategy()
    strategy.execute()