#!/usr/bin/env python3
"""Original deterministic filtered-noise rain bed; no external recording/rights."""
from pathlib import Path
import math, random, struct, wave
rng=random.Random(81021);rate=24000;frames=rate*12;raw=[];low=0
for i in range(frames):
 x=rng.uniform(-1,1);low=.91*low+.09*x
 raw.append((.075*(x-low)+.055*low)*(1+.09*math.sin(2*math.pi*i/frames)))
# Circular crossfade joins waveform as well as amplitude, avoiding a loop click.
n=rate//10
for i in range(n):raw[i]=raw[frames-n+i]*(1-i/n)+raw[i]*(i/n)
path=Path(__file__).resolve().parents[2]/'BuildData/audio/Rain.wav'
with wave.open(str(path),'wb') as out:
 out.setparams((1,2,rate,0,'NONE','not compressed'));out.writeframes(b''.join(struct.pack('<h',round(v*32767)) for v in raw[:-n]))
