#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析系统主入口（仅支持SQLAlchemy策略）
Created on 2025/12/31 10:42
Author: Shuijing
Description: 自动发现策略文件夹中的策略并让用户选择执行
"""

import os
import importlib.util
import glob

class StockAnalysisSystem:
    """股票分析系统主类（仅SQLAlchemy策略）"""

    def __init__(self):
        self.strategies = {}
        self.strategies_dir = "策略"
        self.db_url = self.get_db_url()
        self.load_strategies()

    def get_db_url(self):
        """获取SQLAlchemy数据库URL"""
        user = "root"
        password = "Lhf134652"
        host = "127.0.0.1"
        port = 3306
        database = "stock"
        charset = "utf8mb4"

        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
        print("📊 SQLAlchemy数据库URL配置:")
        print(f"  URL: {db_url}")
        return db_url

    def load_strategies(self):
        """自动发现并加载策略文件夹中的所有策略"""
        print("\n🔍 正在扫描策略文件夹...")

        strategies_path = os.path.join(os.path.dirname(__file__), self.strategies_dir)
        if not os.path.exists(strategies_path):
            print(f"❌ 策略文件夹 '{strategies_path}' 不存在")
            return

        strategy_files = glob.glob(os.path.join(strategies_path, "*.py"))
        strategy_files = [f for f in strategy_files if not f.endswith("__init__.py")]

        if not strategy_files:
            print("❌ 策略文件夹中没有找到策略文件")
            return

        for file_path in strategy_files:
            try:
                file_name = os.path.basename(file_path)
                strategy_name = file_name[:-3]

                spec = importlib.util.spec_from_file_location(strategy_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 查找策略类（以 Strategy 结尾）
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr_name.endswith('Strategy') and attr_name != 'Strategy':
                        # SQLAlchemy策略必须接受 db_url 参数
                        strategy_instance = attr(self.db_url)

                        self.strategies[strategy_name] = {
                            'instance': strategy_instance,
                            'name': getattr(strategy_instance, 'name', strategy_name),
                            'description': getattr(strategy_instance, 'description', '无描述')
                        }
                        print(f"✅ 加载策略: {strategy_name}")
                        break

            except Exception as e:
                print(f"❌ 加载策略 {file_name} 失败: {e}")

    def show_menu(self):
        """显示策略选择菜单"""
        print("\n" + "="*50)
        print("📊 股票分析系统")
        print("="*50)

        if not self.strategies:
            print("❌ 没有可用的策略，请检查策略文件夹")
            return None

        print("可用的策略:")
        for i, (key, strategy_info) in enumerate(self.strategies.items(), 1):
            print(f"{i}. {strategy_info['name']}")
            print(f"   描述: {strategy_info['description']}\n")

        print("0. 退出系统")
        print("="*50)

        while True:
            try:
                choice = input("请选择要执行的策略编号: ")
                if choice == '0':
                    return None
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.strategies):
                    strategy_key = list(self.strategies.keys())[choice_num - 1]
                    return self.strategies[strategy_key]['instance']
                else:
                    print("❌ 请输入有效的编号")
            except ValueError:
                print("❌ 请输入数字")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                return None

    def run(self):
        """运行股票分析系统"""
        print("🚀 启动股票分析系统...")

        while True:
            strategy = self.show_menu()
            if strategy is None:
                break

            print(f"\n🎯 执行策略: {getattr(strategy, 'name', '未知策略')}")
            print("-" * 40)

            try:
                result = strategy.execute()
                # 兼容返回类型
                if hasattr(result, 'shape'):
                    count = result.shape[0]
                elif isinstance(result, list):
                    count = len(result)
                else:
                    count = 0

                if count:
                    print(f"\n✅ 策略执行完成，找到 {count} 只符合条件的股票")
                else:
                    print("\nℹ️  策略执行完成，未找到符合条件的股票")
            except Exception as e:
                print(f"❌ 策略执行失败: {e}")

            input("\n按回车键继续...")

def main():
    system = StockAnalysisSystem()
    system.run()

if __name__ == "__main__":
    main()
