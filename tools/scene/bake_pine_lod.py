"""Blender: albedo-only branch/tree views for distance foliage, not gameplay imagery."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'.cache/pine-lod';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'.cache/county-pack/Pine.glb'));tree=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.update()
for m in list(tree.data.materials):
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL');emit=m.node_tree.nodes.new('ShaderNodeEmission');trans=m.node_tree.nodes.new('ShaderNodeBsdfTransparent');mix=m.node_tree.nodes.new('ShaderNodeMixShader')
 if bs.inputs['Base Color'].links:m.node_tree.links.new(bs.inputs['Base Color'].links[0].from_socket,emit.inputs['Color'])
 else:emit.inputs['Color'].default_value=bs.inputs['Base Color'].default_value
 if bs.inputs['Alpha'].links:m.node_tree.links.new(bs.inputs['Alpha'].links[0].from_socket,mix.inputs[0])
 else:mix.inputs[0].default_value=bs.inputs['Alpha'].default_value
 m.node_tree.links.new(trans.outputs[0],mix.inputs[1]);m.node_tree.links.new(emit.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs['Surface'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.cycles.transparent_max_bounces=64;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
bpy.ops.object.camera_add(location=(0,-25,6.3));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,6.3))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=14;scene.camera=camera;scene.render.filepath=str(OUT/'tree.png');bpy.ops.render.render(write_still=True)
# Isolate a canonical photographed lower branch, without importing a giant source tree.
mesh=tree.data;vertices=[];faces=[];uvs=[];materials=[]
for f in mesh.polygons:
 c=f.center
 if c.x<.2 or abs(c.y)>max(.35,c.x*.37) or c.z<1.6 or c.z>3.3:continue
 start=len(vertices)
 for li in f.loop_indices:
  vertices.append(tuple(mesh.vertices[mesh.loops[li].vertex_index].co));uvs.append(tuple(mesh.uv_layers.active.data[li].uv))
 faces.append(tuple(range(start,len(vertices))));materials.append(f.material_index)
branch=bpy.data.meshes.new('BoughBake');branch.from_pydata(vertices,[],faces)
for m in mesh.materials:branch.materials.append(m)
uv=branch.uv_layers.new()
for f,material in zip(branch.polygons,materials):
 f.material_index=material
 for li in f.loop_indices:uv.data[li].uv=uvs[branch.loops[li].vertex_index]
tree.data=branch
camera.location=(2,-8,6);camera.rotation_euler=(Vector((2,0,2.4))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=4.8;scene.render.filepath=str(OUT/'bough.png');bpy.ops.render.render(write_still=True)
(OUT/'bake.json').write_text(json.dumps({'tree_camera_center_z':6.3,'tree_ortho_scale':14,'tree_pixels':1024,'bough_faces':len(faces),'lighting_baked':False},indent=2))
print('PINE_LOD_ALBEDO_BAKED',len(faces),flush=True)
