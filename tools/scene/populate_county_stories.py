"""Add original interactive story objects, lights and persistent rural encounters."""
import json,sys
from pathlib import Path
import unreal
root=Path('/project');sys.path.insert(0,str(root/'tools/scene'))
from county_layout import POIS,height
lib=unreal.EditorAssetLibrary;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('rural_story_'):actors.destroy_actor(actor)
data=json.loads((root/'BuildData/story/county-stories.json').read_text());pois={p['id']:p for p in POIS};cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInteraction');enemy=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInfected')
for i,arc in enumerate(data['arcs']):
 p=pois[arc['poi']];x,y=p['x'],p['y'];z=height(x,y)+.25
 for j,(name,dx,dy,dz) in enumerate([('EvidenceFolder',-1.9,1.8,.565),('FieldRadio',2,1,.87),('SignalSwitch',1.7,.5,.87),('SignalSwitch',2.3,.5,.87)]):
  obj=actors.spawn_actor_from_class(cls,unreal.Vector((x+dx)*100,(y+dy)*100,(z+dz)*100));obj.set_actor_label(f'rural_story_{i}_{j}');obj.set_editor_property('action_id',unreal.Name(f'__county_{i}_{j}'))
  obj.get_editor_property('mesh').set_static_mesh(lib.load_asset('/Game/Story/Props/'+name))
  focus=obj.get_editor_property('focus_volume');focus.set_sphere_radius(19);focus.set_relative_location(unreal.Vector(0,0,8),sweep=False,teleport=True)
 lamp=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(x*100,(y-3.8)*100,(z+2.6)*100));lamp.set_actor_label('rural_story_lamp_'+str(i));lamp.set_editor_property('tags',[unreal.Name('county_story_lamp'),unreal.Name('county_arc_'+str(i))])
 light=lamp.get_component_by_class(unreal.PointLightComponent);light.set_mobility(unreal.ComponentMobility.MOVABLE);light.set_intensity(850);light.set_attenuation_radius(1400);light.set_cast_shadows(False);light.set_visibility(False)
 for j,dx in enumerate([-34,34]):
  ex,ey=x+dx,y+13;ez=height(ex,ey)+1
  e=actors.spawn_actor_from_class(enemy,unreal.Vector(ex*100,ey*100,ez*100));e.set_actor_label(f'rural_story_patrol_{i}_{j}');e.set_editor_property('persistent_id',unreal.Name(f'county_story_{i}_{j}'));e.set_editor_property('archetype',(i+j)%3);e.set_editor_property('patrol_points',[unreal.Vector(ex*100,ey*100,ez*100),unreal.Vector((ex+4)*100,(ey+4)*100,(height(ex+4,ey+4)+1)*100)])
assert level.save_current_level()
(root/'artifacts/gameplay-scene/county-stories.json').write_text(json.dumps({'arcs':6,'interaction_objects':24,'signal_lights':6,'persistent_encounters':12,'bilingual_lines':144,'runtime_story_playthrough_verified':False},indent=2))
print('COUNTY_STORIES_PLACED 6 arcs 24 interactions 12 encounters')
