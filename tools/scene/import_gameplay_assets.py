import unreal,json
from pathlib import Path
root=Path('/project');lib=unreal.EditorAssetLibrary;manager=unreal.InterchangeManager.get_interchange_manager_scripted()
for name in ['Pistol','Pipe','Bottle','Bow','Arrow','SupplyCrate','Door','FieldRadio','EvidenceFolder','SignalSwitch']:
 if lib.does_asset_exist('/Game/Story/Props/'+name):continue
 params=unreal.ImportAssetParameters();params.set_editor_property('is_automated',True);params.set_editor_property('replace_existing',True)
 assert manager.import_asset('/Game/Story/Props',unreal.InterchangeManager.create_source_data(str(root/'BuildData/props'/(name+'.glb'))),params)
 imported=[lib.load_asset(p) for p in lib.list_assets('/Game/Story/Props',True,False)]
 meshes=[x for x in imported if isinstance(x,unreal.StaticMesh) and x.get_name()==name]
 assert len(meshes)==1,(name,[x.get_path_name() for x in meshes])
 assert lib.rename_asset(meshes[0].get_path_name(),'/Game/Story/Props/'+name)
 nanite=meshes[0].get_editor_property('nanite_settings');nanite.set_editor_property('enabled',False);meshes[0].set_editor_property('nanite_settings',nanite)
 lib.save_loaded_asset(meshes[0])
for path in list((root/'BuildData/audio').glob('[A-Z]*.wav'))+list((root/'BuildData/voices').glob('*.wav'))+list((root/'BuildData/filmvoices').glob('*.wav'))+list((root/'BuildData/countyvoices').glob('*.wav'))+list((root/'BuildData/mainvoices').glob('*.wav'))+list((root/'BuildData/journeyvoices').glob('*.wav')):
 dest='/Game/Story/JourneyVoices' if path.parent.name=='journeyvoices' else '/Game/Story/MainVoices' if path.parent.name=='mainvoices' else '/Game/Story/CountyVoices' if path.parent.name=='countyvoices' else '/Game/Story/FilmVoices' if path.parent.name=='filmvoices' else '/Game/Story/Voices' if path.parent.name=='voices' else '/Game/Story/Audio'
 if lib.does_asset_exist(dest+'/'+path.stem):continue
 task=unreal.AssetImportTask();task.filename=str(path);task.destination_path=dest;task.destination_name=path.stem;task.automated=True;task.save=True;task.factory=unreal.SoundFactory()
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 wave=next((unreal.load_asset(x) for x in task.imported_object_paths if isinstance(unreal.load_asset(x),unreal.SoundWave)),None);assert wave,path.name
 wave.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.PCM)
 if path.stem=='Rain' or path.stem.startswith('Score'):
  wave.set_editor_property('looping',True);wave.set_editor_property('virtualization_mode',unreal.VirtualizationMode.PLAY_WHEN_SILENT)
 lib.save_loaded_asset(wave)
if not lib.does_asset_exist('/Game/Story/Materials/M_Rain'):
 mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_Rain','/Game/Story/Materials',unreal.Material,unreal.MaterialFactoryNew())
 mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
 mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_ADDITIVE)
 node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector)
 node.set_editor_property('constant',unreal.LinearColor(.025,.034,.04,1));unreal.MaterialEditingLibrary.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 unreal.MaterialEditingLibrary.recompile_material(mat);lib.save_loaded_asset(mat)
lib.save_directory('/Game/Story',False,True)
print('GAMEPLAY_PROPS_AND_SOUNDS_IMPORTED')
