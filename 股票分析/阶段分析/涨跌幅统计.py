from sqlalchemy import create_engine
import pandas as pd


class AnnualPctStrategy:
    """策略：统计2025年全年累计涨跌幅，并显示股票名称和板块，返回按涨幅排序结果（SQLAlchemy版）"""

    def __init__(self, db_url=None):
        """
        db_url 示例：
        'mysql+pymysql://root:密码@127.0.0.1:3306/stock?charset=utf8mb4'
        """
        if db_url is None:
            self.db_url = "mysql+pymysql://root:Lhf134652@127.0.0.1:3306/stock?charset=utf8mb4"
        else:
            self.db_url = db_url

        self.name = "2025年全年涨跌幅统计"
        self.description = "计算2025年每只股票年初到年末的累计涨跌幅，并显示名称和板块，按涨幅排序"
        self.thresholds = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    def execute(self):
        try:
            # 创建 SQLAlchemy engine
            engine = create_engine(self.db_url)
            print("✅ 数据库连接成功（SQLAlchemy）")

            # 查询2025年所有日线
            df = pd.read_sql(
                "SELECT ts_code, trade_date, close FROM daily_kline "
                "WHERE trade_date BETWEEN '20250101' AND '20251231'",
                engine
            )
            if df.empty:
                print("❌ 没有找到2025年的日线数据")
                return pd.DataFrame()

            # 查询股票名称和板块
            stock_info = pd.read_sql("SELECT ts_code, name, industry FROM stock_basic", engine)

            # 找每只股票年初收盘价和年末收盘价
            first_day = df.groupby('ts_code')['trade_date'].min().reset_index()
            last_day = df.groupby('ts_code')['trade_date'].max().reset_index()

            first_close = pd.merge(first_day, df, on=['ts_code', 'trade_date'], how='left')
            last_close = pd.merge(last_day, df, on=['ts_code', 'trade_date'], how='left')

            merged = pd.merge(first_close[['ts_code', 'close']],
                              last_close[['ts_code', 'close']],
                              on='ts_code',
                              suffixes=('_start', '_end'))

            # 计算全年涨跌幅
            merged['pct_chg'] = (merged['close_end'] - merged['close_start']) / merged['close_start'] * 100

            # 合并股票信息
            merged = pd.merge(merged, stock_info, on='ts_code', how='left')

            # 按全年涨跌幅排序
            merged_sorted = merged.sort_values(by='pct_chg', ascending=False).reset_index(drop=True)

            # 打印阈值统计
            print("\n年度涨跌幅统计（2025）")
            print("阈值(%) | 涨幅股票数 | 跌幅股票数")
            print("-----------------------------------")
            for th in self.thresholds:
                up_count = (merged_sorted['pct_chg'] >= th).sum()
                down_count = (merged_sorted['pct_chg'] <= -th).sum()
                print(f"{th:>8}% | {up_count:>10} | {down_count:>10}")

            # 特别显示涨幅≥100%或跌幅≤-100%的股票
            print("\n=== 涨幅≥100%的股票（按涨幅排序） ===")
            up_100 = merged_sorted[merged_sorted['pct_chg'] >= 100]
            if not up_100.empty:
                for _, row in up_100.iterrows():
                    print(f"{row['ts_code']} {row['name']} ({row['industry']}) 全年涨幅：{row['pct_chg']:.2f}%")
            else:
                print("无股票涨幅≥100%")

            print("\n=== 跌幅≤-100%的股票（按跌幅排序） ===")
            down_100 = merged_sorted[merged_sorted['pct_chg'] <= -100]
            if not down_100.empty:
                for _, row in down_100.iterrows():
                    print(f"{row['ts_code']} {row['name']} ({row['industry']}) 全年跌幅：{row['pct_chg']:.2f}%")
            else:
                print("无股票跌幅≤-100%")

            # 返回按涨幅排序的完整表格
            return merged_sorted[['ts_code', 'name', 'industry', 'close_start', 'close_end', 'pct_chg']]

        except Exception as e:
            print(f"❌ 策略执行出错: {e}")
            return pd.DataFrame()


# 独立运行示例
if __name__ == "__main__":
    strategy = AnnualPctStrategy()
    df_sorted = strategy.execute()
    # 不生成 CSV，直接返回 DataFrame 并打印
