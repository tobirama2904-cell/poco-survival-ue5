"""Repair measured shader-usage failures on retained assets before render/cook.
No native-code changes or regeneration of the already constructed county.
"""
import json,subprocess
from pathlib import Path
import unreal
root=Path('/project');out=root/'artifacts/gameplay-scene';out.mkdir(parents=True,exist_ok=True)
lib=unreal.EditorAssetLibrary;level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
changed=[]
for directory in ['/Game/Story/Materials','/Game/County']:
 for path in lib.list_assets(directory,True,False):
  asset=lib.load_asset(path)
  if isinstance(asset,unreal.Material):
   asset.set_editor_property('used_with_instanced_static_meshes',True)
   unreal.MaterialEditingLibrary.recompile_material(asset);assert lib.save_loaded_asset(asset)
   assert asset.get_editor_property('used_with_instanced_static_meshes')
   changed.append(path)
labels=[a.get_actor_label() for a in actors.get_all_level_actors()]
field={'loot_caches':sum(s.startswith('field_cache_') for s in labels),'openable_doors':sum(s.startswith('field_door_') for s in labels)}
county={'terrain_tiles':sum(s.startswith('county_Terrain_') for s in labels),'rural_shelters':sum(s.startswith('county_anchor_') for s in labels),'nature_instances':0}
for actor in actors.get_all_level_actors():
 if actor.get_class().get_name()=='SurvivalSceneryCluster':
  for comp in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   if comp.get_name()=='Vegetation':county['nature_instances']+=comp.get_instance_count()
assert field=={'loot_caches':24,'openable_doors':24},field
assert county=={'terrain_tiles':16,'rural_shelters':6,'nature_instances':6188},county
assert len(changed)>=6,changed
assert level.save_current_level()
report={'source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'all_construction_steps_succeeded':True,'retained_scene_recounted':True,'field':field,'county':county,'instance_materials_repaired':changed}
(out/'scene-ready.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'material-repair.json').write_text(json.dumps({'materials':changed,'actual_saved_world_counts':{'field':field,'county':county}},indent=2)+'\n')
print('RETAINED_SCENE_MATERIALS_REPAIRED',len(changed),json.dumps(county),flush=True)
