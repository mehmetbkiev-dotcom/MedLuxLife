#!/usr/bin/env python3
"""Check a translation file against its source chunk.
usage: trp_check.py content/translations/src/<chunk>.json content/translations/<de|tr>/<chunk>.json
Reports missing/empty translations, changed numbers, lost entities/arrows, English left over, and untranslated copies."""
import json, re, sys
src = [s['original'] for s in json.load(open(sys.argv[1]))]
tr = json.load(open(sys.argv[2]))
lang = 'de' if '/de/' in sys.argv[2] else 'tr'
nums = lambda s: sorted(re.findall(r'\d+(?:[.,]\d+)?', s))
problems = []
keep_same = re.compile(r'^(MedLuxLife|WhatsApp|[A-Z0-9+\-–/ .&;()]+|[\d\s+()\-–]+|\S+@\S+)$')
english = re.compile(r'\b(the|and|with|your|you|for|of|to|is|are|our|this|which|will|can|after|before)\b', re.I)
for o in src:
    t = tr.get(o)
    if t is None or not str(t).strip():
        problems.append(('MISSING', o)); continue
    if nums(o) != nums(t):
        problems.append(('NUMBERS', o, t))
    for tok in ('&amp;', '→'):
        if o.count(tok) != t.count(tok):
            problems.append(('TOKEN ' + tok, o, t))
    if t == o and not keep_same.match(o) and len(o.split()) > 1:
        problems.append(('UNCHANGED', o))
    elif len(english.findall(t)) >= 3:
        problems.append(('ENGLISH?', o, t))
extra = set(tr) - set(src)
print('%d source strings, %d translated, %d problems, %d extra keys' % (len(src), len(tr), len(problems), len(extra)))
for p in problems[:60]:
    print(' | '.join(x[:140] for x in p))
