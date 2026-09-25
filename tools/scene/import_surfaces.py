import unreal,json
from pathlib import Path
root=Path('/project');lib=unreal.EditorAssetLibrary
for a in json.loads((root/'BuildData/surfaces.lock.json').read_text())['assets']:
 for f in a['files']:
  name=Path(f['path']).stem;dest='/Game/Story/Surfaces/'+name
  if lib.does_asset_exist(dest):continue
  t=unreal.AssetImportTask();t.filename=str(root/'BuildData/surfaces'/f['path']);t.destination_path='/Game/Story/Surfaces';t.destination_name=name;t.automated=True;t.save=True;t.factory=unreal.TextureFactory();unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
  tex=lib.load_asset(dest);assert tex
  if f['role']!='Diffuse':tex.set_editor_property('srgb',False)
  if f['role']=='nor_dx':tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP)
  lib.save_loaded_asset(tex)
print('PBR_SURFACES_IMPORTED')
