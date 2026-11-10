#!/usr/bin/env python3
"""从最近一次抓取里导出命中 AI 关键词的热榜条目（按词组分组），给研究简报用。
用法（仓库根目录）：uv run python scripts/ai-radar/dump_matches.py [output/news/日期.db] > matches.md"""
import glob
import sqlite3
import sys
from collections import defaultdict

sys.path.insert(0, ".")
from trendradar.core.frequency import load_frequency_words, matches_word_groups  # noqa: E402

db = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("output/news/*.db"))[-1]
groups, filters, gfilters = load_frequency_words("config/frequency_words.txt")
c = sqlite3.connect(db)
last = c.execute("select max(last_crawl_time) from news_items").fetchone()[0]
names = dict(c.execute("select id, name from platforms"))
rows = c.execute(
    "select title, platform_id, rank, url, first_crawl_time from news_items where last_crawl_time=? order by rank",
    (last,),
).fetchall()

by_group = defaultdict(list)
for title, pid, rank, url, first in rows:
    if not matches_word_groups(title, [], filters, gfilters) and not matches_word_groups(title, groups, filters, gfilters):
        continue
    for g in groups:  # 归到第一个命中的词组（词组按优先级排列）
        if matches_word_groups(title, [g], filters, gfilters):
            by_group[g.get("display_name") or g.get("group_key") or str(g)].append((names.get(pid, pid), rank, title, url))
            break

total = sum(len(v) for v in by_group.values())
print(f"# AI 热点原始数据\n数据库：{db}  抓取批次：{last}  当前榜单 {len(rows)} 条，命中 {total} 条\n")
for g, items in by_group.items():
    print(f"## {g}（{len(items)}）")
    for plat, rank, title, url in items:
        print(f"- [{plat} #{rank}] {title}  {url}")
    print()
