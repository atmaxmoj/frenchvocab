#!/usr/bin/env python3
"""从 freqdict epub 解压出的 HTML 抽取词频词条 -> words.csv
词条格式（calibre 生成）:
  <p class="calibre3">...<b>RANK</b><b> HEADWORD</b> <i>POS</i> ENGLISH</p>
  <ul><li class="calibre8">FR_EXAMPLE – <i>EN_TRANS</i><br/>DISP | FREQ</li></ul>
"""
import csv
import glob
import os
import re
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
TEXT_DIR = os.path.join(BASE, "epub_extract", "text")
OUT = os.path.join(BASE, "words.csv")

# 主词条索引在 part0010..part0018
parts = sorted(glob.glob(os.path.join(TEXT_DIR, "part00[12][0-9].html")))

rows = []
seen_ranks = set()

for path in parts:
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    for p in soup.find_all("p", class_="calibre3"):
        bolds = p.find_all("b", class_="calibre6")
        if len(bolds) < 2:
            continue
        rank_txt = bolds[0].get_text(strip=True)
        if not rank_txt.isdigit():
            continue  # 跳过非词条（说明行等）
        rank = int(rank_txt)
        if rank in seen_ranks:
            continue
        headword = bolds[1].get_text(strip=True)

        # 词性：紧跟词头的第一个 <i class="calibre4">
        pos_i = p.find("i", class_="calibre4")
        pos = pos_i.get_text(strip=True) if pos_i else ""

        # 英文释义：<i>(词性)</i> 之后到 </p> 结尾的纯文本
        english = ""
        if pos_i is not None:
            tail = []
            for sib in pos_i.next_siblings:
                if getattr(sib, "get_text", None):
                    tail.append(sib.get_text())
                else:
                    tail.append(str(sib))
            english = re.sub(r"\s+", " ", "".join(tail)).strip()

        # 例句：紧跟的 <ul>/<li class="calibre8">
        ex_fr = ex_en = disp = freq = ""
        ul = p.find_next_sibling("ul")
        li = ul.find("li", class_="calibre8") if ul else None
        if li:
            en_i = li.find("i", class_="calibre4")
            ex_en = en_i.get_text(strip=True) if en_i else ""
            # 法语例句 = li 全文里 en 译文之前、破折号之前的部分
            full = li.get_text("\n", strip=True)
            # 末行通常是 "DISP | FREQ"
            m = re.search(r"(\d+)\s*\|\s*(\d+)", full)
            if m:
                disp, freq = m.group(1), m.group(2)
            # 法语例句：第一段，到 – / - / — 前
            first = full.split("\n")[0]
            ex_fr = re.split(r"\s+[–—-]\s+", first)[0].strip()

        rows.append({
            "rank": rank, "headword": headword, "pos": pos,
            "en": english, "ex_fr": ex_fr, "ex_en": ex_en,
            "dispersion": disp, "freq": freq,
        })
        seen_ranks.add(rank)

# 第二遍：从字母索引补回主索引漏掉的 rank（索引格式：词头 词性 释义 …<a><b>RANK</b></a>）
missing_before = set(range(1, 5001)) - seen_ranks
if missing_before:
    for path in parts:
        with open(path, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        for p in soup.find_all("p", class_="calibre3"):
            bolds = p.find_all("b", class_="calibre6")
            if len(bolds) < 2:
                continue
            last = bolds[-1].get_text(strip=True)
            if not last.isdigit():
                continue
            rank = int(last)
            if rank not in missing_before or rank in seen_ranks:
                continue
            headword = bolds[0].get_text(strip=True)
            pos_i = p.find("i", class_="calibre4")
            pos = pos_i.get_text(strip=True) if pos_i else ""
            english = ""
            if pos_i is not None:
                tail = []
                for sib in pos_i.next_siblings:
                    if sib is bolds[-1] or (getattr(sib, "name", None) and sib.find("b", class_="calibre6")):
                        break
                    tail.append(sib.get_text() if hasattr(sib, "get_text") else str(sib))
                english = re.sub(r"\s+", " ", "".join(tail)).strip()
            rows.append({"rank": rank, "headword": headword, "pos": pos,
                         "en": english, "ex_fr": "", "ex_en": "",
                         "dispersion": "", "freq": ""})
            seen_ranks.add(rank)

rows.sort(key=lambda r: r["rank"])

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["rank", "headword", "pos", "en",
                                       "ex_fr", "ex_en", "dispersion", "freq"])
    w.writeheader()
    w.writerows(rows)

print(f"提取 {len(rows)} 条 -> {OUT}")
if rows:
    print(f"rank 范围: {rows[0]['rank']} .. {rows[-1]['rank']}")
    # 缺号检测
    ranks = [r["rank"] for r in rows]
    missing = sorted(set(range(ranks[0], ranks[-1] + 1)) - set(ranks))
    print(f"缺失 rank 数: {len(missing)}" + (f"  例: {missing[:10]}" if missing else ""))
