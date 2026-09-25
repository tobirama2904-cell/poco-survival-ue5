#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2];d=json.loads((root/'BuildData/story/low-water.json').read_text())
def q(s):return json.dumps(s,ensure_ascii=False)
def arr(ss):return '{'+','.join(map(q,ss))+'}'
sc=d['scenes'];assert len(sc)>=18 and len({s['id'] for s in sc})==len(sc)
assert all(len(s['ru'])==len(s['en'])>=4 and len(s['position'])==3 and max(map(abs,s['position']))<1200 for s in sc)
a=['// Generated from low-water.json. Original narrative.','#include "Core/AmericanStory.h"','namespace survival {','const std::vector<FilmScene>& FilmScenes(){static const std::vector<FilmScene> Scenes={']
for s in sc:a.append('{'+','.join([q(s['id']),q(s['title'])]+[str(float(n))+'f' for n in s['position']]+['true' if s['cinematic'] else 'false',str(s['gate']),arr(s['ru']),arr(s['en']),q(s.get('intent_ru','')),q(s.get('intent_en','')),q(s.get('focus','')),str(s.get('required_events',0)),str(s.get('escort',0))])+'},')
a+=['};return Scenes;}','}'];(root/'Source/PocoSurvival/Private/Core/AmericanStory.cpp').write_text('\n'.join(a)+'\n')
print('ORIGINAL_FILM_CONTENT',len(sc),sum(len(s['ru']) for s in sc),'lines per language; no duration claim')
