"""Original synthesized game sound effects. Not voice, not field recordings."""
import numpy as np,wave
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'BuildData/audio';root.mkdir(exist_ok=True);rng=np.random.default_rng(4014);rate=24000
for name,duration in [('Shot',.65),('Glass',.9),('Footstep',.18)]:
 t=np.arange(int(duration*rate))/rate;n=rng.normal(0,1,len(t));signal=np.zeros_like(t)
 if name=='Shot':signal=.55*n*np.exp(-t*48)+.6*np.sin(2*np.pi*(150*t-55*t*t))*np.exp(-t*13)+.12*n*np.exp(-t*9)
 elif name=='Glass':
  for i in range(23):
   start=rng.uniform(0,.45);e=np.maximum(t-start,0);signal+=np.where(t>=start,rng.uniform(.03,.13)*np.sin(2*np.pi*rng.uniform(1800,7200)*e)*np.exp(-e*rng.uniform(20,65)),0)
 else:signal=.4*np.convolve(n,np.ones(9)/9,mode='same')*np.exp(-t*38)+.22*np.sin(2*np.pi*95*t)*np.exp(-t*45)
 signal=np.tanh(signal);fade=min(180,len(t)//2);signal[:fade]*=np.linspace(0,1,fade);signal[-fade:]*=np.linspace(1,0,fade);signal-=signal.mean();signal=np.clip(signal,-.95,.95)
 with wave.open(str(root/(name+'.wav')),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes((signal*32767).astype('<i2').tobytes())
print('ORIGINAL_GAME_SFX_READY')
