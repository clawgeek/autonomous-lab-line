# -*- coding: utf-8 -*-
"""成片合成：封面片头 + 3D 逐帧序列 + 配音 + 双语字幕"""

import os
import sys
import json
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import imageio_ffmpeg                                        # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
TL = json.load(open(os.path.join(BASE, 'timeline.json'), encoding='utf-8'))
FPS = 24
COVER = TL['cover']
TOTAL = TL['total']


def run(args, desc):
    r = subprocess.run(args, capture_output=True, text=True, cwd=BASE,
                       encoding='utf-8', errors='ignore')
    if r.returncode != 0:
        print('FFMPEG FAIL [%s]' % desc)
        print(r.stderr[-2000:])
        raise SystemExit(1)
    return r


def step_cover():
    out = os.path.join(BASE, 'clips', 'cover.mp4')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run([FF, '-y', '-loglevel', 'error',
         '-loop', '1', '-framerate', str(FPS), '-i', os.path.join(BASE, 'cover.png'),
         '-frames:v', '77',
         '-vf', "scale=2112:1188,zoompan=z='min(zoom+0.00055,1.09)'"
                ":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=%d" % FPS,
         '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS), out],
        'cover')
    return out


def step_main():
    out = os.path.join(BASE, 'clips', 'main.mp4')
    run([FF, '-y', '-loglevel', 'error',
         '-framerate', str(FPS), '-start_number', '77',
         '-i', os.path.join(BASE, 'frames', 'f%05d.jpg'),
         '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), out], 'main')
    return out


def step_concat(a, b):
    lst = os.path.join(BASE, 'clips', 'list.txt')
    with open(lst, 'w', encoding='utf-8') as f:
        f.write("file '%s'\n" % a.replace('\\', '/'))
        f.write("file '%s'\n" % b.replace('\\', '/'))
    out = os.path.join(BASE, 'clips', 'silent.mp4')
    run([FF, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', lst, '-c', 'copy', out], 'concat')
    return out


def step_final(silent):
    out = '产线拆解_项目介绍_1080p.mp4'
    fade_st = max(0.0, TOTAL - 1.6)
    # 用相对路径（cwd=BASE），避免 Windows 盘符冒号被滤镜当成参数分隔
    vf = "ass=subs.ass,fade=t=out:st=%.2f:d=1.4" % fade_st
    run([FF, '-y', '-loglevel', 'error',
         '-i', silent, '-i', os.path.join(BASE, 'narration.wav'),
         '-vf', vf,
         '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', str(FPS),
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
         '-shortest', '-movflags', '+faststart', out], 'final')
    return out


if __name__ == '__main__':
    n = len([x for x in os.listdir(os.path.join(BASE, 'frames')) if x.endswith('.jpg')])
    print('帧数 %d（%.2f s）  配音 %.2f s  封面 %.1f s'
          % (n, n / FPS, TOTAL - COVER - TL['end_hold'], COVER))
    c = step_cover();   print('  片头 ok')
    m = step_main();    print('  正片 ok')
    s = step_concat(c, m); print('  拼接 ok')
    f = step_final(s);  print('成片 →', f)
    print('  大小 %.1f MB' % (os.path.getsize(os.path.join(BASE, f)) / 1e6))
