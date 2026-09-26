import unittest,json,struct,importlib.util,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('woodland_layout',ROOT/'tools/scene/county_layout.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
def glb(data):
 magic,version,size=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and size==len(data)
 n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
def positions(data):
 d,blob=glb(data);result=set()
 for mesh in d['meshes']:
  for p in mesh['primitives']:
   a=d['accessors'][p['attributes']['POSITION']];v=d['bufferViews'][a['bufferView']];assert a['componentType']==5126
   offset=v.get('byteOffset',0)+a.get('byteOffset',0)
   for i in range(a['count']):result.add(tuple(round(x,3) for x in struct.unpack_from('<fff',blob,offset+i*v.get('byteStride',12))))
 return result
class WoodlandArtTests(unittest.TestCase):
 def test_close_understory_leaves_story_and_diagnostic_paths_open(self):
  points=[p for p in layout.placements() if p.get('placement_zone')=='close_understory'];self.assertEqual(len(points),1002)
  for p in points:
   poi=min(layout.POIS,key=lambda a:(p['x']-a['x'])**2+(p['y']-a['y'])**2);dx,dy=p['x']-poi['x'],p['y']-poi['y']
   self.assertFalse(abs(dx)<3.8 and dy<5)
   self.assertFalse(dx<0 and dy<0 and (dx*dx+dy*dy)**.5<20)
 def test_new_tree_cutout_and_budget_if_local(self):
  folder=ROOT/'.cache/county-pack'
  if not (folder/'conifer-source.json').exists():self.skipTest('Refined art not fetched locally')
  d,_=glb((folder/'Pine.glb').read_bytes());leaves=next(m for m in d['materials'] if m['name']=='PhotographedNeedles');self.assertEqual(leaves['alphaMode'],'MASK');self.assertTrue(leaves['doubleSided']);self.assertEqual(leaves['alphaCutoff'],.28)
  r=next(m for m in json.loads((folder/'conditioning.json').read_text())['models'] if m['file']=='Pine.glb');self.assertLessEqual(r['triangles'],10000);self.assertGreater(r['photographed_sprigs'],2000);self.assertFalse(r['mature_tree_scan'])
 def test_terrain_geometry_matches_immutable_base_if_available(self):
  folder=ROOT/'.cache/county-pack';archive=ROOT/'.cache/county-base-002.zip'
  if not archive.exists() or not (folder/'conifer-source.json').exists():self.skipTest('Original source archive unavailable')
  with zipfile.ZipFile(archive) as z:old=z.read('Terrain.glb')
  self.assertEqual(positions(old),positions((folder/'Terrain.glb').read_bytes()))
 def test_ground_has_normal_and_roughness_maps_if_local(self):
  folder=ROOT/'.cache/county-pack'
  if not (folder/'conifer-source.json').exists():self.skipTest('Refined art not fetched locally')
  d,_=glb((folder/'Terrain.glb').read_bytes());m=d['materials'][0];self.assertIn('normalTexture',m);self.assertIn('metallicRoughnessTexture',m['pbrMetallicRoughness'])
 def test_runtime_count_follows_pinned_layout(self):
  s=(ROOT/'tools/scene/repair_materials.py').read_text();self.assertIn("expected['nature_instances']",s)
if __name__=='__main__':unittest.main()
