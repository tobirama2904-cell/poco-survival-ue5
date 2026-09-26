import unittest,json,hashlib,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class LowWaterContent(unittest.TestCase):
 def test_original_cast_and_localized_scene_coverage(self):
  d=json.loads((ROOT/'BuildData/story/low-water.json').read_text());self.assertGreaterEqual(len(d['scenes']),30)
  self.assertEqual({p['id'] for p in d['cast']},{'Daniel','Mara','Ruth','Owen'})
  self.assertTrue(d['voiceover_recorded']);self.assertIsNone(d['measured_hours'])
  for s in d['scenes']:self.assertEqual(len(s['ru']),len(s['en']));self.assertGreaterEqual(len(s['ru']),4)
 def test_pbr_sources_match_hashes(self):
  lock=json.loads((ROOT/'BuildData/surfaces.lock.json').read_text())
  for a in lock['assets']:
   self.assertEqual(a['license'],'CC0-1.0')
   for f in a['files']:self.assertEqual(hashlib.sha256((ROOT/'BuildData/surfaces'/f['path']).read_bytes()).hexdigest(),f['sha256'])
 def test_original_score_pcm_and_provenance(self):
  cues=json.loads((ROOT/'BuildData/audio/score-authorship.json').read_text());self.assertEqual(len(cues),4)
  for c in cues:
   p=ROOT/'BuildData/audio'/(c['name']+'.wav');self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),c['sha256'])
   with wave.open(str(p)) as w:self.assertEqual(w.getnchannels(),1);self.assertEqual(w.getsampwidth(),2);self.assertEqual(w.getnframes()/w.getframerate(),32)

 def test_main_dialogue_clips_exact_coverage_and_integrity(self):
  d=json.loads((ROOT/'BuildData/story/low-water.json').read_text());expected={s['id']+'_'+str(i)+'.wav' for s in d['scenes'][:18] for i,line in enumerate(s['ru']) if ': ' in line}
  actual={p.name for p in (ROOT/'BuildData/filmvoices').glob('*.wav')};self.assertEqual(actual,expected);self.assertEqual(len(actual),97)
  integrity=json.loads((ROOT/'BuildData/filmvoices/integrity.json').read_text());self.assertEqual({f['name'] for f in integrity['files']},expected)
  for f in integrity['files']:
   p=ROOT/'BuildData/filmvoices'/f['name'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
   with wave.open(str(p)) as w:self.assertEqual(w.getframerate(),24000);self.assertEqual(w.getnchannels(),1);self.assertEqual(w.getsampwidth(),2);self.assertGreater(w.getnframes(),2400)
  alignment=json.loads((ROOT/'BuildData/filmvoices/voice-alignment.json').read_text());self.assertEqual(alignment['issues'],[])

 def test_complete_scene_marker_cannot_be_reused_after_failed_build(self):
  gate=(ROOT/'tools/scene/editor_gate.sh').read_text();self.assertIn('field-content,county-content,county-runtime,companion-runtime,companion-support,melee-runtime,forest-runtime,scene-ready,render-verification',gate)
  self.assertIn("all_construction_steps_succeeded",(ROOT/'tools/scene/verify_render.py').read_text())
 def test_unreal_focus_transforms_supply_required_arguments(self):
  import ast
  tree=ast.parse((ROOT/'tools/scene/populate_field.py').read_text())
  for node in ast.walk(tree):
   if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='set_relative_location':self.assertEqual({k.arg for k in node.keywords},{'sweep','teleport'})
