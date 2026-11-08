#!/usr/bin/env bash
# 安装 mingpan-tuiyan 到 DeepSeek Harness 的 skills 目录，并准备 python 依赖。
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${DSH_SKILLS_DIR:-$HOME/.dsh/skills}/mingpan-tuiyan"

echo "来源: $SRC"
echo "目标: $DEST"

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$SRC/SKILL.md" "$SRC/references" "$SRC/scripts" "$SRC/sources" "$DEST/"

echo "安装 sxtwl 到 $DEST/scripts/lib"
python3 -m pip install --quiet --target "$DEST/scripts/lib" sxtwl==2.0.7

echo "自检:"
python3 "$DEST/scripts/paipan.py" --date 1990-05-20 --time 14:30 --gender m --city 上海 | head -12

echo "完成。重启会话后即可在技能目录看到 mingpan-tuiyan。"
