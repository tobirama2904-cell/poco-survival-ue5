"""Simple mobile cutout material instead of the general glTF material graph.
Run from the editor after Pine import; all connections and slot replacements checked.
"""
import unreal

def apply_mobile_foliage():
 lib=unreal.EditorAssetLibrary;edit=unreal.MaterialEditingLibrary
 paths=lib.list_assets('/Game/County/Pine',True,False);assets=[lib.load_asset(p) for p in paths]
 textures=[a for a in assets if isinstance(a,unreal.Texture2D) and 'pine_needles_bough' in a.get_name().lower()]
 assert len(textures)==1,('Expected one baked branch atlas',[a.get_name() for a in assets if isinstance(a,unreal.Texture2D)])
 path='/Game/County/MobileMaterials/M_NeedleBoughCutout'
 if lib.does_asset_exist(path):mat=lib.load_asset(path)
 else:
  mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_NeedleBoughCutout','/Game/County/MobileMaterials',unreal.Material,unreal.MaterialFactoryNew());assert mat
  mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
  mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
  mat.set_editor_property('two_sided',True);mat.set_editor_property('opacity_mask_clip_value',.28);mat.set_editor_property('used_with_instanced_static_meshes',True)
  sample=edit.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D)
  sample.set_editor_property('texture',textures[0]);sample.set_editor_property('parameter_name','BoughAtlas');sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
  assert edit.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  assert edit.connect_material_property(sample,'A',unreal.MaterialProperty.MP_OPACITY_MASK)
  rough=edit.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.88)
  assert edit.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
  spec=edit.create_material_expression(mat,unreal.MaterialExpressionConstant);spec.set_editor_property('r',.15)
  assert edit.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
  edit.recompile_material(mat);assert lib.save_loaded_asset(mat)
 slots=0
 for mesh in assets:
  if not isinstance(mesh,unreal.StaticMesh):continue
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   old=slot.get_editor_property('material_interface')
   if old and ('needle' in old.get_name().lower()):mesh.set_material(i,mat);slots+=1
  assert lib.save_loaded_asset(mesh)
 assert slots>=1,'No actual tree canopy material was replaced'
 print('MOBILE_FOLIAGE_MATERIAL_APPLIED',slots,textures[0].get_path_name(),flush=True)
 return {'tree_material_slots':slots,'texture':textures[0].get_path_name(),'material':path,'image_verified':False}
