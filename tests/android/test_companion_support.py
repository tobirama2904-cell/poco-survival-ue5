import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class CompanionSupportTests(unittest.TestCase):
 def test_hold_disables_warp_and_crouches(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCompanion.cpp').read_text();self.assertIn('!(Game->bMaraHolding&&!RuthRole)&&!Aid.Active()&&Distance>2200',s);self.assertIn('(Game->bMaraHolding&&!Aid.Active())||KneelForAid',s)
 def test_load_cancels_transient_aid(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCompanion.cpp').read_text();self.assertIn('SupportEpoch!=Game->SupportLoadRevision',s);self.assertIn('Aid.Cancel();bAvailable=false;',s)
 def test_injuries_are_not_mistaken_for_new_hits(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();self.assertIn('if (Applied>0){LastImpactTime=',s)
  helper=s[s.index('bool ASurvivalCharacter::ApplySupportResult'):s.index('void ASurvivalCharacter::CompanionCommand')];self.assertNotIn('ClearAllTimersForObject',helper);self.assertNotIn('RestoreVitals',helper)
 def test_commands_not_overlapping_crafting(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();self.assertLess(s.index('if(bCompanionPanel){'),s.index('FieldAction(FMath::Clamp'))
  self.assertIn('if (!IsCinematicLocked() && !bEditingControls){bJournalOpen=',s)
 def test_fourth_actual_frame_and_medical_gate_required(self):
  s=(ROOT/'tools/scene/verify_render.py').read_text();self.assertIn("support.get('passed') is True",s);self.assertIn('len(images)>=4',s)
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalGameMode.cpp').read_text();self.assertIn('exactly_one_bandage_spent',s);self.assertIn('SupportPlayerStart,Player->GetActorLocation())>100',s)
 def test_steering_probe_uses_crouched_height(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCompanion.cpp').read_text();self.assertIn('CompanionProbeHalf(GetCapsuleComponent()->GetScaledCapsuleHalfHeight())',s)
if __name__=='__main__':unittest.main()
