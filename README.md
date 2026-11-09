# 命盘推演 · mingpan-tuiyan

把《中国古代算命术》《三命通会》《滴天髓》《紫微斗数全书》四本书的推演方法，收成一个能真正排盘的 skill：八字四柱与紫微斗数同盘合参，先出盘面，再出断语。

当前版本 **v0.6.3**。

> 本项目用于传统文化研究与文本分析，不主张命理结论具有科学必然性，不构成医疗、法律、投资、婚姻等任何专业建议。完整条款见 [DISCLAIMER.md](DISCLAIMER.md)，第三方来源见 [NOTICE.md](NOTICE.md)。

## 四本书各管一段

| 书 | 管什么 | 在本 skill 中的位置 |
| --- | --- | --- |
| 《中国古代算命术》（洪丕谟、姜玉珍） | 总纲：为什么这样推、按什么顺序推、哪些话不能说 | `references/00-fusion.md` |
| 《三命通会》（万民英） | 立法度：干支、神煞、格局、逐日断法 | `references/10-bazi.md` |
| 《滴天髓》（任铁樵注） | 定权衡：旺衰、中和、源流、通关、寒暖燥湿 | `references/10-bazi.md` |
| 《紫微斗数全书》 | 紫微全部依据：安星、十二宫、四化、大限 | `references/20-ziwei.md` |

一句口诀：通会立法度，滴天髓定权衡。有法度无权衡则堆砌，有权衡无法度则空谈。

## 安装

作为 DeepSeek Harness skill：

```bash
git clone https://github.com/renejo75/mingpan-tuiyan.git
cd mingpan-tuiyan
./install.sh
```

`install.sh` 做两件事：拷到 `~/.dsh/skills/mingpan-tuiyan`，把 `sxtwl` 装进 `scripts/lib`（不污染全局 Python）。

只想跑排盘脚本：

```bash
pip3 install --target scripts/lib sxtwl==2.0.7
python3 scripts/paipan.py --date 1990-05-20 --time 14:30 --gender m --city 上海
```

## 用法

```bash
# 基本排盘
python3 scripts/paipan.py --date 1990-05-20 --time 14:30 --gender m --city 上海

# 加流年、输出 JSON
python3 scripts/paipan.py --date 1990-05-20 --time 14:30 --gender m --lon 121.47 --liunian 2026 --json
```

生日一律按公历输入，农历请先自行换算。`--leap` 控制闰月归本月还是下月。

输出包含：真太阳时、农历、四柱、藏干、十神、纳音、旬空、五行权重、起运与大运、紫微十二宫、五行局、十四主星、四化、大限，可选逐年流年。

`--city` 内置 83 个城市经度；表外用 `--lon` 直接给东经度数。

## 目录

```
SKILL.md              主文档：五条铁律、七步流程、五段式输出
references/
  00-fusion.md        四书定位、体用分工、合参规则、五步算法
  10-bazi.md          十神、旺衰、格局、用神、理气十则、神煞、大运流年
  20-ziwei.md         安星口诀、十二宫、十四主星、辅煞、四化、格局
  30-reading.md       收料与定时、输出模板、六大专题、话术红线
  40-sources.md       版本来源、核验状态、术语表、已知局限
scripts/paipan.py     排盘脚本，纯 Python 3.9+
sources/              《紫微斗数全书》公版原文（维基文库）
DISCLAIMER.md         免责声明与不适用场景
NOTICE.md             第三方组件与文本来源
```

## 已知局限

1. 真太阳时按经度差加均时差估算，与专业天文软件可能有数十秒差异。
2. 节气边界当日出生者，需按具体交节时刻复核。
3. 子时换日有 23:00 与 00:00 两派，脚本固定 23:00 换日，需另一派请改 `scripts/paipan.py` 中晚子时分支。
4. 闰月有「按本月」「按下月」两说，脚本默认按本月，可切。
5. 四化表以《紫微斗数全书》为准，与中州派等流派存在差异。
6. 《中国古代算命术》为版权书，本仓库未收录正文，只取其方法论骨架并标注转引。

## 边界

本 skill 处理的是传统命理文献的推演体系，不主张其结论具有科学必然性。不推断生死寿夭，不推断具体疾病，不做付费化解。涉及健康、法律、财务的实质决策，请交由对应专业人士。脚本在本机运行，不联网、不收集数据。完整条款见 [DISCLAIMER.md](DISCLAIMER.md)。

## 许可

代码与文档 MIT。随包依赖 `sxtwl` 为 BSD 许可，见 <https://github.com/yuangu/sxtwl_cpp>。`sources/` 下《紫微斗数全书》为公版古籍，录入文字取自维基文库并按 CC BY-SA 4.0 署名。授权范围与来源清单见 [NOTICE.md](NOTICE.md)。
