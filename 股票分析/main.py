#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析系统主入口
Created on 2025/12/31 10:42 
Author: Shuijing
Description: 自动发现策略文件夹中的策略并让用户选择执行
"""

import os
import sys
import importlib
import glob

class StockAnalysisSystem:
    """股票分析系统主类"""
    
    def __init__(self):
        self.strategies = {}
        self.strategies_dir = "策略"
        self.db_config = self.get_db_config()
        self.load_strategies()
    
    def get_db_config(self):
        """获取MySQL数据库连接配置"""
        db_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'Lhf134652',
            'database': 'stock',
            'charset': 'utf8mb4'
        }
        
        print("📊 MySQL数据库配置:")
        print(f"  主机: {db_config['host']}")
        print(f"  端口: {db_config['port']}")
        print(f"  数据库: {db_config['database']}")
        print(f"  用户名: {db_config['user']}")
        
        return db_config
    
    def load_strategies(self):
        """自动发现并加载策略文件夹中的所有策略"""
        print("\n🔍 正在扫描策略文件夹...")
        
        # 获取策略文件夹路径
        strategies_path = os.path.join(os.path.dirname(__file__), self.strategies_dir)
        
        if not os.path.exists(strategies_path):
            print(f"❌ 策略文件夹 '{strategies_path}' 不存在")
            return
        
        # 查找所有.py文件（排除__init__.py）
        strategy_files = glob.glob(os.path.join(strategies_path, "*.py"))
        strategy_files = [f for f in strategy_files if not f.endswith("__init__.py")]
        
        if not strategy_files:
            print("❌ 策略文件夹中没有找到策略文件")
            return
        
        for file_path in strategy_files:
            try:
                # 提取文件名（不含扩展名）
                file_name = os.path.basename(file_path)
                strategy_name = file_name[:-3]  # 去掉.py
                
                # 动态导入策略模块
                module_name = f"{self.strategies_dir}.{strategy_name}"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找策略类（以Strategy结尾的类）
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.endswith('Strategy') and 
                        attr_name != 'Strategy'):
                        
                        # 实例化策略类并传递数据库配置
                        try:
                            strategy_instance = attr(self.db_config)
                        except TypeError:
                            # 如果策略不接受db_config参数，使用默认构造
                            strategy_instance = attr()
                            
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
            print(f"   描述: {strategy_info['description']}")
            print()
        
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
                if result:
                    print(f"\n✅ 策略执行完成，找到 {len(result)} 只符合条件的股票")
                else:
                    print("\nℹ️  策略执行完成，未找到符合条件的股票")
            except Exception as e:
                print(f"❌ 策略执行失败: {e}")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    system = StockAnalysisSystem()
    system.run()

if __name__ == "__main__":
    main()