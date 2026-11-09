#!/usr/bin/env bash
# mingpan-tuiyan 通用安装脚本
# 默认不动本机：必须显式给目标。所有改动前先备份，--dry-run 只打印不执行。

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
AD="$(cd "$HERE/adapters" 2>/dev/null && pwd || true)"
STAMP="$(date +%Y%m%d-%H%M%S)"

DRY=0
DO_DEPS=1
TARGETS=()

usage() {
  cat <<'EOF'
用法: ./universal/install.sh [目标...] [选项]

目标（可多选）:
  --claude     装到 ~/.claude/skills/mingpan-tuiyan（Claude Code / Agent Skills）
  --codex      资料装到 ~/.codex/mingpan-tuiyan，指令并入 ~/.codex/AGENTS.md
  --gemini     资料装到 ~/.gemini/mingpan-tuiyan，指令并入 ~/.gemini/GEMINI.md
  --qwen       资料装到 ~/.qwen/mingpan-tuiyan，指令并入 ~/.qwen/QWEN.md
  --generic    资料装到 ~/.local/share/mingpan-tuiyan，只给指令文件，不改任何配置
  --all        以上全部

选项:
  --dry-run    只打印将要做的事
  --no-deps    不尝试安装 sxtwl
  --list       列出目标路径
  -h, --help   显示本帮助

示例:
  ./universal/install.sh --claude --dry-run
  ./universal/install.sh --codex --gemini --qwen
EOF
}

say()  { printf '%s\n' "$*"; }
step() { printf '  → %s\n' "$*"; }

run() {
  if [ "$DRY" -eq 1 ]; then
    printf '  [dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

need_adapter() {
  if [ -z "$AD" ] || [ ! -d "$AD" ]; then
    say "缺少 adapters/ 目录，先跑: python3 universal/tools/build_adapters.py"
    exit 1
  fi
}

payload() {
  # $1 目标目录
  local dest="$1"
  run mkdir -p "$dest"
  for item in references scripts sources DISCLAIMER.md NOTICE.md; do
    [ -e "$REPO/$item" ] || { say "缺少 $item"; exit 1; }
    run cp -R "$REPO/$item" "$dest/"
  done
}

merge_block() {
  # $1 指令文件  $2 片段文件
  local file="$1" block="$2" dir
  dir="$(dirname "$file")"
  run mkdir -p "$dir"
  if [ -f "$file" ] && grep -qF '<!-- BEGIN mingpan-tuiyan -->' "$file"; then
    step "已有旧块，替换: $file"
    if [ "$DRY" -eq 0 ]; then
      cp "$file" "$file.bak-$STAMP"
      awk '/<!-- BEGIN mingpan-tuiyan -->/{skip=1;next} /<!-- END mingpan-tuiyan -->/{skip=0;next} !skip' \
        "$file" > "$file.tmp"
      mv "$file.tmp" "$file"
    fi
  elif [ -f "$file" ]; then
    step "追加到已有文件: $file"
    if [ "$DRY" -eq 0 ]; then cp "$file" "$file.bak-$STAMP"; fi
  else
    step "新建: $file"
  fi
  if [ "$DRY" -eq 0 ]; then
    {
      printf '<!-- BEGIN mingpan-tuiyan -->\n'
      cat "$block"
      printf '\n<!-- END mingpan-tuiyan -->\n'
    } >> "$file"
  else
    printf '  [dry-run] 写入指令块到 %s\n' "$file"
  fi
}

install_deps() {
  local dest="$1"
  [ "$DO_DEPS" -eq 1 ] || return 0
  command -v python3 >/dev/null 2>&1 || { step "未找到 python3，跳过 sxtwl"; return 0; }
  if [ -d "$dest/scripts/lib/sxtwl" ] || [ -f "$dest/scripts/lib/_sxtwl"*.so ] 2>/dev/null; then
    step "sxtwl 已在 $dest/scripts/lib"
    return 0
  fi
  step "安装 sxtwl 到 $dest/scripts/lib"
  run python3 -m pip install --quiet --target "$dest/scripts/lib" sxtwl==2.0.7 || \
    say "  sxtwl 安装失败，稍后可手动: python3 -m pip install --target $dest/scripts/lib sxtwl==2.0.7"
}

do_claude() {
  local dest="$HOME/.claude/skills/mingpan-tuiyan"
  say "Claude：$dest"
  payload "$dest"
  run cp "$AD/claude/SKILL.md" "$dest/SKILL.md"
  install_deps "$dest"
}

do_contextual() {
  # $1 名称  $2 数据目录  $3 指令文件  $4 片段
  say "$1：资料 $2，指令 $3"
  payload "$2"
  merge_block "$3" "$4"
  install_deps "$2"
}

do_generic() {
  local dest="$HOME/.local/share/mingpan-tuiyan"
  say "通用：资料 $dest"
  payload "$dest"
  step "指令文件: $AD/generic/INSTRUCTIONS.md（自行粘贴到目标产品的系统提示词）"
  install_deps "$dest"
}

[ $# -eq 0 ] && { usage; exit 0; }

while [ $# -gt 0 ]; do
  case "$1" in
    --claude) TARGETS+=("claude") ;;
    --codex) TARGETS+=("codex") ;;
    --gemini) TARGETS+=("gemini") ;;
    --qwen) TARGETS+=("qwen") ;;
    --generic) TARGETS+=("generic") ;;
    --all) TARGETS=(claude codex gemini qwen generic) ;;
    --dry-run) DRY=1 ;;
    --no-deps) DO_DEPS=0 ;;
    --list)
      say "claude  ~/.claude/skills/mingpan-tuiyan"
      say "codex   ~/.codex/mingpan-tuiyan + ~/.codex/AGENTS.md"
      say "gemini  ~/.gemini/mingpan-tuiyan + ~/.gemini/GEMINI.md"
      say "qwen    ~/.qwen/mingpan-tuiyan + ~/.qwen/QWEN.md"
      say "generic ~/.local/share/mingpan-tuiyan"
      exit 0 ;;
    -h|--help) usage; exit 0 ;;
    *) say "未知参数: $1"; usage; exit 2 ;;
  esac
  shift
done

[ ${#TARGETS[@]} -eq 0 ] && { usage; exit 0; }
need_adapter
[ "$DRY" -eq 1 ] && say "dry-run：只打印，不改文件"

for t in "${TARGETS[@]}"; do
  case "$t" in
    claude) do_claude ;;
    codex) do_contextual "Codex" "$HOME/.codex/mingpan-tuiyan" "$HOME/.codex/AGENTS.md" "$AD/codex/AGENTS.md" ;;
    gemini) do_contextual "Gemini CLI" "$HOME/.gemini/mingpan-tuiyan" "$HOME/.gemini/GEMINI.md" "$AD/gemini/GEMINI.md" ;;
    qwen) do_contextual "Qwen Code" "$HOME/.qwen/mingpan-tuiyan" "$HOME/.qwen/QWEN.md" "$AD/qwen/QWEN.md" ;;
    generic) do_generic ;;
  esac
done

say "完成。校验一次排盘："
say "  python3 $HOME/.claude/skills/mingpan-tuiyan/scripts/paipan.py --date 1990-05-20 --time 14:30 --gender m --city 上海"
