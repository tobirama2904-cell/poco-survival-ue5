import unittest,json,struct,io
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def glb(path):
 data=path.read_bytes();magic,version,size=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and size==len(data);n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
class ForestLODTests(unittest.TestCase):
 def test_authored_three_levels_if_local(self):
  folder=ROOT/'.cache/county-pack'
  if not (folder/'forest-lods.json').exists():self.skipTest('LOD art not available locally')
  report=json.loads((folder/'forest-lods.json').read_text());self.assertEqual(report['pine_triangles'],[9728,3556,4]);self.assertEqual(report['screens'],[1,.65,.24]);self.assertFalse(report['baked_lighting'])
  for name,budget in [('Pine',10000),('PineMid',3600),('PineFar',4)]:
   d,_=glb(folder/(name+'.glb'));n=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives']);self.assertLessEqual(n,budget);self.assertGreater(n,0)
 def test_cutout_textures_are_power_of_two_if_local(self):
  folder=ROOT/'.cache/county-pack'
  if not (folder/'forest-lods.json').exists():self.skipTest('LOD art not available locally')
  for name in ['Pine','PineMid','PineFar']:
   d,raw=glb(folder/(name+'.glb'));tested=0
   for image in d['images']:
    if not any(s in image.get('name','') for s in ['pine_needles','pine_canopy']):continue
    v=d['bufferViews'][image['bufferView']];p=v.get('byteOffset',0);im=Image.open(io.BytesIO(raw[p:p+v['byteLength']]))
    self.assertTrue(all(n>0 and n&(n-1)==0 for n in im.size));self.assertEqual(im.mode,'RGBA');tested+=1
   self.assertGreater(tested,0)
 def test_real_lod_transfer_and_screen_sizes_required(self):
  s=(ROOT/'tools/scene/populate_county.py').read_text();self.assertIn('set_lod_from_static_mesh(pine,1,mid,0,True)',s);self.assertIn('set_lod_from_static_mesh(pine,2,far,0,False)',s);self.assertIn('set_lod_screen_sizes(pine,[1.0,.65,.24])',s)
  self.assertIn('enable_section_cast_shadow(pine,False,2,0)',s)
 def test_gate_not_weakened_to_hide_timeout(self):
  s=(ROOT/'tools/scene/render_gate.sh').read_text();self.assertIn('35m',s)
  s=(ROOT/'tools/scene/verify_render.py').read_text();self.assertIn('passed=lods_valid and support.get',s);self.assertIn('len(images)>=4',s)
 def test_retained_cook_checks_lods(self):
  s=(ROOT/'tools/scene/repair_materials.py').read_text();self.assertIn("out/'forest-lods.json'",s);self.assertIn('mesh_editor.get_lod_count(mesh)==3',s)
if __name__=='__main__':unittest.main()
