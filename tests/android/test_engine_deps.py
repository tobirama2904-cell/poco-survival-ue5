import hashlib,importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('deps',Path(__file__).resolve().parents[2]/'tools/android/engine_deps.py');deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
class DependencyTests(unittest.TestCase):
    def test_blob_verification_and_atomic_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw=root/'pack';raw.write_bytes(b'header!!payload');target=root/'Engine/a.bin';entry={'Name':'Engine/a.bin','Hash':hashlib.sha1(b'payload').hexdigest()};blob={'PackOffset':'8','Size':'7'}
            deps.install_blob(raw,blob,entry,root);self.assertEqual(target.read_bytes(),b'payload')
            entry['Hash']='0'*40
            with self.assertRaises(ValueError):deps.install_blob(raw,blob,entry,root)
            self.assertEqual(target.read_bytes(),b'payload');self.assertFalse((target.parent/'a.bin.ue-download').exists())
    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ['../bad','/tmp/bad','Engine/../../bad','Engine\\bad','C:/bad']:
                with self.assertRaises(ValueError):deps.destination(Path(tmp),name)
    def test_truncated_blob(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw=root/'pack';raw.write_bytes(b'x')
            with self.assertRaises(ValueError):deps.install_blob(raw,{'PackOffset':'0','Size':'20'},{'Name':'Engine/a','Hash':'0'*40},root)
            self.assertFalse((root/'Engine/a').exists())
if __name__=='__main__':unittest.main()
