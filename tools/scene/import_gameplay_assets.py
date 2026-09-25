import unreal,json
from pathlib import Path
root=Path('/project');lib=unreal.EditorAssetLibrary;manager=unreal.InterchangeManager.get_interchange_manager_scripted()
for name in ['Pistol','Pipe','Bottle']:
 params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
 assert manager.import_asset('/Game/Story/Props',unreal.InterchangeManager.create_source_data(str(root/'BuildData/props'/(name+'.glb'))),params)
 assert lib.does_asset_exist('/Game/Story/Props/'+name),name
for path in list((root/'BuildData/audio').glob('[A-Z]*.wav'))+list((root/'BuildData/voices').glob('*.wav')):
 dest='/Game/Story/Voices' if path.parent.name=='voices' else '/Game/Story/Audio'
 task=unreal.AssetImportTask();task.filename=str(path);task.destination_path=dest;task.destination_name=path.stem;task.automated=True;task.save=True;task.factory=unreal.SoundFactory()
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 wave=next((unreal.load_asset(x) for x in task.imported_object_paths if isinstance(unreal.load_asset(x),unreal.SoundWave)),None);assert wave,path.name
 wave.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.PCM);lib.save_loaded_asset(wave)
lib.save_directory('/Game/Story',False,True)
print('GAMEPLAY_PROPS_AND_SOUNDS_IMPORTED')
