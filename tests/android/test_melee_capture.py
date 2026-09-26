import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class MeleeCaptureTests(unittest.TestCase):
 def test_capture_bound_to_impact_not_a_timer(self):
  actor=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();mode=(ROOT/'Source/PocoSurvival/Private/SurvivalGameMode.cpp').read_text()
  self.assertIn('if(bMeleeProofRequested)',actor);self.assertIn('MELEE_IMPACT_PROOF',actor);self.assertIn('Player->ArmMeleeProofCapture()',mode);self.assertNotIn('CaptureMeleePose',mode)
 def test_gate_still_requires_clips_pose_hand_capture_and_damage(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalGameMode.cpp').read_text();self.assertIn('bMeleeProofClips&&Player->bMeleeProofPose&&Player->bMeleeProofHand&&Player->bMeleeProofCaptured',s);self.assertIn('Pose&&bMeleeInputDebounced&&Once&&Damage&&Recovered',s)
 def test_action_identity_uses_asset_reference(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();self.assertIn('PlayingHumanAnimation==*Standing',s);self.assertIn('PlayingHumanAnimation==*Crouched',s)
if __name__=='__main__':unittest.main()
