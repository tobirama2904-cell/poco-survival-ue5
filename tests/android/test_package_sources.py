import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/android'))
from verify_package_sources import require_matching
class PackageSources(unittest.TestCase):
    def setUp(self):self.base=dict(source_tree='1',engine_lock='2',project_descriptor='3',configuration_tree='4')
    def test_matching_source_allows_infrastructure_only_commit_changes(self):
        require_matching({**self.base,'commit':'new'},{**self.base,'commit':'old'},{**self.base,'commit':'cooked'})
    def test_old_cpp_binary_rejected(self):
        with self.assertRaises(ValueError):require_matching(self.base,{**self.base,'source_tree':'old'},self.base)
    def test_old_cooked_cpp_layout_rejected(self):
        with self.assertRaises(ValueError):require_matching(self.base,self.base,{**self.base,'source_tree':'old'})
    def test_configuration_mismatch_rejected(self):
        with self.assertRaises(ValueError):require_matching(self.base,self.base,{**self.base,'configuration_tree':'old'})
