#!/usr/bin/env python3
"""Original small narrative props in metres; direct glTF, no DCC memory overhead."""
import json,struct,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'BuildData/props'
MATS=[('PaintedCase',[.10,.15,.115,1],.8,.2),('DarkRubber',[.016,.022,.019,1],.9,0),('Metal',[.35,.38,.36,1],.4,.7),('Display',[.15,.26,.13,1],.3,0),('Paper',[.67,.60,.43,1],.95,0),('Folder',[.25,.12,.055,1],.9,0),('Amber',[.58,.31,.07,1],.6,.1)]
class Prop:
 def __init__(self):self.parts={}
 def box(self,c,s,mat):
  # Each face has split normals. Convert native X/Y/Z to glTF X/Z/Y.
  faces=[((1,0,0),[(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)]),((-1,0,0),[(-1,1,-1),(-1,-1,-1),(-1,-1,1),(-1,1,1)]),((0,1,0),[(1,1,-1),(-1,1,-1),(-1,1,1),(1,1,1)]),((0,-1,0),[(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1)]),((0,0,1),[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]),((0,0,-1),[(-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,-1)])]
  v,n,idx=self.parts.setdefault(mat,([],[],[]))
  for normal,points in faces:
   base=len(v)
   for point in points:
    q=[c[i]+s[i]*point[i]/2 for i in range(3)];v.append((q[0],q[2],q[1]));n.append((normal[0],normal[2],normal[1]))
   idx.extend([base,base+2,base+1,base,base+3,base+2])
 def export(self,name):
  blob=bytearray();views=[];accessors=[];primitives=[]
  def buffer(values,fmt,type,component):
   while len(blob)%4:blob.append(0)
   offset=len(blob)
   for item in values:blob.extend(struct.pack('<'+fmt,*(item if isinstance(item,tuple) else (item,))))
   views.append({'buffer':0,'byteOffset':offset,'byteLength':len(blob)-offset});a={'bufferView':len(views)-1,'componentType':component,'count':len(values),'type':type}
   if type=='VEC3':a.update({'min':[min(v[i] for v in values) for i in range(3)],'max':[max(v[i] for v in values) for i in range(3)]})
   accessors.append(a);return len(accessors)-1
  for material,(v,n,i) in self.parts.items():primitives.append({'attributes':{'POSITION':buffer(v,'fff','VEC3',5126),'NORMAL':buffer(n,'fff','VEC3',5126)},'indices':buffer(i,'I','SCALAR',5125),'material':material})
  materials=[{'name':n,'pbrMetallicRoughness':{'baseColorFactor':c,'roughnessFactor':r,'metallicFactor':m}} for n,c,r,m in MATS];materials[3]['emissiveFactor']=[.025,.045,.018]
  doc={'asset':{'version':'2.0','generator':'Original Bellwether story prop author'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0}],'meshes':[{'name':name,'primitives':primitives}],'materials':materials,'buffers':[{'byteLength':len(blob)}],'bufferViews':views,'accessors':accessors}
  data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);blob+=b'\0'*((-len(blob))%4)
  result=struct.pack('<III',0x46546c67,2,12+8+len(data)+8+len(blob))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(blob),0x004e4942)+blob
  (ROOT/(name+'.glb')).write_bytes(result)
p=Prop();p.box((0,0,.105),(.38,.22,.21),0)
for x in [-.17,.17]:
 for z in [.025,.185]:p.box((x,-.116,z),(.02,.013,.02),2)
p.box((-.075,-.116,.115),(.17,.014,.115),1)
for x in [-.14,-.11,-.08,-.05,-.02]:p.box((x,-.126,.115),(.008,.008,.09),2)
p.box((.09,-.118,.145),(.11,.013,.055),3)
for x in [.055,.12]:p.box((x,-.138,.06),(.034,.036,.035),1)
p.box((-.145,.06,.43),(.008,.008,.45),2)
for x in [-.11,.11]:p.box((x,0,.25),(.025,.035,.08),1)
p.box((0,0,.29),(.24,.035,.025),1);p.export('FieldRadio')
p=Prop();p.box((0,0,.012),(.31,.24,.024),5)
for i in range(4):p.box((0,-.006+i*.002,.025+i*.0015),(.275,.205,.001),4)
for i in range(6):p.box((-.015,-.07+i*.025,.032),(.18-(i%3)*.025,.003,.001),1)
p.box((-.11,0,.04),(.008,.22,.007),2);p.export('EvidenceFolder')
p=Prop();p.box((0,0,.035),(.12,.12,.07),2);p.box((0,0,.08),(.08,.08,.025),1);p.box((0,0,.15),(.018,.018,.13),2);p.box((0,0,.21),(.07,.032,.036),6);p.export('SignalSwitch')
print('STORY_PROPS_AUTHORED FieldRadio EvidenceFolder SignalSwitch')
