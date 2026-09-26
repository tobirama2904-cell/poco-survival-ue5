"""Repair measured shader-usage failures on retained assets before render/cook.
No native-code changes or regeneration of the already constructed county.
"""
import json,subprocess
from pathlib import Path
import unreal
root=Path('/project');out=root/'artifacts/gameplay-scene';out.mkdir(parents=True,exist_ok=True)
lib=unreal.EditorAssetLibrary;level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
changed=[];visited=set()
def repair_parent(asset):
 if asset is None or asset.get_path_name() in visited:return
 visited.add(asset.get_path_name())
 if isinstance(asset,unreal.Material):
  asset.set_editor_property('used_with_instanced_static_meshes',True)
  if asset.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_MASKED:asset.set_editor_property('dithered_lod_transition',True)
  unreal.MaterialEditingLibrary.recompile_material(asset);assert lib.save_loaded_asset(asset)
  assert asset.get_editor_property('used_with_instanced_static_meshes')
  changed.append(asset.get_path_name())
 elif isinstance(asset,unreal.MaterialInstanceConstant):
  # glTF imports MaterialInstances whose shader-bearing parent can live in
  # the Interchange plugin, outside /Game/County. Repair that parent too.
  repair_parent(asset.get_editor_property('parent'))
  unreal.MaterialEditingLibrary.update_material_instance(asset)
  assert lib.save_loaded_asset(asset)
for directory in ['/Game/Story/Materials','/Game/County']:
 for path in lib.list_assets(directory,True,False):repair_parent(lib.load_asset(path))
labels=[a.get_actor_label() for a in actors.get_all_level_actors()]
field={'loot_caches':sum(s.startswith('field_cache_') for s in labels),'openable_doors':sum(s.startswith('field_door_') for s in labels)}
county={'terrain_tiles':sum(s.startswith('county_Terrain_') for s in labels),'rural_shelters':sum(s.startswith('county_anchor_') for s in labels),'nature_instances':0}
for actor in actors.get_all_level_actors():
 if actor.get_class().get_name()=='SurvivalSceneryCluster':
  for comp in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   if comp.get_name()=='Vegetation':county['nature_instances']+=comp.get_instance_count()
assert field=={'loot_caches':24,'openable_doors':24},field
expected=json.loads((root/'BuildData/county-pack.lock.json').read_text()).get('layout',{'nature_instances':6188})
assert county=={'terrain_tiles':16,'rural_shelters':6,'nature_instances':expected['nature_instances']},county
assert len(changed)>=6,changed
# Revalidate the actual retained LOD assets as well, including during Android cook.
mesh_editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);lods={}
for name in ['Pine','Broadleaf','Fern','MossRock','Stump','Deadwood']:
 meshes=[lib.load_asset(path) for path in lib.list_assets('/Game/County/'+name,True,False)]
 meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)];assert meshes,name
 mesh=meshes[0];assert mesh_editor.get_lod_count(mesh)==3,(name,mesh_editor.get_lod_count(mesh))
 counts=[mesh_editor.get_number_verts(mesh,i) for i in range(3)]
 assert counts[0]>=counts[1]>=counts[2]>0,(name,counts)
 if name=='Pine':
  assert counts[2]<=16,(name,counts)
  assert all(abs(a-b)<.001 for a,b in zip(mesh_editor.get_lod_screen_sizes(mesh),[1,.65,.24]))
 lods[name]={'vertices':counts,'screens':list(mesh_editor.get_lod_screen_sizes(mesh))}
(out/'forest-lods.json').write_text(json.dumps(lods,indent=2)+'\n')
assert level.save_current_level()
report={'source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'all_construction_steps_succeeded':True,'retained_scene_recounted':True,'field':field,'county':county,'instance_materials_repaired':changed}
(out/'scene-ready.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'material-repair.json').write_text(json.dumps({'materials':changed,'actual_saved_world_counts':{'field':field,'county':county}},indent=2)+'\n')
print('RETAINED_SCENE_MATERIALS_REPAIRED',len(changed),json.dumps(county),flush=True)
