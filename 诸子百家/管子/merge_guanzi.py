#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将管子各篇txt合并成24卷md文件
"""

import os

BASE_DIR = r"D:\01_MyCode\chinese_classic2modern\诸子百家\管子"

# 卷目配置：每卷包含的文件名（不含扩展名），按顺序排列
# 亡佚篇目不对应任何文件，直接跳过（文件中不存在）
# 格式：(卷名, [(文件名, 篇名), ...])
JUAN_MAP = [
    ("卷01", [
        ("01_牧民",    "牧民第一"),
        ("02_形势",    "形势第二"),
        ("03_权修",    "权修第三"),
        ("04_立政",    "立政第四"),
        ("05_乘马",    "乘马第五"),
    ]),
    ("卷02", [
        ("06_七法",    "七法第六"),
        ("07_版法",    "版法第七"),
    ]),
    ("卷03", [
        ("08_幼官",    "幼官第八"),
        ("09_幼官图",  "幼官图第九"),
        ("10_五辅",    "五辅第十"),
    ]),
    ("卷04", [
        ("11_宙合",    "宙合第十一"),
        ("12_枢言",    "枢言第十二"),
    ]),
    ("卷05", [
        ("13_八观",    "八观第十三"),
        ("14_法禁",    "法禁第十四"),
        ("15_重令",    "重令第十五"),
    ]),
    ("卷06", [
        ("16_法法",    "法法第十六"),
        ("17_兵法",    "兵法第十七"),
    ]),
    ("卷07", [
        ("18_匡君大匡", "大匡第十八"),
    ]),
    ("卷08", [
        ("19_匡君中匡", "中匡第十九"),
        ("20_匡君小匡", "小匡第二十"),
        # 王言第二十一 已亡佚，无文件
    ]),
    ("卷09", [
        ("21_霸形",    "霸形第二十二"),
        ("22_霸言",    "霸言第二十三"),
        ("23_问",      "问第二十四"),
        # 谋失第二十五 已亡佚，无文件
    ]),
    ("卷10", [
        ("24_戒",      "戒第二十六"),
        ("25_地图",    "地图第二十七"),
        ("26_参患",    "参患第二十八"),
        ("27_制分",    "制分第二十九"),
        ("28_君臣上",  "君臣上第三十"),
    ]),
    ("卷11", [
        ("29_君臣下",  "君臣下第三十一"),
        ("30_小称",    "小称第三十二"),
        ("31_四称",    "四称第三十三"),
        # 正言第三十四 已亡佚，无文件
    ]),
    ("卷12", [
        ("32_侈靡",    "侈靡第三十五"),
    ]),
    ("卷13", [
        ("33_心术上",  "心术上第三十六"),
        ("34_心术下",  "心术下第三十七"),
        ("35_白心",    "白心第三十八"),
    ]),
    ("卷14", [
        ("36_水地",    "水地第三十九"),
        ("37_四时",    "四时第四十"),
        ("38_五行",    "五行第四十一"),
    ]),
    ("卷15", [
        ("39_势",      "势第四十二"),
        ("40_正",      "正第四十三"),
        ("41_九变",    "九变第四十四"),
        ("42_任法",    "任法第四十五"),
        ("43_明法",    "明法第四十六"),
        ("44_正世",    "正世第四十七"),
        ("45_治国",    "治国第四十八"),
    ]),
    ("卷16", [
        ("46_内业",    "内业第四十九"),
        # 封禅第五十 已亡佚，无文件
        ("48_小问",    "小问第五十一"),
    ]),
    ("卷17", [
        ("49_七主七臣", "七臣七主第五十二"),
        ("50_禁藏",    "禁藏第五十三"),
    ]),
    ("卷18", [
        ("51_入国",    "入国第五十四"),
        ("52_九守",    "九守第五十五"),
        ("53_桓公问",  "桓公问第五十六"),
        ("54_度地",    "度地第五十七"),
    ]),
    ("卷19", [
        ("55_地员",    "地员第五十八"),
        ("56_弟子职",  "弟子职第五十九"),
        # 言昭第六十 已亡佚
        # 修身第六十一 已亡佚
        # 问霸第六十二 已亡佚
        # 牧民解第六十三 已亡佚
    ]),
    ("卷20", [
        ("57_形势解",  "形势解第六十四"),
    ]),
    ("卷21", [
        ("58_立政九败解", "立政九败解第六十五"),
        ("59_版法解",  "版法解第六十六"),
        ("60_明法解",  "明法解第六十七"),
        ("61_巨乘马",  "臣乘马第六十八"),
        ("62_乘马数",  "乘马数第六十九"),
        # 问乘马第七十 已亡佚
    ]),
    ("卷22", [
        ("63_事语",    "事语第七十一"),
        ("64_海王",    "海王第七十二"),
        ("65_国蓄",    "国蓄第七十三"),
        ("66_山国轨",  "山国轨第七十四"),
        ("67_山权数",  "山权数第七十五"),
        ("68_山至数",  "山至数第七十六"),
    ]),
    ("卷23", [
        ("69_地数",    "地数第七十七"),
        ("70_揆度",    "揆度第七十八"),
        ("71_国准",    "国准第七十九"),
        ("72_轻重甲",  "轻重甲第八十"),
    ]),
    ("卷24", [
        ("73_轻重乙",  "轻重乙第八十一"),
        # 轻重丙第八十二 已亡佚
        ("74_轻重丁",  "轻重丁第八十三"),
        ("75_轻重戊",  "轻重戊第八十四"),
        ("76_轻重己",  "轻重己第八十五"),
        # 轻重庚第八十六 已亡佚
    ]),
]


def read_file(filepath):
    """读取文件内容，尝试多种编码"""
    for encoding in ["utf-8", "gbk", "utf-8-sig"]:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read().strip()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return ""


def is_valid_content(content):
    """判断内容是否有效（非空、不只是古文标记）"""
    if not content:
        return False
    # 如果只有【古文】标记，视为无白话翻译
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        return False
    return True


def strip_guwen_header(content):
    """
    判断并处理文件内容：
    - 如果包含【古文】标记，说明是纯古文文件，没有白话翻译
      → 去掉【古文】标记行，保留古文内容，并添加"仅有古文"标记
    - 如果不包含【古文】标记，说明是白话翻译，直接返回全文
    """
    if "【古文】" in content:
        # 纯古文文件：去掉【古文】标记行，保留古文内容
        lines = content.splitlines()
        filtered = []
        for line in lines:
            if "【古文】" in line:
                continue  # 跳过【古文】标记行
            filtered.append(line)
        
        guwen_content = "\n".join(filtered).strip()
        if not guwen_content:
            return ""
        
        # 添加标记，说明此篇仅有古文
        marked = "【仅有古文，无白话翻译】\n\n" + guwen_content
        return marked
    
    # 没有【古文】标记，直接返回全文（白话翻译）
    return content


def merge_juan(juan_name, articles):
    """合并一卷的内容"""
    parts = []
    
    for filename, pian_name in articles:
        filepath = os.path.join(BASE_DIR, filename + ".txt")
        
        if not os.path.exists(filepath):
            print(f"  [跳过] {filename}.txt 不存在")
            continue
        
        raw = read_file(filepath)
        
        # 处理内容
        content = strip_guwen_header(raw)
        
        if not is_valid_content(content):
            print(f"  [无内容] {filename} ({pian_name})，跳过")
            continue
        
        parts.append(content)
        
        # 判断是白话翻译还是古文-only
        if content.startswith("【仅有古文，无白话翻译】"):
            print(f"  [古文-only] {filename} ({pian_name}), {len(content)} 字")
        else:
            print(f"  [白话翻译] {filename} ({pian_name}), {len(content)} 字")
    
    return "\n\n".join(parts)


def main():
    stats = []
    
    for juan_name, articles in JUAN_MAP:
        print(f"\n处理 {juan_name}...")
        content = merge_juan(juan_name, articles)
        
        if not content.strip():
            print(f"  [警告] {juan_name} 没有有效内容，跳过创建文件")
            stats.append((juan_name, 0, 0, 0))
            continue
        
        # 统计
        char_count = len(content.replace("\n", "").replace(" ", ""))
        para_count = len([p for p in content.split("\n\n") if p.strip()])
        byte_size = len(content.encode("utf-8"))
        
        # 输出文件
        out_path = os.path.join(BASE_DIR, f"{juan_name}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        
        stats.append((juan_name, char_count, para_count, byte_size))
        print(f"  -> {out_path} ({char_count} 字, {para_count} 段, {byte_size/1024:.1f}KB)")
    
    # 汇总表
    print("\n" + "="*60)
    print("汇总统计")
    print("="*60)
    print(f"{'卷名':<8} {'字数':>8} {'段落数':>8} {'文件大小':>12}")
    print("-"*60)
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
    print("-"*60)
    print(f"{'合计':<8} {total_chars:>8,} {total_paras:>8} {total_bytes/1024:>10.1f}KB")
    
    return stats


if __name__ == "__main__":
    main()
