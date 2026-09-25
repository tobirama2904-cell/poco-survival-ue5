import hashlib,json,unittest,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class VoiceContent(unittest.TestCase):
 def test_exact_authored_line_coverage_and_pcm(self):
  story=json.loads((ROOT/'BuildData/story/city.json').read_text());lock=json.loads((ROOT/'BuildData/voices/voice-files.lock.json').read_text())
  expected={s['id']+'_'+str(i) for s in story['sites'] for i in range(len(s['lines']))}
  self.assertEqual(expected,{f['id'] for f in lock['clips']})
  for f in lock['clips']:
   p=ROOT/'BuildData/voices'/(f['id']+'.wav');self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'])
   with wave.open(str(p)) as w:
    self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate()),(1,2,24000));self.assertGreater(w.getnframes(),4800)
