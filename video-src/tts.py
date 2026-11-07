# -*- coding: utf-8 -*-
"""
TTS 合成 + 时间轴生成
=====================
逐句合成 → 去掉首尾静音 → 拼接为单轨 → 输出 timeline.json

坑位（实测结论）：
  · 端点是 {BASE}/audio/speech，参数名 voice（不是 voice_id）
  · 每句必须是以句号收尾的完整句
  · 合成结果自带 0.2~0.3s 前导静音，不剪会让字幕比语音抢跑
"""
import os
import sys
import json
import time
import wave
import array
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import narration as N                                        # noqa: E402
import imageio_ffmpeg                                        # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
API_BASE = 'https://api.hcnsec.cn/v1'
API_KEY = os.environ.get(
    'HCNSEC_API_KEY', 'sk-0qERgCPzslT4mR1ULnj0ZKYIfz1SkcdWtaBlN5R5NiPKH910')
MODEL = 'stepaudio-2.5-tts'
SR = 48000

AUDIO = os.path.join(BASE_DIR, 'audio')
os.makedirs(AUDIO, exist_ok=True)

COVER_HOLD = 3.2          # 封面停留（秒），配音从这之后开始
END_HOLD = 2.2


def synth(text, out_mp3, retries=4):
    body = json.dumps({
        'model': MODEL, 'input': text, 'voice': N.VOICE,
        'response_format': 'mp3', 'instruction': N.INSTRUCTION,
        'speed': N.TTS_SPEED, 'sample_rate': SR,
    }, ensure_ascii=False).encode('utf-8')
    for a in range(retries):
        try:
            req = urllib.request.Request(
                API_BASE + '/audio/speech', data=body, method='POST',
                headers={'Content-Type': 'application/json',
                         'Authorization': 'Bearer ' + API_KEY})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = r.read()
            if len(d) < 1200:
                raise RuntimeError('resp too small %d' % len(d))
            with open(out_mp3, 'wb') as f:
                f.write(d)
            return
        except Exception as e:                               # noqa: BLE001
            if a == retries - 1:
                raise
            print('    retry %d: %s' % (a + 1, e))
            time.sleep(2 ** a)


def to_wav(src, dst):
    import subprocess
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', src,
                    '-ac', '1', '-ar', str(SR), '-f', 'wav', dst], check=True)


def read_wav(p):
    with wave.open(p, 'rb') as w:
        n = w.getnframes()
        raw = w.readframes(n)
    a = array.array('h')
    a.frombytes(raw)
    return a


def trim(a, rel=0.02, pad=0.04):
    """按相对峰值阈值去掉首尾静音（留 pad 秒余量）"""
    peak = 0
    for v in a:
        if v > peak:
            peak = v
        elif -v > peak:
            peak = -v
    if peak == 0:
        return a
    th = peak * rel
    i0, i1 = 0, len(a) - 1
    while i0 < len(a) and -th < a[i0] < th:
        i0 += 1
    while i1 > i0 and -th < a[i1] < th:
        i1 -= 1
    p = int(pad * SR)
    i0 = max(0, i0 - p)
    i1 = min(len(a) - 1, i1 + p)
    return a[i0:i1 + 1]


def main():
    shots, cursor = [], COVER_HOLD
    out = array.array('h')
    silence = array.array('h', [0] * int(SR * 60))

    def emit(arr):
        nonlocal out
        out = out + arr

    emit(array.array('h', [0] * int(SR * COVER_HOLD)))

    for si, shot in enumerate(N.SHOTS):
        s_start = cursor
        cues = []
        for ci, (zh, en) in enumerate(shot['cues']):
            tag = '%s_%02d' % (shot['id'], ci)
            mp3 = os.path.join(AUDIO, tag + '.mp3')
            wav = os.path.join(AUDIO, tag + '.wav')
            if not os.path.exists(mp3):
                print('  TTS %s  %s' % (tag, zh[:22]))
                synth(zh, mp3)
            to_wav(mp3, wav)
            a = trim(read_wav(wav))
            dur = len(a) / float(SR)
            emit(a)
            cues.append(dict(zh=zh, en=en, start=round(cursor, 3),
                             end=round(cursor + dur, 3)))
            cursor += dur
            # 句间停顿
            gap = N.GAP_SHOT if ci == len(shot['cues']) - 1 else N.GAP_SENTENCE
            emit(array.array('h', [0] * int(SR * gap)))
            cursor += gap
        shots.append(dict(id=shot['id'], name=shot['name'],
                          start=round(s_start, 3), end=round(cursor, 3),
                          cues=cues))

    emit(array.array('h', [0] * int(SR * END_HOLD)))
    total = cursor + END_HOLD

    wav_out = os.path.join(BASE_DIR, 'narration.wav')
    with wave.open(wav_out, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())

    tl = dict(total=round(total, 3), cover=COVER_HOLD, end_hold=END_HOLD,
              fps=24, shots=shots)
    with open(os.path.join(BASE_DIR, 'timeline.json'), 'w', encoding='utf-8') as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)

    print('\n总时长 %d:%05.2f  (封面 %.1fs + 正文 %.1fs + 尾 %.1fs)'
          % (int(total // 60), total % 60,
             COVER_HOLD, total - COVER_HOLD - END_HOLD, END_HOLD))
    for s in shots:
        print('  %-4s %-4s %6.1f → %6.1f' % (s['id'], s['name'], s['start'], s['end']))
    return tl


if __name__ == '__main__':
    main()
