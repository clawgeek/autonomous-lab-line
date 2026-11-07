# -*- coding: utf-8 -*-
"""中英双语字幕（ASS）生成 —— 时间码直接来自每句音频的真实时长"""

import os
import json

BASE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(BASE, 'timeline.json'), encoding='utf-8'))

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,Microsoft YaHei,50,&H00FFFFFF,&H000000FF,&H00101418,&H78000000,-1,0,0,0,100,100,1.2,0,1,4.0,2.0,2,220,220,268,1
Style: EN,Consolas,32,&H00EDEDED,&H000000FF,&H00101418,&H78000000,0,0,0,0,100,100,0.6,0,1,3.0,1.4,2,220,220,214,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(x):
    if x < 0:
        x = 0
    h = int(x // 3600)
    m = int((x % 3600) // 60)
    s = x % 60
    return '%d:%02d:%05.2f' % (h, m, s)


def clean(t):
    return t.replace('&', '&&').replace('<', '(').replace('>', ')')


def main():
    lines = []
    n = 0
    for shot in TL['shots']:
        for c in shot['cues']:
            st = c['start']
            en = c['end'] + 0.16
            lines.append('Dialogue: 0,%s,%s,ZH,,0,0,0,,%s' % (ts(st), ts(en), clean(c['zh'])))
            lines.append('Dialogue: 0,%s,%s,EN,,0,0,0,,%s' % (ts(st), ts(en), clean(c['en'])))
            n += 1
    out = os.path.join(BASE, 'subs.ass')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(HEAD)
        f.write('\n'.join(lines))
        f.write('\n')
    print('字幕 %d 条（%d 行）→ %s' % (n, len(lines), out))
    print('末条结束:', lines[-1][:60])


if __name__ == '__main__':
    main()
