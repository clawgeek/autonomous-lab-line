# -*- coding: utf-8 -*-
"""封面合成：AI 主视觉 + 程序化排版（文字用系统字体渲染，不会糊）"""

import os
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080
YAHEI = 'C:/Windows/Fonts/msyhbd.ttc'
YAHEI_R = 'C:/Windows/Fonts/msyh.ttc'
MONO = 'C:/Windows/Fonts/consolab.ttf'

GA = (22, 224, 137)      # 强调绿
CY = (86, 168, 255)      # 冷蓝


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.truetype(YAHEI_R, size)


def crop_fill(im, w, h):
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im = im.resize((int(iw * s + 0.5), int(ih * s + 0.5)), Image.LANCZOS)
    iw, ih = im.size
    x = (iw - w) // 2
    y = int((ih - h) * 0.30)          # 略偏上，保住机器人头部
    return im.crop((x, y, x + w, y + h))


def build(src, out):
    base = Image.open(src).convert('RGB')
    # 先切掉生成水印：原图 1536x1024 → 取上部 16:9
    iw, ih = base.size
    base = base.crop((0, 0, iw, int(iw * 9 / 16)))
    im = crop_fill(base, W, H)

    # 左侧压暗（给标题留空间）
    dark = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(dark)
    for x in range(W):
        u = x / float(W)
        if u < 0.14:
            a = 248
        elif u > 0.66:
            a = 0
        else:
            a = int(248 * (1 - ((u - 0.14) / 0.52)) ** 1.45)
        d.line([(x, 0), (x, H)], fill=a)
    black = Image.new('RGB', (W, H), (6, 9, 13))
    im = Image.composite(black, im, dark)
    # 底部压暗
    grad = Image.new('L', (W, H), 0)
    dg = ImageDraw.Draw(grad)
    for y in range(int(H * 0.55), H):
        dg.line([(0, y), (W, y)], fill=int(150 * (y - H * 0.55) / (H * 0.45)))
    im = Image.composite(Image.new('RGB', (W, H), (5, 8, 12)), im, grad)

    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.10)

    dr = ImageDraw.Draw(im, 'RGBA')

    # ---- 顶部小标 ----
    f_kick = font(MONO, 26)
    dr.text((104, 96), 'SELF-DRIVING LAB  /  LINE TEARDOWN', font=f_kick, fill=(160, 178, 196))
    dr.rectangle([104, 140, 172, 145], fill=GA)

    # ---- 主标题 ----
    f_h1 = font(YAHEI, 122)
    dr.text((100, 196), '自主实验室', font=f_h1, fill=(255, 255, 255))
    dr.text((100, 330), '产线拆解', font=f_h1, fill=(255, 255, 255))

    # 绿色下划强调
    dr.rectangle([104, 486, 470, 496], fill=GA)

    # ---- 副标 ----
    f_h2 = font(YAHEI, 54)
    dr.text((102, 530), '十台工站 · 七轴协作', font=f_h2, fill=(232, 240, 247))

    f_en = font(MONO, 30)
    dr.text((104, 604), 'TEN STATIONS  /  7-AXIS  /  RECOMPUTABLE',
            font=font(MONO, 27), fill=(148, 168, 186))

    # ---- 数据条 ----
    chips = [('10', '移液工站'), ('0.923', '七轴臂展 m'), ('16.8', '一阶频率 Hz')]
    x = 104
    for val, lab in chips:
        f_v = font(MONO, 46)
        f_l = font(YAHEI_R, 22)
        dr.text((x, 700), val, font=f_v, fill=GA)
        dr.text((x, 762), lab, font=f_l, fill=(150, 168, 186))
        x += 214
    dr.rectangle([104, 690, 104 + 660, 694], fill=(255, 255, 255, 40))

    # ---- 右下角标记 ----
    f_badge = font(YAHEI, 30)
    txt = '逐帧拆解 · 工程档案同源'
    tw = dr.textlength(txt, font=f_badge)
    dr.rounded_rectangle([W - tw - 150, H - 132, W - 92, H - 64], 8,
                         fill=(10, 14, 18, 170), outline=(86, 168, 255, 120), width=2)
    dr.text((W - tw - 121, H - 118), txt, font=f_badge, fill=(214, 228, 240))

    im.save(out, quality=95)
    print('cover →', out, im.size)


if __name__ == '__main__':
    srcs = sorted(glob.glob(os.path.join(BASE, 'cover_raw', '*.png')))
    build(srcs[0], os.path.join(BASE, 'cover.png'))
