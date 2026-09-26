"""Build connected authored quest districts into the real UE map. Internal art pass."""
import json,random
from pathlib import Path
import unreal
root=Path('/project');d=json.loads((root/'BuildData/story/city.json').read_text())
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
colors=[(.18,.21,.18),(.34,.28,.22),(.16,.19,.20),(.06,.095,.10),(.26,.20,.15),(.42,.33,.21)]
for i,color in enumerate(colors):
 path='/Game/Story/Materials/M_City'+str(i)
 if lib.does_asset_exist(path):continue
 mat=None
 if not mat:mat=tools.create_asset('M_City'+str(i),'/Game/Story/Materials',unreal.Material,unreal.MaterialFactoryNew())
 palette=['concrete_floor_02','brick_wall_001','concrete_floor_02',None,'wood_planks_grey','rusty_metal_04'];texture=palette[i]
 if texture:
  uv=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate);uv.set_editor_property('u_tiling',120.0 if i==0 else 4.0);uv.set_editor_property('v_tiling',120.0 if i==0 else 4.0)
  for suffix,prop in [('Diffuse',unreal.MaterialProperty.MP_BASE_COLOR),('nor_dx',unreal.MaterialProperty.MP_NORMAL)]:
   node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample);node.set_editor_property('texture',lib.load_asset('/Game/Story/Surfaces/'+texture+'_'+suffix))
   if suffix=='nor_dx':node.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
   unreal.MaterialEditingLibrary.connect_material_expressions(uv,'',node,'UVs');unreal.MaterialEditingLibrary.connect_material_property(node,'RGB',prop)
 else:
  node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);node.set_editor_property('constant',unreal.LinearColor(*color,1));unreal.MaterialEditingLibrary.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
 wet=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionScalarParameter);wet.set_editor_property('parameter_name','Wetness');wet.set_editor_property('default_value',0)
 rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate);rough.set_editor_property('const_a',.8);rough.set_editor_property('const_b',.22);unreal.MaterialEditingLibrary.connect_material_expressions(wet,'',rough,'Alpha')
 if texture:
  dry=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample);dry.set_editor_property('texture',lib.load_asset('/Game/Story/Surfaces/'+texture+'_Rough'));dry.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);unreal.MaterialEditingLibrary.connect_material_expressions(uv,'',dry,'UVs');unreal.MaterialEditingLibrary.connect_material_expressions(dry,'R',rough,'A')
 unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 unreal.MaterialEditingLibrary.recompile_material(mat);lib.save_loaded_asset(mat)
cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalCityGeometry');assert cls
city=a.spawn_actor_from_class(cls,unreal.Vector());city.set_actor_label('ConnectedCity_InstancedArchitecture')
for component in city.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
 index=int(component.get_name().replace('Surface',''));component.set_material(0,lib.load_asset('/Game/Story/Materials/M_City'+str(index)))
boxes=0
def box(p,size,surface):
 global boxes
 city.add_box(unreal.Vector(*[v*100 for v in p]),unreal.Vector(*[v*100 for v in size]),surface);boxes+=1
box((0,0,-.6),(640,640,1),0)
# Uninterrupted avenues connect all districts; no loading tunnels or hidden travel.
for x in [-180,0,180]:box((x,0,-.06),(18,620,.08),2)
for y in [-160,40,100,210]:box((0,y,-.055),(620,16,.09),2)
rng=random.Random(1491);buildings=0;interiors=[]
sites=[s['position'] for s in d['sites']]
for cx in range(-270,271,60):
 for cy in range(-270,271,60):
  if abs(cx)<60 and abs(cy)<60:continue # Preserve the detailed imported courtyard.
  if any(abs(cx-p[0])<30 and abs(cy-p[1])<30 for p in sites):continue
  if min(abs(cx-x) for x in [-180,0,180])<20 or min(abs(cy-y) for y in [-160,40,100,210])<19:continue
  w=rng.choice([14,18,22]);depth=rng.choice([12,16,20]);h=rng.choice([8,12,16]);buildings+=1
  # Walkable ground-floor shell, not a solid inaccessible tower.
  for dx in [-w/2,w/2]:box((cx+dx,cy,1.5),(.35,depth,3),1)
  box((cx,cy+depth/2,1.5),(w,.35,3),1)
  for side in [-1,1]:box((cx+side*(w/4+.45),cy-depth/2,1.5),(w/2-.9,.35,3),1)
  box((cx,cy-depth/2,2.8),(1.8,.35,.4),1)
  box((cx,cy,3.15),(w,depth,.3),4)
  if h>3.3:box((cx,cy,(h+3.3)/2),(w,depth,h-3.3),1)
  interiors.append([cx,cy,w,depth])
  # Detailed furnishings are placed by populate_interiors.py; do not overlap them with placeholder cubes.
  box((cx,cy,h+.25),(w+.8,depth+.8,.5),2)
  box((cx,cy,.1),(w+1,depth+1,.4),4)
  for z in range(2,h,3):
   for dx in range(-int(w/2)+2,int(w/2)-1,4):
    for side in [-1,1]:box((cx+dx,cy+side*(depth/2+.035),z),(1.6,.06,1.8),3)
# District-specific structures leave every authored interaction in an open plaza.
for x in [155,167,179]:
 box((x,-193,3.5),(8,12,7),2);box((x,-193,7.2),(9,13,.4),5)
for x in [-15,-5,5,15]:
 box((x,247,3.5),(8,12,.3),4)
 for dx in [-3,3]:box((x+dx,247,1.7),(.25,11,3.4),5)
for x in [208,220]:box((x,108,12),(1,1,24),5)
box((214,108,22),(14,3,.5),2)
existing={str(o.get_editor_property('action_id')):o for o in a.get_all_level_actors() if o.get_class().get_name()=='SurvivalInteraction'}
interaction=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInteraction');cube=lib.load_asset('/Engine/BasicShapes/Cube')
for s in d['sites']:
 if s['id'] in existing:continue
 x,y,z=s['position'];actor=a.spawn_actor_from_class(interaction,unreal.Vector(x*100,y*100,z*100+45));actor.set_actor_label('story_'+s['id']);actor.set_editor_property('action_id',unreal.Name(s['id']))
 mesh=actor.get_editor_property('mesh');mesh.set_static_mesh(cube);mesh.set_world_scale3d(unreal.Vector(.55,.42,.8));mesh.set_material(0,lib.load_asset('/Game/Story/Materials/M_City5'))
# Authored patrol encounters with stable IDs, outside the safe depot and dialogue sites.
enemy=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInfected')
for i,(x,y) in enumerate([(-148,-160),(-205,-130),(-180,-200),(-150,70),(147,-150),(210,-185),(180,65),(225,85),(35,210),(-35,240)]):
 actor=a.spawn_actor_from_class(enemy,unreal.Vector(x*100,y*100,100));actor.set_actor_label('city_encounter_'+str(i));actor.set_editor_property('persistent_id',unreal.Name('city_001_%02d'%i));actor.set_editor_property('archetype',i%3);actor.set_editor_property('patrol_points',[unreal.Vector(x*100,y*100,100),unreal.Vector((x+6)*100,(y+3)*100,100)])
# Three physically present, dressed and animated story characters, not portraits on props.
for role,speaker,pos in [('Leyla','Лейла',[-1.4,14,0]),('Nargis','Наргис',[-188.4,43,0]),('Ilyas','Ильяс',[193.6,101,0])]:
 actor=a.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(*[v*100 for v in pos]),unreal.Rotator(pitch=0,yaw=-90,roll=0));actor.set_actor_label('story_person_'+role);actor.set_editor_property('tags',[unreal.Name(speaker)])
 c=actor.skeletal_mesh_component;c.set_skeletal_mesh_asset(lib.load_asset('/Game/Story/Characters/'+role+'/Body'));c.set_collision_profile_name('NoCollision');c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
 data=c.get_editor_property('animation_data');data.set_editor_property('anim_to_play',lib.load_asset('/Game/Story/Characters/'+role+'/Idle'));data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);c.set_editor_property('animation_data',data)
# AI concept portraits, explicitly not final 3D character assets.
manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
assert manager.import_asset('/Game/Story',unreal.InterchangeManager.create_source_data(str(root/'BuildData/story/portraits.jpg')),params)
(root/'artifacts/gameplay-scene/interiors.json').write_text(json.dumps(interiors))
assert level.save_current_level();lib.save_directory('/Game/Story',False,True)
report={'connected_ground_m':640,'authored_districts':len(d['districts']),'total_action_sites':len(d['sites']),'additional_patrols':10,'instanced_boxes':boxes,'buildings':buildings,'final_art':False,'measured_campaign_hours':None,'traversal_tested':False}
(root/'artifacts/gameplay-scene/city-construction.json').write_text(json.dumps(report,indent=2));print('CITY_CONSTRUCTION_PASS',json.dumps(report))
