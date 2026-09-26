"""Reimport only updated Pine into a retained county; rebuild its exact instances.
Do not regenerate story/character/map content or change the already verified terrain.
"""
import json
from pathlib import Path
import unreal
root=Path('/project');lib=unreal.EditorAssetLibrary;level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
source=root/'.cache/county-pack';params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
manager=unreal.InterchangeManager.get_interchange_manager_scripted()
assert manager.import_asset('/Game/County/Pine',unreal.InterchangeManager.create_source_data(str(source/'Pine.glb')),params)
assets=[lib.load_asset(p) for p in lib.list_assets('/Game/County/Pine',True,False)];meshes=[a for a in assets if isinstance(a,unreal.StaticMesh)];assert len(meshes)==1
mesh=meshes[0];settings=mesh.get_editor_property('nanite_settings');settings.set_editor_property('enabled',False);mesh.set_editor_property('nanite_settings',settings);assert lib.save_loaded_asset(mesh)
for texture in assets:
 if isinstance(texture,unreal.Texture2D) and 'pine_needles_bough' in texture.get_name().lower():
  texture.set_editor_property('do_scale_mips_for_alpha_coverage',True);threshold=texture.get_editor_property('alpha_coverage_thresholds')
  for channel in ['x','y','z']:threshold.set_editor_property(channel,0)
  threshold.set_editor_property('w',.28);texture.set_editor_property('alpha_coverage_thresholds',threshold);assert lib.save_loaded_asset(texture)
for actor in actors.get_all_level_actors():
 if actor.get_actor_label()=='county_Pine':actors.destroy_actor(actor)
cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalSceneryCluster');assert cls
actor=actors.spawn_actor_from_class(cls,unreal.Vector());actor.set_actor_label('county_Pine');actor.configure(mesh,47000,True,False)
points=[p for p in json.loads((source/'county.json').read_text())['instances'] if p['mesh']=='Pine']
for p in points:actor.add_scenery(unreal.Vector(p['x']*100,p['y']*100,p['z']*100),p['yaw'],p['scale'])
assert level.save_current_level();lib.save_directory('/Game/County/Pine',False,True)
(root/'artifacts/gameplay-scene/foliage-reimport.json').write_text(json.dumps({'reimported':'Pine','instances':len(points),'rest_of_retained_scene_unchanged':True,'runtime_render_verified':False},indent=2))
print('RETAINED_FOLIAGE_REIMPORTED',len(points),flush=True)
