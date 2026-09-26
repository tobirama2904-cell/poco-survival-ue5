import importlib.util,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('interior_layout',ROOT/'tools/scene/interior_layout.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class InteriorTests(unittest.TestCase):
 def test_central_access_lane_clear(self):
  rooms=[(0,0,w,d) for w in [14,18,22] for d in [12,16,20]];a=m.dress(rooms);self.assertEqual(a,m.dress(rooms));self.assertEqual({r['model'] for r in a},{'MedicalBox','MedicalTape','Wheelchair','BedFrame','Bookshelf','OfficeDesk','SchoolChair','SchoolDesk','CassettePlayer'})
  for r in a:
   cx,cy,w,d=rooms[r['room']];self.assertGreater(abs(r['x']-cx),m.AISLE_HALF+.5);self.assertLess(abs(r['x']-cx),w/2-.3);self.assertLess(abs(r['y']-cy),d/2-.5);self.assertGreaterEqual(r['z'],.305)
 def test_floor_step_not_previous_seventy_centimetres(self):
  self.assertLessEqual(m.FLOOR_TOP-(-.1),.45)
  s=(ROOT/'tools/scene/expand_city.py').read_text();self.assertIn('box((cx,cy,.1),(w+1,depth+1,.4),4)',s);self.assertNotIn('box((cx,cy,.3),(w+1,depth+1,.6),4)',s);self.assertNotIn('box((cx,cy,.15),(w,depth,.3),4)',s)
 def test_loot_identity_not_new_free_supplies(self):
  s=(ROOT/'tools/scene/populate_interiors.py').read_text();self.assertIn('range(18,24)',s);self.assertNotIn('spawn_actor_from_class(interaction',s)
  for room in [(0,0,14,12),(60,120,22,20)]:
   x,y,z=m.cache_position(room);self.assertGreater(abs(x-room[0]),m.AISLE_HALF+.6);self.assertEqual(z,.315)
 def test_whole_furniture_bounds_clear_central_lane(self):
  lock=json.loads((ROOT/'BuildData/interior-pack.lock.json').read_text());dimensions={a['name']:a['dimensions_m'] for a in lock['models']}
  rooms=[(0,0,w,d) for w in [14,18,22] for d in [12,16,20]]
  for r in m.dress(rooms):
   if r['small']:continue
   cx,cy,w,d=rooms[r['room']];sx,sy,sz=dimensions[r['model']];angle=math.radians(r['yaw']);hx=(abs(math.cos(angle))*sx+abs(math.sin(angle))*sy)/2;hy=(abs(math.sin(angle))*sx+abs(math.cos(angle))*sy)/2
   self.assertGreater(abs(r['x']-cx)-hx,m.AISLE_HALF);self.assertLess(abs(r['x']-cx)+hx,w/2-.15);self.assertLess(abs(r['y']-cy)+hy,d/2-.15)
 def test_local_published_pack_hashes(self):
  import hashlib
  lock=json.loads((ROOT/'BuildData/interior-pack.lock.json').read_text());folder=ROOT/'.cache/interior-pack'
  if not (folder/'conditioning.json').exists():self.skipTest('Interior pack not fetched in this checkout')
  for f in lock['files']:self.assertEqual(hashlib.sha256((folder/f['name']).read_bytes()).hexdigest(),f['sha256'])
 def test_first_party_cc0_sources(self):
  d=json.loads((ROOT/'BuildData/interior-sources.lock.json').read_text());self.assertEqual(len(d['assets']),9)
  for a in d['assets']:
   self.assertEqual(a['license'],'CC0-1.0');self.assertTrue(a['source'].startswith('https://polyhaven.com/a/'));self.assertTrue(a['files'])
if __name__=='__main__':unittest.main()
