import unittest,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('journey_compile',ROOT/'tools/story/compile_journey_dialogue.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class JourneyTests(unittest.TestCase):
 def test_reproducible_original_bilingual_dialogue(self):
  d=json.loads((ROOT/'BuildData/story/journey-dialogue.json').read_text());self.assertEqual(m.compile_text(d),(ROOT/'Source/PocoSurvival/Private/Core/JourneyDialogue.cpp').read_text());self.assertEqual(len(d['conversations']),12);self.assertEqual(len({l for r in d['conversations'] for l in r['ru']}),72)
  self.assertEqual(d['conversations'][-1]['trigger'],'water');self.assertIsNone(d['measured_gameplay_hours'])
 def test_not_a_new_main_quest_dependency(self):
  main=(ROOT/'Source/PocoSurvival/Public/Core/MainCampaign.h').read_text();self.assertNotIn('Journey',main)
 def test_completed_only_and_pause_during_stealth(self):
  actor=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();director=(ROOT/'Source/PocoSurvival/Private/SurvivalWorldDirector.cpp').read_text();self.assertIn('JourneyFinished=ActiveJourney;EndStory()',actor);self.assertIn('ActiveJourney=-1;bCountyStory=false',actor)
  self.assertIn('Threat&&Player->IsJourneyConversation()',director);self.assertIn('JourneyDelay,75.f',director);self.assertIn('!It->IsHidden()',director)
 def test_urgent_main_events_take_priority(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalWorldDirector.cpp').read_text();self.assertIn('Game->MainStory.Has(2)&&!Game->MainStory.Has(4)',s)
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalInteraction.cpp').read_text();self.assertIn('CampaignResult::Advanced&&Player->IsJourneyConversation())Player->EndStory()',s)
 def test_voice_source_exact_coverage(self):
  import hashlib,wave
  d=json.loads((ROOT/'BuildData/story/journey-dialogue.json').read_text());expected={r['id']+'_'+str(i)+'.wav' for r in d['conversations'] for i in range(6)};folder=ROOT/'BuildData/journeyvoices'
  report=json.loads((folder/'voice-alignment.json').read_text());self.assertEqual(report['issues'],[]);self.assertEqual(report['lines_written'],72)
  integrity=json.loads((folder/'integrity.json').read_text());self.assertEqual({f['name'] for f in integrity['files']},expected)
  for f in integrity['files']:
   p=folder/f['name']
   if p.exists():
    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
    with wave.open(str(p)) as w:self.assertEqual(w.getnchannels(),1);self.assertEqual(w.getframerate(),24000)
 def test_casual_dialogue_does_not_force_memory_music(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalWorldDirector.cpp').read_text();self.assertIn('Player->bStoryActive&&!Player->IsJourneyConversation()',s);self.assertIn('!Player->IsJourneyConversation()&&Cycle<42',s)
 def test_actual_native_history_roundtrip_planned(self):
  script=(ROOT/'tools/ue_integration_smoke.py').read_text();self.assertIn('j3.get_journey_heard()==2049',script);self.assertIn("'journey_history_serialization_and_fallback_tested':True",script)
if __name__=='__main__':unittest.main()
