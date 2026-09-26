"""Metre-space room dressing with a clear central access route."""
FLOOR_TOP=.30
AISLE_HALF=1.25

def dress(rooms):
 records=[]
 def put(room,model,x,y,z=0,yaw=180,small=False):
  cx,cy,w,d=rooms[room]
  records.append({'room':room,'model':model,'x':cx+x,'y':cy+y,'z':FLOOR_TOP+.005+z,'yaw':yaw,'small':small})
 for i,(cx,cy,w,d) in enumerate(rooms):
  left=-w/2+1.6;right=w/2-1.4;back=d/2-1.25
  put(i,'Bookshelf',right,back)
  if i%3==0:
   put(i,'BedFrame',left,back-1.1)
   put(i,'Wheelchair',right-1.0,-1.5,yaw=155)
   put(i,'OfficeDesk',left,-2.5,yaw=-90)
   put(i,'MedicalBox',left,-2.5,.793,yaw=-90,small=True)
   put(i,'MedicalTape',left+.25,-2.9,.795,small=True)
   put(i,'CassettePlayer',left-.18,-2.1,.793,yaw=90,small=True)
  elif i%3==1:
   for x in [left,left+1.6]:
    for y in [-d/2+3,-d/2+5.4,1.8]:
     put(i,'SchoolDesk',x,y);put(i,'SchoolChair',x,y-.85)
   put(i,'OfficeDesk',right-1,-1,yaw=90)
   put(i,'MedicalBox',right-1,-1,.793,small=True)
  else:
   put(i,'BedFrame',left,back-1.1)
   put(i,'OfficeDesk',right-1,-1.2,yaw=90)
   put(i,'SchoolChair',right-2.25,-1.2,yaw=90)
   put(i,'CassettePlayer',right-1,-1.2,.793,yaw=90,small=True)
 return records

def cache_position(room):
 cx,cy,w,d=room
 return cx+w/2-1.6,cy-d/2+2.2,FLOOR_TOP+.015
