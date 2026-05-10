#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取国学梦网站《三国志》白话文翻译
网址: https://www.guoxuemeng.com/guoxue/sanguozhi/
"""

import os
import re
import time
import urllib.request
import urllib.error

# 章节配置：{文件名数字: (书名, 卷名, 编号)}
CHAPTERS = {
    # 魏书 (30卷)
    4199: ("魏书", "武帝纪"),
    4200: ("魏书", "文帝纪"),
    4201: ("魏书", "明帝纪"),
    4202: ("魏书", "少帝纪"),
    4203: ("魏书", "后妃传"),
    4204: ("魏书", "董二袁刘传"),
    4205: ("魏书", "吕布张邈臧洪传"),
    4206: ("魏书", "二公孙陶四张传"),
    4207: ("魏书", "诸夏侯曹传"),
    4208: ("魏书", "荀彧攸贾诩传"),
    4209: ("魏书", "袁张凉国田王邴管传"),
    4210: ("魏书", "崔毛徐何邢鲍司马传"),
    4211: ("魏书", "钟繇华歆王朗传"),
    4212: ("魏书", "程郭董刘蒋刘传"),
    4213: ("魏书", "刘司马梁张温贾传"),
    4214: ("魏书", "任苏杜郑仓传"),
    4215: ("魏书", "张乐于张徐传"),
    4216: ("魏书", "二李臧文吕许典二庞阎传"),
    4217: ("魏书", "任城陈萧王传"),
    4218: ("魏书", "武文世王公传"),
    4219: ("魏书", "王卫二刘傅传"),
    4220: ("魏书", "桓二陈徐卫卢传"),
    4221: ("魏书", "和常杨杜赵裴传"),
    4222: ("魏书", "韩崔高孙王传"),
    4223: ("魏书", "辛毗杨阜高堂隆传"),
    4224: ("魏书", "满田牵郭传"),
    4225: ("魏书", "徐胡二王传"),
    4226: ("魏书", "王毋丘诸葛邓钟传"),
    4227: ("魏书", "方技传"),
    4228: ("魏书", "乌丸鲜卑东夷传"),
    # 蜀书 (15卷)
    4229: ("蜀书", "刘二牧传"),
    4230: ("蜀书", "先主传"),
    4231: ("蜀书", "后主传"),
    4232: ("蜀书", "二主妃子传"),
    4233: ("蜀书", "诸葛亮传"),
    4234: ("蜀书", "关张马黄赵传"),
    4235: ("蜀书", "庞统法正传"),
    4236: ("蜀书", "许麋孙简伊秦传"),
    4237: ("蜀书", "董刘马陈董吕传"),
    4238: ("蜀书", "刘彭廖李刘魏杨传"),
    4239: ("蜀书", "霍王向张杨费传"),
    4240: ("蜀书", "杜周杜许孟来尹李谯郤传"),
    4241: ("蜀书", "黄李吕马王张传"),
    4242: ("蜀书", "蒋琬费祎姜维传"),
    4243: ("蜀书", "邓张宗杨传"),
    # 吴书 (20卷)
    4244: ("吴书", "孙破虏讨逆传"),
    4245: ("吴书", "吴主传"),
    4246: ("吴书", "三嗣主传"),
    4247: ("吴书", "刘繇太史慈士燮传"),
    4248: ("吴书", "妃嫔传"),
    4249: ("吴书", "宗室传"),
    4250: ("吴书", "张顾诸葛步传"),
    4251: ("吴书", "张严程阚薛传"),
    4252: ("吴书", "周瑜鲁肃吕蒙传"),
    4253: ("吴书", "程黄韩蒋周陈董甘淩徐潘丁传"),
    4254: ("吴书", "朱治朱然吕范朱桓传"),
    4255: ("吴书", "虞陆张骆陆吾朱传"),
    4256: ("吴书", "陆逊传"),
    4257: ("吴书", "吴主五子传"),
    4258: ("吴书", "贺全吕周钟离传"),
    4259: ("吴书", "潘浚陆凯传"),
    4260: ("吴书", "是仪胡综传"),
    4261: ("吴书", "吴范刘惇赵达传"),
    4262: ("吴书", "诸葛滕二孙濮阳传"),
    4263: ("吴书", "王楼贺韦华传"),
}

BASE_URL = "https://www.guoxuemeng.com/guoxue/{}.html"
OUTPUT_DIR = r"D:\01_MyCode\chinese_classic2modern\历史\三国志"


def fetch_page(url, max_retry=3):
    """获取页面内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    for attempt in range(max_retry):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                content = response.read()
                for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
                    try:
                        return content.decode(encoding)
                    except:
                        continue
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            if attempt < max_retry - 1:
                print(f"  重试 ({attempt+1}/{max_retry}): {e}")
                time.sleep(2)
            else:
                print(f"  错误: 无法获取 {url}: {e}")
                return ""
    return ""


def extract_translation(html):
    """从HTML中提取白话文翻译
    
    页面结构:
    <div class="title"><div class="thot">解释翻译</div>...</div>
    后面跟随 <p>翻译段落</p>
    直到遇到 <div class="title"><div class="thot">相关阅读</div> 或类似结束标记
    """
    
    # 找翻译开始位置
    start_marker = '<div class="thot">解释翻译</div>'
    start_pos = html.find(start_marker)
    
    if start_pos == -1:
        # 尝试其他可能的格式
        start_marker = '解释翻译</div>'
        start_pos = html.find(start_marker)
        if start_pos == -1:
            return ""
        start_pos += len(start_marker)
    else:
        start_pos += len(start_marker)
    
    # 找翻译结束位置
    # 可能以"相关阅读"、"用户评论"、或另一个 <div class="title"> 结束
    end_markers = [
        '<div class="title"><div class="thot">相关阅读</div>',
        '<div class="thot">相关阅读</div>',
        '相关阅读</div>',
        '<div class="title"><div class="thot">用户评论</div>',
        '用户评论</div>',
        '<div class="gxfooter">',
        '<div class="layout">',
    ]
    
    end_pos = len(html)
    for marker in end_markers:
        pos = html.find(marker, start_pos)
        if pos != -1 and pos < end_pos:
            end_pos = pos
    
    # 提取翻译区域的HTML
    translation_html = html[start_pos:end_pos]
    
    # 提取所有 <p> 标签中的文本
    paragraphs = []
    
    # 方法1: 直接提取 <p>...</p> 内容
    p_pattern = r'<p>(.*?)</p>'
    p_matches = re.findall(p_pattern, translation_html, re.DOTALL)
    
    for p_content in p_matches:
        # 清理HTML标签
        text = re.sub(r'<[^>]+>', '', p_content)
        # 清理空白
        text = re.sub(r'\s+', ' ', text).strip()
        # 过滤太短或无意义内容
        if text and len(text) > 5:
            # 过滤导航链接文本
            if not any(skip in text for skip in ['查看原文', '返回目录', '上一章', '下一章', '三国志全文']):
                paragraphs.append(text)
    
    if paragraphs:
        return '\n\n'.join(paragraphs)
    
    # 方法2: 如果方法1失败，直接清理整个区域的HTML标签
    text = re.sub(r'<[^>]+>', ' ', translation_html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text if len(text) > 50 else ""


def clean_translation(text):
    """清理翻译文本"""
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除关键词行
    text = re.sub(r'关键词：.*?(?=\n|$)', '', text)
    # 移除来源行
    text = re.sub(r'来源：.*?(?=\n|$)', '', text)
    # 移除广告
    text = re.sub(r'欢迎您.*?访问.*?(?=\n|$)', '', text)
    # 移除注释标记如 [一] [二] 等（保留原文注释可能不必要）
    # text = re.sub(r'\[[\u4e00-\u9fa5\d]+\]', '', text)
    return text.strip()


def scrape_chapter(chapter_id, book, title):
    """抓取单个章节"""
    url = BASE_URL.format(chapter_id)
    print(f"  抓取: {book}·{title}")
    print(f"  URL: {url}")
    
    html = fetch_page(url)
    if not html:
        return None
    
    translation = extract_translation(html)
    if not translation:
        print(f"  ⚠ 警告: 未找到翻译内容")
        # 调试: 输出页面片段
        if '解释翻译' in html:
            pos = html.find('解释翻译')
            print(f"  调试: 找到'解释翻译'在位置 {pos}")
            print(f"  上下文: {html[pos:pos+300]}")
        return None
    
    translation = clean_translation(translation)
    if len(translation) < 30:
        print(f"  ⚠ 警告: 翻译内容过短 ({len(translation)} 字)")
        return None
    
    print(f"  ✓ 成功: {len(translation)} 字")
    return translation


def save_chapter(book, title, translation, index):
    """保存章节到文件"""
    # 创建书名目录
    book_dir = os.path.join(OUTPUT_DIR, book)
    os.makedirs(book_dir, exist_ok=True)
    
    # 文件名: 序号_标题.md
    # 去除标题中的特殊字符
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    filename = f"{index:02d}_{safe_title}.md"
    filepath = os.path.join(book_dir, filename)
    
    content = f"# {book}·{title}\n\n{translation}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath, len(translation)


def generate_summary(results):
    """生成汇总表"""
    summary_path = os.path.join(OUTPUT_DIR, "三国志汇总表.md")
    
    total_chars = 0
    total_files = 0
    
    # 按书名分组
    books = {}
    for result in results:
        if result:
            idx, book, title, filepath, chars = result
            if book not in books:
                books[book] = []
            books[book].append((idx, title, filepath, chars))
    
    content = "# 三国志白话文翻译汇总表\n\n"
    
    for book_name in ["魏书", "蜀书", "吴书"]:
        if book_name not in books:
            continue
        content += f"## {book_name}\n\n"
        content += "| 序号 | 章节名 | 字数 | 文件大小 |\n"
        content += "|------|--------|------|----------|\n"
        
        book_chars = 0
        for idx, title, filepath, chars in books[book_name]:
            size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            size_kb = f"{size/1024:.1f}KB"
            content += f"| {idx:02d} | {title} | {chars} | {size_kb} |\n"
            book_chars += chars
        
        content += f"**{book_name}小计**: {len(books[book_name])} 卷，{book_chars} 字\n\n"
        total_chars += book_chars
        total_files += len(books[book_name])
    
    content += f"\n## 总计\n\n"
    content += f"- 总卷数: {total_files} 卷\n"
    content += f"- 总字数: {total_chars} 字\n"
    content += f"- 魏书: 30 卷\n"
    content += f"- 蜀书: 15 卷\n"
    content += f"- 吴书: 20 卷\n"
    content += f"\n来源: https://www.guoxuemeng.com/guoxue/sanguozhi/\n"
    content += f"\n抓取时间: 2026-05-10\n"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n📊 汇总表已保存: {summary_path}")
    return summary_path


def main():
    """主函数"""
    print("=" * 60)
    print("《三国志》白话文翻译抓取工具")
    print("来源: https://www.guoxuemeng.com/guoxue/sanguozhi/")
    print("=" * 60)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for book in ["魏书", "蜀书", "吴书"]:
        os.makedirs(os.path.join(OUTPUT_DIR, book), exist_ok=True)
    
    results = []
    index = 1
    success = 0
    failed = 0
    
    total = len(CHAPTERS)
    
    for chapter_id, (book, title) in CHAPTERS.items():
        print(f"\n[{index}/{total}] {book}·{title}")
        
        translation = scrape_chapter(chapter_id, book, title)
        if translation:
            filepath, chars = save_chapter(book, title, translation, index)
            results.append((index, book, title, filepath, chars))
            success += 1
        else:
            results.append(None)
            failed += 1
        
        index += 1
        
        # 避免请求过快
        if index <= total:
            time.sleep(0.8)
    
    # 生成汇总表
    generate_summary(results)
    
    print("\n" + "=" * 60)
    print(f"完成! 成功: {success}/{total}, 失败: {failed}/{total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
