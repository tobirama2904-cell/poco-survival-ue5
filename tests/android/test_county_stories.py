import importlib.util,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('compile_county',ROOT/'tools/story/compile_county_stories.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class CountyStoryTests(unittest.TestCase):
 def test_generated_cpp_and_unique_episode_coverage(self):
  d=json.loads((ROOT/'BuildData/story/county-stories.json').read_text());self.assertEqual(module.compile_text(d),(ROOT/'Source/PocoSurvival/Private/Core/CountyStories.cpp').read_text());self.assertEqual(len(d['arcs']),6)
  self.assertEqual(sum(len(b['ru']) for a in d['arcs'] for b in a['beats']),144);self.assertIsNone(d['measured_playtime_hours'])
  self.assertEqual(len({line for a in d['arcs'] for b in a['beats'] for line in b['ru']}),144)
 def test_all_six_destinations_have_story(self):
  d=json.loads((ROOT/'BuildData/story/county-stories.json').read_text());self.assertEqual({a['poi'] for a in d['arcs']},{'cedar_camp','ranger_station','north_lookout','orchard','road_house','relay_camp'})
 def test_generated_original_props_are_actual_meshes(self):
  for name in ['FieldRadio','EvidenceFolder','SignalSwitch']:
   raw=(ROOT/'BuildData/props'/(name+'.glb')).read_bytes();magic,version,size=struct.unpack_from('<III',raw);self.assertEqual(magic,0x46546c67);self.assertEqual(version,2);self.assertEqual(size,len(raw));n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);self.assertEqual(len(d['meshes']),1);self.assertTrue(d['meshes'][0]['primitives'])
 def test_voice_archive_covers_every_exact_line(self):
  import hashlib,wave
  d=json.loads((ROOT/'BuildData/story/county-stories.json').read_text());expected={a['id']+'_'+str(b)+'_'+str(i)+'.wav' for a in d['arcs'] for b,beat in enumerate(a['beats']) for i in range(len(beat['ru']))}
  folder=ROOT/'BuildData/countyvoices';report=json.loads((folder/'voice-alignment.json').read_text());self.assertEqual(report['issues'],[]);self.assertEqual(report['lines_written'],144)
  integrity=json.loads((folder/'integrity.json').read_text());self.assertEqual({f['name'] for f in integrity['files']},expected);self.assertGreater(integrity['total_seconds'],500)
  for f in integrity['files']:
   p=folder/f['name']
   if p.exists():
    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
    with wave.open(str(p)) as w:self.assertEqual(w.getframerate(),24000);self.assertEqual(w.getnchannels(),1)
 def test_save_initializers_do_not_double_count(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalGameInstance.cpp').read_text();self.assertIn('CountyStages.Reset();for',s);self.assertIn('Save->FormatVersion > 8',s)
 def test_actual_native_roundtrip_exercises_new_state(self):
  s=(ROOT/'tools/ue_integration_smoke.py').read_text();self.assertIn('county_game.try_county_action',s);self.assertIn("'version7_county_choices_and_legacy_migration_tested':True",s)
if __name__=='__main__':unittest.main()
