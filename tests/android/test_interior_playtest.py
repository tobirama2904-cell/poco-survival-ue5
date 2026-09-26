import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class InteriorPlaytestTests(unittest.TestCase):
 def test_actual_open_walk_and_inside_checks_are_required(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalGameMode.cpp').read_text()
  for marker in ['InteriorDoor->Interact(Player,Failure)','bInteriorDoorRotated','Inside&&Grounded&&Walked>250','FMath::Abs(Feet-30)<5','InteriorFloors==6','teleported_inside']:
   self.assertIn(marker,s)
  walk=s[s.index('void ASurvivalGameMode::WalkIntoInterior()'):s.index('void ASurvivalGameMode::CaptureInteriorProof()')]
  self.assertIn('EKeys::W,IE_Pressed',walk);self.assertNotIn('TeleportTo',walk);self.assertNotIn('SetActorLocation',walk)
 def test_previous_melee_and_support_gates_are_preserved(self):
  s=(ROOT/'tools/scene/verify_render.py').read_text()
  for name in ['interior','melee','forest','support','companion','county']:self.assertIn(name+".get('passed') is True",s)
  self.assertIn('len(images)>=6',s)
 def test_probe_spawns_inside_and_preserves_room_bounds(self):
  s=(ROOT/'tools/scene/populate_interiors.py').read_text();self.assertIn('rooms[:6]',s);self.assertIn("unreal.Vector(w,d,1)",s);self.assertIn("unreal.Vector(cx*100,cy*100,160)",s)
 def test_new_runtime_marker_is_cleared(self):
  for file in ['editor_gate.sh','render_gate.sh']:
   self.assertIn('interior-runtime',(ROOT/'tools/scene'/file).read_text())
if __name__=='__main__':unittest.main()
