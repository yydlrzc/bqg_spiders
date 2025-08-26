#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级合并功能使用示例
展示如何使用差分算法、长度优先、基准源设置等策略
"""

from novel_crawler import NovelCrawler

def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建爬虫实例，使用默认配置
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 直接合并，使用默认策略
    crawler.merge_best_content('凡人修仙传')
    
def example_custom_reference_sources():
    """自定义基准源示例"""
    print("\n=== 自定义基准源示例 ===")
    
    # 在初始化时指定基准源
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output',
        reference_sources=['biquge7', 'bqgam', '675m']  # 指定优先域名
    )
    
    # 或者动态配置基准源
    crawler.configure_merge_strategy(
        reference_sources=['biquge7', 'bqgam']  # 只信任这两个源
    )
    
    crawler.merge_best_content('凡人修仙传')
    
def example_length_priority():
    """长度优先策略示例"""
    print("\n=== 长度优先策略示例 ===")
    
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 配置为长度优先
    crawler.configure_merge_strategy(
        enable_diff_merge=False,  # 禁用差分合并
        length_priority_weight=0.9,  # 极高的长度权重
        quality_weight=0.1,
        min_content_length=100  # 最小内容长度
    )
    
    crawler.merge_best_content('凡人修仙传')
    
def example_quality_priority():
    """质量优先策略示例"""
    print("\n=== 质量优先策略示例 ===")
    
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 配置为质量优先
    crawler.configure_merge_strategy(
        enable_diff_merge=True,
        length_priority_weight=0.3,  # 降低长度权重
        quality_weight=0.7,  # 提高质量权重
        min_content_length=300,  # 提高最小长度要求
        similarity_threshold=0.85  # 提高相似度要求
    )
    
    crawler.merge_best_content('凡人修仙传')
    
def example_diff_algorithm():
    """差分算法合并示例"""
    print("\n=== 差分算法合并示例 ===")
    
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 配置差分算法参数
    crawler.configure_merge_strategy(
        enable_diff_merge=True,  # 启用差分合并
        merge_threshold=1.05,  # 低合并阈值，更容易触发合并
        similarity_threshold=0.8,  # 适中的相似度阈值
        length_priority_weight=0.5,
        quality_weight=0.5
    )
    
    crawler.merge_best_content('凡人修仙传')
    
def example_conservative_strategy():
    """保守策略示例（严格筛选）"""
    print("\n=== 保守策略示例 ===")
    
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 配置保守策略
    crawler.configure_merge_strategy(
        reference_sources=['biquge7', 'bqgam'],  # 只信任少数源
        enable_diff_merge=False,  # 禁用差分合并
        length_priority_weight=0.5,
        quality_weight=0.5,
        min_content_length=500,  # 高最小长度要求
        merge_threshold=1.2,  # 高合并阈值
        similarity_threshold=0.95  # 极高相似度要求
    )
    
    crawler.merge_best_content('凡人修仙传')
    
def example_aggressive_strategy():
    """激进策略示例（最大化内容获取）"""
    print("\n=== 激进策略示例 ===")
    
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 配置激进策略
    crawler.configure_merge_strategy(
        enable_diff_merge=True,  # 启用差分合并
        length_priority_weight=0.8,  # 高长度权重
        quality_weight=0.2,
        min_content_length=50,  # 低最小长度要求
        merge_threshold=1.01,  # 极低合并阈值
        similarity_threshold=0.6  # 低相似度要求
    )
    
    crawler.merge_best_content('凡人修仙传')

def example_step_by_step_configuration():
    """分步配置示例"""
    print("\n=== 分步配置示例 ===")
    
    # 1. 创建爬虫实例
    crawler = NovelCrawler(
        domains_file='all_domains.json',
        output_dir='novel_output'
    )
    
    # 2. 查看当前配置
    print("当前基准源:", crawler.reference_sources)
    print("当前合并配置:", crawler.merge_config)
    
    # 3. 逐步调整配置
    print("\n调整基准源...")
    crawler.configure_merge_strategy(reference_sources=['biquge7', 'bqgam'])
    
    print("调整长度权重...")
    crawler.configure_merge_strategy(length_priority_weight=0.7)
    
    print("启用差分合并...")
    crawler.configure_merge_strategy(enable_diff_merge=True)
    
    print("调整合并阈值...")
    crawler.configure_merge_strategy(merge_threshold=1.1)
    
    # 4. 执行合并
    crawler.merge_best_content('凡人修仙传')

def main():
    """主函数 - 展示各种使用方式"""
    print("高级合并功能使用示例\n")
    
    # 选择要运行的示例（注释掉不需要的）
    example_basic_usage()
    # example_custom_reference_sources()
    # example_length_priority()
    # example_quality_priority()
    # example_diff_algorithm()
    # example_conservative_strategy()
    # example_aggressive_strategy()
    # example_step_by_step_configuration()
    
    print("\n=== 配置参数说明 ===")
    print("reference_sources: 基准源列表，优先选择这些域名的内容")
    print("enable_diff_merge: 是否启用差分合并算法")
    print("length_priority_weight: 长度优先权重 (0-1)")
    print("quality_weight: 质量评估权重 (0-1)")
    print("min_content_length: 最小内容长度阈值")
    print("merge_threshold: 合并阈值，合并后内容增长比例")
    print("similarity_threshold: 相似度阈值 (0-1)")
    
    print("\n=== 策略建议 ===")
    print("1. 保守策略: 适用于对质量要求极高的场景")
    print("2. 长度优先: 适用于希望获得最完整内容的场景")
    print("3. 质量优先: 适用于对内容质量要求较高的场景")
    print("4. 差分合并: 适用于多源内容互补的场景")
    print("5. 激进策略: 适用于希望最大化内容获取的场景")

if __name__ == '__main__':
    main()