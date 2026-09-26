"""Import and place the connected rural region in the actual UE map."""
import json,sys,math
from pathlib import Path
import unreal
root=Path('/project');sys.path.insert(0,str(root/'tools/scene'))
from county_layout import height
source=root/'.cache/county-pack';lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
basis=json.loads((root/'artifacts/gameplay-scene/scene-construction.json').read_text())['measured_import_basis_cm'];assert basis==[[100.,0.,0.],[0.,-100.,0.],[0.,0.,100.]],basis
manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
models={}
for name in ['Pine','Broadleaf','Fern','MossRock','Stump','Deadwood','Shelter','Terrain','River']:
 dest='/Game/County/'+name
 assert manager.import_asset(dest,unreal.InterchangeManager.create_source_data(str(source/(name+'.glb'))),params)
 meshes=[lib.load_asset(p) for p in lib.list_assets(dest,True,False)];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)]
 assert meshes,('No imported geometry',name);models[name]=meshes
 for mesh in meshes:
  nanite=mesh.get_editor_property('nanite_settings');nanite.set_editor_property('enabled',False);mesh.set_editor_property('nanite_settings',nanite);lib.save_loaded_asset(mesh)
 if name in ('Terrain','Shelter','MossRock','Stump','Deadwood'):
  for mesh in meshes:
   body=mesh.get_editor_property('body_setup');assert body
   body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True);lib.save_loaded_asset(mesh)
 for path in lib.list_assets(dest,True,False):
  texture=lib.load_asset(path)
  if isinstance(texture,unreal.Texture2D) and 'pine_needles' in texture.get_name().lower():
   texture.set_editor_property('do_scale_mips_for_alpha_coverage',True)
   thresholds=texture.get_editor_property('alpha_coverage_thresholds')
   for channel in ['x','y','z']:thresholds.set_editor_property(channel,0)
   thresholds.set_editor_property('w',.28);texture.set_editor_property('alpha_coverage_thresholds',thresholds);lib.save_loaded_asset(texture)
 lib.save_directory(dest,False,True)
# Repeatable rebuilding must not double the population.
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('county_'):actors.destroy_actor(actor)
data=json.loads((source/'county.json').read_text());cluster_class=unreal.load_class(None,'/Script/PocoSurvival.SurvivalSceneryCluster');assert cluster_class
clusters={}
for name,distance in [('Pine',47000),('Broadleaf',47000),('Fern',9000),('MossRock',24000),('Stump',19000),('Deadwood',23000)]:
 actor=actors.spawn_actor_from_class(cluster_class,unreal.Vector());actor.set_actor_label('county_'+name);actor.configure(models[name][0],distance,name in ('Pine','Broadleaf'),name in ('MossRock','Stump','Deadwood'));clusters[name]=actor
for point in data['instances']:
 clusters[point['mesh']].add_scenery(unreal.Vector(point['x']*100,point['y']*100,point['z']*100),point['yaw'],point['scale'])
def mesh_actor(name,mesh,pos=(0,0,0),collision=True):
 actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in pos]));actor.set_actor_label('county_'+name)
 c=actor.static_mesh_component;c.set_static_mesh(mesh);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('BlockAll' if collision else 'NoCollision');return actor
for mesh in models['Terrain']:mesh_actor(mesh.get_name(),mesh)
mesh_actor('River',models['River'][0],collision=False)
for i,p in enumerate(data['pois']):
 mesh_actor(p['id'],models['Shelter'][0],(p['x'],p['y'],p['z']+.25))
 label=actors.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector((p['x']-2.4)*100,(p['y']-3.62)*100,(p['z']+2.2)*100),unreal.Rotator(pitch=0,yaw=-90,roll=0));label.set_actor_label('county_sign_'+p['id'])
 text=label.get_component_by_class(unreal.TextRenderComponent);text.set_text(p['title']+'\n'+p['detail']);text.set_world_size(12);text.set_text_render_color(unreal.Color(222,207,160,255))
 # Targets are production points of interest and deterministic diagnostic anchors.
 target=actors.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector((p['x']-9)*100,(p['y']-12)*100,(p['z']+4)*100));target.set_actor_label('county_anchor_'+p['id']);target.set_editor_property('tags',[unreal.Name('county_proof'),unreal.Name(p['id'])])
# Usable timber crossing over the eastern stream, with rails and visible supports.
cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalCityGeometry');bridge=actors.spawn_actor_from_class(cls,unreal.Vector());bridge.set_actor_label('county_bridge')
# Terrain banks remain below this deck; broad ramps meet the road rather than a teleport.
x=470+65*math.sin(40/240)
deck=max(height(x-78,40),height(x+78,40))+1.5
bridge.add_box(unreal.Vector(x*100,4000,deck*100),unreal.Vector(15500,700,30),4)
for yy in [36.7,43.3]:
 bridge.add_box(unreal.Vector(x*100,yy*100,(deck+1)*100),unreal.Vector(15500,14,14),4)
 for xx in range(-70,71,10):bridge.add_box(unreal.Vector((x+xx)*100,yy*100,deck*50),unreal.Vector(22,22,deck*100),4)
# Sloped ramps use cube local transforms and collide just like the deck.
cube=lib.load_asset('/Engine/BasicShapes/Cube')
for side in [-1,1]:
 outer=height(x+side*147.5,40)+.1;rise=deck-outer;length=math.hypot(70,rise)
 ramp=mesh_actor('bridge_ramp_'+str(side),cube,(x+side*112.5,40,(deck+outer)/2));ramp.set_actor_scale3d(unreal.Vector(length,7,.30));ramp.set_actor_rotation(unreal.Rotator(pitch=-side*math.degrees(math.atan2(rise,70)),yaw=0,roll=0),False)
report={'connected_extent_m':data['extent_m'],'terrain_tiles':len(models['Terrain']),'rural_shelters':len(data['pois']),'nature_instances':len(data['instances']),'instanced_clusters':len(clusters),'simple_trunk_collision':True,'river_crossing':True,'native_runtime_traversal_verified':False,'final_art':False}
assert report['terrain_tiles']==16 and report['rural_shelters']==6
assert level.save_current_level();lib.save_directory('/Game/County',False,True)
(root/'artifacts/gameplay-scene/county-content.json').write_text(json.dumps(report,indent=2)+'\n');print('COUNTY_CONTENT_PASS',json.dumps(report),flush=True)
