#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速合并脚本
提供常用合并策略的快速访问
"""

import sys
import os
from novel_crawler import NovelCrawler

def quick_merge(novel_title, strategy='default'):
    """快速合并函数
    
    Args:
        novel_title (str): 小说标题
        strategy (str): 合并策略 ('default', 'length', 'quality', 'diff', 'conservative', 'aggressive')
    """
    
    # 策略配置映射
    strategies = {
        'default': {},
        'length': {
            'enable_diff_merge': False,
            'length_priority_weight': 0.9,
            'quality_weight': 0.1,
            'min_content_length': 100
        },
        'quality': {
            'enable_diff_merge': True,
            'length_priority_weight': 0.2,
            'quality_weight': 0.8,
            'min_content_length': 300,
            'similarity_threshold': 0.85
        },
        'diff': {
            'enable_diff_merge': True,
            'merge_threshold': 1.02,
            'length_priority_weight': 0.5,
            'quality_weight': 0.5,
            'similarity_threshold': 0.8
        },
        'conservative': {
            'enable_diff_merge': False,
            'length_priority_weight': 0.5,
            'quality_weight': 0.5,
            'min_content_length': 500,
            'merge_threshold': 1.2,
            'similarity_threshold': 0.95
        },
        'aggressive': {
            'enable_diff_merge': True,
            'length_priority_weight': 0.8,
            'quality_weight': 0.2,
            'min_content_length': 50,
            'merge_threshold': 1.01,
            'similarity_threshold': 0.6
        }
    }
    
    if strategy not in strategies:
        print(f"❌ 未知策略: {strategy}")
        print(f"可用策略: {', '.join(strategies.keys())}")
        return False
        
    try:
        # 初始化爬虫
        print(f"🔧 初始化爬虫...")
        crawler = NovelCrawler()
        
        # 应用策略
        if strategies[strategy]:
            print(f"⚙️  应用{strategy}策略...")
            crawler.configure_merge_strategy(**strategies[strategy])
        
        # 执行合并
        print(f"🚀 开始合并小说: {novel_title}")
        crawler.merge_best_content(novel_title)
        
        print(f"\n🎉 合并完成!")
        
        # 显示结果路径
        result_dir = os.path.join(crawler.output_dir, novel_title, 'merged_best')
        if os.path.exists(result_dir):
            print(f"📁 结果保存在: {result_dir}")
            
        return True
        
    except Exception as e:
        print(f"❌ 合并失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  python {sys.argv[0]} <小说标题> [策略]")
        print("\n可用策略:")
        print("  default     - 默认策略 (推荐)")
        print("  length      - 长度优先策略")
        print("  quality     - 质量优先策略")
        print("  diff        - 差分合并策略")
        print("  conservative - 保守策略")
        print("  aggressive  - 激进策略")
        print("\n示例:")
        print(f"  python {sys.argv[0]} 凡人修仙传")
        print(f"  python {sys.argv[0]} 凡人修仙传 quality")
        return
        
    novel_title = sys.argv[1]
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'default'
    
    print(f"📚 小说: {novel_title}")
    print(f"🎯 策略: {strategy}")
    print("-" * 40)
    
    success = quick_merge(novel_title, strategy)
    
    if success:
        print("\n✅ 任务完成!")
    else:
        print("\n❌ 任务失败!")
        sys.exit(1)

if __name__ == '__main__':
    main()