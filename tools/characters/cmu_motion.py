"""Small, explicit ASF/AMC reader for the pinned public CMU motions; no executable input."""
import math
import numpy as np
from pathlib import Path

def rotation(degrees):
 x,y,z=np.radians(degrees);cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
 return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
def read_asf(path):
 bones={};parents={};mode='';bone=None;units=.45
 for raw in Path(path).read_text().splitlines():
  s=raw.strip();v=s.split()
  if not s or s.startswith('#'):continue
  if s.startswith(':'):mode=s;continue
  if mode==':units' and v[0]=='length':units=float(v[1])
  if mode==':bonedata':
   if s=='begin':bone={'dof':[]};continue
   if s=='end':bones[bone['name']]=bone;bone=None;continue
   if v[0] in ('name','length','direction','axis','dof'):
    if v[0]=='name':bone['name']=v[1]
    elif v[0]=='dof':bone['dof']=v[1:]
    elif v[0]=='length':bone['length']=float(v[1])
    elif v[0]=='direction':bone['direction']=np.array(list(map(float,v[1:4])))
    elif v[0]=='axis':assert v[4]=='XYZ';bone['axis']=rotation(list(map(float,v[1:4])))
  if mode==':hierarchy' and s not in ('begin','end'):
   for child in v[1:]:parents[child]=v[0]
 assert len(bones)==len(parents)==30
 order=[]
 def visit(parent):
  for n in bones:
   if parents[n]==parent:order.append(n);visit(n)
 visit('root');assert len(order)==30
 return bones,parents,order,.0254/units

def read_amc(path):
 frames=[];current=None
 for raw in Path(path).read_text().splitlines():
  v=raw.split()
  if not v or v[0].startswith(('#',':')):continue
  if len(v)==1 and v[0].isdigit():current={};frames.append(current)
  else:assert current is not None;current[v[0]]=list(map(float,v[1:]))
 assert frames and all(len(f['root'])==6 for f in frames)
 return frames

def pose(skeleton,frame):
 bones,parents,order,unit=skeleton;R={'root':rotation(frame['root'][3:])};P={'root':np.array(frame['root'][:3])*unit}
 for name in order:
  b=bones[name];angles=[0.,0.,0.]
  for dof,value in zip(b['dof'],frame.get(name,[])):angles['xyz'.index(dof[1])]=value
  R[name]=R[parents[name]]@b['axis']@rotation(angles)@b['axis'].T
  P[name]=P[parents[name]]+R[name]@b['direction']*b['length']*unit
 return R,P

def select_punch(skeleton,frames):
 # Select an actual forward right-arm extension, not an arbitrary mocap frame.
 values=[]
 for frame in frames[:1800]:
  R,P=pose(skeleton,frame);forward=R['root']@np.array([0.,0.,1.]);forward[1]=0;forward/=np.linalg.norm(forward)
  values.append(float((P['rhand']-P['rclavicle'])@forward))
 peaks=[i for i in range(90,len(values)-90) if values[i]>.44 and values[i]==max(values[i-24:i+25])]
 assert peaks,'No usable forward strike in the inspected motion'
 peak=peaks[0];return peak,values
