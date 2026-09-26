"""Offline material/scale inspection, not a gameplay or mobile-performance frame."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];PACK=ROOT/'.cache/interior-pack'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);objects={}
for name in ['MedicalBox','MedicalTape','Wheelchair','BedFrame','Bookshelf','OfficeDesk','SchoolChair','SchoolDesk','CassettePlayer']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(PACK/(name+'.glb')));o=next(o for o in set(bpy.data.objects)-before if o.type=='MESH');o.hide_render=True;objects[name]=o

def place(name,pos,angle=0):
 o=objects[name].copy();o.data=objects[name].data;bpy.context.collection.objects.link(o);o.hide_render=False;o.location=pos;o.rotation_euler.z=math.radians(angle);return o
place('BedFrame',(-3.2,2,0));place('Wheelchair',(-1.6,1.5,0),-20);place('OfficeDesk',(-3,-1.3,0));place('MedicalBox',(-2.9,-1.35,.788));place('MedicalTape',(-2.4,-1.25,.792));place('CassettePlayer',(-3.55,-1.35,.788),-12);place('Bookshelf',(.4,3,0))
for x,y in [(2,-1),(3.7,-1),(2,1),(3.7,1)]:place('SchoolDesk',(x,y,0));place('SchoolChair',(x,y-.85,0))
bpy.ops.mesh.primitive_plane_add(size=18);floor=bpy.context.object;m=bpy.data.materials.new('Concrete');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'BuildData/surfaces/concrete_floor_02_Diffuse.jpg'));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);floor.data.materials.append(m)
for uv in floor.data.uv_layers.active.data:uv.uv*=5
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Review daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.52,.60,.69,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.8
bpy.ops.object.light_add(type='AREA',location=(-2,-4,8));bpy.context.object.data.energy=1400;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
bpy.ops.object.camera_add(location=(7,-10,7.2));camera=bpy.context.object;camera.rotation_euler=(Vector((0,.7,.7))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=43;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.filepath=str(ROOT/'.cache/interior-props-review.png');bpy.ops.render.render(write_still=True)
