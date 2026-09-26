import unittest,json,math,importlib.util,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('lod_layout',ROOT/'tools/scene/county_layout.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
class ForestLodTests(unittest.TestCase):
 def test_cell_local_offsets_preserve_world_positions(self):
  cells={}
  for p in layout.placements():
   if p['mesh']!='Pine':continue
   key=(math.floor(p['x']/64),math.floor(p['y']/64));centre=((key[0]+.5)*64,(key[1]+.5)*64);local=(p['x']-centre[0],p['y']-centre[1]);self.assertLessEqual(max(map(abs,local)),32)
   self.assertAlmostEqual(local[0]+centre[0],p['x']);self.assertAlmostEqual(local[1]+centre[1],p['y']);cells.setdefault(key,[]).append(p)
  self.assertGreater(len(cells),100)
  self.assertEqual(sum(len(v) for v in cells.values()),sum(p['mesh']=='Pine' for p in layout.placements()))
 def test_collision_not_swapped_with_visual_lod(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalSceneryCluster.cpp').read_text();s=s[s.index('void ASurvivalSceneryCluster::UpdateDistanceLOD'):];self.assertNotIn('Trunks->',s);self.assertIn('Visuals->SetStaticMesh(Desired)',s);self.assertIn('FOREST_LOD_SWAP_FAILED',s);self.assertIn('Visuals->SetVisibility(false)',s)
 def test_simple_material_and_shared_atlas_are_explicit(self):
  s=(ROOT/'tools/scene/populate_county.py').read_text();self.assertIn('M_PineMobileLOD1',s);self.assertIn('MP_OPACITY_MASK',s);self.assertIn('configure_distance_levels',s)
 def test_exact_distance_asset_budgets_if_local(self):
  p=ROOT/'.cache/county-pack/pine-lods.json'
  if not p.exists():self.skipTest('Distance pack absent from excluded cache')
  d=json.loads(p.read_text());self.assertEqual(d['triangles'],[9728,2084,8]);self.assertFalse(d['lighting_baked'])
  for name in d['meshes']:
   raw=(p.parent/(name+'.glb')).read_bytes();magic,version,size=struct.unpack_from('<III',raw);self.assertEqual(magic,0x46546c67);self.assertEqual(size,len(raw));n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);self.assertTrue(any(m.get('alphaMode')=='MASK' for m in g['materials']))
if __name__=='__main__':unittest.main()
