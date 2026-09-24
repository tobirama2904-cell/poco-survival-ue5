import importlib.util,struct,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('inspect_elf',Path(__file__).resolve().parents[2]/'tools/android/inspect_elf.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
class ElfTests(unittest.TestCase):
    def fixture(self,machine=183,truncated=False):
        h=bytearray(64);h[:6]=b'\x7fELF\x02\x01';struct.pack_into('<HH',h,16,3,machine);struct.pack_into('<Q',h,32,64);struct.pack_into('<HH',h,54,56,2)
        size=64+112;return bytes(h)+struct.pack('<IIQQQQQQ',1,5,0,0,0,size+int(truncated),size,16384)+struct.pack('<IIQQQQQQ',2,6,0,0,0,0,0,8)
    def test_actual_header_checks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fixture.so';p.write_bytes(self.fixture());self.assertEqual(elf.inspect(p)['machine'],'AArch64')
            for data in [self.fixture(62),self.fixture(truncated=True),b'not an elf']:
                p.write_bytes(data)
                with self.assertRaises(ValueError):elf.inspect(p)
if __name__=='__main__':unittest.main()
