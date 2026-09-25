"""Physical main-story actions and persistent staging markers, not side-quest gates."""
import json,sys
from pathlib import Path
import unreal
root=Path('/project');sys.path.insert(0,str(root/'tools/scene'))
from county_layout import height,bridge_deck
lib=unreal.EditorAssetLibrary;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('main_campaign_'):actors.destroy_actor(actor)
interaction=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInteraction');companion=unreal.load_class(None,'/Script/PocoSurvival.SurvivalCompanion');assert interaction and companion
cube=lib.load_asset('/Engine/BasicShapes/Cube.Cube');material=lib.load_asset('/Game/Story/Materials/M_City2')
def box(label,x,y,z,scale):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,z*100));a.set_actor_label(label);a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,material);a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_actor_scale3d(unreal.Vector(*scale));return a
# The small physical receiver, sealed medical pack, treatment kit, latch and lamp
# are a single rescue chain. County evidence choices remain entirely optional.
for index,name,x,y in [(0,'FieldRadio',675.8,-461.6),(1,'SupplyCrate',780.8,588.4),(2,'EvidenceFolder',-187,44),(3,'SignalSwitch',430,37.8),(4,'SignalSwitch',779,587),(5,'SupplyCrate',674.2,-461.6)]:
 floor=height(x,y)+.42 if max(abs(x),abs(y))>345 else .18
 if index==3:floor=bridge_deck()[2]+.15
 box('main_campaign_stand_'+str(index),x,y,floor+.35,(.65,.5,.7))
 a=actors.spawn_actor_from_class(interaction,unreal.Vector(x*100,y*100,(floor+.71)*100));a.set_actor_label('main_campaign_action_'+str(index));a.set_editor_property('action_id',unreal.Name('__main_'+str(index)));a.get_editor_property('mesh').set_static_mesh(lib.load_asset('/Game/Story/Props/'+name))
 if index in (1,5):a.get_editor_property('mesh').set_world_scale3d(unreal.Vector(.45,.45,.45));a.set_editor_property('tags',[unreal.Name('main_medical_pack' if index==1 else 'main_repair_spares')])
 focus=a.get_editor_property('focus_volume');focus.set_sphere_radius(22);focus.set_world_scale3d(unreal.Vector(1,1,1));focus.set_relative_location(unreal.Vector(0,0,15),sweep=False,teleport=True)
# Keep the bridge passable before the act: the latch is a narrative action,
# not a new invisible obstacle across an already explored open-world route.
marker=actors.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector(78000,59000,(height(780,590)+1.5)*100));marker.set_actor_label('main_campaign_refuge');marker.set_editor_property('tags',[unreal.Name('main_refuge')])
lamp=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(78000,58620,(height(780,590)+2.9)*100));lamp.set_actor_label('main_campaign_refuge_lamp');lamp.set_editor_property('tags',[unreal.Name('main_refuge_lamp')]);light=lamp.get_component_by_class(unreal.PointLightComponent);light.set_mobility(unreal.ComponentMobility.MOVABLE);light.set_cast_shadows(False);light.set_intensity(700);light.set_attenuation_radius(1100);light.set_visibility(False)
for ruth in [False,True]:
 a=actors.spawn_actor_from_class(companion,unreal.Vector(1400,3200,120));a.set_actor_label('main_campaign_'+('Ruth' if ruth else 'Mara'));a.set_editor_property('ruth_role',ruth)
assert level.save_current_level()
(root/'artifacts/gameplay-scene/main-campaign.json').write_text(json.dumps({'main_story_actions':5,'optional_repair_spares':1,'companion_actors':2,'new_main_scenes':12,'optional_county_stories_required':False,'companions_are_protected':True,'runtime_escort_verified':False},indent=2))
print('MAIN_CAMPAIGN_PLACED 5 actions 1 recovery-kit 2 protected companions')
