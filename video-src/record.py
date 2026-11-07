# -*- coding: utf-8 -*-
"""
逐帧录制（确定性渲染）
========================
把时间轴交给页面：按 1/24 秒步进 + 截图，得到完全平滑的 24fps 序列。
不依赖浏览器帧率，构图与节拍完全可控。

用法：
    python record.py --preview     # 1fps 抽帧，检查构图（约 2 分钟）
    python record.py               # 完整渲染
"""
import os
import sys
import json
import time
import argparse

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from playwright.sync_api import sync_playwright           # noqa: E402

PAGE = 'http://127.0.0.1:8777/dist/final.html?vid=1&notour=1&vq=1'
W, H, FPS = 1920, 1080, 24

TL = json.load(open(os.path.join(BASE, 'timeline.json'), encoding='utf-8'))

# ---- 每段：机位 A → B（缓入缓出），以及 HUD 上要按亮的机位按钮 ----------------
SHOT_CAM = {
    'S1':  dict(view='ref',     a=(16.0, 0.72, 0.0, -1.5708, 0.055, 16.6),
                                b=(13.4, 0.78, 0.0, -1.6208, 0.062, 11.4)),
    'S2':  dict(view='top',     a=(7.0, 0.85, 0.0, -1.1708, 0.460, 17.0),
                                b=(10.5, 0.85, 0.0, -1.3108, 0.560, 16.0)),
    'S3':  dict(view='station', a=(7.80, 1.30, -2.15, 0.10, 0.100, 2.95),
                                b=(7.80, 1.08, -2.12, 0.16, 0.125, 2.30)),
    'S4':  dict(view='station', a=(7.80, 1.06, -2.10, 0.42, 0.120, 2.20),
                                b=(7.80, 1.00, -2.08, 0.56, 0.140, 1.95)),
    'S5':  dict(view='wide',    a=(11.0, 2.28, -2.08, 0.564, -0.270, 3.11),
                                b=(11.0, 2.24, -2.06, 0.620, -0.160, 2.60)),
    'S6':  dict(view='follow',  a=(4.60, 1.08, -1.20, 0.80, 0.100, 3.4),
                                b=(4.60, 0.96, -1.12, 1.02, 0.120, 2.6)),
    'S7':  dict(view='safety',  a=(2.60, 1.00, 0.20, -0.7708, 0.150, 5.8),
                                b=(3.60, 0.95, -0.20, -1.2308, 0.170, 4.6)),
    'S8':  dict(view='zones',   a=(18.30, 0.78, -0.90, 1.1708, 0.240, 9.6),
                                b=(18.30, 0.78, 0.90, 1.0508, 0.240, 9.0)),
    'S9':  dict(view='station', a=(7.80, 1.18, -2.15, 0.44, 0.130, 3.20),
                                b=(7.80, 1.12, -2.15, 0.52, 0.140, 2.90)),
    'S10': dict(view='wide',    a=(6.60, 0.95, 0.0, -2.2308, 0.150, 12.6),
                                b=(7.20, 0.92, 0.0, -2.1408, 0.165, 11.2)),
    'S11': dict(view='ref',     a=(10.0, 0.85, 0.0, -1.8708, 0.100, 13.0),
                                b=(16.0, 0.74, 0.0, -1.5708, 0.055, 17.2)),
}

#: 段落内即时动作（相对该段起点的秒数）
SHOT_CUES = {
    'S1':  [(0.0, dict(view='ref', cut='glass', ex=0.0, sel=-1, t=6.0))],
    'S2':  [(0.0, dict(view='top', t=20.0))],
    'S3':  [(0.0, dict(view='station', t=8.0))],
    'S4':  [(0.0, dict(t=30.0))],
    'S5':  [(0.0, dict(view='wide', t=0.0))],
    'S6':  [(0.0, dict(view='follow', t=13.0))],
    'S7':  [(0.0, dict(view='safety', t=20.0))],
    'S8':  [(0.0, dict(view='zones', t=30.0))],
    'S9':  [(0.0, dict(view='station', ex=0.0, cut='glass', sel=-1, t=14.0)),
            (1.70, dict(sel=1)),
            (8.70, dict(ex=0.62)),                       # 拖完锁住拆解状态
            (12.30, dict(cut='section', ex=0.62))],
    'S10': [(0.0, dict(view='wide', cut='glass', sel=-1, t=36.0))],
    'S11': [(0.0, dict(view='ref', t=44.0))],
}

#: S9 的界面操作脚本（相对秒）
UI_SCRIPT = [
    (1.05, 'move', 'pod'),
    (1.62, 'click', None),
    (6.15, 'move', 'slider'),
    (6.45, 'down', None),
    (8.55, 'up', None),
    (12.05, 'move', 'cut_section'),
    (12.42, 'click', None),
]
DRAG = (6.45, 8.55, 0.62)          # 滑块推动区间与目标值

CURSOR_JS = """
() => {
  if (document.getElementById('vc')) return;
  const s = document.createElement('style');
  s.textContent = `
  #vc{position:fixed;left:-200px;top:-200px;width:16px;height:16px;border-radius:50%;
      background:rgba(15,20,27,.78);border:2px solid #fff;
      box-shadow:0 3px 12px rgba(0,0,0,.5);pointer-events:none;z-index:9999;
      margin:-10px 0 0 -10px;transition:transform .12s ease}
  #vr{position:fixed;left:-200px;top:-200px;border-radius:50%;
      border:2px solid #16E089;pointer-events:none;z-index:9998;opacity:0}
  `;
  document.head.appendChild(s);
  const c = document.createElement('div'); c.id = 'vc'; document.body.appendChild(c);
  const r = document.createElement('div'); r.id = 'vr'; document.body.appendChild(r);
}
"""

TICK_JS = """
([dt, cx, cy, ring, show, v]) => {
  const c = document.getElementById('vc');
  if (c) {
    c.style.left = cx + 'px'; c.style.top = cy + 'px';
    c.style.opacity = show ? 1 : 0;
    c.style.transform = 'scale(' + ((ring >= 0 && ring < 0.22) ? 0.84 : 1) + ')';
  }
  const r = document.getElementById('vr');
  if (r) {
    if (ring >= 0 && ring <= 1) {
      const d = 16 + ring * 88;
      r.style.width = d + 'px'; r.style.height = d + 'px';
      r.style.left = cx + 'px'; r.style.top = cy + 'px';
      r.style.margin = (-d / 2) + 'px 0 0 ' + (-d / 2) + 'px';
      r.style.opacity = (1 - ring) * 0.8;
    } else { r.style.opacity = 0; }
  }
  if (v !== null) {
    const e = document.getElementById('ex');
    if (e) e.value = v * 100;
    window.__vid.apply({ ex: v });
  }
  window.__vid.step(dt);
}
"""


def ease(u):
    return u * u * (3 - 2 * u)


def cam_at(a, b, u):
    e = ease(max(0.0, min(1.0, u)))
    return [a[i] + (b[i] - a[i]) * e for i in range(6)]


def frame_boxes(pg):
    def box(sel):
        el = pg.query_selector(sel)
        if not el:
            return None
        b = el.bounding_box()
        return (b['x'] + b['width'] / 2, b['y'] + b['height'] / 2, b)
    return {
        'pod': (960, 470, None),
        'slider': box('#ex'),
        'cut_section': box('[data-cut="section"]'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--fps', type=int, default=0)
    ap.add_argument('--from', dest='f_from', type=float, default=0.0)
    ap.add_argument('--to', dest='f_to', type=float, default=0.0)
    args = ap.parse_args()

    fps = args.fps or FPS
    nframes = int(round(TL['total'] * fps))
    outdir = os.path.join(BASE, ('pv%d' % int(args.f_from)) if args.preview else 'frames')
    os.makedirs(outdir, exist_ok=True)

    # 逐帧机位表
    path = [None] * nframes
    for s in TL['shots']:
        cfg = SHOT_CAM[s['id']]
        f0 = int(round(s['start'] * fps))
        f1 = min(nframes, int(round(s['end'] * fps)))
        for f in range(f0, f1):
            path[f] = cam_at(cfg['a'], cfg['b'], (f - f0) / max(1, f1 - f0 - 1))

    cues = []
    for s in TL['shots']:
        f0 = int(round(s['start'] * fps))
        for rel, act in SHOT_CUES.get(s['id'], []):
            cues.append((f0 + int(round(rel * fps)), act))
    cues.sort(key=lambda x: x[0])

    s9 = next(s for s in TL['shots'] if s['id'] == 'S9')
    s9_f0 = int(round(s9['start'] * fps))

    step = fps if args.preview else 1
    print('总帧 %d（%d fps，%.1f s），每 %d 帧出一张 → %s'
          % (nframes, fps, TL['total'], step, outdir))

    t_begin = time.time()
    with sync_playwright() as p:
        br = p.chromium.launch(headless=False, args=['--force-device-scale-factor=1'])
        pg = br.new_page(viewport={'width': W, 'height': H})
        pg.on('pageerror', lambda e: print('PAGEERR', e))
        pg.goto(PAGE, wait_until='load')
        pg.wait_for_timeout(1800)
        pg.evaluate(CURSOR_JS)
        bx = frame_boxes(pg)
        print('  控件坐标:', {k: (v[:2] if v else None) for k, v in bx.items()})
        pg.evaluate('(p)=>window.__vid.setPath(p)', path)
        # 从中间开始时要先把帧号对齐，否则机位索引会和实际帧错开
        pg.evaluate('(n)=>{window.__vid.frame=n}', int(args.f_from * fps))

        # S9 光标轨迹（帧 → 位置）
        ui = []
        for rel, kind, tgt in UI_SCRIPT:
            ui.append((s9_f0 + int(round(rel * fps)), kind, tgt))
        ui.sort(key=lambda x: x[0])

        cur = (-200.0, -200.0)
        tgt_pos = (-200.0, -200.0)
        ui_i = 0
        click_f = -9999
        slider = bx['slider'][2] if bx['slider'] else None
        shown = 0

        ci = 0
        f_lo = int(args.f_from * fps)
        f_hi = nframes if args.f_to <= 0 else min(nframes, int(args.f_to * fps))
        for f in range(f_lo, f_hi):
            # 先在段边界执行画面指令（机位按钮 / 剖切 / 拆解 / 选中工站 / 时间跳转）
            while ci < len(cues) and cues[ci][0] <= f:
                pg.evaluate('(c)=>window.__vid.apply(c)', cues[ci][1])
                ci += 1
            while ui_i < len(ui) and ui[ui_i][0] <= f:
                _, kind, name = ui[ui_i]
                if kind == 'move' and name in bx and bx[name]:
                    if name == 'slider':
                        v0 = 0.0
                        tgt_pos = (slider['x'] + 7, slider['y'] + slider['height'] / 2)
                    else:
                        tgt_pos = (bx[name][0], bx[name][1])
                elif kind == 'click':
                    click_f = f
                ui_i += 1

            # 拖拽时滑块手柄跟着走
            v_drag = None
            d0 = s9_f0 + int(round(DRAG[0] * fps))
            d1 = s9_f0 + int(round(DRAG[1] * fps))
            if d0 <= f <= d1:
                v_drag = DRAG[2] * ease((f - d0) / max(1, d1 - d0))
                if slider:
                    tgt_pos = (slider['x'] + 7 + (slider['width'] - 14) * v_drag,
                               slider['y'] + slider['height'] / 2)

            # 平滑跟随
            k = 0.20 if args.preview else 0.22
            cur = (cur[0] + (tgt_pos[0] - cur[0]) * k,
                   cur[1] + (tgt_pos[1] - cur[1]) * k)
            ring = (f - click_f) / (fps * 0.42) if f >= click_f else -1
            if f % step == 0:
                pg.evaluate(TICK_JS, [1000.0 / fps, cur[0], cur[1], ring,
                                      cur[0] > 0, v_drag])
                pg.screenshot(type='jpeg', quality=92,
                              path=os.path.join(outdir, 'f%05d.jpg' % f))
                shown += 1
                if shown % 25 == 0:
                    el = time.time() - t_begin
                    print('  %5.1f%%  视频 %5.1fs  已用 %4.0fs  预计剩余 %4.0fs'
                          % (100.0 * f / nframes, f / fps, el,
                             el / shown * (nframes / step - shown)), flush=True)
            else:
                pg.evaluate(TICK_JS, [1000.0 / fps, cur[0], cur[1], ring,
                                      cur[0] > 0, v_drag])
        br.close()
    print('完成：%d 张，用时 %.0f 秒' % (shown, time.time() - t_begin))


if __name__ == '__main__':
    main()
