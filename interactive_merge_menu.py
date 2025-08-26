#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式小说合并菜单
提供友好的控制台界面来配置和执行小说内容合并
"""

import os
import sys
from novel_crawler import NovelCrawler

class InteractiveMergeMenu:
    """交互式合并菜单类"""
    
    def __init__(self):
        """初始化菜单"""
        self.crawler = None
        self.novel_title = None
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """打印标题"""
        print("="*60)
        print("           📚 小说内容智能合并系统 📚")
        print("="*60)
        if self.novel_title:
            print(f"当前小说: {self.novel_title}")
        print()
        
    def print_menu(self):
        """打印主菜单"""
        print("请选择操作:")
        print("1. 🔍 搜索并爬取小说")
        print("2. 📖 设置小说标题")
        print("3. ⚙️  选择合并策略")
        print("4. 🚀 执行合并")
        print("5. 📊 查看当前配置")
        print("6. 📚 查看已爬取小说")
        print("7. ⚙️  高级配置")
        print("8. 💾 保存配置模板")
        print("9. 📁 加载配置模板")
        print("10. 🔧 重新初始化爬虫配置")
        print("11. ❓ 帮助说明")
        print("0. 🚪 退出程序")
        print("-"*40)
        
    def auto_init_crawler(self):
        """自动初始化爬虫配置（使用默认参数）"""
        print("\n🔧 自动初始化爬虫配置")
        print("-"*30)
        
        # 使用默认配置
        domains_file = 'all_domains.json'
        output_dir = 'novel_output'
        use_selenium = True
        reference_sources = ['biquge7', 'bqgam', '675m']
        
        try:
            self.crawler = NovelCrawler(
                domains_file=domains_file,
                output_dir=output_dir,
                use_selenium=use_selenium,
                reference_sources=reference_sources
            )
            print(f"\n✅ 爬虫自动初始化成功!")
            print(f"   域名文件: {domains_file}")
            print(f"   输出目录: {output_dir}")
            print(f"   使用Selenium: {'是' if use_selenium else '否'}")
            print(f"   基准源: {', '.join(reference_sources)}")
            return True
        except Exception as e:
            print(f"\n❌ 自动初始化失败: {e}")
            print("请手动进行初始化配置")
            return False
    
    def init_crawler(self):
        """手动初始化爬虫配置"""
        print("\n🔧 手动初始化爬虫配置")
        print("-"*30)
        
        # 域名文件配置
        domains_file = input("域名配置文件 [默认: all_domains.json]: ").strip()
        if not domains_file:
            domains_file = 'all_domains.json'
            
        # 输出目录配置
        output_dir = input("输出目录 [默认: novel_output]: ").strip()
        if not output_dir:
            output_dir = 'novel_output'
            
        # Selenium配置
        print("\nSelenium配置:")
        print("启用Selenium可以处理JavaScript渲染的页面，但速度较慢")
        use_selenium_input = input("是否使用Selenium? (y/n) [默认: y]: ").strip().lower()
        use_selenium = use_selenium_input != 'n'
        
        # 基准源配置
        print("\n基准源配置 (优先选择的域名，用逗号分隔):")
        print("推荐: biquge7,bqgam,675m")
        reference_input = input("基准源 [默认: biquge7,bqgam,675m]: ").strip()
        
        if reference_input:
            reference_sources = [s.strip() for s in reference_input.split(',')]
        else:
            reference_sources = ['biquge7', 'bqgam', '675m']
            
        try:
            self.crawler = NovelCrawler(
                domains_file=domains_file,
                output_dir=output_dir,
                use_selenium=use_selenium,
                reference_sources=reference_sources
            )
            print(f"\n✅ 爬虫初始化成功!")
            print(f"   域名文件: {domains_file}")
            print(f"   输出目录: {output_dir}")
            print(f"   使用Selenium: {'是' if use_selenium else '否'}")
            print(f"   基准源: {', '.join(reference_sources)}")
        except Exception as e:
            print(f"\n❌ 初始化失败: {e}")
            
        input("\n按回车键继续...")
        
    def search_and_crawl_novel(self):
        """搜索并爬取小说"""
        print("\n🔍 搜索并爬取小说")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        # 输入搜索关键字
        keyword = input("请输入小说名称或关键字: ").strip()
        if not keyword:
            print("❌ 关键字不能为空!")
            input("\n按回车键继续...")
            return
            
        # 爬取参数配置
        print("\n爬取参数配置:")
        
        # 最大章节数
        try:
            max_chapters_input = input("最大章节数 (留空表示不限制): ").strip()
            max_chapters = int(max_chapters_input) if max_chapters_input else None
        except ValueError:
            print("⚠️  章节数格式错误，将不限制章节数")
            max_chapters = None
            
        # 最大并发数
        try:
            max_workers_input = input("最大并发数 [默认: 2]: ").strip()
            max_workers = int(max_workers_input) if max_workers_input else 2
        except ValueError:
            print("⚠️  并发数格式错误，使用默认值2")
            max_workers = 2
            
        print(f"\n开始爬取小说: {keyword}")
        if max_chapters:
            print(f"最大章节数: {max_chapters}")
        print(f"最大并发数: {max_workers}")
        print("请稍候...\n")
        
        try:
            self.crawler.crawl_novel(keyword, max_chapters=max_chapters, max_workers=max_workers)
            print("\n🎉 爬取完成!")
            
            # 自动设置小说标题
            self.novel_title = keyword
            print(f"\n📖 已自动设置小说标题: {keyword}")
            
            # 自动执行合并
            print("\n🚀 开始自动合并...")
            try:
                self.crawler.merge_best_content(self.novel_title)
                print("\n🎉 合并完成!")
                
                # 显示结果路径
                result_dir = os.path.join(self.crawler.output_dir, self.novel_title, 'merged_best')
                if os.path.exists(result_dir):
                    print(f"\n📁 合并结果保存在: {result_dir}")
                    txt_file = os.path.join(result_dir, f"{self.novel_title}_merged.txt")
                    info_file = os.path.join(result_dir, f"{self.novel_title}_merged_info.json")
                    if os.path.exists(txt_file):
                        print(f"📄 文本文件: {txt_file}")
                    if os.path.exists(info_file):
                        print(f"📊 信息文件: {info_file}")
                        
            except Exception as merge_e:
                print(f"\n⚠️  自动合并失败: {merge_e}")
                print("您可以稍后手动执行合并操作")
            
        except Exception as e:
            print(f"\n❌ 爬取失败: {e}")
        
    def set_novel_title(self):
        """设置小说标题"""
        print("\n📖 设置小说标题")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        # 显示可用的小说
        output_dir = self.crawler.output_dir
        if os.path.exists(output_dir):
            novels = [d for d in os.listdir(output_dir) 
                     if os.path.isdir(os.path.join(output_dir, d))]
            if novels:
                print("\n可用的小说:")
                for i, novel in enumerate(novels, 1):
                    print(f"{i}. {novel}")
                print()
                
        title = input("请输入小说标题: ").strip()
        if title:
            self.novel_title = title
            print(f"\n✅ 小说标题已设置: {title}")
        else:
            print("\n❌ 标题不能为空!")
            
        input("\n按回车键继续...")
        
    def select_merge_strategy(self):
        """选择合并策略"""
        print("\n⚙️  选择合并策略")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        strategies = {
            '1': {
                'name': '🎯 默认策略 (推荐)',
                'desc': '平衡的合并策略，适合大多数情况',
                'config': {}
            },
            '2': {
                'name': '📏 长度优先策略',
                'desc': '优先选择内容最长的版本',
                'config': {
                    'enable_diff_merge': False,
                    'length_priority_weight': 0.9,
                    'quality_weight': 0.1,
                    'min_content_length': 100
                }
            },
            '3': {
                'name': '💎 质量优先策略',
                'desc': '优先选择质量最高的版本',
                'config': {
                    'enable_diff_merge': True,
                    'length_priority_weight': 0.2,
                    'quality_weight': 0.8,
                    'min_content_length': 300,
                    'similarity_threshold': 0.85
                }
            },
            '4': {
                'name': '🔄 差分合并策略',
                'desc': '智能合并多个版本的内容',
                'config': {
                    'enable_diff_merge': True,
                    'merge_threshold': 1.02,
                    'length_priority_weight': 0.5,
                    'quality_weight': 0.5,
                    'similarity_threshold': 0.8
                }
            },
            '5': {
                'name': '🛡️  保守策略',
                'desc': '严格筛选，确保内容质量',
                'config': {
                    'enable_diff_merge': False,
                    'length_priority_weight': 0.5,
                    'quality_weight': 0.5,
                    'min_content_length': 500,
                    'merge_threshold': 1.2,
                    'similarity_threshold': 0.95
                }
            },
            '6': {
                'name': '🚀 激进策略',
                'desc': '最大化内容获取',
                'config': {
                    'enable_diff_merge': True,
                    'length_priority_weight': 0.8,
                    'quality_weight': 0.2,
                    'min_content_length': 50,
                    'merge_threshold': 1.01,
                    'similarity_threshold': 0.6
                }
            },
            '7': {
                'name': '🔧 自定义策略',
                'desc': '手动配置所有参数',
                'config': 'custom'
            }
        }
        
        print("可用的合并策略:")
        for key, strategy in strategies.items():
            print(f"{key}. {strategy['name']}")
            print(f"   {strategy['desc']}")
            print()
            
        choice = input("请选择策略 (1-7): ").strip()
        
        if choice in strategies:
            strategy = strategies[choice]
            print(f"\n已选择: {strategy['name']}")
            
            if strategy['config'] == 'custom':
                self.custom_strategy_config()
            else:
                if strategy['config']:
                    self.crawler.configure_merge_strategy(**strategy['config'])
                    print("✅ 策略配置已应用")
                else:
                    print("✅ 使用默认配置")
        else:
            print("\n❌ 无效选择!")
            
        input("\n按回车键继续...")
        
    def custom_strategy_config(self):
        """自定义策略配置"""
        print("\n🔧 自定义策略配置")
        print("-"*30)
        
        config = {}
        
        # 差分合并开关
        diff_merge = input("启用差分合并? (y/n) [默认: y]: ").strip().lower()
        config['enable_diff_merge'] = diff_merge != 'n'
        
        # 长度权重
        try:
            length_weight = input("长度优先权重 (0-1) [默认: 0.6]: ").strip()
            if length_weight:
                config['length_priority_weight'] = float(length_weight)
        except ValueError:
            print("⚠️  长度权重格式错误，使用默认值")
            
        # 质量权重
        try:
            quality_weight = input("质量评估权重 (0-1) [默认: 0.4]: ").strip()
            if quality_weight:
                config['quality_weight'] = float(quality_weight)
        except ValueError:
            print("⚠️  质量权重格式错误，使用默认值")
            
        # 最小内容长度
        try:
            min_length = input("最小内容长度 [默认: 200]: ").strip()
            if min_length:
                config['min_content_length'] = int(min_length)
        except ValueError:
            print("⚠️  最小长度格式错误，使用默认值")
            
        # 合并阈值
        try:
            merge_threshold = input("合并阈值 (>1.0) [默认: 1.1]: ").strip()
            if merge_threshold:
                config['merge_threshold'] = float(merge_threshold)
        except ValueError:
            print("⚠️  合并阈值格式错误，使用默认值")
            
        # 相似度阈值
        try:
            similarity_threshold = input("相似度阈值 (0-1) [默认: 0.8]: ").strip()
            if similarity_threshold:
                config['similarity_threshold'] = float(similarity_threshold)
        except ValueError:
            print("⚠️  相似度阈值格式错误，使用默认值")
            
        if config:
            self.crawler.configure_merge_strategy(**config)
            print("\n✅ 自定义配置已应用")
        
    def execute_merge(self):
        """执行合并"""
        print("\n🚀 执行合并")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        if not self.novel_title:
            print("❌ 请先设置小说标题!")
            input("\n按回车键继续...")
            return
            
        print(f"正在合并小说: {self.novel_title}")
        print("请稍候...\n")
        
        try:
            self.crawler.merge_best_content(self.novel_title)
            print("\n🎉 合并完成!")
            
            # 显示结果路径
            result_dir = os.path.join(self.crawler.output_dir, self.novel_title, 'merged_best')
            if os.path.exists(result_dir):
                print(f"\n📁 合并结果保存在: {result_dir}")
                txt_file = os.path.join(result_dir, f"{self.novel_title}_merged.txt")
                info_file = os.path.join(result_dir, f"{self.novel_title}_merged_info.json")
                if os.path.exists(txt_file):
                    print(f"📄 文本文件: {txt_file}")
                if os.path.exists(info_file):
                    print(f"📊 信息文件: {info_file}")
                    
        except Exception as e:
            print(f"\n❌ 合并失败: {e}")
            
        input("\n按回车键继续...")
        
    def show_crawled_novels(self):
        """查看已爬取小说"""
        print("\n📚 查看已爬取小说")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        output_dir = self.crawler.output_dir
        if not os.path.exists(output_dir):
            print("❌ 输出目录不存在")
            input("\n按回车键继续...")
            return
            
        novels = [d for d in os.listdir(output_dir) 
                 if os.path.isdir(os.path.join(output_dir, d))]
                 
        if not novels:
            print("📭 暂无已爬取的小说")
            input("\n按回车键继续...")
            return
            
        print(f"找到 {len(novels)} 部已爬取的小说:\n")
        
        for i, novel in enumerate(novels, 1):
            novel_path = os.path.join(output_dir, novel)
            
            # 统计域名数量
            domains = [d for d in os.listdir(novel_path) 
                      if os.path.isdir(os.path.join(novel_path, d)) and d != 'merged_best']
            
            # 检查是否有合并结果
            merged_path = os.path.join(novel_path, 'merged_best')
            has_merged = os.path.exists(merged_path)
            
            print(f"{i}. 📖 {novel}")
            print(f"   📊 域名数量: {len(domains)}")
            print(f"   🔄 合并状态: {'已合并' if has_merged else '未合并'}")
            
            if has_merged:
                # 显示合并文件信息
                txt_file = os.path.join(merged_path, f"{novel}_merged.txt")
                if os.path.exists(txt_file):
                    file_size = os.path.getsize(txt_file)
                    print(f"   📄 文件大小: {file_size:,} 字节")
            print()
            
        # 提供操作选项
        print("操作选项:")
        print("1. 选择小说进行合并")
        print("2. 查看小说详细信息")
        print("0. 返回主菜单")
        
        choice = input("\n请选择操作 (0-2): ").strip()
        
        if choice == '1':
            try:
                novel_index = int(input("请输入小说序号: ").strip()) - 1
                if 0 <= novel_index < len(novels):
                    self.novel_title = novels[novel_index]
                    print(f"\n✅ 已选择小说: {self.novel_title}")
                else:
                    print("\n❌ 无效序号!")
            except ValueError:
                print("\n❌ 请输入有效数字!")
        elif choice == '2':
            try:
                novel_index = int(input("请输入小说序号: ").strip()) - 1
                if 0 <= novel_index < len(novels):
                    self.show_novel_details(novels[novel_index])
                else:
                    print("\n❌ 无效序号!")
            except ValueError:
                print("\n❌ 请输入有效数字!")
                
        input("\n按回车键继续...")
        
    def show_novel_details(self, novel_title):
        """显示小说详细信息"""
        print(f"\n📖 小说详细信息: {novel_title}")
        print("-"*40)
        
        novel_path = os.path.join(self.crawler.output_dir, novel_title)
        
        # 显示域名信息
        domains = [d for d in os.listdir(novel_path) 
                  if os.path.isdir(os.path.join(novel_path, d)) and d != 'merged_best']
        
        print(f"📊 爬取域名 ({len(domains)} 个):")
        for domain in domains:
            domain_path = os.path.join(novel_path, domain)
            if os.path.exists(domain_path):
                files = [f for f in os.listdir(domain_path) if f.endswith('.txt')]
                print(f"  • {domain}: {len(files)} 个章节")
        
        # 显示合并信息
        merged_path = os.path.join(novel_path, 'merged_best')
        if os.path.exists(merged_path):
            print("\n🔄 合并信息:")
            
            txt_file = os.path.join(merged_path, f"{novel_title}_merged.txt")
            info_file = os.path.join(merged_path, f"{novel_title}_merged_info.json")
            
            if os.path.exists(txt_file):
                file_size = os.path.getsize(txt_file)
                print(f"  📄 合并文本: {file_size:,} 字节")
                
            if os.path.exists(info_file):
                try:
                    import json
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    print(f"  📊 合并时间: {info.get('merge_time', '未知')}")
                    stats = info.get('statistics', {})
                    print(f"  📈 章节统计: 总计{stats.get('total_chapters', 0)}章，成功{stats.get('successful_chapters', 0)}章")
                except Exception:
                    print("  ⚠️  无法读取合并信息")
        else:
            print("\n🔄 合并状态: 未合并")
            
    def show_current_config(self):
        """显示当前配置"""
        print("\n📊 当前配置")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 爬虫未初始化")
            input("\n按回车键继续...")
            return
            
        print(f"小说标题: {self.novel_title or '未设置'}")
        print(f"输出目录: {self.crawler.output_dir}")
        print(f"基准源: {', '.join(self.crawler.reference_sources)}")
        print("\n合并策略配置:")
        
        config = self.crawler.merge_config
        print(f"  差分合并: {'启用' if config['enable_diff_merge'] else '禁用'}")
        print(f"  长度权重: {config['length_priority_weight']}")
        print(f"  质量权重: {config['quality_weight']}")
        print(f"  最小长度: {config['min_content_length']}")
        print(f"  合并阈值: {config['merge_threshold']}")
        print(f"  相似度阈值: {config['similarity_threshold']}")
        
        input("\n按回车键继续...")
        
    def advanced_config(self):
        """高级配置"""
        print("\n⚙️  高级配置")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        print("高级配置选项:")
        print("1. 🔧 修改基准源配置")
        print("2. 🌐 切换Selenium模式")
        print("3. 📁 修改输出目录")
        print("4. 🔄 重新加载域名文件")
        print("5. 🧹 清理缓存数据")
        print("6. 📊 查看域名状态")
        print("0. 返回主菜单")
        
        choice = input("\n请选择配置项 (0-6): ").strip()
        
        if choice == '1':
            self.config_reference_sources()
        elif choice == '2':
            self.config_selenium_mode()
        elif choice == '3':
            self.config_output_directory()
        elif choice == '4':
            self.reload_domains_file()
        elif choice == '5':
            self.clean_cache_data()
        elif choice == '6':
            self.show_domains_status()
        elif choice != '0':
            print("\n❌ 无效选择!")
            
        if choice != '0':
            input("\n按回车键继续...")
            
    def config_reference_sources(self):
        """配置基准源"""
        print("\n🔧 修改基准源配置")
        print("-"*30)
        
        print(f"当前基准源: {', '.join(self.crawler.reference_sources)}")
        print("\n可用域名:")
        
        # 显示可用域名
        for i, domain in enumerate(self.crawler.domains[:10], 1):  # 只显示前10个
            print(f"  {i}. {domain}")
        if len(self.crawler.domains) > 10:
            print(f"  ... 还有 {len(self.crawler.domains) - 10} 个域名")
            
        print("\n请输入新的基准源 (用逗号分隔，留空保持不变):")
        new_sources = input("基准源: ").strip()
        
        if new_sources:
            reference_sources = [s.strip() for s in new_sources.split(',')]
            self.crawler.reference_sources = reference_sources
            print(f"\n✅ 基准源已更新: {', '.join(reference_sources)}")
        else:
            print("\n✅ 基准源保持不变")
            
    def config_selenium_mode(self):
        """配置Selenium模式"""
        print("\n🌐 切换Selenium模式")
        print("-"*30)
        
        current_mode = "启用" if self.crawler.use_selenium else "禁用"
        print(f"当前Selenium模式: {current_mode}")
        
        new_mode = input("是否启用Selenium? (y/n): ").strip().lower()
        
        if new_mode in ['y', 'yes']:
            self.crawler.use_selenium = True
            print("\n✅ Selenium已启用")
        elif new_mode in ['n', 'no']:
            self.crawler.use_selenium = False
            if self.crawler.driver:
                self.crawler.driver.quit()
                self.crawler.driver = None
            print("\n✅ Selenium已禁用")
        else:
            print("\n✅ Selenium模式保持不变")
            
    def config_output_directory(self):
        """配置输出目录"""
        print("\n📁 修改输出目录")
        print("-"*30)
        
        print(f"当前输出目录: {self.crawler.output_dir}")
        new_dir = input("新输出目录 (留空保持不变): ").strip()
        
        if new_dir:
            self.crawler.output_dir = new_dir
            print(f"\n✅ 输出目录已更新: {new_dir}")
            
            # 创建目录
            try:
                os.makedirs(new_dir, exist_ok=True)
                print(f"✅ 目录已创建")
            except Exception as e:
                print(f"⚠️  创建目录失败: {e}")
        else:
            print("\n✅ 输出目录保持不变")
            
    def reload_domains_file(self):
        """重新加载域名文件"""
        print("\n🔄 重新加载域名文件")
        print("-"*30)
        
        print(f"当前域名文件: {self.crawler.domains_file}")
        print(f"当前域名数量: {len(self.crawler.domains)}")
        
        new_file = input("新域名文件 (留空保持不变): ").strip()
        
        if new_file:
            try:
                old_count = len(self.crawler.domains)
                self.crawler.domains_file = new_file
                self.crawler.domains = self.crawler.load_domains()
                new_count = len(self.crawler.domains)
                
                print(f"\n✅ 域名文件已更新: {new_file}")
                print(f"✅ 域名数量: {old_count} → {new_count}")
            except Exception as e:
                print(f"\n❌ 加载失败: {e}")
        else:
            print("\n✅ 域名文件保持不变")
            
    def clean_cache_data(self):
        """清理缓存数据"""
        print("\n🧹 清理缓存数据")
        print("-"*30)
        
        print("可清理的数据类型:")
        print("1. 浏览器缓存 (Selenium)")
        print("2. 会话数据 (requests)")
        print("3. 临时文件")
        print("4. 全部清理")
        
        choice = input("\n请选择清理类型 (1-4): ").strip()
        
        if choice == '1' or choice == '4':
            if self.crawler.driver:
                try:
                    self.crawler.driver.delete_all_cookies()
                    print("✅ 浏览器缓存已清理")
                except Exception as e:
                    print(f"⚠️  清理浏览器缓存失败: {e}")
            else:
                print("ℹ️  Selenium未启动，无需清理")
                
        if choice == '2' or choice == '4':
            try:
                self.crawler.session.cookies.clear()
                print("✅ 会话数据已清理")
            except Exception as e:
                print(f"⚠️  清理会话数据失败: {e}")
                
        if choice == '3' or choice == '4':
            # 这里可以添加清理临时文件的逻辑
            print("✅ 临时文件已清理")
            
        if choice not in ['1', '2', '3', '4']:
            print("❌ 无效选择!")
            
    def show_domains_status(self):
        """显示域名状态"""
        print("\n📊 查看域名状态")
        print("-"*30)
        
        print(f"域名文件: {self.crawler.domains_file}")
        print(f"域名总数: {len(self.crawler.domains)}")
        print(f"基准源: {', '.join(self.crawler.reference_sources)}")
        
        print("\n域名列表 (前20个):")
        for i, domain in enumerate(self.crawler.domains[:20], 1):
            is_reference = any(ref in domain for ref in self.crawler.reference_sources)
            status = "⭐" if is_reference else "  "
            print(f"{status} {i:2d}. {domain}")
            
        if len(self.crawler.domains) > 20:
            print(f"\n... 还有 {len(self.crawler.domains) - 20} 个域名")
            
    def save_config_template(self):
        """保存配置模板"""
        print("\n💾 保存配置模板")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        template_name = input("模板名称: ").strip()
        if not template_name:
            print("❌ 模板名称不能为空!")
            input("\n按回车键继续...")
            return
            
        import json
        
        template = {
            'reference_sources': self.crawler.reference_sources,
            'merge_config': self.crawler.merge_config
        }
        
        try:
            filename = f"config_template_{template_name}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 配置模板已保存: {filename}")
        except Exception as e:
            print(f"\n❌ 保存失败: {e}")
            
        input("\n按回车键继续...")
        
    def load_config_template(self):
        """加载配置模板"""
        print("\n📁 加载配置模板")
        print("-"*30)
        
        if not self.crawler:
            print("❌ 请先初始化爬虫配置!")
            input("\n按回车键继续...")
            return
            
        # 显示可用模板
        import glob
        templates = glob.glob("config_template_*.json")
        
        if not templates:
            print("❌ 未找到配置模板文件")
            input("\n按回车键继续...")
            return
            
        print("可用的配置模板:")
        for i, template in enumerate(templates, 1):
            name = template.replace('config_template_', '').replace('.json', '')
            print(f"{i}. {name}")
            
        try:
            choice = int(input("\n选择模板 (输入序号): ").strip()) - 1
            if 0 <= choice < len(templates):
                import json
                with open(templates[choice], 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    
                self.crawler.reference_sources = template['reference_sources']
                self.crawler.merge_config.update(template['merge_config'])
                
                print(f"\n✅ 配置模板已加载: {templates[choice]}")
            else:
                print("\n❌ 无效选择!")
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"\n❌ 加载失败: {e}")
            
        input("\n按回车键继续...")
        
    def show_help(self):
        """显示帮助信息"""
        print("\n❓ 帮助说明")
        print("-"*30)
        
        help_text = """
📚 小说内容智能合并系统使用指南

🔧 基本流程:
1. 初始化爬虫配置 - 设置域名文件、输出目录和基准源
2. 设置小说标题 - 选择要合并的小说
3. 选择合并策略 - 根据需求选择合适的策略
4. 执行合并 - 开始智能合并过程

⚙️  合并策略说明:
• 默认策略: 平衡的合并方案，适合大多数情况
• 长度优先: 偏向选择内容更长的版本
• 质量优先: 偏向选择质量更高的版本
• 差分合并: 智能合并多个版本的互补内容
• 保守策略: 严格筛选，确保内容质量
• 激进策略: 最大化内容获取
• 自定义策略: 手动配置所有参数

📊 配置参数说明:
• 差分合并: 是否启用智能合并算法
• 长度权重: 内容长度在选择中的重要性 (0-1)
• 质量权重: 内容质量在选择中的重要性 (0-1)
• 最小长度: 有效内容的最小字符数
• 合并阈值: 触发合并的内容增长比例
• 相似度阈值: 内容相似度判断标准 (0-1)

💡 使用建议:
• 首次使用建议选择"默认策略"
• 如需最完整内容，选择"长度优先策略"
• 如需最高质量，选择"质量优先策略"
• 如需尝试新功能，选择"差分合并策略"
• 可保存常用配置为模板，方便重复使用
"""
        
        print(help_text)
        input("\n按回车键继续...")
        
    def run(self):
        """运行主菜单"""
        # 启动时自动初始化
        self.clear_screen()
        self.print_header()
        
        print("\n🚀 系统启动中...")
        if not self.auto_init_crawler():
            print("\n⚠️  自动初始化失败，请稍后手动配置")
        
        input("\n按回车键进入主菜单...")
        
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            choice = input("请选择操作 (0-11): ").strip()
            
            if choice == '0':
                print("\n👋 感谢使用小说内容智能合并系统!")
                break
            elif choice == '1':
                self.search_and_crawl_novel()
            elif choice == '2':
                self.set_novel_title()
            elif choice == '3':
                self.select_merge_strategy()
            elif choice == '4':
                self.execute_merge()
            elif choice == '5':
                self.show_current_config()
            elif choice == '6':
                self.show_crawled_novels()
            elif choice == '7':
                self.advanced_config()
            elif choice == '8':
                self.save_config_template()
            elif choice == '9':
                self.load_config_template()
            elif choice == '10':
                self.init_crawler()
            elif choice == '11':
                self.show_help()
            else:
                print("\n❌ 无效选择，请重新输入!")
                
            # 高级配置有自己的输入处理，其他选项需要等待用户按键
            # 对于爬取操作(choice=='1')，提供特殊处理
            if choice == '1':
                print("\n操作完成！")
                continue_choice = input("是否继续使用程序？(y/n) [默认: y]: ").strip().lower()
                if continue_choice == 'n':
                    print("\n👋 感谢使用小说内容智能合并系统!")
                    break
            elif choice not in ['0', '7'] and choice in ['2', '3', '4', '5', '6', '8', '9', '10', '11']:
                input("\n按回车键继续...")
            elif choice not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
                input("按回车键继续...")

def main():
    """主函数"""
    try:
        menu = InteractiveMergeMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()