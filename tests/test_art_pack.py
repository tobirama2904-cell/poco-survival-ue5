import unittest,tempfile,json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from art_pack import safe_path,sha,validate_model,zip_tree
class ArtPipelineTests(unittest.TestCase):
 def test_safe_relative_path(self):self.assertEqual(safe_path('textures/a.jpg'),Path('textures/a.jpg'))
 def test_traversal_is_rejected(self):
  for x in ['../a','textures/../../a','%2e%2e/a','/etc/passwd','C:/file','a\\b']:
   with self.subTest(x=x),self.assertRaises(ValueError):safe_path(x)
 def test_hash_known_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a';p.write_bytes(b'abc');self.assertEqual(sha(p),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
 def test_archive_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/'source';source.mkdir();(source/'model.bin').write_bytes(b'geometry'*100)
   result=zip_tree(source,root/'pack.zip');self.assertGreater(result['bytes'],0)
   with zipfile.ZipFile(root/'pack.zip') as z:self.assertEqual(z.read('model.bin'),b'geometry'*100)
 def test_minimum_model_and_dependency_checks(self):
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d);(folder/'a.bin').write_bytes(b'0'*36)
   doc={'asset':{'version':'2.0'},'buffers':[{'uri':'a.bin','byteLength':36}],'accessors':[{'count':3}],'meshes':[{'primitives':[{'attributes':{'POSITION':0}}]}]}
   (folder/'a.gltf').write_text(json.dumps(doc));asset={'id':'fixture','entrypoint':'a.gltf','files':[{'path':'a.gltf'},{'path':'a.bin'}]}
   self.assertEqual(validate_model(folder,asset)['triangles'],1)
   (folder/'a.bin').unlink()
   with self.assertRaises(AssertionError):validate_model(folder,asset)
 def test_empty_model_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d);(folder/'a.gltf').write_text(json.dumps({'asset':{'version':'2.0'}}))
   with self.assertRaises(AssertionError):validate_model(folder,{'id':'empty','entrypoint':'a.gltf','files':[{'path':'a.gltf'}]})
if __name__=='__main__':unittest.main()
