"""Offline asset look-development render only. Never labelled an Unreal game frame."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];assets=ROOT/'.cache/county-pack'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
objects={}
for name in ['Pine','Broadleaf','Fern','MossRock','Stump','Deadwood','Shelter']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(assets/(name+'.glb')));new=[o for o in set(bpy.data.objects)-before if o.type=='MESH'];o=new[0];objects[name]=o;o.hide_render=True

def place(name,pos,scale=1,yaw=0):
 o=objects[name].copy();o.data=objects[name].data;bpy.context.collection.objects.link(o);o.hide_render=False;o.location=pos;o.scale=(scale,-scale if name=='Shelter' else scale,scale);o.rotation_euler.z=yaw;return o
place('Shelter',(0,1,.05))
for x,y,s in [(-6,4,1),(-8,7,1.2),(6,6,1.4),(9,10,1),(4,12,1.5),(-4,12,1.2),(-12,12,1.4),(12,2,.9)]:place('Pine',(x,y,0),s,x*.4)
for p in [(-6,-2,0),(6,-1,0),(9,6,0)]:place('Broadleaf',p,1.2)
for x,y,s in [(-4,-4,.7),(5,-3,.8),(-8,-1,.6)]:place('MossRock',(x,y,0),s,x)
place('Stump',(4,-6,0),1.5);place('Deadwood',(-6,0,0),1.2,1)
for i in range(32):
 x=math.sin(i*2.3)*9;y=math.cos(i*1.7)*7
 if abs(x)<3.8 and -4<y<5:continue
 place('Fern',(x,y,.01),1.1,i)
bpy.ops.mesh.primitive_plane_add(size=90);ground=bpy.context.object
m=bpy.data.materials.new('Real forest floor');m.use_nodes=True;nodes=m.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'.cache/nature-sources/ground/forest_ground_04_diff_1k.jpg'));m.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color']);nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95;ground.data.materials.append(m)
for loop in ground.data.uv_layers.active.data:loop.uv*=12
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Asset preview daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.47,.57,.69,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.65
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(30),math.radians(-25),math.radians(-30)));bpy.context.object.data.energy=2.1;bpy.context.object.data.angle=.12
bpy.ops.object.camera_add(location=(13,-18,9));camera=bpy.context.object;camera.rotation_euler=(Vector((0,2,2.5))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=34;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=1000;scene.render.resolution_y=680;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'.cache/county-asset-review.png');bpy.ops.render.render(write_still=True)
