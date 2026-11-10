#!/usr/bin/env python3
"""用 TrendRadar 自己的解析和匹配函数验证 AI 雷达配置。
用法（在 TrendRadar 仓库根目录）：uv run python ../verify_ai_config.py   退出码 1 = 有用例失败"""
import sys
import yaml

sys.path.insert(0, ".")
from trendradar.core.frequency import load_frequency_words, matches_word_groups  # noqa: E402

word_groups, filter_words, global_filters = load_frequency_words("config/frequency_words.txt")
print(f"词组 {len(word_groups)} 个，全局过滤词 {len(global_filters)} 个")

SHOULD_MATCH = [
    "用AI写代码一周后，我把Cursor卸了",
    "DeepSeek V4发布，开源权重同步上线",
    "用DeepSeek写论文被导师发现了",
    "Claude Code新功能：后台智能体",
    "OpenAI发布GPT-6，奥特曼称迎来拐点",
    "可灵2.5上线，AI视频进入1080P时代",
    "豆包大模型日活破亿",
    "MCP协议成了Agent的USB接口？",
    "AI眼镜双十一销量暴涨",
    "知乎热议：大模型会取代程序员吗",
    "n8n和Dify哪个更适合做AI工作流",
]
SHOULD_NOT_MATCH = [
    "Air Jordan新配色发售",           # Air 不是 AI
    "MacBook Air降价",                # Air 不是 AI
    "震惊！AI竟然能做这个",            # 全局过滤：标题党
    "双十一快递爆仓",
    "工厂自动化改造补贴政策出台",        # 不带 AI 的自动化不收
]

fails = 0
for t in SHOULD_MATCH:
    ok = matches_word_groups(t, word_groups, filter_words, global_filters)
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} 应匹配   {t}")
for t in SHOULD_NOT_MATCH:
    ok = not matches_word_groups(t, word_groups, filter_words, global_filters)
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} 不应匹配 {t}")

cfg = yaml.safe_load(open("config/config.yaml", encoding="utf-8"))
ids = [s["id"] for s in cfg["platforms"]["sources"]]
print("热榜平台：", ids)
for need in ["zhihu", "douyin"]:
    if need not in ids:
        fails += 1
        print("FAIL 缺少平台", need)
yahoo = next(f for f in cfg["rss"]["feeds"] if f["id"] == "yahoo-finance")
if yahoo.get("enabled", True):
    fails += 1
    print("FAIL 雅虎财经没关")
print(f"\n失败 {fails} 项")
sys.exit(1 if fails else 0)
