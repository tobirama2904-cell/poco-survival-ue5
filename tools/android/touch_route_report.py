"""Analyze native Android event-thread logs, not game-control acceptance."""
import re
PATTERN=re.compile(r'Received targeted motion event from pointer (\d+) \(id (\d+)\) action (\d+): \(([-.\d]+), ([-.\d]+)\)')
def analyze_touch_route(text):
 events=[]
 for line in text.splitlines():
  match=PATTERN.search(line)
  if match:
   pointer,handle,action,x,y=match.groups();events.append({'pointer':int(pointer),'handle':int(handle),'action':int(action),'x':float(x),'y':float(y)})
 return {'native_targeted_events':events,'event_count':len(events),'native_android_events_observed':bool(events),'game_button_dispatch_verified':False,'coordinate_transform_correctness_verified':False,'physical_device_tested':False}
