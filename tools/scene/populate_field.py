"""Actual placed loot, usable doors and main-cast blocking, not map-size inflation."""
import unreal,json
from pathlib import Path
root=Path('/project');a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
for actor in a.get_all_level_actors():
 if actor.get_actor_label().startswith(('field_cache_','field_door_','film_cast_','film_gate_')):a.destroy_actor(actor)
cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInteraction')
for prop in ['SupplyCrate','Door']:
 mesh=lib.load_asset('/Game/Story/Props/'+prop);assert mesh
 # StaticMeshEditorSubsystem is intentionally absent in the headless commandlet.
 # Same verified BodySetup path as courtyard import. No simulated rigid-body door.
 body=mesh.get_editor_property('body_setup');assert body,prop
 body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);lib.save_loaded_asset(mesh)
positions=[(2,13),(13,31),(-115,42),(-185,46),(-148,103),(-210,110),(0,205),(20,236),(159,-182),(4,211),(-6,209),(195,-153),(208,46),(215,100),(185,105),(170,-123),(-118,44),(25,242),(-255,-60),(255,-60),(-240,205),(240,205),(-230,-215),(230,-215)]
def prop(label,id,name,pos,scale=1,z=15):
 obj=a.spawn_actor_from_class(cls,unreal.Vector(pos[0]*100,pos[1]*100,z));obj.set_actor_label(label);obj.set_editor_property('action_id',unreal.Name(id));m=obj.get_editor_property('mesh');m.set_static_mesh(lib.load_asset('/Game/Story/Props/'+name));m.set_world_scale3d(unreal.Vector(scale,scale,scale));obj.get_editor_property('focus_volume').set_relative_location(unreal.Vector(0,0,70),sweep=False,teleport=True);return obj
for i,pos in enumerate(positions):prop('field_cache_'+str(i),'__cache_'+str(i),'SupplyCrate',pos)
for i,(x,y,w,d) in enumerate(json.loads((root/'artifacts/gameplay-scene/interiors.json').read_text())[:24]):
 door=prop('field_door_'+str(i),'__door_'+str(i),'Door',(x-.6,y-d/2-.05),z=35);door.get_editor_property('focus_volume').set_relative_location(unreal.Vector(60,0,100),sweep=False,teleport=True)
for i,pos in enumerate([(179,-183),(182,-183)]):
 gate=prop('film_gate_'+str(i),'__gate_open' if i==0 else '__gate_hold','SupplyCrate',pos,.8)
 gate.get_editor_property('mesh').set_material(0,lib.load_asset('/Game/Story/Materials/M_City'+('5' if i==0 else '3')))
# Licensed body proxies remain explicitly provisional, not newly finished cast art.
for role,body,pos in [('Mara','Leyla',(14,32)),('Ruth','Nargis',(-187,45)),('Owen','Ilyas',(2,210)),('Mara_Gate','Leyla',(181,-184))]:
 obj=a.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(pos[0]*100,pos[1]*100,0),unreal.Rotator(pitch=0,yaw=-90,roll=0));obj.set_actor_label('film_cast_'+role);obj.set_editor_property('tags',[unreal.Name('american_cast'),unreal.Name(role.split('_')[0])]);c=obj.skeletal_mesh_component;c.set_skeletal_mesh_asset(lib.load_asset('/Game/Story/Characters/'+body+'/Body'));c.set_collision_profile_name('NoCollision');c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);data=c.get_editor_property('animation_data');data.set_editor_property('anim_to_play',lib.load_asset('/Game/Story/Characters/'+body+'/Talk'));data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);c.set_editor_property('animation_data',data)
assert level.save_current_level()
(root/'artifacts/gameplay-scene/field-content.json').write_text(json.dumps({'loot_caches':24,'openable_doors':min(24,len(json.loads((root/'artifacts/gameplay-scene/interiors.json').read_text()))),'main_cast_body_proxies':4,'final_art':False}))
