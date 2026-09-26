import importlib.util,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('county',ROOT/'tools/scene/county_layout.py');county=importlib.util.module_from_spec(spec);spec.loader.exec_module(county)
class CountyTests(unittest.TestCase):
 def test_deterministic_complete_layout(self):
  a=county.placements();self.assertEqual(a,county.placements());self.assertGreater(len(a),5800)
  self.assertEqual({p['mesh'] for p in a},{'Pine','Broadleaf','Fern','MossRock','Stump','Deadwood'})
  for p in a:
   self.assertTrue(all(math.isfinite(p[k]) for k in ['x','y','z','yaw','scale']));self.assertLessEqual(max(abs(p['x']),abs(p['y'])),county.EXTENT)
 def test_six_accessible_clearings(self):
  self.assertEqual(len(county.POIS),6)
  for p in county.POIS:
   z=county.height(p['x'],p['y'])
   for x,y in [(0,0),(3,4),(-3,-4),(-9,-12)]:self.assertAlmostEqual(z,county.height(p['x']+x,p['y']+y),places=8)
   self.assertFalse(county.clear(p['x'],p['y']))
 def test_existing_campaign_ground_not_raised(self):
  for x in range(-290,291,20):
   for y in range(-290,291,20):self.assertAlmostEqual(county.height(x,y),-.7)
 def test_continuity_river_and_boundary(self):
  for y in [-900,-500,0,40,500,900]:self.assertLess(county.height(county.river_x(y),y),-2)
  for x in range(-1000,1001,40):
   for y in range(-1000,1001,40):self.assertLess(abs(county.height(x+.001,y)-county.height(x,y)),.003)
  self.assertGreater(county.height(1190,0),80)
 def test_mobile_assets_disable_nanite_and_retain_collision(self):
  source=(ROOT/'tools/scene/populate_county.py').read_text();self.assertIn("nanite.set_editor_property('enabled',False)",source);self.assertIn('CTF_USE_COMPLEX_AS_SIMPLE',source)
  gate=(ROOT/'tools/scene/verify_render.py').read_text();self.assertIn("county.get('passed') is True",gate);self.assertIn('len(images)>=6',gate)
  self.assertIn('measured_import_basis_cm',source)
 def test_art_pack_checksums_if_local(self):
  import hashlib
  folder=ROOT/'.cache/county-pack'
  if not (folder/'conditioning.json').exists():self.skipTest('Pack is fetched on scene worker')
  for model in json.loads((folder/'conditioning.json').read_text())['models']:
   f=folder/model['file'];self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),model['sha256']);self.assertEqual(f.stat().st_size,model['bytes'])
if __name__=='__main__':unittest.main()
