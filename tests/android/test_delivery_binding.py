"""Synthetic evidence consistency tests, not tests of a real APK or device."""
import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('delivery',ROOT/'tools/android/check_delivery.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DeliveryBindingTests(unittest.TestCase):
 def fixture(self):
  sha='a'*64;cert='b'*64;images={x+'.png':str(i)*64 for i,x in enumerate(['start','move','restart'],1)}
  apk=dict(package_run='123',sha256=sha,bytes=100,signature_verified=True,arm64_library_verified=True,certificate_sha256=cert,embedded_game_archives=['assets/game.pak'])
  install=dict(apk_sha256=sha,apk_package_run='123',screenshots=[{'file':x} for x in images])
  for k in ['installed','launch_survived','restart_survived','visible_frames_verified','touch_movement_verified','player_position_inventory_progress_restore_verified','journal_touch_confirmed','fresh_save_after_touch_verified']:install[k]=True
  identity=dict(source_tree='tree',engine_lock='engine',project_descriptor='project',configuration_tree='config');source=dict(package_run='123',matching_game_source_verified=True,native=identity.copy(),cooked=identity.copy(),packaging=identity.copy())
  review=dict(apk_sha256=sha,package_run=123,verdict='development-only',images=images.copy())
  return [sha,100,apk,install,source,review,cert,images]
 def test_complete_bound_development_evidence(self):
  r=m.validate(*self.fixture());self.assertTrue(r['development_candidate_evidence_bound']);self.assertFalse(r['final_game']);self.assertFalse(r['physical_poco_verified'])
 def test_stale_apk_or_install_is_rejected(self):
  for index in [2,3,5]:
   a=self.fixture();a[index]['sha256' if index==2 else 'apk_sha256']='c'*64
   with self.assertRaises(ValueError):m.validate(*a)
 def test_input_injection_alone_does_not_pass(self):
  a=self.fixture();a[3]['touch_input_injected']=True;a[3]['touch_movement_verified']=False
  with self.assertRaises(ValueError):m.validate(*a)
 def test_wrong_source_rejected_even_with_claimed_matching_flag(self):
  a=self.fixture();a[4]['native']['source_tree']='wrong'
  with self.assertRaises(ValueError):m.validate(*a)
 def test_unreviewed_image_and_wrong_package_rejected(self):
  a=self.fixture();a[5]['images'].pop('move.png')
  with self.assertRaises(ValueError):m.validate(*a)
  a=self.fixture();a[5]['package_run']=999
  with self.assertRaises(ValueError):m.validate(*a)
 def test_source_report_from_other_package_rejected(self):
  a=self.fixture();a[4]['package_run']='122'
  with self.assertRaises(ValueError):m.validate(*a)
 def test_final_game_label_rejected(self):
  a=self.fixture();a[5]['verdict']='final-game'
  with self.assertRaises(ValueError):m.validate(*a)
if __name__=='__main__':unittest.main()
