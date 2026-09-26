import unittest,importlib.util,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('save_probe',ROOT/'tools/android/save_state_probe.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def fixture():
 # Schematic uesave v0.7 JSON, NOT a claimed actual game save.
 props={'FormatVersion':8,'SaveGeneration':2,'bHasPlayerState':True,'PlayerLocation':{'x':0.,'y':1400.,'z':96.},'MapName':'CanalDistrict','FieldItems':[0]*9,'FilmProgress':1,'FilmDecision':0,'LootedCaches':0,'OpenDoors':0,'CountyStages':[0]*6,'MainStoryEvents':0}
 return {'root':{'save_game_type':'/Script/PocoSurvival.SurvivalSaveGame','properties':{k+'_0':v for k,v in props.items()}}}
class SaveProbeTests(unittest.TestCase):
 def test_real_values_not_file_presence_or_hash_only(self):
  a=m.canonical_save(fixture());b=copy.deepcopy(a);b['generation']=3;b['position'][1]+=450;c=copy.deepcopy(b);c['generation']=4
  result=m.compare_saves(a,b,c);self.assertTrue(result['touch_movement_verified']);self.assertTrue(result['player_position_inventory_progress_restore_verified']);self.assertFalse(result['full_world_restore_equality_verified']);self.assertFalse(result['physical_device_tested'])
 def test_unchanged_save_not_movement_and_stale_not_restore(self):
  a=m.canonical_save(fixture());self.assertFalse(m.compare_saves(a,a,a)['touch_movement_verified']);self.assertFalse(m.compare_saves(a,a,a)['player_position_inventory_progress_restore_verified'])
 def test_inventory_or_spawn_reset_is_rejected(self):
  a=m.canonical_save(fixture());b=copy.deepcopy(a);b['generation']=3;b['position'][0]+=300;c=copy.deepcopy(b);c['generation']=4;c['field_items'][0]=1
  self.assertFalse(m.compare_saves(a,b,c)['player_position_inventory_progress_restore_verified']);c=copy.deepcopy(a);c['generation']=4;self.assertFalse(m.compare_saves(a,b,c)['player_position_inventory_progress_restore_verified'])
 def test_raw_or_malformed_decoder_fields_fail_closed(self):
  for key,value in [('PlayerLocation',[0]*24),('FieldItems',[0]*36),('SaveGeneration',True),('bHasPlayerState',False),('MapName',''),('FormatVersion',999)]:
   d=fixture();d['root']['properties'][key+'_0']=value
   with self.assertRaises((AssertionError,TypeError,KeyError)):m.canonical_save(d)
 def test_native_observed_omitted_defaults(self):
  d=fixture()
  for key in ['FormatVersion','FilmProgress','FilmDecision','LootedCaches','OpenDoors','CountyStages','MainStoryEvents']:d['root']['properties'].pop(key+'_0')
  s=m.canonical_save(d);self.assertEqual(s['format'],8);self.assertEqual(s['county'],[0]*6);self.assertEqual(s['film_progress'],0)
 def test_no_teleport_in_android_probe(self):
  s=(ROOT/'tools/android/device_save_probe.py').read_text();self.assertIn('return journal_title_matches(result.stdout)',s);self.assertNotIn('set_actor_location',s);self.assertIn("'GVAS'",s)
if __name__=='__main__':unittest.main()
