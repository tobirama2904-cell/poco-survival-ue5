import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('health',ROOT/'tools/scene/render_health.py');health=importlib.util.module_from_spec(spec);spec.loader.exec_module(health)
class RenderHealthTests(unittest.TestCase):
 def test_actual_sky_failure_blocks_delivery(self):
  text='LogMaterial: Warning: Failed to compile Material for platform SF_VULKAN_SM5, Default Material will be used in game.\n\t(Node Saturate) Missing Saturate input'
  self.assertEqual(len(health.material_failures(text)),2)
 def test_instance_fallback_not_a_green_render(self):
  self.assertTrue(health.material_failures('Material M_City0 missing bUsedWithInstancedStaticMeshes=True! Default Material will be used in game.'))
 def test_unrelated_diagnostic_not_a_shader_failure(self):
  self.assertFalse(health.material_failures('SOFTWARE_VULKAN_IMAGE_FALLBACK: R64 buffer-only format excluded; renderer selects its R32G32 image fallback'))
 def test_pinned_editor_unnamed_saturate_pin(self):
  script=(ROOT/'tools/scene/prepare_mobile_scene.py').read_text();self.assertIn("assert unreal.MaterialEditingLibrary.connect_material_expressions(compress,'',limit,'')",script);self.assertNotIn("limit,'Input'",script)
 def test_cook_only_after_actual_corrected_render(self):
  script=(ROOT/'tools/android/cook_host.sh').read_text();self.assertLess(script.index('bash tools/scene/render_gate.sh'),script.index('-run=Cook'))
  self.assertIn('runuser -u ue4', (ROOT/'.github/workflows/android-cook.yml').read_text())
if __name__=='__main__':unittest.main()
