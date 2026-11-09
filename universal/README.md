# 通用安装版

同一个命盘推演，按各平台的约定出不同外壳。正文只有一份（`core.md`），改内容只改它，再跑生成脚本。

## 先看这张表

| 你的环境 | 装什么 | 要不要 Python |
| --- | --- | --- |
| Claude Code / 支持 Agent Skills 的产品 | `adapters/claude/SKILL.md` → `~/.claude/skills/mingpan-tuiyan/` | 要，排盘靠它 |
| Codex CLI | `adapters/codex/AGENTS.md` → 并入 `~/.codex/AGENTS.md` | 要 |
| Gemini CLI | `adapters/gemini/GEMINI.md` → 并入 `~/.gemini/GEMINI.md` | 要 |
| Qwen Code | `adapters/qwen/QWEN.md` → 并入 `~/.qwen/QWEN.md` | 要 |
| 任意 agent（WorkBuddy 等） | `adapters/generic/INSTRUCTIONS.md` | 要 |
| 豆包智能体 | `adapters/doubao/system-prompt.md` | 不要，但排盘要用户贴 |
| 纯对话框（千问网页、ChatGPT、Claude 网页、Gemini 网页） | `adapters/chat/usage.md` | 不要 |

有 Python 的：装脚本，模型自己排盘，最准。
没 Python 的：用提示词版，盘面由用户贴进来，模型只做解读与校验。这是能力差异，不是配置问题，别指望纯对话模型精确排盘。

## 快速安装

```bash
# 先看会动哪些路径
./universal/install.sh --all --dry-run

# 只装 Claude
./universal/install.sh --claude

# 装 Codex + Gemini + Qwen
./universal/install.sh --codex --gemini --qwen
```

规则：

- 不给参数不动作，只打印用法。
- 改文件前先备份成 `*.bak-时间戳`。
- 指令块用 `<!-- BEGIN mingpan-tuiyan -->` 包住，重跑会替换而不是叠加。
- `--no-deps` 跳过 sxtwl 安装。

装完验证：

```bash
python3 ~/.claude/skills/mingpan-tuiyan/scripts/paipan.py --date 1990-05-20 --time 14:30 --gender m --city 上海
```

## 豆包怎么用

1. 打开智能体创建页，把 `adapters/doubao/system-prompt.md` 全文贴进「角色设定 / 系统提示词」。
2. 用户只给出生信息时，模型会让他先跑脚本拿盘面，或接受他贴已排好的盘。
3. 想要现成盘面又没 Python，用下面的网页版。

## 网页渲染器

`tools/chart.html`，双击就能开，不联网。

用法：在有脚本的机器上跑

```bash
python3 scripts/paipan.py --date 1990-05-20 --time 14:30 --gender m --city 上海 --json
```

把整段 JSON 粘进页面，点「渲染盘面」，得到四柱、五行、大运、紫微十二宫，再点「生成解读提示词」，复制到任何对话产品里。

它只渲染、不计算。原因很直接：节气时刻与紫微安星依赖寿星天文历，在浏览器里再实现一套，就会有两个版本对不上，出了问题没法判断谁错。算只有一处。

## 目录

```
core.md                  正文（单一来源）
src/doubao.md            豆包系统提示词源文件
src/chat.md              纯对话使用说明源文件
adapters/                生成物，别手改
  claude/SKILL.md
  codex/AGENTS.md
  gemini/GEMINI.md
  qwen/QWEN.md
  generic/INSTRUCTIONS.md
  doubao/system-prompt.md
  chat/usage.md
tools/build_adapters.py  生成脚本
tools/chart.html         离线渲染器
install.sh               安装脚本
```

改完源文件：

```bash
python3 universal/tools/build_adapters.py
```

## 边界

各工具的配置目录与文件名按通行约定写（`~/.codex/AGENTS.md`、`~/.gemini/GEMINI.md`、`~/.qwen/QWEN.md`）。你的版本如果改了路径，直接改 `install.sh` 里对应的三行，或者用 `--generic` 手动放置。

本包不替代各工具的官方文档，也不保证在未安装的工具上生效。
内容用于传统文化研究与文本分析，不构成医疗、法律、投资、婚姻建议，详见仓库根目录 `DISCLAIMER.md`。
