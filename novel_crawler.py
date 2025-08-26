#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说爬虫脚本
根据关键字搜索笔趣阁网站，获取小说章节内容并保存到txt文件
支持多域名并行爬取和章节内容比对校验
"""

import json
import requests
import re
import time
import os
import hashlib
from urllib.parse import urljoin, quote, urlparse
from bs4 import BeautifulSoup
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import sys
from datetime import datetime
import threading


class CrawlDisplay:
    """爬取过程美化显示类"""
    
    def __init__(self):
        """初始化显示器"""
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
        self.domain_lines = {}  # 存储每个域名的行号
        self.total_lines = 0    # 总行数
        self.progress_data = {} # 存储每个域名的进度数据
        
    def colored_text(self, text, color):
        """返回彩色文本"""
        if sys.platform == 'win32':
            # Windows 系统启用 ANSI 颜色支持
            os.system('')
        return f"{self.colors.get(color, '')}{text}{self.colors['end']}"
        
    def print_header(self, title):
        """打印标题头部"""
        border = "═" * 60
        print(f"\n{self.colored_text(border, 'cyan')}")
        print(f"{self.colored_text(f'  📚 {title}', 'bold')}")
        print(f"{self.colored_text(border, 'cyan')}\n")
        
    def print_section(self, title):
        """打印章节标题"""
        print(f"\n{self.colored_text(f'🔍 {title}', 'blue')}")
        print(f"{self.colored_text('─' * 40, 'blue')}")
        
    def print_domain_start(self, domain_name, book_title):
        """打印域名开始爬取信息"""
        print(f"\n{self.colored_text(f'🌐 [{domain_name}]', 'purple')} {self.colored_text('开始爬取', 'bold')}: {book_title}")
        
    def print_progress(self, current, total, chapter_title, domain_name):
        """打印进度条"""
        percentage = (current / total) * 100
        filled_length = int(30 * current // total)
        bar = '█' * filled_length + '░' * (30 - filled_length)
        
        # 截断章节标题以适应显示
        display_title = chapter_title[:25] + '...' if len(chapter_title) > 25 else chapter_title
        
        print(f"\r{self.colored_text(f'[{domain_name}]', 'purple')} "
              f"{self.colored_text(f'[{bar}]', 'green')} "
              f"{self.colored_text(f'{percentage:5.1f}%', 'yellow')} "
              f"({current}/{total}) {display_title}", end='', flush=True)
        
    def print_chapter_success(self, domain_name, content_length):
        """打印章节成功信息"""
        print(f" {self.colored_text('✓', 'green')} {content_length:,} 字")
        
    def print_chapter_failed(self, domain_name, reason="获取失败"):
        """打印章节失败信息"""
        print(f" {self.colored_text('✗', 'red')} {reason}")
        
    def print_domain_summary(self, domain_name, success_count, total_count):
        """打印域名爬取总结"""
        if success_count > 0:
            print(f"\n{self.colored_text(f'✅ [{domain_name}]', 'green')} 爬取完成！"
                  f"成功获取 {self.colored_text(str(success_count), 'bold')}/{total_count} 章")
        else:
            print(f"\n{self.colored_text(f'❌ [{domain_name}]', 'red')} 爬取失败！未获取到任何章节内容")
            
    def print_search_results(self, domain_count):
        """打印搜索结果"""
        print(f"\n{self.colored_text('🔍 搜索完成', 'green')}：在 {self.colored_text(str(domain_count), 'bold')} 个域名中找到结果")
        
    def print_crawl_summary(self, successful_domains):
        """打印爬取总结"""
        print(f"\n{self.colored_text('📊 爬取总结', 'cyan')}")
        print(f"{self.colored_text('─' * 40, 'cyan')}")
        print(f"成功爬取的域名数: {self.colored_text(str(len(successful_domains)), 'bold')}")
        for domain in successful_domains:
            domain_name = domain.replace('https://', '').replace('http://', '').replace('www.', '').replace('.', '_')
            print(f"  {self.colored_text('✓', 'green')} {domain_name}")
            
    def print_comparison_start(self, novel_title):
        """打印比对开始信息"""
        print(f"\n{self.colored_text('🔄 开始内容比对', 'yellow')}: {novel_title}")
        
    def print_merge_start(self, novel_title):
        """打印合并开始信息"""
        print(f"\n{self.colored_text('🔧 开始合成最佳版本', 'blue')}: {novel_title}")
        
    def print_time_info(self, start_time, end_time):
        """打印时间信息"""
        duration = end_time - start_time
        print(f"\n{self.colored_text('⏱️  耗时', 'cyan')}: {duration.total_seconds():.1f} 秒")
        
    def print_title(self, title):
        """打印主标题"""
        print(f"\n{self.colored_text('=' * 60, 'cyan')}")
        print(f"{self.colored_text(title, 'bold')}")
        print(f"{self.colored_text('=' * 60, 'cyan')}")
        
    def print_search_result(self, domain_name, result_count):
        """打印搜索结果"""
        print(f"    ✅ {self.colored_text(domain_name, 'green')} - 找到 {self.colored_text(str(result_count), 'bold')} 个结果")
        
    def print_crawl_summary(self, successful_count):
        """打印爬取总结"""
        print(f"\n{self.colored_text('📊 爬取总结', 'cyan')}")
        print(f"{self.colored_text('─' * 40, 'cyan')}")
        print(f"  成功爬取的域名数: {self.colored_text(str(successful_count), 'bold')}")
        
    def print_compare_start(self):
        """打印比对开始信息"""
        print(f"\n{self.colored_text('🔄 章节比对阶段', 'yellow')}")
        print("─" * 50)
        
    def print_merge_start(self):
        """打印合并开始信息"""
        print(f"\n{self.colored_text('🔧 最佳版本合成阶段', 'blue')}")
        print("─" * 50)
        
    def init_multi_domain_progress(self, domains):
        """初始化多域名进度显示
        
        Args:
            domains (list): 域名列表
        """
        self.progress_data = {}
        self.last_update_time = 0
        self.progress_lock = threading.Lock()  # 添加线程锁
        self.display_initialized = False
        
        print(f"\n{self.colored_text('📚 并发爬取进度', 'yellow')}")
        print("─" * 80)
        
        # 初始化进度数据
        for domain in sorted(domains):  # 排序确保顺序一致
            domain_name = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('.')[0]
            self.progress_data[domain] = {
                'name': domain_name,
                'current': 0,
                'total': 0,
                'chapter_title': '准备中...',
                'status': 'waiting'
            }
        
        self.display_initialized = True
        print(f"  初始化完成，开始爬取 {len(domains)} 个域名...\n")
        
    def update_domain_progress(self, domain, current, total, chapter_title, status='running'):
        """更新指定域名的进度
        
        Args:
            domain (str): 域名
            current (int): 当前章节数
            total (int): 总章节数
            chapter_title (str): 当前章节标题
            status (str): 状态 ('running', 'success', 'failed')
        """
        if domain not in self.progress_data:
            return
            
        with self.progress_lock:  # 使用线程锁保护
            # 更新进度数据
            self.progress_data[domain].update({
                'current': current,
                'total': total,
                'chapter_title': chapter_title[:30],  # 限制长度
                'status': status
            })
            
            # 限制更新频率，避免闪烁
            import time
            current_time = time.time()
            
            # 每2秒或者重要状态变化时显示进度
            if (current_time - self.last_update_time > 2.0 or 
                status in ['success', 'failed']):
                self._show_progress_summary()
                self.last_update_time = current_time
        
    def _show_progress_summary(self):
        """显示进度汇总"""
        if not self.display_initialized:
            return
            
        # 统计各状态的域名数量
        status_counts = {'waiting': 0, 'running': 0, 'success': 0, 'failed': 0}
        total_progress = 0
        active_domains = []
        
        for domain, data in self.progress_data.items():
            status_counts[data['status']] += 1
            if data['total'] > 0:
                progress = (data['current'] / data['total']) * 100
                total_progress += progress
                
            if data['status'] == 'running' and data['current'] > 0:
                active_domains.append(f"{data['name']}({data['current']}/{data['total']})")
        
        avg_progress = total_progress / len(self.progress_data) if self.progress_data else 0
        
        # 显示汇总信息
        print(f"\r  📊 进度汇总: 平均 {avg_progress:.1f}% | "
              f"运行中: {self.colored_text(str(status_counts['running']), 'cyan')} | "
              f"完成: {self.colored_text(str(status_counts['success']), 'green')} | "
              f"失败: {self.colored_text(str(status_counts['failed']), 'red')} | "
              f"等待: {status_counts['waiting']}", end='', flush=True)
        
        # 如果有活跃域名，显示详细信息
        if active_domains and len(active_domains) <= 3:
            print(f" | 活跃: {', '.join(active_domains[:3])}", end='', flush=True)
        
    def _format_progress_line(self, data):
        """格式化单行进度显示
        
        Args:
            data (dict): 进度数据
            
        Returns:
            str: 格式化的进度行
        """
        # 计算进度
        if data['total'] > 0:
            percentage = (data['current'] / data['total']) * 100
            filled_length = int(30 * data['current'] // data['total'])
        else:
            percentage = 0
            filled_length = 0
            
        # 生成进度条
        bar = '█' * filled_length + '░' * (30 - filled_length)
        
        # 根据状态选择颜色
        if data['status'] == 'success':
            bar_color = 'green'
            name_color = 'green'
        elif data['status'] == 'failed':
            bar_color = 'red'
            name_color = 'red'
        elif data['status'] == 'running':
            bar_color = 'blue'
            name_color = 'cyan'
        else:  # waiting
            bar_color = 'white'
            name_color = 'white'
        
        # 格式化输出
        domain_name = self.colored_text(f"{data['name']:<12}", name_color)
        progress_bar = self.colored_text(bar, bar_color)
        percentage_text = self.colored_text(f"{percentage:>6.1f}%", 'yellow')
        count_text = f"{data['current']:>3}/{data['total']:<3}"
        chapter_text = data['chapter_title'][:35]  # 限制章节名长度
        
        return f"{domain_name} {progress_bar} {percentage_text} {count_text} {chapter_text}"
    

            
    def finish_domain_progress(self, domain, success_count, total_count):
        """完成域名进度显示
        
        Args:
            domain (str): 域名
            success_count (int): 成功章节数
            total_count (int): 总章节数
        """
        if success_count > 0:
            status_text = f"完成! 成功 {success_count}/{total_count} 章"
            self.update_domain_progress(domain, success_count, total_count, status_text, 'success')
        else:
            status_text = "失败! 未获取到内容"
            self.update_domain_progress(domain, 0, total_count, status_text, 'failed')
            
    def finalize_progress_display(self):
        """完成所有进度显示，移动光标到最后"""
        if self.display_initialized:
            # 显示最终详细结果
            print("\n\n📋 最终结果详情:")
            print("─" * 60)
            
            for domain in sorted(self.progress_data.keys()):
                data = self.progress_data[domain]
                line = self._format_progress_line(data)
                print(f"  {line}")
            
            print()  # 添加一个空行分隔


class NovelCrawler:
    """小说爬虫类"""
    
    def __init__(self, domains_file='all_domains.json', output_dir='novel_output', use_selenium=True, reference_sources=None):
        """初始化爬虫
        
        Args:
            domains_file (str): 域名配置文件路径
            output_dir (str): 输出目录
            use_selenium (bool): 是否使用Selenium
            reference_sources (list): 基准源列表，用于内容合并时的优先级设置
        """
        self.domains_file = domains_file
        self.output_dir = output_dir
        self.domains = self.load_domains()
        self.session = requests.Session()
        self.use_selenium = use_selenium
        self.driver = None
        self.display = CrawlDisplay()  # 添加美化显示器
        
        # 设置基准源优先级（默认值）
        self.reference_sources = reference_sources or ['bqgam', 'biquge', '675m', 'bqg67', 'biqu10']
        
        # 合并策略配置
        self.merge_config = {
            'enable_diff_merge': True,  # 是否启用差分合并
            'length_priority_weight': 0.6,  # 长度优先权重
            'quality_weight': 0.4,  # 质量评估权重
            'min_content_length': 200,  # 最小内容长度
            'merge_threshold': 1.1,  # 合并阈值（合并后内容增长比例）
            'similarity_threshold': 0.8  # 相似度阈值
        }
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        if use_selenium:
            self._init_selenium()
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def configure_merge_strategy(self, **kwargs):
        """配置合并策略参数
        
        Args:
            **kwargs: 合并策略配置参数
                - reference_sources: 基准源列表
                - enable_diff_merge: 是否启用差分合并
                - length_priority_weight: 长度优先权重
                - quality_weight: 质量评估权重
                - min_content_length: 最小内容长度
                - merge_threshold: 合并阈值
                - similarity_threshold: 相似度阈值
        """
        if 'reference_sources' in kwargs:
            self.reference_sources = kwargs['reference_sources']
            
        for key, value in kwargs.items():
            if key in self.merge_config:
                self.merge_config[key] = value
                
        print(f"合并策略已更新: {kwargs}")
    
    def load_domains(self):
        """加载域名配置文件
        
        Returns:
            list: 域名列表
        """
        try:
            with open(self.domains_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('domains', [])
        except Exception as e:
            print(f"加载域名配置文件失败: {e}")
            return []
    
    def search_novel_single_domain(self, domain, keyword):
        """在单个域名中搜索小说
        
        Args:
            domain (str): 域名
            keyword (str): 搜索关键字
            
        Returns:
            tuple: (域名, 搜索结果列表)
        """
        try:
            # 构建搜索URL
            search_url = f"{domain.rstrip('/')}/s?q={quote(keyword)}"
            print(f"尝试搜索: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 解析搜索结果
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找搜索结果的JavaScript代码
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'loadmore' in script.string:
                    # 尝试获取搜索API
                    api_match = re.search(r'\$.getJSON\("([^"]+)"', script.string)
                    if api_match:
                        api_url = api_match.group(1)
                        if not api_url.startswith('http'):
                            api_url = urljoin(domain, api_url)
                        
                        # 确保API URL包含搜索关键字
                        if '?q=' in api_url and not api_url.endswith('?q='):
                            # API URL已经包含完整的查询参数
                            pass
                        elif '?q=' in api_url and api_url.endswith('?q='):
                            # API URL缺少查询关键字，添加关键字
                            api_url += quote(keyword)
                        else:
                            # API URL不包含查询参数，添加完整的查询参数
                            separator = '&' if '?' in api_url else '?'
                            api_url += f"{separator}q={quote(keyword)}"
                        
                        # 先调用hm.html API（根据网站的搜索逻辑）
                        hm_url = urljoin(domain, f"/user/hm.html?q={quote(keyword)}")
                        try:
                            hm_response = self.session.get(hm_url, timeout=10)
                        except:
                            pass  # hm.html可能不存在，继续执行
                        
                        # 调用搜索API
                        api_response = self.session.get(api_url, timeout=10)
                        if api_response.status_code == 200:
                            try:
                                search_results = api_response.json()
                                if search_results and isinstance(search_results, list) and len(search_results) > 0:
                                    print(f"在 {domain} 找到 {len(search_results)} 个结果")
                                    return domain, search_results
                            except json.JSONDecodeError:
                                continue
            
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            print(f"搜索 {domain} 失败: {e}")
        
        return domain, []
    
    def search_novel_all_domains(self, keyword, max_workers=3):
        """在所有域名中并行搜索小说
        
        Args:
            keyword (str): 搜索关键字
            max_workers (int): 最大并发数
            
        Returns:
            dict: {域名: 搜索结果列表}
        """
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有搜索任务
            future_to_domain = {
                executor.submit(self.search_novel_single_domain, domain, keyword): domain 
                for domain in self.domains
            }
            
            # 收集结果
            for future in as_completed(future_to_domain):
                domain, search_results = future.result()
                domain_name = self.get_domain_name(domain)
                if search_results:
                    results[domain] = search_results
                    self.display.print_search_result(domain_name, len(search_results))
                else:
                    print(f"    ❌ {domain_name} - 未找到结果")
        
        return results
    
    def get_chapter_list(self, domain, book_url):
        """获取章节列表
        
        Args:
            domain (str): 域名
            book_url (str): 小说详情页URL
            
        Returns:
            list: 章节链接列表
        """
        try:
            # 构建完整URL
            if not book_url.startswith('http'):
                full_url = urljoin(domain, book_url)
            else:
                full_url = book_url
            
            print(f"获取章节列表: {full_url}")
            
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找章节列表 - 支持多种链接模式
            chapters = []
            # 尝试多种章节链接模式
            patterns = [
                r'/index/\d+/\d+\.html',  # bqgam.com 模式
                r'/book/\d+/\d+\.html',   # 675m.com 模式
                r'/\d+/\d+\.html',        # 通用模式
            ]
            
            for pattern in patterns:
                chapter_links = soup.find_all('a', href=re.compile(pattern))
                if chapter_links:
                    break
            
            for link in chapter_links:
                href = link.get('href')
                title = link.get_text().strip()
                if href and title:
                    chapters.append({
                        'title': title,
                        'url': href
                    })
            
            print(f"找到 {len(chapters)} 个章节")
            return chapters
            
        except Exception as e:
            print(f"获取章节列表失败: {e}")
            return []
    
    def get_chapter_content(self, domain, chapter_url, thread_driver=None):
        """获取章节内容
        
        Args:
            domain (str): 域名
            chapter_url (str): 章节URL
            thread_driver (webdriver.Chrome, optional): 线程专用的WebDriver实例
            
        Returns:
            tuple: (章节标题, 章节内容)
        """
        try:
            # 构建完整URL
            if not chapter_url.startswith('http'):
                full_chapter_url = urljoin(domain, chapter_url)
            else:
                full_chapter_url = chapter_url
            
            # 方法1: 尝试geturl API
            try:
                geturl_api = f"{domain.rstrip('/')}/user/geturl.html?url={full_chapter_url}"
                response = self.session.get(geturl_api, timeout=10, allow_redirects=False)
                
                if response.status_code in [301, 302]:
                    real_url = response.headers.get('Location')
                    if real_url:
                        content_response = self.session.get(real_url, timeout=10)
                        if content_response.status_code == 200:
                            title, content = self._extract_content_from_html(content_response.text)
                            if title and content and len(content) > 50:  # 确保内容不是"加载中"
                                return title, content
            except:
                pass
            
            # 方法2: 使用Selenium（如果启用）
            if self.use_selenium:
                # 优先使用线程专用的WebDriver
                if thread_driver:
                    title, content = self.get_chapter_content_selenium(domain, chapter_url, thread_driver)
                    if title and content:
                        return title, content
                else:
                    # 检查WebDriver状态，如果不存在则重新初始化
                    if not self.driver:
                        self._init_selenium()
                    
                    if self.driver:
                        title, content = self.get_chapter_content_selenium(domain, chapter_url)
                        if title and content:
                            return title, content
            
            # 方法3: 直接访问章节页面
            try:
                direct_response = self.session.get(full_chapter_url, timeout=10)
                if direct_response.status_code == 200:
                    title, content = self._extract_content_from_html(direct_response.text)
                    if title and content and len(content) > 50:
                        return title, content
            except:
                pass
            
            # 方法4: 尝试其他可能的API端点
            try:
                # 有些网站使用不同的API
                alt_apis = [
                    f"{domain.rstrip('/')}/user/book_read.html?bid={chapter_url.split('/')[-2]}&cid={chapter_url.split('/')[-1].replace('.html', '')}",
                    f"{domain.rstrip('/')}/read{chapter_url}",
                    f"{domain.rstrip('/')}/chapter{chapter_url}"
                ]
                
                for api_url in alt_apis:
                    try:
                        api_response = self.session.get(api_url, timeout=10)
                        if api_response.status_code == 200:
                            title, content = self._extract_content_from_html(api_response.text)
                            if title and content and len(content) > 50:
                                return title, content
                    except:
                        continue
            except:
                pass
            
            return None, None
            
        except Exception as e:
            print(f"获取章节内容失败: {e}")
            return None, None
    
    def _init_selenium(self):
        """初始化Selenium WebDriver"""
        try:
            # 如果已有driver，先关闭
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 使用webdriver-manager自动管理驱动程序
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Selenium WebDriver 初始化成功")
            return True
        except Exception as e:
            print(f"Selenium WebDriver 初始化失败: {e}")
            self.driver = None
            return False
    
    def _create_thread_driver(self):
        """为当前线程创建独立的WebDriver实例
        
        Returns:
            webdriver.Chrome: Chrome WebDriver实例，失败返回None
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 使用webdriver-manager自动管理驱动程序
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"创建线程WebDriver失败: {e}")
            return None
    
    def get_chapter_content_selenium(self, domain, chapter_url, thread_driver=None):
        """使用Selenium获取章节内容
        
        Args:
            domain (str): 域名
            chapter_url (str): 章节URL
            thread_driver (webdriver.Chrome, optional): 线程专用的WebDriver实例
            
        Returns:
            tuple: (章节标题, 章节内容)
        """
        # 使用传入的线程driver或者实例的driver
        driver = thread_driver if thread_driver else self.driver
        if not driver:
            return None, None
            
        try:
            # 构建完整URL
            if not chapter_url.startswith('http'):
                full_chapter_url = urljoin(domain, chapter_url)
            else:
                full_chapter_url = chapter_url
            
            # 访问页面
            driver.get(full_chapter_url)
            
            # 等待页面加载
            time.sleep(2)  # 减少等待时间以提高并发效率
            
            # 等待内容加载完成
            try:
                WebDriverWait(driver, 8).until(
                    lambda d: d.title != "加载中……" and len(d.page_source) > 2000
                )
            except TimeoutException:
                pass  # 继续处理，不打印错误信息避免并发时输出混乱
            
            # 获取页面源码
            page_source = driver.page_source
            
            # 提取标题和内容
            title, content = self._extract_content_from_html(page_source)
            
            if title and content and len(content) > 50:
                return title, content
            
            return None, None
            
        except Exception as e:
            # 在并发模式下减少错误输出
            return None, None
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("WebDriver已关闭")
            except Exception as e:
                print(f"关闭WebDriver时出错: {e}")
    
    def __del__(self):
        """清理资源"""
        self.cleanup()
    
    def _extract_content_from_html(self, html_text):
        """
        从HTML中提取章节标题和内容
        
        Args:
            html_text (str): HTML文本
            
        Returns:
            tuple: (标题, 内容)
        """
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            
            # 检查是否是"加载中"页面
            if "加载中" in html_text or len(html_text) < 2000:
                return None, None
            
            # 提取标题 - 尝试多种选择器
            title = None
            title_selectors = [
                'h1.wap_none',
                'h1',
                '.title',
                '.chapter-title',
                '.book-title',
                'h2',
                'h3'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text().strip()
                    if title_text and title_text != "加载中……" and len(title_text) > 2:
                        title = title_text
                        break
            
            # 提取内容 - 尝试多种选择器
            content = None
            content_selectors = [
                '#chaptercontent',
                '.content',
                '.chapter-content',
                '.text-content',
                '#content',
                '.txt',
                '.book-content',
                '.read-content',
                'div[class*="content"]',
                'div[id*="content"]'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text().strip()
                    if content_text and len(content_text) > 50:  # 确保有实际内容
                        # 清理内容
                        content = re.sub(r'\n\s*\n', '\n\n', content_text)
                        break
            
            # 如果没有找到专门的内容区域，尝试从body中提取
            if not content:
                body = soup.find('body')
                if body:
                    # 移除脚本和样式标签
                    for script in body(["script", "style"]):
                        script.decompose()
                    
                    body_text = body.get_text().strip()
                    if len(body_text) > 200:
                        content = re.sub(r'\n\s*\n', '\n\n', body_text)
            
            return title or "未知章节", content
            
        except Exception as e:
            print(f"解析HTML失败: {e}")
            return None, None
    
    def get_domain_name(self, domain):
        """从域名URL中提取域名名称
        
        Args:
            domain (str): 完整域名URL
            
        Returns:
            str: 域名名称
        """
        parsed = urlparse(domain)
        return parsed.netloc.replace('www.', '').replace('.', '_')
    
    def save_novel_by_domain(self, novel_title, domain, chapters_data):
        """按域名保存小说到不同文件夹
        
        Args:
            novel_title (str): 小说名称
            domain (str): 域名
            chapters_data (list): 章节数据列表
        """
        domain_name = self.get_domain_name(domain)
        # 清理文件名中的非法字符
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
        domain_dir = os.path.join(self.output_dir, safe_title, domain_name)
        
        # 创建域名目录
        if not os.path.exists(domain_dir):
            os.makedirs(domain_dir)
        
        filename = os.path.join(domain_dir, f"{safe_title}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for chapter_title, chapter_content in chapters_data:
                    if chapter_title and chapter_content:
                        f.write(f"{chapter_title}\n")
                        f.write("=" * 50 + "\n")
                        f.write(f"{chapter_content}\n\n")
            
            print(f"小说已保存到: {filename}")
            
            # 同时保存章节数据为JSON格式，便于后续比对
            json_filename = os.path.join(domain_dir, f"{safe_title}_chapters.json")
            chapters_json = []
            for chapter_title, chapter_content in chapters_data:
                if chapter_title and chapter_content:
                    chapters_json.append({
                        'title': chapter_title,
                        'content': chapter_content,
                        'content_hash': hashlib.md5(chapter_content.encode('utf-8')).hexdigest()
                    })
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(chapters_json, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def calculate_similarity(self, text1, text2):
        """计算两个文本的相似度
        
        Args:
            text1 (str): 文本1
            text2 (str): 文本2
            
        Returns:
            float: 相似度 (0-1)
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def compare_chapters(self, novel_title):
        """比对不同域名的章节内容
        
        Args:
            novel_title (str): 小说名称
        """
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', novel_title)
        novel_dir = os.path.join(self.output_dir, safe_title)
        if not os.path.exists(novel_dir):
            print(f"未找到小说目录: {novel_dir}")
            return
        
        # 收集所有域名的章节数据
        domain_chapters = {}
        for domain_name in os.listdir(novel_dir):
            domain_path = os.path.join(novel_dir, domain_name)
            if os.path.isdir(domain_path):
                json_file = os.path.join(domain_path, f"{safe_title}_chapters.json")
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            chapters = json.load(f)
                            domain_chapters[domain_name] = chapters
                    except Exception as e:
                        print(f"读取 {json_file} 失败: {e}")
        
        if len(domain_chapters) < 2:
            print("需要至少两个域名的数据才能进行比对")
            return
        
        # 生成比对报告
        comparison_report = {
            'novel_title': novel_title,
            'domains': list(domain_chapters.keys()),
            'comparison_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'chapter_comparison': []
        }
        
        # 按章节标题分组
        chapters_by_title = defaultdict(dict)
        for domain_name, chapters in domain_chapters.items():
            for chapter in chapters:
                title = chapter['title']
                chapters_by_title[title][domain_name] = chapter
        
        # 比对每个章节
        for title, domain_data in chapters_by_title.items():
            if len(domain_data) < 2:
                continue  # 跳过只有一个域名的章节
            
            chapter_report = {
                'title': title,
                'domains_count': len(domain_data),
                'similarities': [],
                'content_hashes': {}
            }
            
            # 计算内容哈希
            for domain_name, chapter_data in domain_data.items():
                chapter_report['content_hashes'][domain_name] = chapter_data['content_hash']
            
            # 计算相似度
            domain_names = list(domain_data.keys())
            for i in range(len(domain_names)):
                for j in range(i + 1, len(domain_names)):
                    domain1, domain2 = domain_names[i], domain_names[j]
                    content1 = domain_data[domain1]['content']
                    content2 = domain_data[domain2]['content']
                    
                    similarity = self.calculate_similarity(content1, content2)
                    chapter_report['similarities'].append({
                        'domain1': domain1,
                        'domain2': domain2,
                        'similarity': similarity
                    })
            
            comparison_report['chapter_comparison'].append(chapter_report)
        
        # 保存比对报告
        report_file = os.path.join(novel_dir, 'comparison_report.json')
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(comparison_report, f, ensure_ascii=False, indent=2)
            print(f"比对报告已保存到: {report_file}")
            
            # 生成简要摘要
            self.generate_comparison_summary(comparison_report, novel_dir)
            
        except Exception as e:
            print(f"保存比对报告失败: {e}")
    
    def generate_comparison_summary(self, comparison_report, output_dir):
        """生成比对摘要
        
        Args:
            comparison_report (dict): 比对报告
            output_dir (str): 输出目录
        """
        summary_file = os.path.join(output_dir, 'comparison_summary.txt')
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"章节内容比对摘要\n")
                f.write(f"小说名称: {comparison_report['novel_title']}\n")
                f.write(f"比对时间: {comparison_report['comparison_time']}\n")
                f.write(f"参与比对的域名: {', '.join(comparison_report['domains'])}\n")
                f.write("=" * 60 + "\n\n")
                
                total_chapters = len(comparison_report['chapter_comparison'])
                high_similarity_count = 0
                low_similarity_count = 0
                
                for chapter in comparison_report['chapter_comparison']:
                    f.write(f"章节: {chapter['title']}\n")
                    f.write(f"域名数量: {chapter['domains_count']}\n")
                    
                    avg_similarity = 0
                    if chapter['similarities']:
                        similarities = [s['similarity'] for s in chapter['similarities']]
                        avg_similarity = sum(similarities) / len(similarities)
                        
                        if avg_similarity >= 0.8:
                            high_similarity_count += 1
                            f.write(f"平均相似度: {avg_similarity:.3f} (高)\n")
                        elif avg_similarity >= 0.5:
                            f.write(f"平均相似度: {avg_similarity:.3f} (中)\n")
                        else:
                            low_similarity_count += 1
                            f.write(f"平均相似度: {avg_similarity:.3f} (低)\n")
                        
                        for sim in chapter['similarities']:
                            f.write(f"  {sim['domain1']} vs {sim['domain2']}: {sim['similarity']:.3f}\n")
                    
                    f.write("\n")
                
                f.write("=" * 60 + "\n")
                f.write(f"总章节数: {total_chapters}\n")
                f.write(f"高相似度章节 (>=0.8): {high_similarity_count}\n")
                f.write(f"低相似度章节 (<0.5): {low_similarity_count}\n")
                
            print(f"比对摘要已保存到: {summary_file}")
            
        except Exception as e:
            print(f"生成比对摘要失败: {e}")
    
    def crawl_novel_single_domain_with_selenium(self, keyword, domain, search_results, max_chapters=None, use_multi_progress=False):
        """使用Selenium爬取单个域名的小说（支持并行）
        
        Args:
            keyword (str): 搜索关键字
            domain (str): 域名
            search_results (list): 搜索结果列表
            max_chapters (int, optional): 最大章节数限制
            use_multi_progress (bool): 是否使用多域名进度显示
            
        Returns:
            tuple: (是否成功, 小说标题)
        """
        domain_name = self.get_domain_name(domain)
        thread_driver = None
        
        try:
            # 为当前线程创建独立的WebDriver
            thread_driver = self._create_thread_driver()
            if not thread_driver:
                if use_multi_progress:
                    self.display.update_domain_progress(domain, 0, 0, "WebDriver创建失败", 'failed')
                return False, None
            
            # 选择第一个搜索结果
            first_result = search_results[0]
            book_url = first_result.get('url_list')
            book_title = first_result.get('articlename', keyword)
            
            # 如果不使用多域名进度显示，则使用原有的显示方式
            if not use_multi_progress:
                self.display.print_domain_start(domain_name, book_title)
            
            # 获取章节列表
            chapters = self.get_chapter_list(domain, book_url)
            if not chapters:
                if use_multi_progress:
                    self.display.finish_domain_progress(domain, 0, 0)
                else:
                    self.display.print_domain_summary(domain_name, 0, 0)
                return False, None
            
            # 限制章节数量
            if max_chapters and len(chapters) > max_chapters:
                chapters = chapters[:max_chapters]
                if not use_multi_progress:
                    print(f"  📊 限制爬取前 {max_chapters} 章（共 {len(chapters)} 章可用）")
            
            # 初始化进度（如果使用多域名进度显示）
            if use_multi_progress:
                self.display.update_domain_progress(domain, 0, len(chapters), "开始爬取...", 'running')
            
            # 爬取章节内容
            chapters_data = []
            for i, chapter in enumerate(chapters, 1):
                if use_multi_progress:
                    # 更新多域名进度显示
                    self.display.update_domain_progress(domain, i, len(chapters), chapter['title'], 'running')
                else:
                    # 使用原有的进度显示
                    self.display.print_progress(i, len(chapters), chapter['title'], domain_name)
                
                # 使用线程专用的WebDriver
                title, content = self.get_chapter_content(domain, chapter['url'], thread_driver)
                
                # 根据结果处理
                if title and content and len(content) > 50:
                    chapters_data.append((title, content))
                    if not use_multi_progress:
                        self.display.print_chapter_success(domain_name, len(content))
                else:
                    if not use_multi_progress:
                        reason = "内容为空" if not content else f"内容过短({len(content) if content else 0}字)"
                        self.display.print_chapter_failed(domain_name, reason)
                
                # 添加延时，避免请求过快
                time.sleep(0.5)  # 减少延时以提高并发效率
            
            # 完成进度显示
            if use_multi_progress:
                self.display.finish_domain_progress(domain, len(chapters_data), len(chapters))
            
            # 保存到文件
            if chapters_data:
                self.save_novel_by_domain(book_title, domain, chapters_data)
                if not use_multi_progress:
                    self.display.print_domain_summary(domain_name, len(chapters_data), len(chapters))
                return True, book_title
            else:
                if not use_multi_progress:
                    self.display.print_domain_summary(domain_name, 0, len(chapters))
                return False, None
                
        except Exception as e:
            if use_multi_progress:
                self.display.update_domain_progress(domain, 0, 0, f"错误: {str(e)[:20]}", 'failed')
            else:
                print(f"\n{self.display.colored_text(f'❌ [{domain_name}]', 'red')} 爬取异常: {e}")
            return False, None
        finally:
            # 确保关闭线程专用的WebDriver
            if thread_driver:
                try:
                    thread_driver.quit()
                except:
                    pass
    
    def crawl_novel_single_domain(self, keyword, domain, search_results, max_chapters=None, use_multi_progress=False):
        """爬取单个域名的小说
        
        Args:
            keyword (str): 搜索关键字
            domain (str): 域名
            search_results (list): 搜索结果列表
            max_chapters (int, optional): 最大章节数限制
            use_multi_progress (bool): 是否使用多域名进度显示
            
        Returns:
            tuple: (是否成功, 小说标题)
        """
        domain_name = self.get_domain_name(domain)
        
        try:
            # 选择第一个搜索结果
            first_result = search_results[0]
            book_url = first_result.get('url_list')
            book_title = first_result.get('articlename', keyword)
            
            # 如果不使用多域名进度显示，则使用原有的显示方式
            if not use_multi_progress:
                self.display.print_domain_start(domain_name, book_title)
            
            # 获取章节列表
            chapters = self.get_chapter_list(domain, book_url)
            if not chapters:
                if use_multi_progress:
                    self.display.finish_domain_progress(domain, 0, 0)
                else:
                    self.display.print_domain_summary(domain_name, 0, 0)
                return False, None
            
            # 限制章节数量
            if max_chapters and len(chapters) > max_chapters:
                chapters = chapters[:max_chapters]
                if not use_multi_progress:
                    print(f"  📊 限制爬取前 {max_chapters} 章（共 {len(chapters)} 章可用）")
            
            # 初始化进度（如果使用多域名进度显示）
            if use_multi_progress:
                self.display.update_domain_progress(domain, 0, len(chapters), "开始爬取...", 'running')
            
            # 爬取章节内容
            chapters_data = []
            for i, chapter in enumerate(chapters, 1):
                if use_multi_progress:
                    # 更新多域名进度显示
                    self.display.update_domain_progress(domain, i, len(chapters), chapter['title'], 'running')
                else:
                    # 使用原有的进度显示
                    self.display.print_progress(i, len(chapters), chapter['title'], domain_name)
                
                title, content = self.get_chapter_content(domain, chapter['url'])
                
                # 根据结果处理
                if title and content and len(content) > 50:
                    chapters_data.append((title, content))
                    if not use_multi_progress:
                        self.display.print_chapter_success(domain_name, len(content))
                else:
                    if not use_multi_progress:
                        reason = "内容为空" if not content else f"内容过短({len(content) if content else 0}字)"
                        self.display.print_chapter_failed(domain_name, reason)
                
                # 添加延时，避免请求过快
                time.sleep(0.8)  # 减少延时以提高并发效率
            
            # 完成进度显示
            if use_multi_progress:
                self.display.finish_domain_progress(domain, len(chapters_data), len(chapters))
            
            # 保存到文件
            if chapters_data:
                self.save_novel_by_domain(book_title, domain, chapters_data)
                if not use_multi_progress:
                    self.display.print_domain_summary(domain_name, len(chapters_data), len(chapters))
                return True, book_title
            else:
                if not use_multi_progress:
                    self.display.print_domain_summary(domain_name, 0, len(chapters))
                return False, None
                
        except Exception as e:
            if use_multi_progress:
                self.display.update_domain_progress(domain, 0, 0, f"错误: {str(e)[:20]}", 'failed')
            else:
                print(f"\n{self.display.colored_text(f'❌ [{domain_name}]', 'red')} 爬取异常: {e}")
            return False, None
    
    def crawl_novel(self, keyword, max_chapters=None, max_workers=2):
        """爬取小说主函数（支持多域名）
        
        Args:
            keyword (str): 搜索关键字
            max_chapters (int, optional): 最大章节数限制
            max_workers (int): 最大并发数
        """
        # 美化显示：开始爬取
        self.display.print_title(f"🔍 开始搜索小说: {keyword}")
        mode = 'Selenium模式' if self.use_selenium else '普通模式'
        print(f"  🔧 使用模式: {self.display.colored_text(mode, 'cyan')}")
        
        # 1. 在所有域名中搜索小说
        print(f"\n{self.display.colored_text('📡 搜索阶段', 'yellow')}")
        print("─" * 50)
        
        all_search_results = self.search_novel_all_domains(keyword)
        if not all_search_results:
            print(f"\n{self.display.colored_text('❌ 搜索失败', 'red')} - 所有域名都未找到相关小说")
            return
        
        print(f"\n{self.display.colored_text('✅ 搜索完成', 'green')} - 在 {len(all_search_results)} 个域名中找到结果")
        
        # 2. 如果使用Selenium，为了避免多线程冲突，改为串行处理
        print(f"\n{self.display.colored_text('📚 爬取阶段', 'yellow')}")
        print("─" * 50)
        
        successful_domains = []
        novel_titles = set()  # 收集所有小说名称
        
        # 并行爬取所有域名的内容，使用多域名进度显示
        print(f"  ⚡ 开始并行爬取（最大并发数: {max_workers}）...")
        
        # 初始化多域名进度显示
        domains_list = list(all_search_results.keys())
        self.display.init_multi_domain_progress(domains_list)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 根据是否使用Selenium选择不同的爬取方法
            if self.use_selenium:
                # 使用支持并行的Selenium方法
                future_to_domain = {
                    executor.submit(self.crawl_novel_single_domain_with_selenium, keyword, domain, search_results, max_chapters, True): domain
                    for domain, search_results in all_search_results.items()
                }
            else:
                # 使用普通的并行方法
                future_to_domain = {
                    executor.submit(self.crawl_novel_single_domain, keyword, domain, search_results, max_chapters, True): domain
                    for domain, search_results in all_search_results.items()
                }
            
            # 收集结果
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    success, novel_title = future.result()
                    if success and novel_title:
                        successful_domains.append(domain)
                        novel_titles.add(novel_title)
                except Exception as e:
                    domain_name = self.get_domain_name(domain)
                    self.display.update_domain_progress(domain, 0, 0, f"异常: {str(e)[:20]}", 'failed')
        
        # 完成进度显示
        self.display.finalize_progress_display()
        
        # 显示爬取总结
        self.display.print_crawl_summary(len(successful_domains))
        if successful_domains:
            for domain in successful_domains:
                print(f"    ✅ {self.display.colored_text(self.get_domain_name(domain), 'green')}")
        
        # 3. 进行章节内容比对
        if len(successful_domains) >= 2 and novel_titles:
            self.display.print_compare_start()
            for novel_title in novel_titles:
                print(f"  📖 比对小说: {self.display.colored_text(novel_title, 'blue')}")
                self.compare_chapters(novel_title)
                
                # 4. 合成最佳版本
                self.display.print_merge_start()
                print(f"  📝 合成小说: {self.display.colored_text(novel_title, 'blue')}")
                self.merge_best_content(novel_title)
        else:
            print(f"\n{self.display.colored_text('ℹ️  提示', 'yellow')} - 只有一个域名成功，无法进行内容比对")
        
        # 5. 清理资源
        self.cleanup()
    
    def merge_best_content(self, novel_title):
        """合成最佳版本的小说内容
        
        Args:
            novel_title (str): 小说标题
        """
        try:
            novel_dir = os.path.join(self.output_dir, novel_title)
            if not os.path.exists(novel_dir):
                print(f"小说目录不存在: {novel_dir}")
                return
            
            # 读取比对报告
            comparison_file = os.path.join(novel_dir, 'comparison_report.json')
            if not os.path.exists(comparison_file):
                print("比对报告不存在，无法合成最佳版本")
                return
            
            with open(comparison_file, 'r', encoding='utf-8') as f:
                comparison_data = json.load(f)
            
            print(f"正在分析 {len(comparison_data)} 个章节的内容质量...")
            
            # 收集所有域名的章节数据
            domain_chapters = {}
            for domain_name in os.listdir(novel_dir):
                domain_path = os.path.join(novel_dir, domain_name)
                if os.path.isdir(domain_path):
                    chapters_file = os.path.join(domain_path, f'{novel_title}_chapters.json')
                    if os.path.exists(chapters_file):
                        with open(chapters_file, 'r', encoding='utf-8') as f:
                            domain_chapters[domain_name] = json.load(f)
            
            if not domain_chapters:
                print("未找到任何域名的章节数据")
                return
            
            print(f"找到 {len(domain_chapters)} 个域名的章节数据")
            
            # 合成最佳内容
            merged_chapters = []
            chapter_stats = {'total': 0, 'merged': 0, 'skipped': 0}
            
            # 获取章节列表（以第一个域名为基准）
            first_domain = list(domain_chapters.keys())[0]
            base_chapters = domain_chapters[first_domain]
            
            for chapter_info in base_chapters:
                chapter_title = chapter_info['title']
                chapter_stats['total'] += 1
                
                # 收集该章节在所有域名中的内容
                chapter_contents = []
                for domain_name, chapters in domain_chapters.items():
                    for ch in chapters:
                        if ch['title'] == chapter_title:
                            chapter_contents.append({
                                'domain': domain_name,
                                'content': ch['content'],
                                'length': len(ch['content'])
                            })
                            break
                
                if not chapter_contents:
                    print(f"跳过章节: {chapter_title} (未找到内容)")
                    chapter_stats['skipped'] += 1
                    continue
                
                # 选择最佳内容（使用高级合并策略）
                best_content = self._select_best_chapter_content(chapter_title, chapter_contents, comparison_data, self.reference_sources)
                
                if best_content:
                    merged_chapters.append({
                        'title': chapter_title,
                        'content': best_content['content'],
                        'source_domain': best_content['domain'],
                        'content_length': best_content['length']
                    })
                    chapter_stats['merged'] += 1
                else:
                    print(f"跳过章节: {chapter_title} (无有效内容)")
                    chapter_stats['skipped'] += 1
            
            # 保存合成版本
            if merged_chapters:
                self._save_merged_novel(novel_title, merged_chapters, chapter_stats)
                print(f"✓ 合成完成！共处理 {chapter_stats['total']} 章，成功合成 {chapter_stats['merged']} 章，跳过 {chapter_stats['skipped']} 章")
            else:
                print("✗ 合成失败，未找到有效章节内容")
                
        except Exception as e:
            print(f"合成最佳版本时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _select_best_chapter_content(self, chapter_title, chapter_contents, comparison_data, reference_sources=None):
        """选择最佳的章节内容 - 使用高级合并策略
        
        Args:
            chapter_title (str): 章节标题
            chapter_contents (list): 各域名的章节内容列表
            comparison_data (dict): 比对数据
            reference_sources (list): 基准源列表，优先选择这些源的内容
            
        Returns:
            dict: 最佳内容信息，包含domain、content、length
        """
        if not chapter_contents:
            return None
        
        # 如果只有一个内容，清理后返回
        if len(chapter_contents) == 1:
            cleaned_content = self._clean_chapter_content(chapter_contents[0]['content'])
            return {
                'domain': chapter_contents[0]['domain'],
                'content': cleaned_content,
                'length': len(cleaned_content)
            }
        
        # 过滤掉明显错误的内容（太短或包含错误信息）
        valid_contents = []
        for content_info in chapter_contents:
            content = content_info['content']
            # 过滤条件：内容长度大于配置的最小长度，不包含常见错误信息
            if (len(content) > self.merge_config['min_content_length'] and 
                '加载中' not in content and 
                '页面不存在' not in content and 
                '章节不存在' not in content and
                '正在加载' not in content):
                valid_contents.append(content_info)
        
        if not valid_contents:
            # 如果没有有效内容，选择最长的并清理
            best = max(chapter_contents, key=lambda x: x['length'])
            cleaned_content = self._clean_chapter_content(best['content'])
            return {
                'domain': best['domain'],
                'content': cleaned_content,
                'length': len(cleaned_content)
            }
        
        # 策略1: 基准源优先
        if reference_sources:
            for ref_source in reference_sources:
                for content_info in valid_contents:
                    if ref_source in content_info['domain'] and content_info['length'] > self.merge_config['min_content_length']:
                        cleaned_content = self._clean_chapter_content(content_info['content'])
                        return {
                            'domain': content_info['domain'],
                            'content': cleaned_content,
                            'length': len(cleaned_content)
                        }
        
        # 策略2: 长度优先 + 质量评估
        best_content = self._select_by_length_and_quality(valid_contents)
        
        # 策略3: 如果有比对数据，优先选择相似度高的域名内容
        if chapter_title in comparison_data:
            chapter_comparison = comparison_data[chapter_title]
            domain_scores = {}
            
            # 计算每个域名的平均相似度得分
            for domain_name in [c['domain'] for c in valid_contents]:
                scores = []
                for comparison in chapter_comparison.get('comparisons', []):
                    if domain_name in comparison['domains']:
                        scores.append(comparison['similarity'])
                
                if scores:
                    domain_scores[domain_name] = sum(scores) / len(scores)
            
            # 如果有相似度数据，选择得分最高且内容较长的
            if domain_scores:
                # 综合考虑相似度和内容长度
                scored_contents = []
                for content_info in valid_contents:
                    domain = content_info['domain']
                    similarity_score = domain_scores.get(domain, 0.5)
                    length_score = min(content_info['length'] / 3000, 1.0)  # 标准化长度得分
                    combined_score = similarity_score * 0.7 + length_score * 0.3
                    scored_contents.append((combined_score, content_info))
                
                # 选择综合得分最高的
                best_content = max(scored_contents, key=lambda x: x[0])[1]
        
        # 策略4: 差分算法合并（如果有多个相似内容且启用了差分合并）
        if len(valid_contents) > 1 and self.merge_config['enable_diff_merge']:
            merged_content = self._merge_with_diff_algorithm(valid_contents, best_content)
            if merged_content and len(merged_content) > len(best_content['content']):
                return {
                    'domain': 'merged',
                    'content': merged_content,
                    'length': len(merged_content)
                }
        
        # 清理选中的最佳内容
        cleaned_content = self._clean_chapter_content(best_content['content'])
        return {
            'domain': best_content['domain'],
            'content': cleaned_content,
            'length': len(cleaned_content)
        }
    
    def _clean_chapter_content(self, content):
        """清理章节内容中的广告信息
        
        Args:
            content (str): 原始章节内容
            
        Returns:
            str: 清理后的章节内容
        """
        import re
        
        if not content:
            return content
        
        # 定义需要清理的广告模式
        ad_patterns = [
            # 收藏本站相关
            r'请收藏本站：[^\n]*',
            r'收藏本站：[^\n]*',
            r'本站地址：[^\n]*',
            r'收藏网址：[^\n]*',
            
            # 笔趣阁手机版相关
            r'笔趣阁手机版：[^\n]*',
            r'手机版：[^\n]*',
            r'手机站：[^\n]*',
            r'移动版：[^\n]*',
            
            # 来源站点信息
            r'来源于[^\n]*站[^\n]*',
            r'本章来自[^\n]*',
            r'转载请注明[^\n]*',
            r'更新最快[^\n]*',
            r'\(来源:.*?\)',  # 清理来源标记
            
            # 点击相关
            r'『点此报错』[^\n]*',
            r'『加入书签』[^\n]*',
            r'『点击报错』[^\n]*',
            r'『点击收藏』[^\n]*',
            r'\[点此报错\][^\n]*',
            r'\[加入书签\][^\n]*',
            
            # 网址链接
            r'https?://[^\s\n]*',
            r'www\.[^\s\n]*',
            r'm\.[^\s\n]*\.(?:com|net|org|cn|cc)[^\s\n]*',
            
            # 威信平台推广相关
            r'威信.*?平台.*?方法.*?',  # 清理威信平台推广
            r'腾讯威博.*?扫描.*?',  # 清理腾讯威博推广
            r'通讯录.*?查找.*?',  # 清理通讯录相关
            r'搜寻.*?验证标记.*?',  # 清理搜寻验证相关
            r'wang--yu----.*?',  # 清理具体威信号
            r'忘语.*?威信.*?',  # 清理作者威信推广
            r'实体签名书.*?',  # 清理签名书推广
            r'神秘大奖.*?',  # 清理奖品推广
            r'\(.*?威信.*?\)',  # 清理括号内威信相关内容
            r'平台下面.*?公众号.*?',  # 清理平台公众号推广
            r'等.*?正文开始上传.*?',  # 清理上传相关推广
            r'\(.*?\)\s*\(',  # 清理连续的括号内容
            r'----.*?',  # 清理破折号后的内容
            
            # 其他广告信息
            r'\(未完待续[^\)]*\)',
            r'未完待续[^\n]*',
            r'最新章节[^\n]*',
            r'更新时间[^\n]*',
            r'字数统计[^\n]*',
            r'阅读提示[^\n]*',
            
            # 特殊字符和编码
            r'&[a-zA-Z]+;',  # HTML实体
            r'\\u[0-9a-fA-F]{4}',  # Unicode编码
            
            # 多余的空行（3个以上连续换行符）
            r'\n{3,}',
        ]
        
        cleaned_content = content
        
        # 逐个应用清理模式
        for pattern in ad_patterns:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
        
        # 清理多余的空白字符
        cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)  # 多个空格/制表符合并为一个空格
        cleaned_content = re.sub(r'\n[ \t]+', '\n', cleaned_content)  # 行首空白字符
        cleaned_content = re.sub(r'[ \t]+\n', '\n', cleaned_content)  # 行尾空白字符
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)  # 多个换行符合并为两个
        
        # 清理开头和结尾的空白字符
        cleaned_content = cleaned_content.strip()
        
        return cleaned_content
    
    def _select_by_length_and_quality(self, valid_contents):
        """基于长度和质量选择最佳内容
        
        Args:
            valid_contents (list): 有效内容列表
            
        Returns:
            dict: 最佳内容信息
        """
        best_content = None
        best_score = -1
        
        for content_info in valid_contents:
            content = content_info['content']
            
            # 计算内容质量分数（基于长度和内容特征）
            length_score = min(len(content) / 2000, 1.0)  # 长度分数，最大1.0
            
            # 简单的质量评估
            quality_score = 0.5  # 基础分数
            if len(content) > 1000:  # 内容较长
                quality_score += 0.3
            if '章' in content or '节' in content:  # 包含章节标识
                quality_score += 0.1
            if content.count('\n') > 5:  # 有合理的段落分布
                quality_score += 0.1
            
            # 使用配置的权重计算总分
            total_score = (length_score * self.merge_config['length_priority_weight'] + 
                          quality_score * self.merge_config['quality_weight'])
            
            if total_score > best_score:
                best_score = total_score
                best_content = content_info
                
        return best_content or valid_contents[0]
    
    def _merge_with_diff_algorithm(self, valid_contents, base_content):
        """使用差分算法合并多个内容版本
        
        Args:
            valid_contents (list): 有效内容列表
            base_content (dict): 基准内容
            
        Returns:
            str: 合并后的内容
        """
        try:
            import difflib
            
            base_text = base_content['content']
            base_lines = base_text.splitlines()
            
            # 收集所有不同版本的行
            all_lines = set(base_lines)
            for content_info in valid_contents:
                if content_info['domain'] != base_content['domain']:
                    lines = content_info['content'].splitlines()
                    all_lines.update(lines)
            
            # 使用最长的内容作为基础，补充缺失的行
            longest_content = max(valid_contents, key=lambda x: x['length'])
            longest_lines = longest_content['content'].splitlines()
            
            # 简单的合并策略：保持最长版本的结构，补充有价值的行
            merged_lines = longest_lines.copy()
            
            # 查找其他版本中可能缺失的重要内容
            for content_info in valid_contents:
                if content_info['domain'] != longest_content['domain']:
                    other_lines = content_info['content'].splitlines()
                    
                    # 查找在最长版本中不存在但在其他版本中存在的有价值行
                    for line in other_lines:
                        line = line.strip()
                        if (len(line) > 10 and  # 行长度足够
                            line not in '\n'.join(merged_lines) and  # 不重复
                            not any(ad in line.lower() for ad in ['广告', '推广', '收藏', '点击']) and  # 不是广告
                            any(char in line for char in '，。！？；：')):
                            # 在适当位置插入这行内容
                            merged_lines.append(line)
            
            merged_text = '\n'.join(merged_lines)
            
            # 如果合并后的内容明显更长且质量更好，返回合并结果
            if len(merged_text) > len(base_text) * self.merge_config['merge_threshold']:
                return self._clean_chapter_content(merged_text)
            
            return None
            
        except Exception as e:
            print(f"差分合并失败: {e}")
            return None
    
    def _save_merged_novel(self, novel_title, merged_chapters, stats):
        """保存合成的小说
        
        Args:
            novel_title (str): 小说标题
            merged_chapters (list): 合成的章节列表
            stats (dict): 统计信息
        """
        try:
            novel_dir = os.path.join(self.output_dir, novel_title)
            
            # 创建合成版本目录
            merged_dir = os.path.join(novel_dir, 'merged_best')
            if not os.path.exists(merged_dir):
                os.makedirs(merged_dir)
            
            # 保存合成的txt文件
            txt_file = os.path.join(merged_dir, f'{novel_title}_merged.txt')
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"小说名称: {novel_title}\n")
                f.write(f"合成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"章节总数: {stats['merged']}\n")
                f.write("=" * 50 + "\n\n")
                
                for i, chapter in enumerate(merged_chapters, 1):
                    f.write(f"第{i}章 {chapter['title']}\n")
                    f.write(f"(来源: {chapter['source_domain']}, 长度: {chapter['content_length']})\n")
                    f.write("-" * 30 + "\n")
                    f.write(chapter['content'])
                    f.write("\n\n")
            
            # 保存合成信息的JSON文件
            json_file = os.path.join(merged_dir, f'{novel_title}_merged_info.json')
            merged_info = {
                'novel_title': novel_title,
                'merge_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': stats,
                'chapters': [{
                    'index': i + 1,
                    'title': chapter['title'],
                    'source_domain': chapter['source_domain'],
                    'content_length': chapter['content_length']
                } for i, chapter in enumerate(merged_chapters)]
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(merged_info, f, ensure_ascii=False, indent=2)
            
            print(f"合成版本已保存到: {merged_dir}")
            print(f"  - 文本文件: {txt_file}")
            print(f"  - 信息文件: {json_file}")
            
        except Exception as e:
            print(f"保存合成版本时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小说爬虫脚本（支持多域名并行爬取和内容比对）')
    parser.add_argument('keyword', help='搜索关键字')
    parser.add_argument('--max-chapters', type=int, help='最大章节数限制')
    parser.add_argument('--domains-file', default='all_domains.json', help='域名配置文件路径')
    parser.add_argument('--output-dir', default='novel_output', help='输出目录')
    parser.add_argument('--max-workers', type=int, default=2, help='最大并发数')
    parser.add_argument('--compare-only', action='store_true', help='仅进行内容比对（不爬取新内容）')
    parser.add_argument('--use-selenium', action='store_true', help='使用Selenium处理JavaScript')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = NovelCrawler(args.domains_file, args.output_dir, args.use_selenium)
    
    if args.compare_only:
        # 仅进行内容比对
        print(f"开始比对小说内容...")
        # 查找输出目录中的所有小说
        if os.path.exists(args.output_dir):
            for novel_name in os.listdir(args.output_dir):
                novel_path = os.path.join(args.output_dir, novel_name)
                if os.path.isdir(novel_path):
                    print(f"比对小说: {novel_name}")
                    crawler.compare_chapters(novel_name)
        else:
            print(f"输出目录不存在: {args.output_dir}")
    else:
        # 开始爬取
        crawler.crawl_novel(args.keyword, args.max_chapters, args.max_workers)

if __name__ == '__main__':
    main()