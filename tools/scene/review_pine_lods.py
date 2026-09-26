"""Offline comparison of distance meshes; not a gameplay or performance test."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
for name,x in [('Pine',-11),('PineMid',0),('PineFar',11)]:
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'.cache/county-pack'/(name+'.glb')))
 for obj in set(bpy.data.objects)-old:
  if obj.type=='MESH':obj.location.x+=x
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Review');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.5,.6,.7,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.6
bpy.ops.object.light_add(type='SUN',rotation=(.4,-.5,-.3));bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=(0,-45,8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=35;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.cycles.transparent_max_bounces=48;scene.render.resolution_x=1200;scene.render.resolution_y=560;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'.cache/pine-lods-review.png');bpy.ops.render.render(write_still=True)
