import unittest,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/android'))
from device_save_probe import DeviceSaveProbe
class TouchDwellTests(unittest.TestCase):
 def test_real_held_touch_stays_at_same_coordinate(self):
  calls=[]
  with tempfile.TemporaryDirectory() as d:
   p=DeviceSaveProbe(lambda *args:calls.append(args),lambda *args:'',lambda *args:None,Path(d),960,540);p.press(.89,.075)
   self.assertEqual(calls,[('shell','input','touchscreen','swipe','854','40','854','40','2000')]);self.assertEqual(p.log[0]['touchscreen_press']['duration_ms'],2000)
 def test_close_diagnostic_never_satisfies_the_gate(self):
  emulator=(ROOT/'tools/android/emulator_check.py').read_text();probe=(ROOT/'tools/android/device_save_probe.py').read_text()
  self.assertIn('diagnostic only; not gate evidence',emulator);self.assertIn('journal_closed_by_same_touch_control',probe)
  required=emulator[emulator.index("for key in ['installed'"):]
  required=required[:required.index(']')]
  self.assertNotIn('journal_close',required)
 def test_screen_recording_stops_before_keyboard_diagnosis(self):
  s=(ROOT/'tools/android/emulator_check.py').read_text();failure=s[s.index("report['failure']"):]
  self.assertLess(failure.index('stop_video()'),failure.index("'keyevent','61'"));self.assertIn("'actual Android emulator screen recording'",s)
 def test_keyboard_is_failure_only_not_success_path(self):
  s=(ROOT/'tools/android/emulator_check.py').read_text();prefix=s[:s.index("report['failure']")]
  self.assertNotIn("'keyevent','61'",prefix);self.assertIn("report['keyboard_diagnostic_is_touch_proof']=False",s)
if __name__=='__main__':unittest.main()
