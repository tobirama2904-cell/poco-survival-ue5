import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class NativeHygiene(unittest.TestCase):
 def test_matching_unreal_header_is_first(self):
  for p in (ROOT/'Source/PocoSurvival/Private').glob('*.cpp'):
   h=ROOT/'Source/PocoSurvival/Public'/(p.stem+'.h')
   if h.exists():
    include=next(line for line in p.read_text().splitlines() if line.startswith('#include'))
    self.assertEqual(include,f'#include "{p.stem}.h"',str(p))
 def test_retry_safe_material_builders(self):
  for file in ['tools/scene/expand_city.py','tools/scene/prepare_mobile_scene.py']:
   self.assertNotIn('delete_all_material_expressions', (ROOT/file).read_text())
