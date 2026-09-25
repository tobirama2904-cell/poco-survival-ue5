"""Patch actual retained map for mobile; run inside the licensed editor commandlet.
A real sky mesh avoids the measured mobile SkyAtmosphere missing-mesh failure.
No claimed final art quality; this is a renderer compatibility correction.
"""
import json
from pathlib import Path
import unreal
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert level.load_level('/Game/Worlds/CanalDistrict')
removed=0
for actor in actors.get_all_level_actors():
 if isinstance(actor,unreal.SkyAtmosphere):actors.destroy_actor(actor);removed+=1
path='/Game/Environment/MobileSky/M_MobileSkyPhotographicV3'
if unreal.EditorAssetLibrary.does_asset_exist(path):
 material=unreal.load_asset(path)
else:
 material=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_MobileSkyPhotographicV3','/Game/Environment/MobileSky',unreal.Material,unreal.MaterialFactoryNew())
 assert material
 material.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
 material.set_editor_property('two_sided',True)
 material.set_editor_property('is_sky',True)
 color=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionVectorParameter,0,0)
 color.set_editor_property('parameter_name','SkyColor');color.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
 cubes=[unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets('/Game/Environment/Sky',True,False)]
 cube=next(c for c in cubes if isinstance(c,unreal.TextureCube))
 sample=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionTextureSampleParameterCube);sample.set_editor_property('texture',cube);sample.set_editor_property('parameter_name','CountySky');sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
 view=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionCameraVectorWS)
 reverse=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionMultiply);reverse.set_editor_property('const_b',-1)
 assert unreal.MaterialEditingLibrary.connect_material_expressions(view,'',reverse,'A');assert unreal.MaterialEditingLibrary.connect_material_expressions(reverse,'',sample,'UVs')
 compress=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionDivide);compress.set_editor_property('const_b',4)
 assert unreal.MaterialEditingLibrary.connect_material_expressions(sample,'RGB',compress,'A')
 limit=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionSaturate);assert unreal.MaterialEditingLibrary.connect_material_expressions(compress,'',limit,'')
 tint=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionMultiply);assert unreal.MaterialEditingLibrary.connect_material_expressions(limit,'',tint,'A');weights=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionConstant3Vector);weights.set_editor_property('constant',unreal.LinearColor(.2126,.7152,.0722,1))
 luminance=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionDotProduct)
 assert unreal.MaterialEditingLibrary.connect_material_expressions(color,'',luminance,'A');assert unreal.MaterialEditingLibrary.connect_material_expressions(weights,'',luminance,'B')
 assert unreal.MaterialEditingLibrary.connect_material_expressions(luminance,'',tint,'B')
 assert unreal.MaterialEditingLibrary.connect_material_property(tint,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 unreal.MaterialEditingLibrary.recompile_material(material)
 unreal.EditorAssetLibrary.save_loaded_asset(material)
for actor in actors.get_all_level_actors():
 if actor.get_actor_label()=='mobile_sky_dome':actors.destroy_actor(actor)
sky=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));sky.set_actor_label('mobile_sky_dome')
component=sky.static_mesh_component;component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Sphere.Sphere'))
component.set_material(0,material);component.set_collision_profile_name('NoCollision');component.set_editor_property('cast_shadow',False)
component.set_mobility(unreal.ComponentMobility.MOVABLE);sky.set_editor_property('tags',[unreal.Name('environment_sky')])
sky.set_actor_scale3d(unreal.Vector(12000,12000,12000))
for actor in actors.get_all_level_actors():
 if isinstance(actor,unreal.DirectionalLight) or isinstance(actor,unreal.SkyLight):
  actor.get_component_by_class(unreal.LightComponentBase).set_mobility(unreal.ComponentMobility.MOVABLE)
for actor in actors.get_all_level_actors():
 if isinstance(actor,unreal.PostProcessVolume):
  settings=actor.get_editor_property('settings')
  for key,value in [('override_bloom_intensity',True),('bloom_intensity',.12),('override_lens_flare_intensity',True),('lens_flare_intensity',0.0),('override_auto_exposure_bias',True),('auto_exposure_bias',-.50)]:settings.set_editor_property(key,value)
  actor.set_editor_property('settings',settings)
# Actual original ambience, not an advertised completed soundtrack.
# PCM is deliberately explicit for this small loop; no platform codec ambiguity.
# AudioSettings is not exported to Python in the pinned editor. The commandlet
# receives its PCM default through the Engine ini override before audio startup.
wind_path='/Game/Audio/Ambience/WindLoop'
wind=unreal.load_asset(wind_path)
if wind is None:
 task=unreal.AssetImportTask();task.filename='/project/BuildData/audio/wind-loop.wav';task.destination_path='/Game/Audio/Ambience';task.destination_name='WindLoop';task.automated=True;task.save=True
 task.factory=unreal.SoundFactory()
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 wind=next((unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.SoundWave)),None)
assert isinstance(wind,unreal.SoundWave),'Original wind SoundWave import failed'
wind.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.PCM)
wind.set_editor_property('looping',True);unreal.EditorAssetLibrary.save_loaded_asset(wind)
for actor in actors.get_all_level_actors():
 if actor.get_actor_label()=='courtyard_wind':actors.destroy_actor(actor)
ambience=actors.spawn_actor_from_class(unreal.AmbientSound,unreal.Vector(0,0,200));ambience.set_actor_label('courtyard_wind')
ambience.audio_component.set_sound(wind);ambience.audio_component.set_volume_multiplier(.22);ambience.audio_component.set_editor_property('auto_activate',True)
assert level.save_current_level()
r={'phase':'mobile-scene-correction','removed_sky_atmospheres':removed,'actual_sky_mesh':sky.get_path_name(),'unlit_sky_material':material.get_path_name(),'ambient_sound':wind.get_path_name(),'mobile_render_verified':False,'final_art':False}
Path('/project/artifacts/android-build/mobile-scene-correction.json').write_text(json.dumps(r,indent=2)+'\n')
print('MOBILE_SCENE_CORRECTED',json.dumps(r),flush=True)
