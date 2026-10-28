#!/usr/bin/env python3
"""xlang (uk/ru/ar) matches the text exactly as WordPress prints it, and WordPress "texturizes" text (" - " → " &#8211; ",
"&" → "&amp;", ' → &#8217; …). For a translation file this writes <lang>/<name>_texturized.json with the printed form of every key
that appears differently on the given live English pages. usage: xlang_texturized.py NAME PATH [PATH …]"""
import html, json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import trp, xlang


def main(name, paths):
    printed = {}
    for p in paths:
        h = subprocess.run(['curl', '-sS', '--max-time', '120', trp.W + p + ('&' if '?' in p else '?') + 'tx=1'], capture_output=True).stdout.decode('utf8', 'ignore')
        for s in xlang.strings(h):
            printed.setdefault(trp.loose(s), set()).add(s)
    for lang in ('uk', 'ru', 'ar'):
        src = json.load(open(ROOT / 'content/translations' / lang / (name + '.json')))
        out = {}
        for k, v in src.items():
            for s in printed.get(trp.loose(k), ()):
                if s != k:
                    out[s] = v
        json.dump(out, open(ROOT / 'content/translations' / lang / (name + '_texturized.json'), 'w'), ensure_ascii=False, indent=1)
        print(lang, len(out), 'printed variants')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
