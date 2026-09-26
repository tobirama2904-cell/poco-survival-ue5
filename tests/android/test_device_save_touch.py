"""Synthetic probe tests; not Android execution evidence."""
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/android'))
from device_save_probe import DeviceSaveProbe,journal_title_matches
class DeviceSaveTouchTests(unittest.TestCase):
 def test_pure_probe_imports_without_site_packages(self):
  import subprocess
  code="import sys; sys.path.insert(0, %r); import device_save_probe; assert device_save_probe.journal_title_matches('РЮКЗАК ДЭНИЕЛ РИД')" % str(ROOT/'tools/android')
  subprocess.run([sys.executable,'-S','-c',code],check=True,capture_output=True,text=True)
 def test_title_with_spaces_and_homoglyphs(self):
  for s in ['РЮКЗАК • ДЭНИЕЛ РИД','Рюкзак\nДэниел Рид','PЮKЗAK • ДЭНИЕЛ РИД','РЮКЗАКДЭНИЕЛРИД']:
   self.assertTrue(journal_title_matches(s),s)
 def test_hud_hint_is_not_menu_evidence(self):
  for s in ['Подробности в рюкзаке','Дэниел Рид вернулся. Подробности в рюкзаке','РЮКЗАК','РЮКЗАК МАРА ЭЛЛИС']:
   self.assertFalse(journal_title_matches(s),s)
 def test_restart_uses_real_map_and_menu_not_fixed_story_delay(self):
  s=(ROOT/'tools/android/emulator_check.py').read_text();section=s[s.index("adb('shell','am','force-stop'"):]
  self.assertNotIn('time.sleep(90)',section);self.assertLess(section.index('probe.journal(True)'),section.index("probe.save('after-restart'"));self.assertIn('No real map-load evidence after restart',section)
 def test_initial_snapshot_requires_write_newer_than_existing_autosave(self):
  with tempfile.TemporaryDirectory() as t:
   p=DeviceSaveProbe(lambda *a:None,lambda *a:'',lambda *a:None,Path(t),960,540)
   p.journal=lambda value:None
   groups=iter([[{'state':{'generation':12}}],[{'state':{'generation':12}}],[{'state':{'generation':13}}]])
   p.collect=lambda label:next(groups)
   with patch('device_save_probe.time.sleep'):result=p.save('before')
   self.assertEqual(result['generation'],13)
   self.assertEqual(p.log[0]['generation_before_save_touch'],12)
 def test_restart_autosave_does_not_count_as_manual_save(self):
  with tempfile.TemporaryDirectory() as t:
   p=DeviceSaveProbe(lambda *a:None,lambda *a:'',lambda *a:None,Path(t),960,540);p.journal=lambda value:None
   groups=iter([[{'state':{'generation':21}}],[{'state':{'generation':21}}],[{'state':{'generation':22}}]])
   p.collect=lambda label:next(groups)
   with patch('device_save_probe.time.sleep'):result=p.save('restart',20)
   self.assertEqual(result['generation'],22)
 def test_previous_generation_remains_a_floor(self):
  with tempfile.TemporaryDirectory() as t:
   p=DeviceSaveProbe(lambda *a:None,lambda *a:'',lambda *a:None,Path(t),960,540);p.journal=lambda value:None
   groups=iter([[],[{'state':{'generation':20}}],[{'state':{'generation':21}}]])
   p.collect=lambda label:next(groups)
   with patch('device_save_probe.time.sleep'):result=p.save('move',20)
   self.assertEqual(result['generation'],21)
if __name__=='__main__':unittest.main()
