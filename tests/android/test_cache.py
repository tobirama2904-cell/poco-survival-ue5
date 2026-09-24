import importlib.util,io,tarfile,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('restore',Path(__file__).resolve().parents[2]/'tools/android/restore_cache.py');restore=importlib.util.module_from_spec(spec);spec.loader.exec_module(restore)
class CacheTests(unittest.TestCase):
    def archive(self,name,kind=None):
        out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w:gz') as t:
            member=tarfile.TarInfo(name);member.size=3
            if kind:member.type=kind;member.linkname='/etc/passwd';member.size=0
            t.addfile(member,io.BytesIO(b'obj') if not kind else None)
        out.seek(0);return out
    def test_valid_object(self):
        name='home/ue4/UnrealEngine/Engine/Intermediate/Build/Android/arm64/Core/a.o'
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(restore.extract(self.archive(name),Path(tmp),3)['restored_bytes'],3)
            self.assertEqual((Path(tmp)/name).read_bytes(),b'obj')
    def test_unsafe_locations(self):
        for name in ['/etc/passwd','../bad','project/Source/bad.cpp','home/ue4/UnrealEngine/Engine/Source/bad','project/Binaries/Android/../../../bad']:
            self.assertFalse(restore.allowed(name))
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):restore.extract(self.archive('project/Binaries/Android/link',tarfile.SYMTYPE),Path(tmp))
    def test_declared_size_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):restore.extract(self.archive('project/Binaries/Android/a.so'),Path(tmp),2)
    def test_plugin_cache(self):
        self.assertTrue(restore.allowed('home/ue4/UnrealEngine/Engine/Plugins/EnhancedInput/Intermediate/Build/Android/arm64/a.o'))
if __name__=='__main__':unittest.main()
