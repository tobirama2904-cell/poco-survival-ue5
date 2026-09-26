"""Strict subset of uesave v0.7 JSON, never byte-pattern guesses at coordinates.
Unsupported/raw/malformed properties fail closed. Comparisons are explicitly a
player-position/inventory/progression subset, not every actor in a saved world.
"""
import math

def canonical_save(document):
 root=document['root'];assert root['save_game_type'].split('.')[-1]=='SurvivalSaveGame'
 p=root['properties']
 def get(key):return p[key+'_0']
 def integer(v,low,high):
  assert type(v) is int and low<=v<=high;return v
 version=integer(get('FormatVersion'),6,8)
 generation=integer(get('SaveGeneration'),0,2**63-1)
 assert get('bHasPlayerState') is True
 point=get('PlayerLocation');assert isinstance(point,dict)
 xyz=[point[k] for k in ('x','y','z')]
 assert all(type(v) in (int,float) and math.isfinite(v) and abs(v)<=1000000 for v in xyz)
 map_name=get('MapName');assert isinstance(map_name,str) and map_name
 inventory=get('FieldItems');assert isinstance(inventory,list) and len(inventory)==9
 inventory=[integer(v,0,256) for v in inventory]
 result={'generation':generation,'map':map_name,'position':xyz,'field_items':inventory,'film_progress':integer(get('FilmProgress'),0,30),'film_decision':integer(get('FilmDecision'),0,2),'format':version}
 for key in ['LootedCaches','OpenDoors']:result[key]=integer(get(key),0,(1<<24)-1)
 if version>=7:
  county=get('CountyStages');assert isinstance(county,list) and len(county)==6;result['county']=[integer(v,0,4) for v in county]
 if version>=8:result['main_events']=integer(get('MainStoryEvents'),0,31)
 return result

def compare_saves(before,moved,restarted):
 distance=math.dist(before['position'][:2],moved['position'][:2])
 movement=(before['map']==moved['map'] and moved['generation']>before['generation'] and 50<distance<2000 and abs(before['position'][2]-moved['position'][2])<250)
 fields=['map','field_items','film_progress','film_decision','LootedCaches','OpenDoors','county','main_events']
 restored=(restarted['generation']>moved['generation'] and math.dist(moved['position'],restarted['position'])<10 and all(moved.get(k)==restarted.get(k) for k in fields))
 return {'touch_movement_verified':movement,'moved_cm':distance,'player_position_inventory_progress_restore_verified':restored,'full_world_restore_equality_verified':False,'physical_device_tested':False}
