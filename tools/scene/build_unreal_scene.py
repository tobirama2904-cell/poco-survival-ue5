"""Execute inside the pinned editor. No claim of rendering from this commandlet."""
import json,hashlib,traceback,struct,re
from pathlib import Path
import unreal
root=Path('/project');source=root/'.cache/scene-source';report_dir=root/'artifacts/gameplay-scene';report_dir.mkdir(parents=True,exist_ok=True)
recipe=json.loads((source/'courtyard.json').read_text());assert hashlib.sha256((source/'courtyard.glb').read_bytes()).hexdigest()==recipe['glb_sha256']
asset_tools=unreal.AssetToolsHelpers.get_asset_tools()
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mesh_tools=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
report={'phase':'native-editor-scene-construction','source_glb_sha256':recipe['glb_sha256'],'visual_render_tested':False,'android_package_tested':False,'physical_device_tested':False}
def import_file(file,destination):
 # AssetTools.ImportAssetTasks completed the import but then tried to sync
 # the Content Browser, crashing in FSlateApplication under a commandlet.
 # Call the synchronous Interchange API directly, without a browser callback.
 manager=unreal.InterchangeManager.get_interchange_manager_scripted()
 data=unreal.InterchangeManager.create_source_data(str(file))
 params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
 assert manager.import_asset(destination,data,params),('Interchange import failed',str(file))
 unreal.EditorAssetLibrary.save_directory(destination,False,True)
 paths=list(unreal.EditorAssetLibrary.list_assets(destination,True,False));print('IMPORTED_PATHS',json.dumps(paths));assert paths,('Import produced no assets',str(file))
 return paths
try:
 import_file(source/'courtyard.glb','/Game/Environment/Courtyard')
 import_file(source/'sky.hdr','/Game/Environment/Sky')
 # Importer versions differ on mesh-name versus node-name preference.
 # Both names come from the pinned GLB; never guess axes from engine folklore.
 raw=(source/'courtyard.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length]);del raw
 aliases={}
 for node in gltf.get('nodes',[]):
  if node.get('name','').startswith('FRAME_'):
   label=node['name'].split('FRAME_',1)[1];aliases[node['name']]=label
   aliases[re.sub('[^A-Za-z0-9_]','_',gltf['meshes'][node['mesh']].get('name',node['name']))]=label
 meshes=[];frames={}
 for path in unreal.EditorAssetLibrary.list_assets('/Game/Environment/Courtyard',True,False):
  ob=unreal.load_asset(path)
  if isinstance(ob,unreal.StaticMesh):
   name=ob.get_name();print('MESH',name)
   label=next((value for key,value in aliases.items() if name==key or name.endswith('_'+key)),None)
   if label:
    box=ob.get_bounding_box();frames[label]=(box.min+box.max)*.5
   else:meshes.append(ob)
 assert all(k in frames for k in ['ORIGIN','X','Y','Z']),str(frames)
 origin=frames['ORIGIN'];axes=[frames[k]-origin for k in ['X','Y','Z']]
 for axis in axes:assert abs((axis.x**2+axis.y**2+axis.z**2)**.5-100)<.1,('Invalid metre conversion',axis)
 def dot(a,b):return a.x*b.x+a.y*b.y+a.z*b.z
 assert abs(dot(axes[0],axes[1]))<.1 and abs(dot(axes[0],axes[2]))<.1 and abs(dot(axes[1],axes[2]))<.1
 def point(p):return origin+axes[0]*p[0]+axes[1]*p[1]+axes[2]*p[2]
 report['measured_import_basis_cm']=[[v.x,v.y,v.z] for v in axes]
 assert level.new_level('/Game/Worlds/CanalDistrict'),'Could not create actual map package'
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 for mesh in meshes:
  # Interchange enables Nanite by default in this engine. Mobile must retain the
  # authored mesh, not the aggressively reduced Nanite fallback (256 yard tris).
  nanite=mesh.get_editor_property('nanite_settings')
  nanite.set_editor_property('enabled',False)
  mesh.set_editor_property('nanite_settings',nanite)
  assert not mesh.get_editor_property('nanite_settings').get_editor_property('enabled')
  body=mesh.get_editor_property('body_setup')
  assert body,('Missing mesh collision body',mesh.get_name())
  body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  body.set_editor_property('double_sided_geometry',True)
  actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));actor.set_actor_label(mesh.get_name());actor.static_mesh_component.set_static_mesh(mesh)
  actor.static_mesh_component.set_collision_profile_name('BlockAll')
  unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 def native(name):
  cls=unreal.load_class(None,'/Script/PocoSurvival.'+name);assert cls,name;return cls
 for item in recipe['interactions']:
  actor=actors.spawn_actor_from_class(native('SurvivalInteraction'),point(item['position']));actor.set_actor_label('objective_'+item['action']);actor.set_editor_property('action_id',unreal.Name(item['action']))
 for p in [[-11,-6,3.5],[13,-6,3.5],[-10,14,3.5],[16,12,3.5]]:
  actors.spawn_actor_from_class(native('SurvivalPoweredLight'),point(p))
 for index,item in enumerate(recipe['infected']):
  actor=actors.spawn_actor_from_class(native('SurvivalInfected'),point(item['position']));actor.set_actor_label('infected_engineering_proxy');actor.set_editor_property('persistent_id',unreal.Name('canal_infected_%03d'%index));actor.set_editor_property('patrol_points',[point(p) for p in item['patrol']])
 spawn=point(recipe['spawn']);look=point(recipe['look_at']);rotation=unreal.MathLibrary.find_look_at_rotation(spawn,look)
 start=actors.spawn_actor_from_class(unreal.PlayerStart,spawn,unreal.Rotator(pitch=-10.0,yaw=rotation.yaw,roll=0.0));start.set_actor_label('safe_player_spawn')
 measured_start=start.get_actor_rotation()
 assert abs(measured_start.pitch+10)<.1 and abs(measured_start.roll)<.1,('Invalid spawn camera rotation',measured_start)
 report['spawn_rotation_degrees']={'pitch':measured_start.pitch,'yaw':measured_start.yaw,'roll':measured_start.roll}
 camera=actors.spawn_actor_from_class(unreal.CameraActor,point(recipe['intro_camera']),unreal.MathLibrary.find_look_at_rotation(point(recipe['intro_camera']),point(recipe['intro_look_at'])))
 camera.set_editor_property('tags',[unreal.Name('intro_camera')]);camera.camera_component.set_editor_property('field_of_view',68)
 world.get_world_settings().set_editor_property('default_game_mode',native('SurvivalGameMode'))
 sun=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1800),unreal.Rotator(pitch=-35.0,yaw=-42.0,roll=0.0));sun.set_actor_label('late_afternoon_sun')
 light=sun.get_component_by_class(unreal.DirectionalLightComponent);light.set_mobility(unreal.ComponentMobility.MOVABLE);light.set_editor_property('intensity',3.0);light.set_editor_property('light_color',unreal.Color(255,221,178,255))
 light.set_editor_property('atmosphere_sun_light',True);light.set_editor_property('dynamic_shadow_distance_movable_light',6000)
 actors.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector())
 sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,2000));sl=sky.get_component_by_class(unreal.SkyLightComponent);sl.set_mobility(unreal.ComponentMobility.MOVABLE)
 cubes=[unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets('/Game/Environment/Sky',True,False)]
 cube=next((c for c in cubes if isinstance(c,unreal.TextureCube)),None);assert cube,'HDR must import as an actual TextureCube'
 sl.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);sl.set_editor_property('cubemap',cube);sl.set_editor_property('intensity',.8)
 post=actors.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector());post.set_editor_property('unbound',True)
 settings=post.get_editor_property('settings');settings.set_editor_property('override_auto_exposure_min_brightness',True);settings.set_editor_property('auto_exposure_min_brightness',.7);settings.set_editor_property('override_auto_exposure_max_brightness',True);settings.set_editor_property('auto_exposure_max_brightness',.7);post.set_editor_property('settings',settings)
 # Native actor health/stamina methods are exercised inside a real editor world.
 player=actors.spawn_actor_from_class(native('SurvivalCharacter'),spawn+unreal.Vector(0,0,300))
 assert player.get_health()==100 and player.get_stamina()==100
 assert player.restore_vitals(80,60)
 unreal.GameplayStatics.apply_damage(player,25,None,None,unreal.DamageType)
 assert player.get_health()==55
 player.attack();assert player.get_stamina()==42
 assert not player.restore_vitals(101,50)
 actors.destroy_actor(player)
 report.update({'map':'/Game/Worlds/CanalDistrict','native_vitals_damage_attack_cost_tested':True,'static_mesh_count':len(meshes),'nanite_disabled_for_mobile_geometry':True,'interactions_placed':len(recipe['interactions']),'enemy_proxies_placed':len(recipe['infected']),'actors_in_saved_scene':len(actors.get_all_level_actors()),'source_triangles':recipe['triangles'],'complete_campaign':False,'final_character_art':False})
 assert level.save_current_level(),'Map save failed'
 unreal.EditorAssetLibrary.save_directory('/Game',False,True)
 (report_dir/'scene-construction.json').write_text(json.dumps(report,indent=2)+'\n');print('GAMEPLAY_SCENE_CONSTRUCTION_PASS',json.dumps(report))
except Exception as e:
 report['error']=str(e);report['traceback']=traceback.format_exc();(report_dir/'scene-construction-failure.json').write_text(json.dumps(report,indent=2)+'\n');raise
