from sqlalchemy import create_engine
import pandas as pd


class TemplateStrategy:
    """策略模板 - 使用 SQLAlchemy 连接 MySQL"""

    def __init__(self, db_url=None):
        """
        db_url 示例：
        'mysql+pymysql://root:密码@127.0.0.1:3306/stock?charset=utf8mb4'
        """
        if db_url is None:
            self.db_url = "mysql+pymysql://root:Lhf134652@127.0.0.1:3306/stock?charset=utf8mb4"
        else:
            self.db_url = db_url

        self.name = "策略名称"  # 修改为您的策略名称
        self.description = "策略描述"  # 修改为策略描述

    def execute(self):
        """执行策略分析"""
        try:
            # 创建 SQLAlchemy engine
            engine = create_engine(self.db_url)
            print("✅ 数据库连接成功（SQLAlchemy）")

            # 在这里实现您的策略逻辑
            # 示例：查询 daily_kline 表前 5 条记录
            print("执行策略逻辑...")
            result = pd.read_sql("SELECT * FROM daily_kline LIMIT 5", engine)
            print(result)

            # 返回字典列表形式，方便前端或其他程序使用
            return result.to_dict('records')

        except Exception as e:
            print(f"❌ 策略执行过程中出错: {e}")
            return []


# 保留独立运行功能
if __name__ == "__main__":
    strategy = TemplateStrategy()
    strategy.execute()
