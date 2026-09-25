"""Narrow first-spawn regression alarm for Arsen's tan clothing, not art approval.
stdlib PNG decoder keeps the licensed editor container independent of Pillow.
"""
import struct,zlib
from pathlib import Path
def pixels(path):
 data=Path(path).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';pos=8;packed=b''
 while pos<len(data):
  n=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+n];pos+=12+n
  if kind==b'IHDR':w,h,depth,color,compression,filtration,interlace=struct.unpack('>IIBBBBB',chunk)
  if kind==b'IDAT':packed+=chunk
  if kind==b'IEND':break
 assert depth==8 and color in (2,6) and not interlace and 0<w<=4096 and 0<h<=4096
 channels=3 if color==2 else 4;stride=w*channels;raw=zlib.decompress(packed);assert len(raw)==h*(stride+1)
 previous=bytearray(stride);image=[]
 for y in range(h):
  start=y*(stride+1);filter=raw[start];row=bytearray(raw[start+1:start+1+stride]);assert filter in range(5)
  for i in range(stride):
   a=row[i-channels] if i>=channels else 0;b=previous[i];c=previous[i-channels] if i>=channels else 0
   if filter==1:predict=a
   elif filter==2:predict=b
   elif filter==3:predict=(a+b)//2
   elif filter==4:
    p=a+b-c;da,db,dc=abs(p-a),abs(p-b),abs(p-c);predict=a if da<=db and da<=dc else b if db<=dc else c
   else:predict=0
   row[i]=(row[i]+predict)&255
  image.append(row);previous=row
 return w,h,channels,image
def character_presence(path):
 w,h,c,rows=pixels(path);count=0;total=0
 for y in range(int(h*.4),int(h*.65)):
  for x in range(int(w*.35),int(w*.53)):
   r,g,b=rows[y][x*c:x*c+3];total+=1
   count+=r>22 and g>16 and r>g*1.06 and g>b*1.04
 fraction=count/max(total,1)
 return {'test':'fixed first-spawn tan-clothing regression alarm; not general character recognition','candidate_pixels':count,'region_pixels':total,'fraction':round(fraction,5),'passed':fraction>.012}
