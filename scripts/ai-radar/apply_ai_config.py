#!/usr/bin/env python3
"""把 TrendRadar 配置改成「AI 垂直热点雷达」。用法：python3 apply_ai_config.py <TrendRadar 仓库目录>
可重复运行（幂等）：每次都从原文的固定锚点重写对应区块。"""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])


def E(word: str) -> str:
    """英文词边界：中文字符在 Python 里也算 \\w，\\bAI\\b 匹配不到「用AI写代码」，所以用前后不是英文字母来判断。"""
    return rf"(?<![A-Za-z]){word}(?![A-Za-z])"


GLOBAL_FILTER = """[GLOBAL_FILTER]
# 过滤标题党
震惊
太可怕了
"""

WORD_GROUPS = "\n\n".join([
    "[WORD_GROUPS]",
    # 1 账号核心：Agent / 自动化
    "/" + "|".join(["智能体", E("Agent"), E("Agents"), E("MCP"), "Manus", "OpenClaw", "AI工作流", "AI自动化",
                    E("n8n"), "Dify", "Coze", "扣子"]) + "/ => AI Agent/自动化",
    # 2 AI 编程
    "/" + "|".join(["AI编程", r"Vibe ?Coding", "Claude Code", E("Codex"), E("Cursor"), E("Copilot"),
                    "Windsurf", E("Trae"), "通义灵码"]) + "/ => AI编程",
    # 3 多模态
    "/" + "|".join(["多模态", "AI视频", "AI绘画", "AI生图", "文生视频", "图生视频", "可灵", "即梦", E("Sora"),
                    E("Veo"), "Midjourney", "海螺AI", E("Vidu"), "Nano Banana"]) + "/ => 多模态/AI视频",
    # 4-8 主要模型和公司
    "/" + "|".join(["深度求索", "梁文锋", E("DeepSeek")]) + "/ => DeepSeek",
    "/" + "|".join(["Kimi", "月之暗面", "豆包", "通义", "千问", E("Qwen"), "智谱", E("GLM"), "MiniMax",
                    "腾讯元宝", "混元", "文心一言", "阶跃星辰"]) + "/ => 国产大模型",
    "/" + "|".join([E("OpenAI"), E("ChatGPT"), "Sam Altman", "奥特曼"]) + "/ => OpenAI",
    "/" + "|".join([E("Anthropic"), E("Claude")]) + "/ => Claude",
    "/" + "|".join([E("Gemini"), E("DeepMind")]) + "/ => Gemini",
    # 9 AI 硬件和具身（限 8 条，避免挤占核心话题）
    "/" + "|".join(["AI眼镜", "AI手机", "AI ?PC", "具身智能", "人形机器人", "宇树", "智元机器人"])
    + "/ => AI硬件/具身\n@8",
    # 10 兜底：泛 AI（限 15 条）
    "/" + "|".join(["人工智能", "大模型", E("AI"), E("AIGC"), E("LLM"), E("AGI")]) + "/ => AI综合\n@15",
]) + "\n"


def rewrite_frequency_words(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    gi = lines.index("[GLOBAL_FILTER]")
    wi = lines.index("[WORD_GROUPS]")
    # 全局过滤区的正文到下一段注释为止；中间的语法说明注释原样保留
    gend = next(i for i in range(gi + 1, wi) if lines[i].startswith("# ───"))
    new = lines[:gi] + GLOBAL_FILTER.rstrip("\n").split("\n") + ["", "", ""] + lines[gend:wi] + [WORD_GROUPS]
    path.write_text("\n".join(new), encoding="utf-8")


PLATFORMS = [
    ("zhihu", "知乎", "zhihu.com"),
    ("douyin", "抖音", "douyin.com"),
    ("weibo", "微博", "weibo.com"),
    ("bilibili-hot-search", "bilibili 热搜", "bilibili.com"),
    ("baidu", "百度热搜", "baidu.com"),
    ("toutiao", "今日头条", "toutiao.com"),
    ("ithome", "IT之家", "ithome.com"),
    ("juejin", "稀土掘金", "juejin.cn"),
    ("aihot", "AIHOT", None),  # 聚合源，链接指向各家原站，不做域名校验，否则数据会被整批丢弃
]


def rewrite_config(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    block = "  sources:\n"
    for pid, name, dom in PLATFORMS:
        block += f'    - id: "{pid}"\n      name: "{name}"\n'
        if dom:
            block += f'      expected_domain: "{dom}"\n'
    # 只替换 platforms 下的 sources 列表（从 "  sources:" 到 RSS 区块分隔注释之前）
    text, n = re.subn(r"  sources:\n(?:    .*\n|[ \t]*\n)+(?=# =+\n# 3\. )", block + "\n\n\n", text, count=1)
    assert n == 1, "没找到 platforms.sources 区块"
    # 关掉雅虎财经 RSS（与 AI 无关），保留 Hacker News
    text, n = re.subn(r'(      url: "https://finance\.yahoo\.com/news/rssindex"\n)(?!      enabled: false)',
                      r"\1      enabled: false                  # AI 雷达不需要财经源\n", text, count=1)
    path.write_text(text, encoding="utf-8")


rewrite_frequency_words(root / "config/frequency_words.txt")
rewrite_config(root / "config/config.yaml")
print("done")
