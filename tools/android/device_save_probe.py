"""Android emulator-only touch/menu/save probes using real app output.
No teleport, injected save state, or guessed byte offsets are used.
"""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
from save_state_probe import canonical_save
PACKAGE='com.pocosurvival.game'
def journal_title_matches(text):
 # Match the actual title, not the ordinary HUD hint "details in backpack".
 translated=text.upper().translate(str.maketrans({'P':'Р','K':'К','A':'А','E':'Е','H':'Н','O':'О','C':'С','T':'Т','M':'М','B':'В','X':'Х','3':'З'}))
 compact=re.sub('[^А-ЯЁ]','',translated)
 return bool(re.search('РЮКЗАКД[ЭЕ]НИЕЛРИД',compact))
class DeviceSaveProbe:
 def __init__(self,adb,text,screenshot,root,width,height):
  self.adb=adb;self.text=text;self.screenshot=screenshot;self.root=root;self.width=width;self.height=height;self.log=[];self.press_ms=2000
 def journal_visible(self,filename):
  from PIL import Image # Installed by the actual emulator workflow; not needed by pure probe tests.
  p=self.root/filename;self.screenshot(filename)
  with Image.open(p) as im:
   crop=im.crop((int(self.width*.09),int(self.height*.175),int(self.width*.64),int(self.height*.24)))
   crop.resize((crop.width*4,crop.height*4)).save(self.root/'journal-title.png')
  result=subprocess.run(['tesseract',str(self.root/'journal-title.png'),'stdout','-l','rus+eng','--psm','11'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
  result.check_returncode()
  self.log.append({'image':filename,'ocr':result.stdout})
  return journal_title_matches(result.stdout)
 def press(self,x,y):
  # adb's zero-dwell tap can begin/end between frames on the translated,
  # software-rendered emulator. Record a real held touch, not a game command.
  px,py=str(round(self.width*x)),str(round(self.height*y))
  self.log.append({'touchscreen_press':{'x':int(px),'y':int(py),'duration_ms':self.press_ms}})
  self.adb('shell','input','touchscreen','swipe',px,py,px,py,str(self.press_ms))
 def journal(self,opened):
  if self.journal_visible('android-journal-initial-'+str(len(self.log))+'.png')==opened:return
  # A queued toggle must get time to become visible before another toggle is
  # injected. Otherwise slow presentation can turn a successful open into close.
  for attempt in range(3):
   self.press(.89,.075)
   for observation in range(6):
    time.sleep(4)
    if self.journal_visible('android-journal-'+('open' if opened else 'closed')+'-'+str(len(self.log))+'.png')==opened:return
  raise RuntimeError('Journal touch/OCR confirmation failed; not claiming accepted touch input')
 def journal_close_by_touch(self):
  # Diagnostic only: it never satisfies the save/movement gate.
  self.journal(True)
  for attempt in range(3):
   self.press(.89,.075)
   time.sleep(12)
   if not self.journal_visible('android-journal-close-'+str(attempt)+'.png'):
    self.log.append({'journal_closed_by_same_touch_control':True,'attempts':attempt+1});return True
  self.log.append({'journal_closed_by_same_touch_control':False,'attempts':3});return False
 def save(self,label,after_generation=-1):
  self.journal(True);self.screenshot('android-backpack-'+label+'.png')
  prior=self.collect(label+'-pre-touch')
  generation_floor=max([after_generation]+[r['state']['generation'] for r in prior])
  self.log.append({'snapshot':label,'generation_before_save_touch':generation_floor})
  self.press(.75,.075)
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   records=self.collect(label)
   if records:
    best=max(records,key=lambda r:r['state']['generation'])
    if best['state']['generation']>generation_floor:
     self.log.append({'snapshot':label,'save':best});self.journal(False);self.persist();return best['state']
   time.sleep(5)
  self.persist();raise RuntimeError('No newly written, decodable player save after touch Save')
 def collect(self,label):
  routes=[('run-as',['run-as',PACKAGE],'files')]
  for path in ['/sdcard/Android/data/'+PACKAGE+'/files','/sdcard/UnrealGame/PocoSurvival','/sdcard/UE4Game/PocoSurvival']:
   routes += [('run-as',['run-as',PACKAGE],path),('shell',[],path)]
  records=[];seen=set()
  for i,(mode,prefix,directory) in enumerate(routes):
   found=self.text('shell',*prefix,'find',directory,'-type','f','-name','Survival_*.sav',check=False)
   self.log.append({'snapshot':label,'probe':mode,'directory':directory,'result':found[:1500]})
   for path in found.splitlines():
    if not path.startswith(directory+'/') or not path.endswith(('/Survival_A.sav','/Survival_B.sav')):continue
    raw=self.adb('exec-out',*prefix,'cat',path,check=False).stdout
    if not raw.startswith(b'GVAS') or len(raw)>2*1024**2:continue
    sha=hashlib.sha256(raw).hexdigest()
    if sha in seen:continue
    seen.add(sha);file=self.root/(label+'-'+str(i)+'-'+Path(path).name);file.write_bytes(raw);decoded=file.with_suffix('.json')
    run=subprocess.run(['.cache/save-reader/uesave','to-json','-i',str(file),'-o',str(decoded)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if run.returncode:
     self.log.append({'decode_failure':file.name,'error':run.stderr[:2000]});continue
    try:state=canonical_save(json.loads(decoded.read_text()))
    except (AssertionError,KeyError,TypeError,ValueError) as e:
     self.log.append({'schema_failure':file.name,'error':type(e).__name__+': '+str(e)});continue
    records.append({'file':file.name,'sha256':sha,'bytes':len(raw),'state':state})
  return records
 def persist(self):
  (self.root/'save-touch-probe.json').write_text(json.dumps(self.log,ensure_ascii=False,indent=2)+'\n')
