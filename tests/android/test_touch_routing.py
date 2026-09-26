import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/android'))
from touch_route_report import analyze_touch_route
class TouchRouteTests(unittest.TestCase):
 def test_preserves_actual_coordinates_without_claiming_button_activation(self):
  d=analyze_touch_route('LogAndroid: Verbose: Received targeted motion event from pointer 0 (id 0) action 0: (853.11, 39.62)\nLogAndroid: Verbose: Received targeted motion event from pointer 0 (id 0) action 1: (853.11, 39.62)')
  self.assertEqual(d['event_count'],2);self.assertEqual(d['native_targeted_events'][0]['x'],853.11);self.assertFalse(d['game_button_dispatch_verified'])
 def test_no_events_is_not_success(self):self.assertFalse(analyze_touch_route('ordinary system noise')['native_android_events_observed'])
 def test_probe_waits_for_presentation_instead_of_blind_toggling(self):
  s=(ROOT/'tools/android/device_save_probe.py').read_text();block=s[s.index(' def journal(self,opened):'):s.index(' def journal_close_by_touch')]
  self.assertIn('for observation in range(6)',block);self.assertEqual(block.count('self.press(.89,.075)'),1)
 def test_diagnostics_are_runtime_flags_not_binary_changes(self):
  s=(ROOT/'tools/android/emulator_check.py').read_text();self.assertIn('-LogCmds="LogAndroid Verbose"',s);self.assertIn("'game_button_dispatch_verified'",(ROOT/'tools/android/touch_route_report.py').read_text())
if __name__=='__main__':unittest.main()
