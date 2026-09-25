#!/usr/bin/env python3
"""Original deterministic synthesized cues. No recordings, borrowed melodies or TTS.
These are authored placeholder arrangements, not a claim of orchestral/live scoring.
"""
import numpy as np, wave, hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'BuildData/audio';sr=24000;n=sr*32;t=np.arange(n)/sr;rng=np.random.default_rng(9617);out=[]
def note(track,at,midi,duration,amp):
 start=int(at*sr);end=min(n,start+int(duration*sr));u=np.arange(end-start)/sr;f=440*2**((midi-69)/12)
 signal=sum(np.sin(2*np.pi*f*h*u+.07*h)*np.exp(-u*(.45+.22*h))/h**1.6 for h in range(1,6))
 env=np.minimum(u/.012,1)*np.minimum((duration-u)/.12,1);track[start:end]+=amp*signal*np.maximum(env,0)
def save(name,a):
 peak=max(1,float(np.max(np.abs(a)))/.65);a=a/peak;fade=np.minimum(np.arange(n)/(sr*1.3),1)*np.minimum(np.arange(n)[::-1]/(sr*1.3),1);data=np.rint(a*fade*32767).astype('<i2').tobytes();p=root/(name+'.wav')
 with wave.open(str(p),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(data)
 out.append({'name':name,'seconds':32,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'authorship':'original deterministic synthesis; tools/scene/compose_score.py'})
for name in ['ScoreExplore','ScoreStealth','ScoreCombat','ScoreMemory']:
 a=np.zeros(n)
 if name=='ScoreExplore':
  for at,m in [(1,57),(5,64),(12,59),(17,60),(25,55)]:note(a,at,m,6,.12)
 if name=='ScoreMemory':
  for j,chord in enumerate([(45,52,59),(41,48,55),(48,55,59),(43,50,57)]):
   for k,m in enumerate(chord):note(a,j*8+k*.18,m,7.5,.11)
  for j,m in enumerate([69,67,64,62,60,64,59,57]):note(a,j*3.5+1,m,3.2,.10)
 if name=='ScoreStealth':
  a+=.025*np.sin(2*np.pi*55*t)*(1+.35*np.sin(2*np.pi*t/8))
  for j in range(12):note(a,j*2.5+1,[45,52,46][j%3],2,.055)
 if name=='ScoreCombat':
  for j in range(56):
   at=j*.55;start=int(at*sr);end=min(n,start+int(.3*sr));u=np.arange(end-start)/sr
   a[start:end]+=.15*np.sin(2*np.pi*(55*u+1.7*(1-np.exp(-u*25))))*np.exp(-u*13)
   note(a,at,[45,45,52,46][j%4],.65,.085)
 save(name,a)
# Short original pluck for actual arrow release.
u=np.arange(int(sr*.32))/sr;sound=.23*np.sin(2*np.pi*(125*u+3*(1-np.exp(-u*35))))*np.exp(-u*15)+rng.normal(0,.035,len(u))*np.exp(-u*35)
with wave.open(str(root/'Bow.wav'),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(np.rint(sound*32767).astype('<i2').tobytes())
(root/'score-authorship.json').write_text(json.dumps(out,indent=2)+'\n');print('ORIGINAL_SCORE_CUES',len(out),'32 seconds each; silence handled by runtime mixer')
