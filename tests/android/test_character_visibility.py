import importlib.util,unittest,struct,zlib,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('frame_character',ROOT/'tools/scene/frame_character.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CharacterVisibility(unittest.TestCase):
 def test_measured_loaded_but_invisible_character_is_rejected(self):
  self.assertFalse(m.character_presence(ROOT/'docs/verification/2026-09-25-invisible-human-rejected.png')['passed'])
 def test_decoder_and_positive_fixed_view_region(self):
  def chunk(name,data):return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
  w,h=640,360;raw=bytearray()
  for y in range(h):
   raw.append(0)
   for x in range(w):raw.extend((130,100,70) if 245<x<300 and 160<y<240 else (80,90,100))
  png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.png';p.write_bytes(png);self.assertTrue(m.character_presence(p)['passed'])
