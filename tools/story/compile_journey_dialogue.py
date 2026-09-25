#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def compile_text(d):
 q=lambda s:json.dumps(s,ensure_ascii=False);arr=lambda ss:'{'+','.join(q(s) for s in ss)+'}'
 rows=d['conversations'];assert len(rows)==12 and len({r['id'] for r in rows})==12
 lines=['// Generated from original journey-dialogue.json.','#include "Core/JourneyDialogue.h"','namespace survival {','const std::vector<JourneyScene>& JourneyScenes(){static const std::vector<JourneyScene> Scenes={']
 for r in rows:
  assert r['trigger'] in ['walk','rain','rest','night','hurt','water'];assert len(r['ru'])==len(r['en'])==6;assert r['min_scene']<=r['max_scene']
  lines.append('{'+','.join([q(r['id']),str(r['min_scene']),str(r['max_scene']),'JourneyTrigger::'+r['trigger'].capitalize(),arr(r['ru']),arr(r['en'])])+'},')
 return '\n'.join(lines+['};return Scenes;}','}'])+'\n'
if __name__=='__main__':(ROOT/'Source/PocoSurvival/Private/Core/JourneyDialogue.cpp').write_text(compile_text(json.loads((ROOT/'BuildData/story/journey-dialogue.json').read_text())))
