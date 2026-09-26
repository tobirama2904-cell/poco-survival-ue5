import json,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class FoliagePerformanceTests(unittest.TestCase):
 def test_small_masked_shader_graph(self):
  s=(ROOT/'tools/scene/mobile_foliage_material.py').read_text();self.assertEqual(s.count('edit.create_material_expression('),3);self.assertIn('BLEND_MASKED',s);self.assertIn("'used_with_instanced_static_meshes',True",s);self.assertIn("MP_OPACITY_MASK",s)
 def test_patch_does_not_replace_story_or_terrain(self):
  s=(ROOT/'tools/scene/patch_retained_foliage.py').read_text();self.assertIn("actor.get_actor_label()=='county_Pine'",s);self.assertNotIn("startswith('county_')",s);self.assertIn("'rest_of_retained_scene_unchanged':True",s)
 def test_corrected_frame_gate_before_cooking(self):
  s=(ROOT/'tools/android/cook_host.sh').read_text();self.assertLess(s.index('patch_retained_foliage.py'),s.index('repair_materials.py'));self.assertLess(s.index('repair_materials.py'),s.index('bash tools/scene/render_gate.sh'));self.assertLess(s.index('bash tools/scene/render_gate.sh'),s.index('-run=Cook'))
 def test_no_other_model_or_layout_changes(self):
  folder=ROOT/'.cache/county-pack'
  if not (folder/'bough-bake.json').exists():self.skipTest('New pack not fetched')
  old=json.loads((ROOT/'BuildData/county-base-003.lock.json').read_text())
  for f in old['files']:
   if f['name']=='county.json' or f['name'].endswith('.glb') and f['name']!='Pine.glb':self.assertEqual(hashlib.sha256((folder/f['name']).read_bytes()).hexdigest(),f['sha256'])
 def test_baked_atlas_is_cutout_not_solid_rectangle(self):
  p=ROOT/'.cache/county-pack/bough-bake.json'
  if not p.exists():self.skipTest('New pack not fetched')
  d=json.loads(p.read_text());self.assertEqual(d['source_sprigs_per_bough'],13);self.assertGreater(d['alpha_coverage_fraction'],.15);self.assertLess(d['alpha_coverage_fraction'],.5)
if __name__=='__main__':unittest.main()
