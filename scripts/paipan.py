#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""命盘排盘：八字四柱 + 紫微斗数。

用法：
  python3 paipan.py --date 1990-05-20 --time 14:30 --gender m --lon 121.47
  python3 paipan.py --date 1990-05-20 --time 14:30 --gender f --lon 121.47 --json

依赖：sxtwl（随 skill 附带于 scripts/lib，无需另行安装）。
历法换算以 sxtwl（寿星天文历）为准，节气、农历均由天文算法计算。
真太阳时 = 标准时 + 经度时差 + 均时差；节气判定用标准时（同一绝对时刻，经度差抵消）。
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "lib"), _HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import sxtwl
except ImportError:
    sys.stderr.write(
        "缺少 sxtwl。请把 sxtwl 装到 %s/lib：\n"
        "  pip3 install --target %s/lib sxtwl\n" % (_HERE, _HERE)
    )
    raise

# ---------------------------------------------------------------- 基础表

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
GAN_WX = "木木火火土土金金水水"
ZHI_WX = "水土木木土火火土金金土水"
WX = "木火土金水"

CANG = {
    "子": "癸", "丑": "己癸辛", "寅": "甲丙戊", "卯": "乙",
    "辰": "戊乙癸", "巳": "丙戊庚", "午": "丁己", "未": "己丁乙",
    "申": "庚壬戊", "酉": "辛", "戌": "戊辛丁", "亥": "壬甲",
}

NAYIN = [
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火",
    "涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土",
    "霹雳火", "松柏木", "长流水", "沙中金", "山下火", "平地木",
    "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金",
    "桑柘木", "大溪水", "沙中土", "天上火", "石榴木", "大海水",
]
NAYIN_WX = "".join(n[-1] for n in NAYIN)

CITY_LON = {
    "北京": 116.41,
    "上海": 121.47,
    "广州": 113.26,
    "深圳": 114.06,
    "天津": 117.20,
    "重庆": 106.55,
    "成都": 104.07,
    "杭州": 120.15,
    "南京": 118.80,
    "武汉": 114.31,
    "西安": 108.94,
    "苏州": 120.58,
    "郑州": 113.63,
    "长沙": 112.94,
    "沈阳": 123.43,
    "青岛": 120.38,
    "大连": 121.62,
    "厦门": 118.09,
    "福州": 119.30,
    "昆明": 102.83,
    "贵阳": 106.63,
    "南宁": 108.37,
    "海口": 110.20,
    "合肥": 117.23,
    "南昌": 115.89,
    "济南": 117.00,
    "太原": 112.55,
    "石家庄": 114.51,
    "哈尔滨": 126.53,
    "长春": 125.32,
    "呼和浩特": 111.75,
    "银川": 106.23,
    "兰州": 103.83,
    "西宁": 101.78,
    "乌鲁木齐": 87.62,
    "拉萨": 91.11,
    "香港": 114.17,
    "澳门": 113.54,
    "台北": 121.56,
    "宁波": 121.55,
    "温州": 120.70,
    "无锡": 120.31,
    "佛山": 113.12,
    "东莞": 113.75,
    "珠海": 113.58,
    "中山": 113.39,
    "惠州": 114.42,
    "汕头": 116.68,
    "泉州": 118.68,
    "常州": 119.97,
    "徐州": 117.28,
    "烟台": 121.45,
    "唐山": 118.18,
    "洛阳": 112.45,
    "襄阳": 112.14,
    "宜昌": 111.29,
    "岳阳": 113.13,
    "株洲": 113.13,
    "桂林": 110.29,
    "柳州": 109.42,
    "三亚": 109.51,
    "丽江": 100.23,
    "大理": 100.27,
    "绍兴": 120.58,
    "嘉兴": 120.75,
    "台州": 121.42,
    "金华": 119.65,
    "莆田": 119.01,
    "漳州": 117.65,
    "赣州": 114.94,
    "九江": 115.99,
    "芜湖": 118.38,
    "蚌埠": 117.39,
    "扬州": 119.41,
    "盐城": 120.16,
    "连云港": 119.22,
    "淄博": 118.05,
    "潍坊": 119.16,
    "临沂": 118.35,
    "济宁": 116.59,
    "保定": 115.46,
    "邯郸": 114.54,
    "秦皇岛": 119.60,
}

JU_BY_WX = {"水": ("水二局", 2), "木": ("木三局", 3), "金": ("金四局", 4),
            "土": ("土五局", 5), "火": ("火六局", 6)}

JIEQI_NAMES = ["立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满",
               "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
               "寒露", "霜降", "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"]

# 12 节 → 月支（寅月起）
JIE_TO_MONTH_ZHI = {0: 2, 2: 3, 4: 4, 6: 5, 8: 6, 10: 7,
                    12: 8, 14: 9, 16: 10, 18: 11, 20: 0, 22: 1}

PALACE_NAMES = ["命宫", "父母", "福德", "田宅", "官禄", "奴仆",
                "迁移", "疾厄", "财帛", "子女", "夫妻", "兄弟"]

# 十四主星：按紫微逆/顺布列（相对索引）
BEIDOU_FROM_ZIWEI = [0, -1, None, -3, -4, -5, None, None, -8, None, None, None]  # 紫微天机(空)太阳武曲天同(空)(空)廉贞
NANDOU_FROM_TIANFU = [0, 1, 2, 3, 4, 5, 6, None, None, None, 10]  # 天府太阴贪狼巨门天相天梁七杀(空3)破军

BEIDOU_NAMES = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞"]
NANDOU_NAMES = ["天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]

# 四化（《紫微斗数全书》"安禄权科忌四星变化诀"）
SIHUA = {
    "甲": ("廉贞", "破军", "武曲", "太阳"),
    "乙": ("天机", "天梁", "紫微", "太阴"),
    "丙": ("天同", "天机", "文昌", "廉贞"),
    "丁": ("太阴", "天同", "天机", "巨门"),
    "戊": ("贪狼", "太阴", "右弼", "天机"),
    "己": ("武曲", "贪狼", "天梁", "文曲"),
    "庚": ("太阳", "武曲", "太阴", "天同"),
    "辛": ("巨门", "太阳", "文曲", "文昌"),
    "壬": ("天梁", "紫微", "天府", "武曲"),
    "癸": ("破军", "巨门", "太阴", "贪狼"),
}

LU_CUN = {"甲": 2, "乙": 3, "丙": 5, "丁": 6, "戊": 5,
          "己": 6, "庚": 8, "辛": 9, "壬": 11, "癸": 0}  # 0=子


def fix(i, n=12):
    return i % n


def gz_index(gan, zhi):
    """干支在六十甲子中的序号（0=甲子）。"""
    for i in range(60):
        if i % 10 == gan and i % 12 == zhi:
            return i
    raise ValueError("非法干支组合")


def nayin_of(gan, zhi):
    n = gz_index(gan, zhi) // 2
    return NAYIN[n], NAYIN_WX[n]


def is_yang(i):
    return i % 2 == 0


def wuxing_of_gan(g):
    return WX.index(GAN_WX[g])


def sheng(a):
    return (a + 1) % 5


def ke(a):
    return (a + 2) % 5


def shishen(day_gan, other_gan):
    d = wuxing_of_gan(day_gan)
    o = wuxing_of_gan(other_gan)
    same = (is_yang(day_gan) == is_yang(other_gan))
    if d == o:
        return "比肩" if same else "劫财"
    if sheng(d) == o:
        return "食神" if same else "伤官"
    if ke(d) == o:
        return "偏财" if same else "正财"
    if ke(o) == d:
        return "七杀" if same else "正官"
    return "偏印" if same else "正印"


# ---------------------------------------------------------------- 历法

def jieqi_list(year):
    """返回该年立春起的 24 节气（北京时间），可跨到次年立春前一节气。"""
    arr = sxtwl.getJieQiByYear(year)
    out = []
    for it in arr:
        t = sxtwl.JD2DD(it.jd)
        dt = datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(t.m)) + \
            timedelta(seconds=round(t.s))
        out.append(((it.jqIndex - 3) % 24, dt))
    return out


def solar_terms_around(dt):
    """取覆盖 dt 的 24 节气序列（立春起），必要时用前后年补齐。"""
    terms = jieqi_list(dt.year - 1) + jieqi_list(dt.year) + jieqi_list(dt.year + 1)
    terms.sort(key=lambda x: x[1])
    return terms


def equation_of_time(dt):
    """均时差（分钟）。"""
    n = dt.timetuple().tm_yday
    b = 2.0 * math.pi * (n - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def true_solar(dt, lon):
    return dt + timedelta(minutes=(lon - 120.0) * 4.0 + equation_of_time(dt))


def lunar_of(dt):
    d = sxtwl.fromSolar(dt.year, dt.month, dt.day)
    return {
        "year": d.getLunarYear(), "month": d.getLunarMonth(),
        "day": d.getLunarDay(), "leap": d.isLunarLeap(),
        "month_cn": {"正": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
                     "七": 7, "八": 8, "九": 9, "十": 10, "冬": 11, "腊": 12}.get("x", d.getLunarMonth()),
    }


def day_gz(dt):
    """日干支，23:00 后按次日（晚子时换日）。"""
    d = dt
    if dt.hour >= 23:
        d = dt + timedelta(days=1)
    gz = sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ()
    return gz.tg, gz.dz


# ---------------------------------------------------------------- 八字

def build_bazi(dt_std, lon, gender, yun_years=8):
    dt_true = true_solar(dt_std, lon)
    terms = solar_terms_around(dt_std)

    # 年柱：立春分界
    lichun = [t for i, t in terms if i == 0]
    base_year = dt_std.year
    if not any(t.year == base_year and t <= dt_std for t in lichun):
        base_year -= 1
    ygan = (base_year - 4) % 10
    yzhi = (base_year - 4) % 12

    # 月柱：以 12 节为界
    jie = [(i, t) for i, t in terms if i % 2 == 0]
    cur = None
    for idx, (i, t) in enumerate(jie):
        if t <= dt_std:
            cur = (i, t, idx)
    month_zhi = JIE_TO_MONTH_ZHI[cur[0]]
    # 五虎遁：寅宫干 = 年干*2+2
    yin_gan = (ygan * 2 + 2) % 10
    month_gan = (yin_gan + (month_zhi - 2) % 12) % 10

    # 日柱
    dgan, dzhi = day_gz(dt_true)

    # 时柱（五鼠遁）
    hour_zhi = ((dt_true.hour + 1) // 2) % 12
    hour_gan = ((dgan % 5) * 2 + hour_zhi) % 10

    pillars = [
        ("年", ygan, yzhi), ("月", month_gan, month_zhi),
        ("日", dgan, dzhi), ("时", hour_gan, hour_zhi),
    ]

    # 十神 / 藏干 / 纳音
    detail = []
    for label, g, z in pillars:
        ny, nywx = nayin_of(g, z)
        detail.append({
            "label": label,
            "gan": GAN[g], "zhi": ZHI[z],
            "gan_wx": GAN_WX[g], "zhi_wx": ZHI_WX[z],
            "gan_shishen": "日主" if label == "日" else shishen(dgan, g),
            "cang": [{"gan": c, "shishen": shishen(dgan, GAN.index(c))} for c in CANG[ZHI[z]]],
            "nayin": ny, "nayin_wx": nywx,
            "xunkong": xun_kong(g, z),
        })

    # 五行统计（天干各 1，地支本气按 1，藏干中气余气各 1，粗略权重）
    wx_count = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}
    for label, g, z in pillars:
        wx_count[GAN_WX[g]] += 1.0
        cangs = CANG[ZHI[z]]
        weights = [1.0, 0.5, 0.3][:len(cangs)]
        for c, w in zip(cangs, weights):
            wx_count[GAN_WX[GAN.index(c)]] += w

    # 大运
    yang_year = is_yang(ygan)
    forward = (yang_year and gender == "m") or ((not yang_year) and gender == "f")
    if forward:
        nxt = [t for i, t in jie if t > dt_std][0]
        delta = nxt - dt_std
    else:
        prv = [t for i, t in jie if t <= dt_std][-1]
        delta = dt_std - prv
    total_days = delta.total_seconds() / 86400.0
    years = int(total_days // 3)
    months = int(round((total_days % 3) * 4))
    if months >= 12:
        years += months // 12
        months %= 12
    start_age = years + months / 12.0

    mgz = gz_index(month_gan, month_zhi)
    dayun = []
    start_dt = dt_std + timedelta(days=start_age * 365.2422)
    for k in range(1, yun_years + 1):
        gz = (mgz + k) % 60 if forward else (mgz - k) % 60
        g, z = gz % 10, gz % 12
        age0 = start_age + (k - 1) * 10
        age1 = age0 + 10
        y0 = start_dt.year + (k - 1) * 10
        dayun.append({
            "ganzhi": GAN[g] + ZHI[z], "gan": GAN[g], "zhi": ZHI[z],
            "shishen": shishen(dgan, g),
            "age_start": round(age0, 1), "age_end": round(age1, 1),
            "year_start": y0,
            "cang": [{"gan": c, "shishen": shishen(dgan, GAN.index(c))} for c in CANG[ZHI[z]]],
        })

    return {
        "dt_std": dt_std, "dt_true": dt_true,
        "year_gan": ygan, "year_zhi": yzhi,
        "month_gan": month_gan, "month_zhi": month_zhi,
        "day_gan": dgan, "day_zhi": dzhi,
        "hour_gan": hour_gan, "hour_zhi": hour_zhi,
        "pillars": detail, "wx_count": wx_count,
        "forward": forward, "start_age": start_age,
        "start_years": years, "start_months": months,
        "dayun": dayun,
        "jieqi_ref": {"prev": cur[1], "name": JIEQI_NAMES[cur[0]]},
    }


def xun_kong(gan, zhi):
    idx = gz_index(gan, zhi)
    xun = idx - (idx % 10)  # 旬首
    k1 = (xun + 10) % 12
    k2 = (xun + 11) % 12
    return ZHI[k1] + ZHI[k2]


# ---------------------------------------------------------------- 紫微

def build_ziwei(lunar, hour_zhi, ygan, yzhi, gender, leap_rule="same"):
    """leap_rule: same=闰月按本月计；next=闰月按下月计。"""
    m = lunar["month"]
    if lunar["leap"] and leap_rule == "next":
        m = m + 1
    m = fix(m - 1, 12) + 1  # 1-12
    h = hour_zhi

    ming = fix(2 + (m - 1) - h)
    shen = fix(2 + (m - 1) + h)

    # 命宫天干（五虎遁）
    yin_gan = (ygan * 2 + 2) % 10
    ming_gan = (yin_gan + (ming - 2) % 12) % 10
    _, ju_wx = nayin_of(ming_gan, ming)
    ju_name, ju_num = JU_BY_WX[ju_wx]

    # 紫微（转 0=寅 计算）
    day = lunar["day"]
    offset = 0
    while (day + offset) % ju_num != 0:
        offset += 1
    q = ((day + offset) // ju_num) % 12
    zi = q - 1
    zi = zi + offset if offset % 2 == 0 else zi - offset
    zi = fix(zi)                       # 0=寅
    ziwei_zi = fix(zi + 2)             # 0=子
    tianfu_zi = fix(4 - ziwei_zi)

    pos = {}  # 星 -> 宫（0=子）
    offsets = {"紫微": 0, "天机": -1, "太阳": -3, "武曲": -4, "天同": -5, "廉贞": -8}
    for name, off in offsets.items():
        pos[name] = fix(ziwei_zi + off)
    noff = {"天府": 0, "太阴": 1, "贪狼": 2, "巨门": 3, "天相": 4, "天梁": 5, "七杀": 6, "破军": 10}
    for name, off in noff.items():
        pos[name] = fix(tianfu_zi + off)

    # 六吉
    pos["文昌"] = fix(10 - h)   # 戌起子时逆
    pos["文曲"] = fix(4 + h)    # 辰起子时顺
    zuo = fix(4 + (m - 1))      # 辰起正月顺
    you = fix(10 - (m - 1))     # 戌起正月逆
    pos["左辅"], pos["右弼"] = zuo, you

    kui_yue = {
        "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),
        "乙": (0, 8), "己": (0, 8), "辛": (2, 6),
        "丙": (11, 9), "丁": (11, 9), "壬": (3, 5), "癸": (3, 5),
    }
    kui, yue = kui_yue[GAN[ygan]]
    pos["天魁"], pos["天钺"] = kui, yue

    lu = LU_CUN[GAN[ygan]]
    pos["禄存"] = lu
    pos["擎羊"] = fix(lu + 1)
    pos["陀罗"] = fix(lu - 1)

    ma_map = {0: 2, 4: 2, 8: 2, 1: 8, 5: 8, 9: 8,
              2: 11, 6: 11, 10: 11, 3: 5, 7: 5, 11: 5}  # 年支→天马
    pos["天马"] = ma_map[yzhi]

    group = yzhi % 4  # 0:子辰申 1:丑巳酉 2:寅午戌 3:卯未亥
    huo_base = {0: 2, 1: 3, 2: 1, 3: 9}[group]
    ling_base = {0: 10, 1: 10, 2: 3, 3: 10}[group]
    pos["火星"] = fix(huo_base + h)
    pos["铃星"] = fix(ling_base + h)

    pos["地空"] = fix(11 - h)
    pos["地劫"] = fix(11 + h)

    # 常用小星（《全书》口诀）
    pos["红鸾"] = fix(3 - yzhi)
    pos["天喜"] = fix(pos["红鸾"] + 6)
    pos["天刑"] = fix(9 + (m - 1))
    pos["天姚"] = fix(1 + (m - 1))
    pos["天哭"] = fix(6 - yzhi)
    pos["天虚"] = fix(6 + yzhi)
    pos["龙池"] = fix(4 + yzhi)
    pos["凤阁"] = fix(10 - yzhi)
    pos["台辅"] = fix(6 + h)
    pos["封诰"] = fix(2 + h)
    pos["天伤"] = fix(ming + 6)   # 命前六位
    pos["天使"] = fix(ming - 6)   # 命后六位

    # 四化
    lu_x, quan_x, ke_x, ji_x = SIHUA[GAN[ygan]]
    hua = {}
    for star, kind in ((lu_x, "禄"), (quan_x, "权"), (ke_x, "科"), (ji_x, "忌")):
        if star in pos:
            hua.setdefault(pos[star], []).append(star + "化" + kind)

    # 十二宫
    stars_at = {}
    for star, idx in pos.items():
        stars_at.setdefault(idx, []).append(star)

    palaces = []
    for b in range(12):
        off = (b - ming) % 12
        palaces.append({
            "branch": ZHI[b],
            "gan": GAN[(yin_gan + (b - 2) % 12) % 10],
            "name": PALACE_NAMES[off],
            "is_shen": b == shen,
            "main": [s for s in stars_at.get(b, []) if s in
                     ("紫微", "天机", "太阳", "武曲", "天同", "廉贞",
                      "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军")],
            "aux": [s for s in stars_at.get(b, []) if s not in
                    ("紫微", "天机", "太阳", "武曲", "天同", "廉贞",
                     "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军")],
            "hua": hua.get(b, []),
        })

    # 大限
    forward = (is_yang(ygan) and gender == "m") or ((not is_yang(ygan)) and gender == "f")
    daxian = []
    for k in range(12):
        b = fix(ming + (k if forward else -k))
        pal = next(p for p in palaces if p["branch"] == ZHI[b])
        daxian.append({
            "age_start": ju_num + k * 10, "age_end": ju_num + k * 10 + 9,
            "branch": ZHI[b], "palace": pal["name"], "stars": pal["main"],
        })

    return {
        "ming": ZHI[ming], "shen": ZHI[shen],
        "ming_gan": GAN[ming_gan], "ju": ju_name, "ju_num": ju_num,
        "ziwei": ZHI[ziwei_zi], "tianfu": ZHI[tianfu_zi],
        "palaces": palaces, "daxian": daxian,
        "forward": forward,
    }


# ---------------------------------------------------------------- 神煞

TIANYI = {  # 日干 → 天乙贵人（两支）
    "甲": "丑未", "乙": "子申", "丙": "亥酉", "丁": "亥酉", "戊": "丑未",
    "己": "子申", "庚": "丑未", "辛": "寅午", "壬": "卯巳", "癸": "卯巳",
}
WENCHANG = {"甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
            "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}
YANGREN = {"甲": "卯", "乙": "寅", "丙": "午", "丁": "巳", "戊": "午",
           "己": "巳", "庚": "酉", "辛": "申", "壬": "子", "癸": "亥"}
LUSHEN = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
          "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
TAOHUA = {"申": "酉", "子": "酉", "辰": "酉", "寅": "卯", "午": "卯", "戌": "卯",
          "巳": "午", "酉": "午", "丑": "午", "亥": "子", "卯": "子", "未": "子"}
YIMA = {"申": "寅", "子": "寅", "辰": "寅", "寅": "申", "午": "申", "戌": "申",
        "巳": "亥", "酉": "亥", "丑": "亥", "亥": "巳", "卯": "巳", "未": "巳"}
HUAGAI = {"申": "辰", "子": "辰", "辰": "辰", "巳": "丑", "酉": "丑", "丑": "丑",
          "寅": "戌", "午": "戌", "戌": "戌", "亥": "未", "卯": "未", "未": "未"}


def shensha(b):
    out = []
    dg = GAN[b["day_gan"]]
    branches = [ZHI[p[2]] for p in
                [("", b["year_gan"], b["year_zhi"]), ("", b["month_gan"], b["month_zhi"]),
                 ("", b["day_gan"], b["day_zhi"]), ("", b["hour_gan"], b["hour_zhi"])]]
    names = ["年", "月", "日", "时"]

    def mark(star, targets):
        hit = [names[i] for i, z in enumerate(branches) if z in targets]
        if hit:
            out.append("%s在%s支" % (star, "、".join(hit)))

    mark("天乙贵人", TIANYI[dg])
    mark("文昌", WENCHANG[dg])
    mark("羊刃", YANGREN[dg])
    mark("禄神", LUSHEN[dg])
    mark("桃花", TAOHUA[ZHI[b["year_zhi"]]])
    mark("驿马", YIMA[ZHI[b["year_zhi"]]])
    mark("华盖", HUAGAI[ZHI[b["year_zhi"]]])
    return out


# ---------------------------------------------------------------- 渲染

def render(data):
    b = data["bazi"]
    z = data["ziwei"]
    L = []
    L.append("命盘推演 · %s · %s · 经度 %.2fE" % (
        data["dt_std"].strftime("%Y-%m-%d %H:%M"),
        "男" if data["gender"] == "m" else "女", data["lon"]))
    L.append("真太阳时 %s" % b["dt_true"].strftime("%Y-%m-%d %H:%M"))
    lu = data["lunar"]
    ly = data["lunar"]["year"]
    L.append("农历 %s年（%s干支年）%s%s月%s日 %s时" % (
        cn_year(ly), GAN[b["year_gan"]] + ZHI[b["year_zhi"]],
        "闰" if lu["leap"] else "", cn_num(lu["month"]), cn_num(lu["day"]),
        ZHI[b["hour_zhi"]]))
    L.append("")
    L.append("【四柱】")
    L.append("       年柱    月柱    日柱    时柱")
    for key, label in (("gan", "天干"), ("zhi", "地支")):
        L.append("%s   " % label + "  ".join("  %s    " % p[key] for p in b["pillars"]))
    L.append("藏干   " + "  ".join(" ".join(c["gan"] for c in p["cang"]).ljust(6) for p in b["pillars"]))
    L.append("十神   " + "  ".join(p["gan_shishen"].ljust(6) for p in b["pillars"]))
    L.append("纳音   " + "  ".join(p["nayin"].ljust(6) for p in b["pillars"]))
    L.append("旬空   " + "  ".join(p["xunkong"].ljust(6) for p in b["pillars"]))
    L.append("")
    wx = b["wx_count"]
    L.append("【五行】" + "  ".join("%s%.1f" % (k, wx[k]) for k in "木火土金水"))
    L.append("【日主】%s%s（%s），生于%s月" % (
        GAN[b["day_gan"]], GAN_WX[b["day_gan"]],
        "阳" if is_yang(b["day_gan"]) else "阴", ZHI[b["month_zhi"]]))
    L.append("")
    L.append("【大运】%s行，起运 %.1f 岁（%d岁%d个月）" % (
        "顺" if b["forward"] else "逆", b["start_age"], b["start_years"], b["start_months"]))
    for d in b["dayun"]:
        L.append("  %5.1f-%5.1f岁 %s年 %s%s（%s）藏干 %s" % (
            d["age_start"], d["age_end"], d["year_start"], d["gan"], d["zhi"],
            d["shishen"], " ".join(c["gan"] + c["shishen"] for c in d["cang"])))
    ss = shensha(b)
    if ss:
        L.append("【神煞】" + "；".join(ss))
    L.append("")
    L.append("【紫微】命宫 %s（%s%s） 身宫 %s 五行局 %s 紫微在%s 天府在%s" % (
        z["ming"], z["ming_gan"], z["ming"], z["shen"], z["ju"], z["ziwei"], z["tianfu"]))
    L.append("")
    for p in z["palaces"]:
        line = "%s%s %s%s" % (p["gan"], p["branch"], p["name"], "·身" if p["is_shen"] else "")
        line = line.ljust(14)
        stars = " ".join(p["main"]) if p["main"] else "（空宫）"
        aux = " ".join(p["aux"] + p["hua"])
        L.append("  " + line + stars + ("   " + aux if aux else ""))
    L.append("")
    L.append("【大限】%s行" % ("顺" if z["forward"] else "逆"))
    for d in z["daxian"]:
        L.append("  %2d-%2d岁 %s%s（%s） %s" % (
            d["age_start"], d["age_end"], "", d["branch"], d["palace"], " ".join(d["stars"])))
    return "\n".join(L)


def cn_year(y):
    d = "〇一二三四五六七八九"
    return "".join(d[int(c)] for c in str(y))


def cn_num(n):
    d = "〇一二三四五六七八九"
    if n <= 10:
        return d[n] if n < 10 else "十"
    if n < 20:
        return "十" + d[n % 10]
    if n < 30:
        return "廿" + (d[n % 10] if n % 10 else "")
    return d[n // 10] + "十" + (d[n % 10] if n % 10 else "")


# ---------------------------------------------------------------- 入口

def main():
    ap = argparse.ArgumentParser(description="八字四柱 + 紫微斗数排盘")
    ap.add_argument("--date", required=True, help="公历生日 YYYY-MM-DD")
    ap.add_argument("--time", default="12:00", help="出生钟表时间 HH:MM（当地标准时）")
    ap.add_argument("--gender", default="m", choices=["m", "f"], help="m男 f女")
    ap.add_argument("--lon", type=float, default=None, help="出生地经度（东经为正）")
    ap.add_argument("--city", default=None, help="出生城市，自动取经度（见 CITY_LON）")
    ap.add_argument("--leap", default="same", choices=["same", "next"], help="闰月处理")
    ap.add_argument("--liunian", type=int, action="append", default=[],
                    help="指定流年（可重复），如 --liunian 2026")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    if args.lon is None:
        if args.city:
            if args.city not in CITY_LON:
                sys.exit("未收录城市：%s。请改用 --lon 指定经度。" % args.city)
            args.lon = CITY_LON[args.city]
        else:
            sys.stderr.write("提示：未给经度，按 120E 计算，真太阳时可能有偏差。\n")
            args.lon = 120.0

    y, m, d = [int(x) for x in args.date.split("-")]
    hh, mm = [int(x) for x in args.time.split(":")]
    dt = datetime(y, m, d, hh, mm)

    b = build_bazi(dt, args.lon, args.gender)
    lu = lunar_of(b["dt_true"])
    ly = lu["year"]
    ly_gan, ly_zhi = (ly - 4) % 10, (ly - 4) % 12
    z = build_ziwei(lu, b["hour_zhi"], ly_gan, ly_zhi, args.gender, args.leap)

    data = {
        "dt_std": dt, "dt_true": b["dt_true"], "gender": args.gender,
        "lon": args.lon, "lunar": lu, "bazi": b, "ziwei": z,
    }

    if args.liunian and not args.json:
        L = render(data).split("\n")
        L.append("")
        L.append("【流年】")
        for yr in args.liunian:
            idx = (yr - 4) % 60
            g, z = idx % 10, idx % 12
            age = yr - dt.year + 1
            step = None
            for d in b["dayun"]:
                if d["year_start"] <= yr < d["year_start"] + 10:
                    step = d
            L.append("  %d年 %s%s（%s）%d岁 大运 %s %s 紫微流年宫 %s" % (
                yr, GAN[g], ZHI[z], shishen(b["day_gan"], g), age,
                step["ganzhi"] if step else "未起运",
                step["shishen"] if step else "",
                ZHI[z]))
        print("\n".join(L))
        return

    if args.json:
        def enc(o):
            if isinstance(o, datetime):
                return o.strftime("%Y-%m-%d %H:%M:%S")
            raise TypeError
        print(json.dumps(data, ensure_ascii=False, indent=2, default=enc))
    else:
        print(render(data))


if __name__ == "__main__":
    main()
