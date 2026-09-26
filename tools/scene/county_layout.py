"""Deterministic metre-space Bellwether terrain and exclusion-aware vegetation.
Shared by authoring, Unreal placement and portable tests. No gameplay duration claim.
"""
import math,random
EXTENT=1200.0
POIS=[
 {'id':'cedar_camp','x':-610.,'y':-510.,'title':'RED CEDAR CAMP','detail':'Evacuation buses never reached this road.','kind':'camp'},
 {'id':'ranger_station','x':675.,'y':-460.,'title':'BELLWETHER RANGER STATION','detail':'Keep the channel clear. Return borrowed radios.','kind':'station'},
 {'id':'north_lookout','x':-575.,'y':690.,'title':'NORTH RIDGE LOOKOUT','detail':'Last watch: October 18. Two names crossed out.','kind':'lookout'},
 {'id':'orchard','x':780.,'y':590.,'title':'ELLIS ORCHARD','detail':'Leave half the harvest for the next family.','kind':'farm'},
 {'id':'road_house','x':-925.,'y':70.,'title':'MILE 19 ROADHOUSE','detail':'Rooms upstairs. Shelter without payment.','kind':'station'},
 {'id':'relay_camp','x':120.,'y':970.,'title':'COUNTY RELAY 04','detail':'If you hear the river, you are already late.','kind':'camp'},
]
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def river_x(y):return 470+65*math.sin(y/240)
def raw_height(x,y):
 edge=smooth(300,510,max(abs(x),abs(y)))
 hills=10+10*math.sin(x/240)*math.cos(y/330)+7*math.sin((x+y)/410)**2
 h=-.7+edge*hills
 # The river is well outside the established campaign quarter.
 bank=smooth(11,64,abs(x-river_x(y)))
 return -2.2*(1-bank)+h*bank+85*smooth(1090,1190,max(abs(x),abs(y)))
_POI_HEIGHTS={p['id']:raw_height(p['x'],p['y']) for p in POIS}
def height(x,y):
 z=raw_height(x,y)
 for p in POIS:
  d=math.hypot(x-p['x'],y-p['y']);blend=smooth(15,32,d)
  if blend<1:z=_POI_HEIGHTS[p['id']]*(1-blend)+z*blend
 return z

def clear(x,y):
 if max(abs(x),abs(y))<345:return False
 if abs(x-river_x(y))<25:return False
 # East-west county road and six broad paths to the clearings.
 if abs(y-40)<9:return False
 if any(math.hypot(x-p['x'],y-p['y'])<27 for p in POIS):return False
 return True

def placements(seed=28031):
 r=random.Random(seed);records=[]
 for kind,count in [('Pine',1500),('Broadleaf',380),('Fern',1500),('MossRock',230),('Stump',110),('Deadwood',100)]:
  placed=0
  while placed<count:
   x,y=r.uniform(-1140,1140),r.uniform(-1140,1140)
   if not clear(x,y):continue
   # Meadows and denser ridges, rather than a uniform scatter.
   if kind in ('Pine','Broadleaf') and math.sin(x/135)*math.cos(y/180)>.58:continue
   records.append({'mesh':kind,'x':round(x,3),'y':round(y,3),'z':round(height(x,y),4),'yaw':r.uniform(0,360),'scale':r.uniform(.78,1.30)})
   placed+=1
 # Dense groves around the six destinations and an authored western woodland.
 for centre in POIS+[{'x':-510.,'y':420.}]:
  for i in range(85):
   angle=r.uniform(0,math.tau);radius=r.uniform(30,85);x=centre['x']+math.cos(angle)*radius;y=centre['y']+math.sin(angle)*radius
   if not clear(x,y):continue
   records.append({'mesh':'Pine','x':x,'y':y,'z':height(x,y),'yaw':r.uniform(0,360),'scale':r.uniform(.85,1.5)})
   for j in range(3):
    px,py=x+r.uniform(-3,3),y+r.uniform(-3,3)
    records.append({'mesh':'Fern','x':px,'y':py,'z':height(px,py),'yaw':r.uniform(0,360),'scale':r.uniform(.9,1.7)})
 # Close understory and crown silhouettes around authored destinations.
 # Keep interiors, front approach, story interactables and diagnostic path clear.
 for poi in POIS:
  for kind,count,low,high in [('Pine',28,18,31),('Broadleaf',9,12,25),('Fern',130,5.8,28)]:
   placed=0;attempts=0
   while placed<count and attempts<2000:
    attempts+=1;angle=r.uniform(0,math.tau);radius=r.uniform(low,high);dx=math.cos(angle)*radius;dy=math.sin(angle)*radius
    if (abs(dx)<3.8 and dy<5) or (dx<0 and dy<0 and radius<20):continue
    x,y=poi['x']+dx,poi['y']+dy
    if abs(y-40)<9 or abs(x-river_x(y))<25:continue
    scale=r.uniform(.7,1.05) if kind=='Pine' else r.uniform(.7,1.35)
    records.append({'mesh':kind,'x':x,'y':y,'z':height(x,y),'yaw':r.uniform(0,360),'scale':scale,'placement_zone':'close_understory'})
    placed+=1
 # Close, inspectable nature at the edge of the urban quarter; no quest path blockage.
 for x,y in [(-36,25),(32,29),(-45,-22),(44,-24),(-83,47),(78,49),(-48,89),(42,87)]:
  records.append({'mesh':'Pine','x':x,'y':y,'z':-.1,'yaw':r.uniform(0,360),'scale':r.uniform(.65,.85)})
  for j in range(5):
   px,py=x+r.uniform(-3,3),y+r.uniform(-3,3)
   records.append({'mesh':'Fern','x':px,'y':py,'z':-.09,'yaw':r.uniform(0,360),'scale':r.uniform(.8,1.4)})
 return records

def bridge_deck():
 x=river_x(40)
 return x,40.,max(height(x-78,40),height(x+78,40))+1.5
