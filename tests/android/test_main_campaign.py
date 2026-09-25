import json,unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class MainCampaignTests(unittest.TestCase):
 def test_single_continuation_not_side_quest_dependencies(self):
  d=json.loads((ROOT/'BuildData/story/low-water.json').read_text());self.assertEqual(len(d['scenes']),30);self.assertEqual(sum(len(s['ru']) for s in d['scenes']),194)
  self.assertIsNone(d['measured_hours']);self.assertEqual(d['target_playtime_hours'],[12,24])
  self.assertEqual([s['id'] for s in d['scenes'][:2]],['arrival','depot']);self.assertEqual(d['scenes'][17]['id'],'free_roam')
  for s in d['scenes'][18:]:self.assertTrue(s['intent_ru']);self.assertTrue(s['intent_en']);self.assertEqual(s['gate'],0);self.assertGreater(s['escort'],0)
 def test_bridge_story_and_action_match_actual_crossing(self):
  spec=importlib.util.spec_from_file_location('layout',ROOT/'tools/scene/county_layout.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  x,y,z=m.bridge_deck();d=json.loads((ROOT/'BuildData/story/low-water.json').read_text())
  for i in [26,27]:
   p=d['scenes'][i]['position'];self.assertLess(abs(p[0]-x),77.5);self.assertEqual(p[1],y);self.assertAlmostEqual(p[2],z+.15)
  script=(ROOT/'tools/scene/populate_main_continuation.py').read_text();self.assertIn('floor=bridge_deck()[2]+.15',script)
 def test_companion_camera_sample_occurs_after_blend(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalGameMode.cpp').read_text();capture=s[s.index('void ASurvivalGameMode::CaptureCompanionFilmProof()'):]
  self.assertIn('GetViewTarget()',capture);self.assertIn('companion-runtime.json',capture)
  self.assertIn("companion.get('passed') is True",(ROOT/'tools/scene/verify_render.py').read_text())
 def test_saved_state_native_test_and_protected_quest_pack(self):
  s=(ROOT/'tools/ue_integration_smoke.py').read_text();self.assertIn('version8_main_rescue_and_legacy_migration_tested',s);self.assertIn('main_game.try_main_action',s)
  h=(ROOT/'Source/PocoSurvival/Public/Core/MainCampaign.h').read_text();self.assertNotIn('Spend(Supply::Bandage)',h);self.assertIn('protected quest item',h)
 def test_recorded_main_lines_match_dialogue_and_hashes(self):
  import hashlib,wave
  d=json.loads((ROOT/'BuildData/story/low-water.json').read_text());expected={s['id']+'_'+str(i)+'.wav' for s in d['scenes'][18:] for i in range(len(s['ru']))}
  folder=ROOT/'BuildData/mainvoices';integrity=json.loads((folder/'integrity.json').read_text());self.assertEqual({f['name'] for f in integrity['files']},expected)
  self.assertEqual(json.loads((folder/'voice-alignment.json').read_text())['issues'],[])
  for f in integrity['files']:
   p=folder/f['name']
   if p.exists():
    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
    with wave.open(str(p)) as w:self.assertEqual(w.getframerate(),24000);self.assertEqual(w.getnchannels(),1)
 def test_companion_evidence_cleared_and_banter_can_pause(self):
  self.assertIn('companion-runtime.json',(ROOT/'tools/scene/render_gate.sh').read_text())
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();self.assertIn('StoryAudio->SetPaused(Pause)',s);self.assertIn('bEditingControls||bJournalOpen',s)
  self.assertIn('MainActive||Available.Num()', (ROOT/'Source/PocoSurvival/Private/SurvivalHUD.cpp').read_text())
 def test_companion_not_claimed_as_full_tactical_ai(self):
  s=(ROOT/'Source/PocoSurvival/Public/SurvivalCompanion.h').read_text();self.assertIn('Protected narrative escort',s);self.assertIn('Not yet tactical combat',s)
if __name__=='__main__':unittest.main()
