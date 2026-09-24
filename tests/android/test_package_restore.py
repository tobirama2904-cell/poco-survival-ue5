import importlib.util,io,tarfile,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('package_restore',Path(__file__).resolve().parents[2]/'tools/android/restore_package_inputs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PackageRestoreTests(unittest.TestCase):
    def archive(self,name='project/Binaries/Android/game.so',link=False):
        buf=io.BytesIO()
        with tarfile.open(fileobj=buf,mode='w:gz') as t:
            item=tarfile.TarInfo(name)
            if link:item.type=tarfile.SYMTYPE;item.linkname='/escape'
            else:item.size=4
            t.addfile(item,None if link else io.BytesIO(b'ELF!'))
        buf.seek(0);return buf
    def test_subset_restore_and_rejections(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);r=m.extract(self.archive(),('project','Binaries','Android'),root,32);self.assertEqual(r['bytes'],4)
            for stream in [self.archive('../escape'),self.archive('/absolute'),self.archive(link=True)]:
                with self.assertRaises(ValueError):m.extract(stream,('project','Binaries','Android'),root,32)
            with self.assertRaises(ValueError):m.extract(self.archive(),('project','Binaries','Android'),root,2)
