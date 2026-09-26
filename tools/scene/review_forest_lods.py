import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.read_factory_settings(use_empty=True)
for i,name in enumerate(['Pine','PineMid','PineFar']):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'.cache/county-pack'/(name+'.glb')))
 for o in set(bpy.data.objects)-before:
  if o.type=='MESH':
   o.location.x=(i-1)*12
   if name=='PineFar':o.visible_shadow=False
bpy.ops.mesh.primitive_plane_add(size=100);o=bpy.context.object;m=bpy.data.materials.new('neutral');m.diffuse_color=(.18,.20,.16,1);o.data.materials.append(m)
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('review');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.5,.6,.7,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.8
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(30),math.radians(-20),math.radians(-35)));bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=(0,-45,14));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=39;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.cycles.transparent_max_bounces=64;scene.render.resolution_x=1100;scene.render.resolution_y=510;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'.cache/forest-lods/comparison.png');bpy.ops.render.render(write_still=True)
