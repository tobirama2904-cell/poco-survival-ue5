"""Populate the actual existing accessible rooms; no map-size/duration claim."""
import unreal,json,sys
from pathlib import Path
ROOT=Path('/project');sys.path.insert(0,str(ROOT/'tools/scene'))
from interior_layout import dress,cache_position
lib=unreal.EditorAssetLibrary;level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
pack=ROOT/'.cache/interior-pack';manifest=json.loads((pack/'conditioning.json').read_text());meshes={}
manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
for item in manifest['models']:
 dest='/Game/Interiors/'+item['name'];assert manager.import_asset(dest,unreal.InterchangeManager.create_source_data(str(pack/item['file'])),params)
 found=[lib.load_asset(p) for p in lib.list_assets(dest,True,False)];found=[m for m in found if isinstance(m,unreal.StaticMesh)];assert len(found)==1,(item['name'],len(found));m=found[0]
 settings=m.get_editor_property('nanite_settings');settings.set_editor_property('enabled',False);m.set_editor_property('nanite_settings',settings)
 body=m.get_editor_property('body_setup');assert body;body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True);lib.save_loaded_asset(m);meshes[item['name']]=m
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('interior_detail_'):actors.destroy_actor(actor)
rooms=json.loads((ROOT/'artifacts/gameplay-scene/interiors.json').read_text());records=dress(rooms)
for i,r in enumerate(records):
 actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(r['x']*100,r['y']*100,r['z']*100),unreal.Rotator(pitch=0,yaw=r['yaw'],roll=0));actor.set_actor_label('interior_detail_'+str(i)+'_'+r['model']);component=actor.static_mesh_component;component.set_static_mesh(meshes[r['model']]);component.set_mobility(unreal.ComponentMobility.STATIC);component.set_collision_profile_name('NoCollision' if r['small'] else 'BlockAll');component.set_cull_distance(5000);component.set_editor_property('cast_shadow',not r['small'])
# Reuse six existing non-story loot IDs, preserving their finite saved contents.
# Bow cache, clinic/plot supplies, dam-dependent caches and quest packs stay put.
moved=[]
for actor in actors.get_all_level_actors():
 if actor.get_class().get_name()!='SurvivalInteraction':continue
 action=str(actor.get_editor_property('action_id'))
 for index in range(18,24):
  if action=='__cache_'+str(index) and index-18<len(rooms):
   x,y,z=cache_position(rooms[index-18]);actor.set_actor_location(unreal.Vector(x*100,y*100,z*100),False,True);moved.append(index)
assert len(moved)==min(6,len(rooms)),moved
assert level.save_current_level();lib.save_directory('/Game/Interiors',False,True)
report={'rooms_dressed':len(rooms),'props':len(records),'unique_source_models':len(meshes),'retained_loot_ids_moved':moved,'floor_top_m':.30,'cull_distance_m':50,'new_gameplay_duration_claimed':False,'in_game_walkthrough_verified':False}
(ROOT/'artifacts/gameplay-scene/interior-detail.json').write_text(json.dumps(report,indent=2)+'\n');print('INTERIOR_DETAIL_READY',json.dumps(report),flush=True)
