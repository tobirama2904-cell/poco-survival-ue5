"""Low-memory geometry/material inspection, explicitly not a gameplay frame."""
import struct,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];im=Image.new('RGB',(1200,550),(25,34,39));draw=ImageDraw.Draw(im)
for slot,name in enumerate(['FieldRadio','EvidenceFolder','SignalSwitch']):
 raw=(ROOT/'BuildData/props'/(name+'.glb')).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];tri=[];points=[]
 def accessor(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];size=3 if a['type']=='VEC3' else 1;fmt=('f' if a['componentType']==5126 else 'I')*size
  return [struct.unpack_from('<'+fmt,binary,v.get('byteOffset',0)+a.get('byteOffset',0)+j*size*4) for j in range(a['count'])]
 for p in g['meshes'][0]['primitives']:
  vertices=[(x,z,y) for x,y,z in accessor(p['attributes']['POSITION'])];normals=[(x,z,y) for x,y,z in accessor(p['attributes']['NORMAL'])];idx=[a[0] for a in accessor(p['indices'])];color=g['materials'][p['material']]['pbrMetallicRoughness']['baseColorFactor']
  for k in range(0,len(idx),3):
   face=[vertices[j] for j in idx[k:k+3]];normal=normals[idx[k]];brightness=.40+.60*max(0,normal[0]*.4-normal[1]*.5+normal[2]*.7);rgb=tuple(int(255*min(1,(c*brightness)**.4545)) for c in color[:3]);tri.append((sum(x*.3-y*.7+z*.4 for x,y,z in face),face,rgb));points+=face
 def project(p):x,y,z=p;return x*.85+y*.55,-z*.9-y*.40+x*.24
 projected=[project(p) for p in points];lo=[min(p[i] for p in projected) for i in range(2)];hi=[max(p[i] for p in projected) for i in range(2)];scale=min(310/(hi[0]-lo[0]),350/(hi[1]-lo[1]))
 for depth,face,color in sorted(tri):
  vertices=[project(p) for p in face];draw.polygon([(slot*400+200+(x-(lo[0]+hi[0])/2)*scale,255+(y-(lo[1]+hi[1])/2)*scale) for x,y in vertices],fill=color)
 draw.text((slot*400+40,450),name,fill=(224,218,188))
draw.text((30,515),'ASSET GEOMETRY REVIEW — NOT AN UNREAL GAME FRAME',fill=(163,185,179));out=ROOT/'.cache/story-props-review.png';out.parent.mkdir(exist_ok=True);im.save(out)
