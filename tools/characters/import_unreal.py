"""UE commandlet: import the verified GLBs, keep deterministic native paths."""
import json
from pathlib import Path
import unreal
root=Path('/project');lib=unreal.EditorAssetLibrary;manager=unreal.InterchangeManager.get_interchange_manager_scripted();report=[]
for role in ['Arsen','Leyla','Nargis','Ilyas','Infected']:
 dest='/Game/Story/Characters/'+role
 if all(lib.does_asset_exist(dest+'/'+name) for name in ['Body','Idle','Walk','Run','Crouch','Talk']):
  report.append({'role':role,'skeletal_mesh':dest+'/Body.Body','animations':['Idle','Walk','Run','Crouch','Talk'],'reused_verified_import':True});continue
 params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
 assert manager.import_asset(dest,unreal.InterchangeManager.create_source_data(str(root/'.cache/characters'/(role+'.glb'))),params),role
 assets=[lib.load_asset(p) for p in lib.list_assets(dest,True,False)];meshes=[p for p in assets if isinstance(p,unreal.SkeletalMesh)];assert len(meshes)==1,(role,[str(p) for p in meshes]);mesh=meshes[0]
 final=dest+'/Body'
 if mesh.get_path_name().split('.')[0]!=final:assert lib.rename_asset(mesh.get_path_name(),final)
 clips=[]
 for clip in ['Idle','Walk','Run','Crouch','Talk']:
  options=[p for p in assets if isinstance(p,unreal.AnimSequence) and clip.lower() in p.get_name().lower()];assert len(options)==1,(role,clip,[p.get_name() for p in assets]);anim=options[0]
  anim.set_editor_property('enable_root_motion',False);anim.set_editor_property('force_root_lock',True)
  final=dest+'/'+clip
  if anim.get_path_name().split('.')[0]!=final:assert lib.rename_asset(anim.get_path_name(),final)
  lib.save_loaded_asset(anim);clips.append(clip)
 probe=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(0,0,0))
 probe.skeletal_mesh_component.set_skeletal_mesh_asset(mesh)
 origin,extent=probe.get_actor_bounds(False)
 assert 55<extent.z<130,(role,'unexpected skeletal bounds in cm',extent)
 unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(probe)
 lib.save_directory(dest,False,True);report.append({'role':role,'skeletal_mesh':mesh.get_path_name(),'animations':clips,'body_height_cm':extent.z*2})
(root/'artifacts/gameplay-scene/character-import.json').write_text(json.dumps(report,indent=2));print('CHARACTER_IMPORT_PASS',json.dumps(report))
