#!/usr/bin/env python3
"""把 universal/core.md 生成到各平台的适配文件。

单一正文，多个外壳。改内容只改 core.md 与 src/，再跑本脚本。
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "adapters"

CORE = (ROOT / "core.md").read_text(encoding="utf-8")

TARGETS = {
    "claude": {
        "file": "SKILL.md",
        "dir": "~/.claude/skills/mingpan-tuiyan",
        "data": "~/.claude/skills/mingpan-tuiyan",
        "head": "",
    },
    "codex": {
        "file": "AGENTS.md",
        "dir": "~/.codex/mingpan-tuiyan",
        "data": "~/.codex/mingpan-tuiyan",
        "head": "> 安装位置：资料在 `~/.codex/mingpan-tuiyan`，指令并入 `~/.codex/AGENTS.md`。\n>\n> 排盘脚本需要 Python 3.9+ 与 sxtwl，见文末「排盘」一节。\n\n",
    },
    "gemini": {
        "file": "GEMINI.md",
        "dir": "~/.gemini/mingpan-tuiyan",
        "data": "~/.gemini/mingpan-tuiyan",
        "head": "> 安装位置：资料在 `~/.gemini/mingpan-tuiyan`，指令并入 `~/.gemini/GEMINI.md`。\n>\n> Gemini CLI 读不到本目录外的东西时，把路径换成绝对路径。\n\n",
    },
    "qwen": {
        "file": "QWEN.md",
        "dir": "~/.qwen/mingpan-tuiyan",
        "data": "~/.qwen/mingpan-tuiyan",
        "head": "> 安装位置：资料在 `~/.qwen/mingpan-tuiyan`，指令并入 `~/.qwen/QWEN.md`。\n>\n> 排盘脚本需要 Python 3.9+ 与 sxtwl，见文末「排盘」一节。\n\n",
    },
    "generic": {
        "file": "INSTRUCTIONS.md",
        "dir": "~/.local/share/mingpan-tuiyan",
        "data": "~/.local/share/mingpan-tuiyan",
        "head": "> 通用版：没有 skill 目录约定的 agent，把本文件内容放进系统提示词或项目指令文件。\n>\n> 资料目录约定在 `~/.local/share/mingpan-tuiyan`，也可以用绝对路径替换文中的 `{{DIR}}`。\n\n",
    },
}

FRONTMATTER = """---
name: mingpan-tuiyan
description: Use when the user asks to cast, verify, or interpret a Chinese birth chart (八字/四柱/子平, 紫微斗数), including 排盘、起盘、看命、算命、命理分析、大运流年、合婚、择业择时, or supplies a birth date, time, and place for a reading.
---

"""


def render(platform: str) -> str:
    cfg = TARGETS[platform]
    body = CORE.replace("{{DIR}}", cfg["data"])
    head = cfg["head"].replace("{{DIR}}", cfg["data"])
    if platform == "claude":
        return FRONTMATTER + head + body
    return head + body


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for platform, cfg in TARGETS.items():
        d = OUT / platform
        d.mkdir(parents=True, exist_ok=True)
        text = render(platform)
        if "{{DIR}}" in text:
            print(f"error: {platform} 仍有未替换的 {{{{DIR}}}}", file=sys.stderr)
            return 1
        (d / cfg["file"]).write_text(text, encoding="utf-8")
        print(f"wrote adapters/{platform}/{cfg['file']}")

    for name, src, dst in (
        ("doubao", "src/doubao.md", "doubao/system-prompt.md"),
        ("chat", "src/chat.md", "chat/usage.md"),
    ):
        (OUT / name).mkdir(parents=True, exist_ok=True)
        (OUT / dst).write_text((ROOT / src).read_text(encoding="utf-8"), encoding="utf-8")
        print(f"wrote adapters/{dst}")

    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
