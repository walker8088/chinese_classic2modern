#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将荀子全集.md按12卷本拆分，输出卷01.md ~ 卷12.md
"""

import re
import os

BASE_DIR = r"D:\01_MyCode\chinese_classic2modern\诸子百家\荀子"
INPUT_FILE = os.path.join(BASE_DIR, "荀子全集.md")

# 卷目配置：每卷包含的篇目（篇名第X格式，与文件中的##标题对应）
JUAN_MAP = [
    ("卷01", [
        "劝学篇第一",
        "修身篇第二",
        "不苟篇第三",
        "荣辱篇第四",
    ]),
    ("卷02", [
        "非相篇第五",
        "非十二子篇第六",
        "仲尼篇第七",
        "儒效篇第八",
    ]),
    ("卷03", [
        "王制篇第九",
        "富国篇第十",
        "王霸篇第十一",
        "君道篇第十二",
    ]),
    ("卷04", [
        "臣道篇第十三",
        "致士篇第十四",
    ]),
    ("卷05", [
        "议兵篇第十五",
        "强国篇第十六",
        "天论篇第十七",
    ]),
    ("卷06", [
        "正论篇第十八",
    ]),
    ("卷07", [
        "礼论篇第十九",
    ]),
    ("卷08", [
        "乐论篇第二十",
    ]),
    ("卷09", [
        "解蔽篇第二十一",
    ]),
    ("卷10", [
        "正名篇第二十二",
    ]),
    ("卷11", [
        "性恶篇第二十三",
        "君子篇第二十四",
    ]),
    ("卷12", [
        "成相篇第二十五",
        "赋篇第二十六",
        "大略篇第二十七",
        "宥坐篇第二十八",
        "子道篇第二十九",
        "法行篇第三十",
        "哀公篇第三十一",
        "尧问篇第三十二",
    ]),
]


def read_file(filepath):
    for encoding in ["utf-8", "utf-8-sig", "gbk"]:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return ""


def split_chapters(content):
    """
    将全文按 ## 篇名第X 标题拆分为各篇章节字典
    返回: { "劝学篇第一": "正文内容", ... }
    """
    # 用 ## 作为章节分割符
    pattern = re.compile(r"^## (.+?)$", re.MULTILINE)
    matches = list(pattern.finditer(content))

    chapters = {}
    for i, match in enumerate(matches):
        pian_name = match.group(1).strip()
        start = match.start()  # 包含 ## 行
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        pian_content = content[start:end].strip()
        chapters[pian_name] = pian_content

    return chapters


def has_real_content(pian_content):
    """
    判断章节是否有实际译文内容（不只是占位符）
    跳过 ## 标题行、--- 分隔符、> 缺：... 占位行
    """
    lines = pian_content.splitlines()
    meaningful = []
    for line in lines[1:]:  # 跳过第一行 ## 标题
        s = line.strip()
        if not s or s == "---" or s.startswith(">"):
            continue
        meaningful.append(s)
    return len("".join(meaningful)) > 30


def merge_juan(juan_name, pian_names, chapters):
    """合并一卷的内容，缺译文的篇目标记【缺译文】"""
    parts = []

    for pian_name in pian_names:
        if pian_name not in chapters:
            print(f"  [警告] {pian_name} 未找到对应内容")
            continue
        pian_content = chapters[pian_name]
        if not has_real_content(pian_content):
            # 缺译文：保留章节标题，加标记
            placeholder = f"## {pian_name}\n\n【缺译文】\n"
            parts.append(placeholder)
            print(f"  [缺译文] {pian_name}，已标记")
            continue
        parts.append(pian_content)
        char_count = len(pian_content)
        print(f"  [合并] {pian_name}, {char_count} 字")

    return "\n\n".join(parts)


def main():
    print(f"读取 {INPUT_FILE} ...")
    content = read_file(INPUT_FILE)
    if not content:
        print("无法读取文件！")
        return

    print(f"文件大小: {len(content)} 字符\n")

    # 拆分章节
    chapters = split_chapters(content)
    print(f"共拆分出 {len(chapters)} 个章节\n")

    stats = []

    for juan_name, pian_names in JUAN_MAP:
        print(f"处理 {juan_name}...")
        juan_content = merge_juan(juan_name, pian_names, chapters)

        # 统计（含【缺译文】标记也计入）
        char_count = len(juan_content.replace("\n", "").replace(" ", ""))
        para_count = max(1, len([p for p in juan_content.split("\n\n") if p.strip()]))
        byte_size = len(juan_content.encode("utf-8"))

        # 输出文件（始终创建）
        out_path = os.path.join(BASE_DIR, f"{juan_name}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(juan_content + "\n")

        stats.append((juan_name, char_count, para_count, byte_size))
        print(f"  -> {out_path} ({char_count} 字, {para_count} 段, {byte_size/1024:.1f}KB)\n")

    # 汇总表
    print("=" * 60)
    print("汇总统计")
    print("=" * 60)
    print(f"{'卷名':<8} {'字数':>8} {'段落数':>8} {'文件大小':>12}")
    print("-" * 60)
    total_chars = 0
    total_paras = 0
    total_bytes = 0
    for juan_name, chars, paras, bsize in stats:
        if chars > 0:
            print(f"{juan_name:<8} {chars:>8,} {paras:>8} {bsize/1024:>10.1f}KB")
            total_chars += chars
            total_paras += paras
            total_bytes += bsize
        else:
            print(f"{juan_name:<8} {'(无内容)':>8}")
    print("-" * 60)
    print(f"{'合计':<8} {total_chars:>8,} {total_paras:>8} {total_bytes/1024:>10.1f}KB")


if __name__ == "__main__":
    main()
