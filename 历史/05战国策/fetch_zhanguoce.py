"""
战国策白话文翻译批量抓取脚本
从国学梦网站抓取所有篇目的白话文翻译，按国家组织为md文件
"""

import urllib.request
import urllib.error
import re
import time
import json
import os
import sys

BASE_URL = "https://www.guoxuemeng.com"
OUTPUT_DIR = r"D:\01_MyCode\chinese_classic2modern\诸子百家\战国策"

# 各国家/地区的篇目URL列表
COUNTRIES = {
    "东周": {
        "url_range": range(5518, 5546),
        "prefix": "东周"
    },
    "西周": {
        "url_range": range(5546, 5563),
        "prefix": "西周"
    },
    "秦": {
        "url_range": range(5563, 5627),
        "prefix": "秦"
    },
    "齐": {
        "url_range": range(5627, 5686),
        "prefix": "齐"
    },
    "楚": {
        "url_range": range(5686, 5738),
        "prefix": "楚"
    },
    "赵": {
        "url_range": range(5738, 5804),
        "prefix": "赵"
    },
    "魏": {
        "url_range": range(5804, 5888),
        "prefix": "魏"
    },
    "韩": {
        "url_range": range(5888, 5958),
        "prefix": "韩"
    },
    "燕": {
        "url_range": range(5958, 5990),
        "prefix": "燕"
    },
    "宋卫": {
        "url_range": range(5990, 6005),
        "prefix": "宋卫"
    },
    "中山": {
        "url_range": range(6005, 6015),
        "prefix": "中山"
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def fetch_page(url, retries=3):
    """抓取页面内容，失败重试"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                return html
        except Exception as e:
            print(f"  [重试 {attempt+1}/{retries}] {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return None


def extract_translation(html):
    """从HTML中提取白话文翻译内容 - 基于真实HTML结构"""
    if not html:
        return None, None

    # 提取页面标题 (h1标签)
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = ""
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        title = re.sub(r'原文解释翻译.*$', '', title).strip()
        title = re.sub(r'-战国策.*$', '', title).strip()

    # 核心逻辑：找到 <div class="thot">解释翻译</div> 的位置
    # 这是翻译部分的开始标记
    marker = '<div class="thot">解释翻译</div>'
    start_idx = html.find(marker)

    if start_idx == -1:
        # 备用：尝试找其他格式
        alt_patterns = [
            '>解释翻译</div>',
            '>解释翻译</h2>',
            '>解释翻译</h3>',
            '解释翻译',
        ]
        for pat in alt_patterns:
            start_idx = html.find(pat)
            if start_idx != -1:
                break

    if start_idx == -1:
        return title, None

    # 找到翻译内容结束的位置
    # 翻译内容后面是"相关阅读"部分：<div class="laallb">
    end_markers = [
        '<div class="laallb">',
        '<div class="contextdhall',
        'class="footer"',
        'id="comments"',
        '<div class="laall"',
    ]

    end_pos = len(html)
    for em in end_markers:
        idx = html.find(em, start_idx)
        if idx != -1 and idx < end_pos:
            end_pos = idx

    # 提取翻译部分的HTML（从标记到结束标记之间）
    translation_html = html[start_idx:end_pos]

    # 先尝试提取 <p> 标签内容
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', translation_html, re.DOTALL)

    if paragraphs:
        cleaned = []
        for p in paragraphs:
            text = clean_html(p).strip()
            if text and len(text) > 8:
                if '上一篇' in text or '下一篇' in text:
                    continue
                if '相关阅读' in text or '你可能喜欢' in text:
                    continue
                cleaned.append(text)
        if cleaned:
            translation = "\n\n".join(cleaned)
        else:
            translation = None
    else:
        # 如果没有 <p> 标签，翻译内容可能是直接以纯文本形式存在
        # 找到解释翻译标记之后的文本，直到结束标记
        # 跳过 <span>[挑错/完善]</span></div> 这些标记
        after_marker = html[start_idx:]
        # 找到最后一个 </div>（即解释翻译标题的div）之后的内容
        skip_divs = 0
        content_start = 0
        i = 0
        while i < min(len(after_marker), 300):
            if after_marker[i:i+6] == '</div>':
                skip_divs += 1
                if skip_divs >= 1:
                    content_start = i + 6
                    break
            i += 1

        if content_start == 0:
            content_start = after_marker.find('</div>')
            if content_start != -1:
                content_start += 6

        if content_start > 0 and content_start < len(after_marker):
            raw_text = after_marker[content_start:]
            # 清理到结束标记
            for em in end_markers:
                idx = raw_text.find(em)
                if idx != -1:
                    raw_text = raw_text[:idx]
                    break
            # 清理HTML标签
            text = clean_html(raw_text).strip()
            if text and len(text) > 8:
                translation = text
            else:
                translation = None
        else:
            translation = None

    return title, translation


def clean_html(text):
    """清理HTML标签和特殊字符"""
    # 移除script和style标签
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 解码HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#039;', "'")
    text = text.replace('&ldquo;', '\u201c')
    text = text.replace('&rdquo;', '\u201d')
    text = text.replace('&mdash;', '\u2014')
    text = text.replace('&hellip;', '\u2026')
    # 清理多余空白
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


def process_country(country_name, config):
    """处理一个国家的所有篇目"""
    print(f"\n{'='*60}")
    print(f"正在处理: {country_name}")
    print(f"{'='*60}")

    articles = []
    success_count = 0
    fail_count = 0

    for article_id in config["url_range"]:
        url = f"{BASE_URL}/guoxue/{article_id}.html"
        sys.stdout.write(f"\r  [{country_name}] 抓取 {article_id}... ")
        sys.stdout.flush()

        html = fetch_page(url)
        if not html:
            print(f"\n  [失败] {url}")
            fail_count += 1
            continue

        title, translation = extract_translation(html)

        if translation:
            # 用抓取到的标题或用默认标题
            if not title:
                title = f"{config['prefix']}·第{article_id - config['url_range'].start + 1}篇"
            articles.append({
                "title": title,
                "translation": translation,
                "url": url
            })
            success_count += 1
        else:
            print(f"\n  [无翻译] {url}")
            fail_count += 1

        # 请求间隔，避免被封
        time.sleep(0.5)

    print(f"\n  {country_name} 完成: 成功 {success_count}, 失败 {fail_count}")
    return articles, success_count, fail_count


def save_to_md(country_name, articles, output_dir):
    """保存为Markdown文件"""
    if not articles:
        print(f"  [跳过] {country_name} 无有效内容")
        return

    filepath = os.path.join(output_dir, f"{country_name}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 《战国策·{country_name}》白话文翻译\n\n")

        for i, article in enumerate(articles, 1):
            f.write(f"## {i}. {article['title']}\n\n")
            f.write(f"{article['translation']}\n\n")
            f.write("---\n\n")

    print(f"  [保存] {filepath} ({len(articles)}篇)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_success = 0
    total_fail = 0

    for country_name, config in COUNTRIES.items():
        articles, success, fail = process_country(country_name, config)
        save_to_md(country_name, articles, OUTPUT_DIR)
        total_success += success
        total_fail += fail

    print(f"\n{'='*60}")
    print(f"全部完成! 成功: {total_success}, 失败: {total_fail}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
