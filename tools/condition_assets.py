"""Blender CPU conditioning + studio previews. These are NOT gameplay captures.
Source art remains untouched. Candidate meshes require later in-engine review.
"""
import bpy,sys,json,math,struct
import _cycles
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];work=Path(args[0]);root=Path(__file__).resolve().parents[1]
lock_path=Path(args[1]) if len(args)>1 else root/'content/assets.lock.json'
lock=json.loads(lock_path.read_text());out=work/'mobile';out.mkdir(parents=True,exist_ok=True)
preview=work/'previews';preview.mkdir(exist_ok=True)
results=[]

def tri_count(obj):return sum(max(0,len(p.vertices)-2) for p in obj.data.polygons)

def studio_render(asset,meshes):
 points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)])
 center=(low+high)/2;radius=max(.2,(high-low).length/2)
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.use_denoising=bool(getattr(_cycles,'with_openimagedenoise',False));scene.cycles.samples=32 if scene.cycles.use_denoising else 96
 scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
 world=bpy.data.worlds.new('Neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.25,.29,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
 bpy.ops.object.camera_add(location=center+Vector((1.4,-1.9,1.1))*radius);camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=46;camera.data.clip_end=max(100,20*radius);scene.camera=camera
 for offset,power,size in [((-2,-3,4),850,3),((3,1,2),650,2),((-1,3,2),350,2)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*radius);light=bpy.context.object;light.data.energy=power*radius*radius;light.data.shape='DISK';light.data.size=size*radius;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.mesh.primitive_plane_add(size=radius*14,location=(center.x,center.y,low.z-.006));floor=bpy.context.object
 m=bpy.data.materials.new('Studio floor');m.diffuse_color=(.11,.13,.15,1);floor.data.materials.append(m)
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str(preview/(asset+'.png'));bpy.ops.render.render(write_still=True)

for asset in lock['assets']:
 name=asset['id'];bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(work/'source'/name/asset['entrypoint']))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes,name
 before=sum(tri_count(o) for o in meshes);architecture=name.startswith('modular_');texture_limit=2048 if architecture else 1024
 changed=0
 for image in bpy.data.images:
  w,h=image.size[:]
  if max(w,h)>texture_limit:
   factor=texture_limit/max(w,h);image.scale(max(1,round(w*factor)),max(1,round(h*factor)));image.pack();changed+=1
 decimated=0
 for obj in meshes:
  count=tri_count(obj);budget=40000 if architecture else 25000
  if count<=budget or obj.data.shape_keys or any(m.type=='ARMATURE' for m in obj.modifiers):continue
  bpy.context.view_layer.objects.active=obj
  mod=obj.modifiers.new('Candidate mesh reduction','DECIMATE');mod.ratio=budget/count;mod.use_collapse_triangulate=True
  bpy.ops.object.modifier_apply(modifier=mod.name);decimated+=1
 after=sum(tri_count(o) for o in meshes);assert 0<after<=before
 destination=out/(name+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(destination),export_format='GLB',export_apply=True,export_animations=True)
 data=destination.read_bytes();assert data[:4]==b'glTF' and len(data)>1000
 length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);assert doc.get('meshes')
 row={'id':name,'source_triangles':before,'candidate_triangles':after,'mesh_count':len(meshes),'texture_limit':texture_limit,'resized_images':changed,'reduced_meshes':decimated,'bytes':len(data),'engine_import_validated':False};results.append(row)
 print('CONDITIONED',json.dumps(row),flush=True)
 if name in ['portable_generator','metal_tool_chest','sofa_02','fire_hydrant']:studio_render(name,meshes)
(out/'conditioning-report.json').write_text(json.dumps({'purpose':'Mobile candidates, not final LODs; physical-device and Unreal validation pending','assets':results},indent=2))
(out/'CREDITS.md').write_text((work/'source/CREDITS.md').read_text())
print('ART_CONDITIONING_COMPLETE',len(results),flush=True)
