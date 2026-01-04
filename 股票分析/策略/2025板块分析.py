import pymysql
import pandas as pd


class IndustryAnnualPctStrategy:
    """
    统计 2025 年各板块涨跌幅（去极值后平均），用于中长期方向判断
    """

    def __init__(self, db_config=None, trim_pct=0.05):
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

        self.trim_pct = trim_pct  # 去极值比例（前后 5%）
        self.year = "2025"
        self.name = "2025板块分析"
        self.description = "统计2025年各板块涨跌幅（去极值后平均）"

    def execute(self) -> pd.DataFrame:
        print(f"\n🎯 执行策略: {self.year}年板块年度涨跌幅统计（去极值）")
        print("-" * 60)

        try:
            # 连接MySQL数据库
            conn = pymysql.connect(**self.db_config)
            print("✅ MySQL数据库连接成功")

            # === 1. 读取 2025 年日线 ===
            df = pd.read_sql(
                """
                SELECT ts_code, trade_date, close
                FROM daily_kline
                WHERE trade_date BETWEEN '20250101' AND '20251231'
                """,
                conn
            )

            if df.empty:
                print("❌ 没有 2025 年日线数据")
                return pd.DataFrame()

            # === 2. 股票基础信息 ===
            stock_info = pd.read_sql(
                "SELECT ts_code, name, industry FROM stock_basic",
                conn
            )

            # === 3. 计算个股年初 / 年末收盘价 ===
            first_close = (
                df.sort_values("trade_date")
                .groupby("ts_code")
                .first()
                .reset_index()
            )

            last_close = (
                df.sort_values("trade_date")
                .groupby("ts_code")
                .last()
                .reset_index()
            )

            merged = pd.merge(
                first_close[["ts_code", "close"]],
                last_close[["ts_code", "close"]],
                on="ts_code",
                suffixes=("_start", "_end")
            )

            # === 4. 个股全年涨跌幅 ===
            merged["pct_chg"] = (
                (merged["close_end"] - merged["close_start"])
                / merged["close_start"] * 100
            )

            # 合并板块
            merged = pd.merge(merged, stock_info, on="ts_code", how="left")
            merged = merged.dropna(subset=["industry"])

            # === 5. 板块统计（去极值） ===
            results = []

            for industry, g in merged.groupby("industry"):
                if len(g) < 5:
                    continue  # 样本太少直接忽略

                g_sorted = g.sort_values("pct_chg")
                trim_n = int(len(g_sorted) * self.trim_pct)

                if trim_n > 0:
                    g_trim = g_sorted.iloc[trim_n:-trim_n]
                else:
                    g_trim = g_sorted

                results.append({
                    "industry": industry,
                    "stock_count": len(g),
                    "used_count": len(g_trim),
                    "avg_pct_chg": g_trim["pct_chg"].mean(),
                    "median_pct_chg": g_trim["pct_chg"].median(),
                    "max_pct_chg": g_trim["pct_chg"].max(),
                    "min_pct_chg": g_trim["pct_chg"].min(),
                })

            result_df = pd.DataFrame(results)
            result_df = result_df.sort_values(
                by="avg_pct_chg", ascending=False
            ).reset_index(drop=True)

            # === 6. 美化输出 ===
            self.pretty_print(result_df)

            return result_df

        except pymysql.Error as e:
            print(f"❌ MySQL数据库连接失败: {e}")
            print("请检查：")
            print("1. MySQL服务是否启动")
            print("2. 数据库连接信息是否正确")
            print("3. 是否安装了pymysql库 (pip install pymysql)")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ 策略执行异常: {e}")
            return pd.DataFrame()
        finally:
            if 'conn' in locals() and conn:
                conn.close()
                print("✅ 数据库连接已关闭")

    @staticmethod
    def pretty_print(df: pd.DataFrame, top_n=50, bottom_n=20):
        """
        美化打印板块年度表现
        top_n / bottom_n: 控制显示多少条最强/最弱
        """
        if df.empty:
            print("⚠️ 无可展示结果")
            return

        print("📊 板块年度表现（去极值后）\n")
        print(f"总板块数: {len(df)}, 平均涨幅: {df['avg_pct_chg'].mean():.2f}%\n")

        show_cols = [
            "industry",
            "stock_count",
            "avg_pct_chg",
            "median_pct_chg",
            "max_pct_chg",
            "min_pct_chg"
        ]

        # TOP N
        top = df.head(top_n)[show_cols]
        print(f"🔺 表现最强板块 TOP {top_n}")
        print(top.to_string(
            index=False,
            formatters={
                "avg_pct_chg": "{:.2f}%".format,
                "median_pct_chg": "{:.2f}%".format,
                "max_pct_chg": "{:.2f}%".format,
                "min_pct_chg": "{:.2f}%".format,
            }
        ))

        print("\n")

        # BOTTOM N
        bottom = df.tail(bottom_n)[show_cols]
        print(f"🔻 表现最弱板块 BOTTOM {bottom_n}")
        print(bottom.to_string(
            index=False,
            formatters={
                "avg_pct_chg": "{:.2f}%".format,
                "median_pct_chg": "{:.2f}%".format,
                "max_pct_chg": "{:.2f}%".format,
                "min_pct_chg": "{:.2f}%".format,
            }
        ))

        print("\n⚡ 提示：你可以修改 top_n / bottom_n 参数来显示更多或更少板块。")


if __name__ == "__main__":
    strategy = IndustryAnnualPctStrategy(trim_pct=0.05)
    df = strategy.execute()

    # 安全判断（不会再炸）
    if not df.empty:
        df.to_csv("2025_industry_annual_pct_trimmed.csv", index=False)