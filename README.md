# 小说爬虫脚本（多域名版）

一个基于Python的小说爬虫工具，支持多域名并行爬取、章节内容比对校验和合并。能够根据关键字在多个笔趣阁网站中搜索小说，获取章节内容并自动生成最佳版本。

## 本工具仅供个人学习、研究和技术交流使用

## 功能特性

- 🔍 **多域名搜索**: 在多个笔趣阁域名中并行搜索小说
- 📚 **并行爬取**: 同时从多个域名爬取相同小说的章节内容
- 🤖 **自动初始化**: 程序启动时自动初始化爬虫配置，无需手动设置
- 🔄 **智能合并**: 爬取完成后自动合并多域名内容，生成最佳版本
- 📁 **分类存储**: 将不同域名的结果保存到独立文件夹中
- 🔍 **内容比对**: 自动比对相同章节在不同域名的内容差异
- 📊 **质量报告**: 生成详细的相似度分析和比对摘要
- 💾 **多格式保存**: 同时保存txt和JSON格式，便于后续处理
- 🛡️ **错误处理**: 完善的异常处理和重试机制
- ⚙️ **高度可配置**: 支持自定义并发数、输出目录等参数
- 🌐 **Selenium支持**: 集成Selenium WebDriver处理动态内容

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install requests beautifulsoup4 lxml selenium webdriver-manager
```

## 使用方法

### 推荐使用方式：交互式菜单

```bash
# 启动交互式菜单
python interactive_merge_menu.py
```

## 配置文件格式

`all_domains.json` 文件应包含网站的域名列表：

```json
[
    "https://www.biquge.com",
    "https://www.biquge.net",
    "https://www.biquge.org",
    "https://www.biquge.info",
    "https://www.biquge.cc"
]
```

> **注意**: 脚本会并行访问所有域名，建议域名数量控制在5个以内以避免过多并发请求。

## 输出文件结构

脚本会创建以下目录结构：

```
novel_output/                    # 输出根目录
├── 搜索关键字/                   # 按关键字分组
│   ├── domain1_name/            # 第一个域名的结果
│   │   ├── 搜索关键字.txt        # 格式化的小说内容
│   │   └── 搜索关键字_chapters.json  # 章节数据（含哈希）
│   ├── domain2_name/            # 第二个域名的结果
│   │   ├── 搜索关键字.txt
│   │   └── 搜索关键字_chapters.json
│   ├── merged/                  # 智能合并结果（新增）
│   │   ├── 搜索关键字_merged.txt # 合并后的最佳版本
│   │   ├── 搜索关键字_merged_chapters.json # 合并章节数据
│   │   └── merge_report.json    # 合并过程报告
│   ├── comparison_report.json   # 详细比对报告
│   └── comparison_summary.txt   # 比对摘要
```

### TXT文件格式
```
第一章 章节标题
==================================================
章节内容...

第二章 章节标题
==================================================
章节内容...
```

### JSON文件格式
```json
[
  {
    "title": "第一章 章节标题",
    "content": "章节内容...",
    "content_hash": "md5哈希值"
  }
]
```

### 比对报告格式
```json
{
  "keyword": "搜索关键字",
  "domains": ["domain1_name", "domain2_name"],
  "comparison_time": "2024-01-01 12:00:00",
  "chapter_comparison": [
    {
      "title": "第一章 章节标题",
      "domains_count": 2,
      "similarities": [
        {
          "domain1": "domain1_name",
          "domain2": "domain2_name",
          "similarity": 0.95
        }
      ],
      "content_hashes": {
        "domain1_name": "hash1",
        "domain2_name": "hash2"
      }
    }
  ]
}
```

## 注意事项

1. **自动初始化**: 程序首次运行会自动初始化Selenium WebDriver，可能需要几分钟时间
2. **并发控制**: 建议max_workers设置为2-3，避免对服务器造成过大压力
3. **网络环境**: 确保网络连接稳定，部分域名可能需要特定网络环境
4. **文件编码**: 输出文件使用UTF-8编码，确保中文显示正常
5. **域名有效性**: 定期检查域名配置文件中的域名是否仍然有效
6. **存储空间**: 多域名爬取会产生更多文件，注意磁盘空间
7. **内容质量**: 通过相似度比对可以识别内容质量较差的域名
8. **浏览器依赖**: 程序依赖Chrome浏览器，确保系统已安装Chrome
9. **版权声明**: 请遵守相关法律法规，仅用于个人学习研究
10. **免责声明**: 详见文档末尾的免责声明和开源协议

## 智能合并功能说明

### 合并策略
- **内容完整性优先**: 选择章节数量最多的版本作为基础
- **质量优先**: 在相同章节中选择内容最完整、格式最好的版本
- **自动去重**: 基于内容哈希自动识别和处理重复章节
- **智能补全**: 从其他域名补充缺失的章节

### 合并算法
1. **章节对齐**: 基于章节标题和序号进行智能对齐
2. **内容评分**: 根据长度、格式、完整性对章节内容评分
3. **最优选择**: 为每个章节选择评分最高的版本
4. **格式统一**: 统一章节标题格式和内容排版

### 合并报告
- 详细记录每个章节的选择来源
- 统计各域名的贡献度
- 标记处理过程中的异常情况

## 比对功能说明

### 相似度计算
- 使用SequenceMatcher计算文本相似度（0-1范围）
- 0.8以上为高相似度，0.5-0.8为中等，0.5以下为低相似度

### 哈希校验
- 使用MD5哈希快速识别完全相同的内容
- 便于快速筛选和去重

### 比对报告
- 详细的JSON格式报告，包含所有比对数据
- 简要的TXT格式摘要，便于快速查看
- 统计信息包括总章节数、高/低相似度章节数量

## 参数说明

### 交互式菜单选项

- **搜索小说**: 输入关键字在所有域名中搜索
- **爬取小说**: 选择搜索结果进行多域名并行爬取
- **智能合并**: 自动合并已爬取的多域名内容
- **内容比对**: 分析不同域名版本的内容差异
- **查看结果**: 浏览本地已爬取的小说列表
- **系统设置**: 配置输出目录、并发数等参数

### 类初始化参数

- `domains_file`: 域名配置文件路径
- `output_dir`: 输出目录路径

### 爬取方法参数

- `keyword`: 搜索关键字
- `max_chapters`: 最大章节数限制
- `max_workers`: 最大并发数（建议2-3个）

## 快速开始

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **启动程序**:
   ```bash
   python interactive_merge_menu.py
   ```

3. **首次使用**:
   - 程序会自动初始化Selenium WebDriver
   - 选择"搜索小说"输入关键字
   - 选择搜索结果进行爬取
   - 爬取完成后使用"智能合并"获得最佳版本

4. **查看结果**:
    - 在`novel_output/关键字/merged/`目录下找到合并后的最佳版本
    - 使用"查看结果"功能浏览所有已爬取的小说

---

## 免责声明

### 使用限制
本工具仅供个人学习、研究和技术交流使用，严禁用于以下用途：
- 商业用途或盈利活动
- 大规模批量爬取或数据挖掘
- 违反网站服务条款的行为
- 侵犯版权或知识产权的活动
- 任何可能对目标网站造成负担的行为

### 法律责任
- 用户在使用本工具时应遵守所在国家和地区的相关法律法规
- 用户应尊重目标网站的robots.txt文件和服务条款
- 因使用本工具而产生的任何法律纠纷或损失，开发者概不负责
- 用户应自行承担使用本工具的所有风险和责任

### 版权声明
- 本工具爬取的内容版权归原作者和原网站所有
- 用户不得将爬取的内容用于商业用途或二次分发
- 建议用户在使用爬取内容时注明来源
- 如有版权争议，请立即停止使用并删除相关内容

### 技术说明
- 本工具采用合理的访问频率，避免对目标服务器造成过大负担
- 建议用户设置适当的延迟和并发限制
- 如遇到访问限制或封禁，请立即停止使用

## 开源协议

本项目采用 **MIT License** 开源协议，具体条款如下：

```
MIT License

Copyright (c) 2024 Novel Crawler Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 协议要点
- ✅ **自由使用**: 可以自由使用、修改和分发本软件
- ✅ **商业使用**: 允许在商业项目中使用（但爬取内容需遵守版权法）
- ✅ **修改权利**: 可以修改源代码并分发修改版本
- ✅ **分发权利**: 可以分发原版或修改版本
- ⚠️ **保留声明**: 必须在所有副本中保留版权声明和许可声明
- ❌ **无担保**: 软件按"现状"提供，不提供任何明示或暗示的担保

---

**最后提醒**: 请在使用本工具前仔细阅读并理解上述免责声明和开源协议。继续使用本工具即表示您同意遵守所有相关条款。