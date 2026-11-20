# -*- coding: utf-8 -*-
"""生成毕业设计插图：图1 三因子级联认证流程图 / 图2 系统模块框图"""
from PIL import Image, ImageDraw, ImageFont

S = 2  # 缩放倍数：逻辑坐标 -> 像素
FONT_B = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_R = "/System/Library/Fonts/Hiragino Sans GB.ttc"

_C = {}


def f(path, size, bold=False):
    key = (path, size, bold)
    if key not in _C:
        _C[key] = ImageFont.truetype(path, int(size * S))
    return _C[key]


def px(v):
    return int(round(v * S))


# ---------- 颜色 ----------
INK = "#16283F"
NAVY = "#2F5D9E"
NAVY_F = "#EAF1FB"
AMBER = "#C88A2B"
AMBER_F = "#FFF7E6"
GREEN = "#2E8B57"
GREEN_F = "#E9F5EC"
RED = "#C0392B"
RED_F = "#FDECEA"
DARK_RED = "#8E2F26"
DARK_RED_F = "#F7E5E2"
GREY = "#8A97A8"
LINE = "#4A5A70"


def canvas(w, h, bg="white"):
    img = Image.new("RGB", (px(w), px(h)), bg)
    return img, ImageDraw.Draw(img)


def text_block(d, cx, cy, lines, size=16, fill=INK, bold=False, lh=1.45, font=None):
    ft = font or f(FONT_B if bold else FONT_R, size)
    n = len(lines)
    step = size * lh
    y0 = cy - (n - 1) * step / 2
    for i, ln in enumerate(lines):
        d.text((px(cx), px(y0 + i * step)), ln, font=ft, fill=fill, anchor="mm")


def box(d, x0, y0, x1, y1, lines, size=16, fill=NAVY_F, border=NAVY,
        bold=False, r=10, width=1.6, txtfill=None):
    d.rounded_rectangle([px(x0), px(y0), px(x1), px(y1)], radius=px(r),
                        fill=fill, outline=border, width=px(width))
    text_block(d, (x0 + x1) / 2, (y0 + y1) / 2, lines, size=size,
               fill=txtfill or INK, bold=bold)


def diamond(d, cx, cy, w, h, lines, size=15, fill=AMBER_F, border=AMBER, bold=False):
    pts = [(px(cx), px(cy - h / 2)), (px(cx + w / 2), px(cy)),
           (px(cx), px(cy + h / 2)), (px(cx - w / 2), px(cy))]
    d.polygon(pts, fill=fill, outline=border, width=px(1.6))
    text_block(d, cx, cy, lines, size=size, bold=bold)


def arrow(d, pts, color=LINE, width=1.7, head=9):
    p = [(px(x), px(y)) for x, y in pts]
    d.line(p, fill=color, width=px(width), joint="curve")
    (x0, y0), (x1, y1) = p[-2], p[-1]
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    hs = px(head) * 1.6
    a1 = (x1 - hs * math.cos(ang - 0.4), y1 - hs * math.sin(ang - 0.4))
    a2 = (x1 - hs * math.cos(ang + 0.4), y1 - hs * math.sin(ang + 0.4))
    d.polygon([(x1, y1), a1, a2], fill=color)


def label(d, x, y, s, size=13, fill="#6B7A8F", anchor="lm", bold=False):
    d.text((px(x), px(y)), s, font=f(FONT_B if bold else FONT_R, size),
           fill=fill, anchor=anchor)


def vlabel(img, x, y, s, size=13, fill="#6B7A8F"):
    """竖排文字（自下而上），(x, y) 为文字块中心"""
    ft = f(FONT_R, size)
    bb = ft.getbbox(s)
    w, h = bb[2] - bb[0] + 8, bb[3] - bb[1] + 8
    tmp = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    td = ImageDraw.Draw(tmp)
    td.text((4 - bb[0], 4 - bb[1]), s, font=ft, fill=fill)
    rot = tmp.rotate(90, expand=True)
    img.paste(rot, (px(x - rot.width / 2 / S), px(y - rot.height / 2 / S)), rot)


def title(d, s, sub=None):
    d.text((px(660), px(34)), s, font=f(FONT_B, 25, True), fill=INK, anchor="mm")
    if sub:
        d.text((px(660), px(66)), sub, font=f(FONT_R, 14), fill="#6B7A8F", anchor="mm")


# ============================================================
# 图1  三因子级联认证流程图
# ============================================================
def fig1(path):
    W, H = 1320, 1352
    img, d = canvas(W, H)
    title(d, "图 1   多重验证门禁系统三因子级联认证流程",
          "认证顺序：RFID 卡（持有物）→ PIN 密码（知识）→ 指纹（生物特征）；任一环节失败或超时进入右侧异常处理分支")

    MC = 360          # 主流程中轴
    BUS = 660         # 异常汇流母线

    # 主流程
    box(d, 120, 88, 600, 142, ["上电初始化：OLED / 键盘 / RC522 / AS608 / 存储 / RTC"],
        size=15, bold=True)
    arrow(d, [(MC, 142), (MC, 178)])
    box(d, 120, 180, 600, 234, ["待机：RC522 轮询寻卡，等待刷卡"],
        size=16, bold=True)
    arrow(d, [(MC, 234), (MC, 240)])

    diamond(d, MC, 294, 330, 108, ["卡 UID 已登记且状态正常？"], size=15)
    arrow(d, [(MC, 348), (MC, 384)])

    box(d, 100, 386, 620, 464,
        ["一级通过：开启 10 s 认证窗口", "OLED 倒计时 / LED 提示输入 PIN"], size=16)
    arrow(d, [(MC, 464), (MC, 470)])

    diamond(d, MC, 524, 340, 108, ["窗口内输入 PIN 且校验正确？"], size=15)
    arrow(d, [(MC, 578), (MC, 614)])

    box(d, 100, 616, 620, 694,
        ["二级通过：进入第三因子", "提示按压指纹（AS608 模板搜索）"], size=16)
    arrow(d, [(MC, 694), (MC, 700)])

    diamond(d, MC, 754, 330, 108, ["指纹模板匹配成功？"], size=15)
    arrow(d, [(MC, 808), (MC, 844)])

    box(d, 100, 846, 620, 924,
        ["三级通过：继电器吸合，电磁锁动作 3 s", "OLED / LED / 蜂鸣器提示成功"], size=16,
        fill=GREEN_F, border=GREEN, bold=True)
    arrow(d, [(MC, 924), (MC, 960)])
    box(d, 120, 962, 600, 1024,
        ["写入成功日志（用户 / 时间 / 各级耗时）"], size=16, fill=GREEN_F, border=GREEN)
    arrow(d, [(MC, 1024), (MC, 1060)])
    box(d, 120, 1062, 600, 1118,
        ["失败计数清零，返回待机"], size=16, fill=GREEN_F, border=GREEN)
    arrow(d, [(MC, 1118), (MC, 1164)])
    box(d, 200, 1166, 520, 1220, ["返回待机 · 轮询下一张卡"], size=15,
        fill="#F1F4F9", border=GREY, bold=True)

    # 右侧异常处理
    box(d, 700, 400, 1180, 470,
        ["失败计数 +1；蜂鸣器短鸣", "OLED 显示失败原因"], size=16,
        fill=RED_F, border=RED, bold=True)
    arrow(d, [(940, 470), (940, 510)])
    box(d, 700, 512, 1180, 580,
        ["写入失败日志（时间 / 卡 UID / 阶段 / 原因）"], size=16, fill=RED_F, border=RED)
    arrow(d, [(940, 580), (940, 604)])
    diamond(d, 940, 656, 320, 108, ["连续失败次数 ≥ 3？"], size=15,
            fill=DARK_RED_F, border=DARK_RED)
    arrow(d, [(940, 710), (940, 746)])
    box(d, 700, 748, 1180, 828,
        ["锁定终端 60～300 s；蜂鸣器长鸣", "日志标记「可疑」并高亮"], size=16,
        fill=DARK_RED_F, border=DARK_RED, bold=True)
    arrow(d, [(940, 828), (940, 864)])
    box(d, 700, 866, 1180, 926, ["锁定计时结束，自动解除"], size=16,
        fill="#F1F4F9", border=GREY)

    # 异常汇流母线：自 D1 向下贯通所有失败出口，并从 y=435 处进入失败处理
    d.line([(px(BUS), px(294)), (px(BUS), px(754))], fill=RED, width=px(1.7))
    for y in (294, 524, 754):
        d.line([(px(525 if y == 294 else 520), px(y)), (px(BUS), px(y))],
               fill=RED, width=px(1.7))
        d.ellipse([px(BUS - 4), px(y - 4), px(BUS + 4), px(y + 4)], fill=RED)
    arrow(d, [(BUS, 435), (700, 435)], color=RED)

    # 失败原因标注
    label(d, 528, 276, "否：非法卡 / 已锁卡", 13, RED)
    label(d, 528, 506, "超时 → 窗口超时", 13, RED)
    label(d, 528, 540, "错误 → PIN 错误", 13, RED)
    label(d, 528, 736, "否：指纹不符", 13, RED)

    # 失败后返回待机（右侧外环）
    arrow(d, [(1180, 896), (1272, 896), (1272, 1193), (522, 1193)], color=GREY, head=9)
    vlabel(img, 1288, 1045, "锁定解除后返回待机", 12, "#8A97A8")

    # 左侧主循环返回
    arrow(d, [(200, 1193), (56, 1193), (56, 207), (118, 207)], color=NAVY, head=9)
    vlabel(img, 40, 700, "主循环：返回待机轮询", 12, NAVY)

    # 图例
    ly = 1272
    d.rounded_rectangle([px(60), px(ly - 26), px(1260), px(ly + 26)], radius=px(8),
                        fill="#FAFBFD", outline="#D8E0EA", width=px(1.2))
    d.rounded_rectangle([px(78), px(ly - 12), px(118), px(ly + 12)], radius=px(5),
                        fill=NAVY_F, outline=NAVY, width=px(1.2))
    label(d, 128, ly, "处理步骤", 13, INK)
    diamond(d, 300, ly, 56, 30, [], size=1, fill=AMBER_F, border=AMBER)
    label(d, 334, ly, "判断", 13, INK)
    d.line([(px(410), px(ly)), (px(462), px(ly))], fill=RED, width=px(1.8))
    label(d, 472, ly, "异常分支", 13, INK)
    d.line([(px(570), px(ly)), (px(622), px(ly))], fill=NAVY, width=px(1.8))
    label(d, 632, ly, "正常流程", 13, INK)
    d.rounded_rectangle([px(742), px(ly - 12), px(782), px(ly + 12)], radius=px(5),
                        fill=GREEN_F, outline=GREEN, width=px(1.2))
    label(d, 792, ly, "认证通过 / 开锁", 13, INK)
    d.rounded_rectangle([px(920), px(ly - 12), px(960), px(ly + 12)], radius=px(5),
                        fill=DARK_RED_F, outline=DARK_RED, width=px(1.2))
    label(d, 970, ly, "锁定 / 可疑行为", 13, INK)
    label(d, 1100, ly, "注：窗口 10 s 为待整定值", 12, "#8A97A8")

    img.save(path, dpi=(300, 300))
    print("saved", path, img.size)


# ============================================================
# 图2  系统模块框图
# ============================================================
def fig2(path):
    W, H = 1320, 952
    img, d = canvas(W, H)
    title(d, "图 2   多重验证门禁系统硬件模块与接口框图",
          "箭头旁为接口类型；虚线框为功能分区")

    def zone(x0, y0, x1, y1, name):
        for xx in range(px(x0), px(x1), px(12)):
            d.line([(xx, px(y0)), (min(xx + 6, px(x1)), px(y0))], fill="#C6D0DC", width=px(1.4))
            d.line([(xx, px(y1)), (min(xx + 6, px(x1)), px(y1))], fill="#C6D0DC", width=px(1.4))
        for yy in range(px(y0), px(y1), px(12)):
            d.line([(px(x0), yy), (px(x0), min(yy + 6, px(y1)))], fill="#C6D0DC", width=px(1.4))
            d.line([(px(x1), yy), (px(x1), min(yy + 6, px(y1)))], fill="#C6D0DC", width=px(1.4))
        label(d, x0 + 10, y0 - 12, name, 13, "#7C8B9E", bold=True)

    zone(40, 130, 400, 560, "感知 / 输入层")
    zone(440, 130, 900, 700, "控制层（STM32F103C8T6）")
    zone(940, 130, 1280, 548, "输出 / 执行层")
    zone(440, 730, 1280, 900, "通信 / 应用层")

    # 输入模块
    box(d, 60, 160, 380, 216, ["4×4 矩阵键盘"], size=16)
    label(d, 220, 238, "GPIO 扫描 / 防抖", 12, "#6B7A8F", anchor="mm")
    box(d, 60, 262, 380, 318, ["RC522 读卡模块（13.56 MHz）"], size=16)
    label(d, 220, 340, "SPI1 / 3.3 V", 12, "#6B7A8F", anchor="mm")
    box(d, 60, 364, 380, 420, ["AS608 指纹模块"], size=16)
    label(d, 220, 442, "USART2 / 57600 bps", 12, "#6B7A8F", anchor="mm")
    box(d, 60, 466, 380, 522, ["DS1302 实时时钟"], size=16)
    label(d, 220, 544, "三线接口 / 掉电走时", 12, "#6B7A8F", anchor="mm")

    # 主控
    d.rounded_rectangle([px(440), px(130), px(900), px(700)], radius=px(12),
                        fill="#F7FAFE", outline=NAVY, width=px(2.2))
    d.text((px(670), px(162)), "STM32F103C8T6  主控", font=f(FONT_B, 19, True),
           fill=NAVY, anchor="mm")
    inner = [
        (452, 190, 888, 268, ["认证状态机", "IDLE→F1→窗口→F2→F3→GRANT / LOCKOUT"], NAVY_F, NAVY),
        (452, 284, 888, 352, ["用户与权限管理", "卡 UID / 指纹 ID / PIN 哈希 / 角色"], NAVY_F, NAVY),
        (452, 368, 888, 436, ["窗口定时器（1 ms 节拍）", "非阻塞计时，超时即复位"], NAVY_F, NAVY),
        (452, 452, 888, 520, ["日志环形缓冲 + 断网补传"], NAVY_F, NAVY),
        (452, 536, 888, 604, ["内部 Flash 存储", "用户表 / 参数 / 日志"], "#F2F6FC", NAVY),
        (452, 620, 888, 680, ["电源管理与抗冲击设计"], "#F2F6FC", NAVY),
    ]
    for x0, y0, x1, y1, lines, fl, bd in inner:
        box(d, x0, y0, x1, y1, lines, size=15, fill=fl, border=bd, r=8, width=1.4)

    # 输出模块
    box(d, 960, 160, 1260, 216, ["OLED 0.96″ 显示屏"], size=16)
    label(d, 1110, 238, "I2C1：阶段 / 倒计时", 12, "#6B7A8F", anchor="mm")
    box(d, 960, 262, 1260, 318, ["三色 LED + 有源蜂鸣器"], size=16,
        fill=AMBER_F, border=AMBER)
    label(d, 1110, 340, "GPIO / PWM：分级提示", 12, "#6B7A8F", anchor="mm")
    box(d, 960, 364, 1260, 430, ["继电器（光耦隔离）"], size=16,
        fill=AMBER_F, border=AMBER)
    arrow(d, [(1110, 430), (1110, 452)], color=LINE)
    box(d, 960, 454, 1260, 510, ["12 V 电磁锁（断电开锁）"], size=15,
        fill=AMBER_F, border=AMBER, bold=True)
    label(d, 1110, 532, "独立 12 V 供电 + 续流二极管", 12, "#6B7A8F", anchor="mm")

    # 通信 / 应用
    box(d, 460, 760, 760, 830, ["ESP-01S（Wi-Fi 透传）", "AT 指令 / HTTP POST"], size=15)
    arrow(d, [(830, 795), (900, 795)], color=LINE)
    box(d, 900, 750, 1260, 840,
        ["Web 后台（React + Supabase）", "用户管理 / 通行日志 / 异常高亮 / 导出"], size=15,
        fill=GREEN_F, border=GREEN)
    label(d, 866, 775, "USART3", 12, "#6B7A8F", anchor="mm")
    label(d, 866, 818, "Wi-Fi", 12, "#6B7A8F", anchor="mm")

    # 连接线（输入 -> 主控）
    for y in (188, 290, 392, 494):
        arrow(d, [(382, y), (438, y)], color=LINE)

    # 主控 <-> 输出
    for y in (188, 290, 397):
        arrow(d, [(902, y), (958, y)], color=LINE)

    # 主控 -> ESP
    arrow(d, [(670, 702), (670, 758)], color=LINE)
    # 主控 <-> Flash 已在内框体现

    # 供电说明
    d.rounded_rectangle([px(60), px(636), px(410), px(778)], radius=px(8),
                        fill="#FBFCFE", outline="#D8E0EA", width=px(1.2))
    d.text((px(78), px(658)), "供电设计", font=f(FONT_B, 14, True), fill=INK, anchor="lm")
    for i, s in enumerate(["12 V / 2 A 适配器分路：",
                           "12 V → 电磁锁（经继电器）",
                           "5 V → 继电器 / 键盘 / OLED",
                           "3.3 V → 主控 / RC522 / ESP-01S",
                           "单点共地，锁线圈反并 1N4007"]):
        d.text((px(78), px(690 + i * 17)), s, font=f(FONT_R, 12), fill="#5A6B80", anchor="lm")

    # 技术栈说明
    d.rounded_rectangle([px(60), px(800), px(410), px(902)], radius=px(8),
                        fill="#FBFCFE", outline="#D8E0EA", width=px(1.2))
    d.text((px(78), px(822)), "软件与后台", font=f(FONT_B, 14, True), fill=INK, anchor="lm")
    for i, s in enumerate(["固件：C + HAL + 1 ms 非阻塞状态机",
                           "后台：React + TypeScript + Supabase",
                           "通信：HTTP + JSON（断网补传）"]):
        d.text((px(78), px(852 + i * 17)), s, font=f(FONT_R, 12), fill="#5A6B80", anchor="lm")

    img.save(path, dpi=(300, 300))
    print("saved", path, img.size)


if __name__ == "__main__":
    import os
    BASE = os.path.dirname(os.path.abspath(__file__))
    OUT = os.path.abspath(os.path.join(BASE, "..", "out"))
    os.makedirs(OUT, exist_ok=True)
    fig1(os.path.join(OUT, "fig1-auth-flow.png"))
    fig2(os.path.join(OUT, "fig2-system-block.png"))
