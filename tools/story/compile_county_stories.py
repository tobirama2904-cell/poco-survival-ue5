#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def compile_text(d):
 arcs=d['arcs'];assert len(arcs)==6 and len({a['id'] for a in arcs})==6
 q=lambda s:json.dumps(s,ensure_ascii=False)
 arr=lambda items:'{'+','.join(q(x) for x in items)+'}'
 lines=['// Generated from county-stories.json. Original narrative.','#include "Core/CountyStories.h"','namespace survival {','const std::vector<CountyArc>& CountyArcs(){static const std::vector<CountyArc> Data={']
 for a in arcs:
  assert len(a['beats'])==4 and len(a['choices'])==2
  beats=[]
  for b in a['beats']:
   assert len(b['ru'])==len(b['en'])>=6
   beats.append('{'+arr(b['ru'])+','+arr(b['en'])+'}')
  lines.append('{'+','.join(q(a[k]) for k in ['id','title','title_en','poi'])+','+arr([c[0] for c in a['choices']])+','+arr([c[1] for c in a['choices']])+',{{'+','.join(beats)+'}}},')
 return '\n'.join(lines+['};return Data;}','}'])+'\n'
if __name__=='__main__':
 d=json.loads((ROOT/'BuildData/story/county-stories.json').read_text());(ROOT/'Source/PocoSurvival/Private/Core/CountyStories.cpp').write_text(compile_text(d))
 print('COUNTY_STORY_COMPILED',sum(len(b['ru']) for a in d['arcs'] for b in a['beats']))
