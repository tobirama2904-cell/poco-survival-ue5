"""Blender: preserve close tree, author a medium crown and bake a cheap distant silhouette.
Source is immutable county-art-003. No engine or third-party proprietary content.
"""
import bpy,bmesh,json,math,struct,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];PACK=ROOT/'.cache/county-pack';OUT=ROOT/'.cache/forest-lods';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(PACK/'Pine.glb'))
tree=next(o for o in bpy.context.scene.objects if o.type=='MESH');tree.name='Pine'
for im in bpy.data.images:
 if 'pine_needles' in im.name.lower():im.scale(256,512)
report=json.loads((PACK/'conditioning.json').read_text());records=[]
def export(ob,name):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 p=PACK/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_animations=False)
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);binary=raw[20+n:]
 for m in d['materials']:
  if 'Needles' in m['name'] or 'Impostor' in m['name']:m.update(alphaMode='MASK',alphaCutoff=.28,doubleSided=True)
 text=json.dumps(d,separators=(',',':')).encode();text+=b' '*((-len(text))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+binary)
 tri=sum(len(f.vertices)-2 for f in ob.data.polygons);records.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'triangles':tri,'source':'Original conifer / CC0 photographs','license':'Original geometry / CC0 textures'})
 print('FOREST_LOD_EXPORTED',name,tri,flush=True)
export(tree,'Pine')
# Keep one complete two-plane sprig in four; enlarge retained sprays mildly.
# Do not collapse all foliage into the trunk, which caused the earlier bare tree.
mid=tree.copy();mid.data=tree.data.copy();mid.name='PineMid';mid.data.name='PineMid';bpy.context.collection.objects.link(mid)
bm=bmesh.new();bm.from_mesh(mid.data);leaves=[f for f in bm.faces if f.material_index==1];assert len(leaves)%4==0
remove=[]
for i in range(0,len(leaves),4):
 group=leaves[i:i+4]
 if (i//4)%4:remove.extend(group)
 else:
  vertices={v for f in group for v in f.verts};centre=sum((v.co for v in vertices),Vector())/len(vertices)
  for v in vertices:v.co=centre+(v.co-centre)*1.65
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(mid.data);bm.free();export(mid,'PineMid');mid.hide_render=True
# Bake ALBEDO, not illumination: distant material remains lit by the actual scene.
original_nodes={}
for m in tree.data.materials:
 nodes=m.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
 emission=nodes.new('ShaderNodeEmission');color=bs.inputs['Base Color'];alpha=bs.inputs['Alpha']
 if color.is_linked:m.node_tree.links.new(color.links[0].from_socket,emission.inputs['Color'])
 else:emission.inputs['Color'].default_value=color.default_value
 transparent=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader')
 if 'Needles' in m.name:
  needle_tex=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image and 'pine_needles' in n.image.name.lower())
  cut=nodes.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.28;m.node_tree.links.new(needle_tex.outputs['Alpha'],cut.inputs[0]);m.node_tree.links.new(cut.outputs[0],mix.inputs[0])
 else:mix.inputs[0].default_value=1
 m.node_tree.links.new(transparent.outputs[0],mix.inputs[1]);m.node_tree.links.new(emission.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],output.inputs['Surface'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.transparent_max_bounces=64;scene.cycles.use_denoising=False;scene.render.film_transparent=True;scene.view_settings.view_transform='Standard';scene.render.resolution_x=256;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.look='None'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=16;scene.camera=cam
atlas=np.zeros((512,512,4),dtype=np.float32);width=height=0
for i in range(2):
 angle=i*math.pi/2;target=Vector((0,0,6.3));cam.location=target+Vector((math.cos(angle)*30,math.sin(angle)*30,0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 frame=cam.data.view_frame(scene=scene);width=max(v.x for v in frame)-min(v.x for v in frame);height=max(v.y for v in frame)-min(v.y for v in frame)
 scene.render.filepath=str(OUT/f'canopy-{i}.png');bpy.ops.render.render(write_still=True)
 # Loaded PNG pixels are linear, as needed when writing a new Blender image.
 image=bpy.data.images.load(scene.render.filepath,check_existing=False);pixels=np.array(image.pixels[:],dtype=np.float32).reshape((512,256,4));atlas[:,i*256:(i+1)*256]=pixels;bpy.data.images.remove(image)
# Grow RGB into transparent borders without growing alpha (mip fringe prevention).
valid=atlas[:,:,3]>.02
for step in range(12):
 colours=np.zeros_like(atlas[:,:,:3]);counts=np.zeros(valid.shape,dtype=np.float32)
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
  v=np.roll(valid,shift,axis);colours+=np.roll(atlas[:,:,:3],shift,axis)*v[:,:,None];counts+=v
 add=(~valid)&(counts>0);atlas[add,:3]=colours[add]/counts[add,None];valid|=add
# Artistic compensation for overlapping cutout planes, still lit at runtime.
atlas[:,:,:3]=np.minimum(1,atlas[:,:,:3]*1.65)
image=bpy.data.images.new('pine_canopy_impostor',width=512,height=512,alpha=True);image.pixels.foreach_set(atlas.ravel());image.filepath_raw=str(OUT/'pine_canopy_impostor.png');image.file_format='PNG';image.save();image.pack()
mat=bpy.data.materials.new('PineCanopyImpostor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9;t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;mat.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(t.outputs['Alpha'],bs.inputs['Alpha']);mat.use_backface_culling=False
if hasattr(mat,'surface_render_method'):mat.surface_render_method='DITHERED'
verts=[];faces=[];uv=[];normals=[]
for i in range(2):
 angle=i*math.pi/2;side=Vector((-math.sin(angle),math.cos(angle),0));out=Vector((math.cos(angle),math.sin(angle),0));base=Vector((0,0,6.3-height/2));start=len(verts)
 for x,z,u,v in [(-.5,0,0,0),(.5,0,1,0),(.5,1,1,1),(-.5,1,0,1)]:
  verts.append(tuple(base+side*width*x+Vector((0,0,height*z))));uv.append(((i+u)/2,v));normals.append(tuple((out*.55+side*x*.3+Vector((0,0,.7))).normalized()))
 faces.append((start,start+1,start+2,start+3))
mesh=bpy.data.meshes.new('PineFar');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);layer=mesh.uv_layers.new()
for face in mesh.polygons:
 face.use_smooth=True
 for li in face.loop_indices:layer.data[li].uv=uv[mesh.loops[li].vertex_index]
mesh.normals_split_custom_set_from_vertices(normals);far=bpy.data.objects.new('PineFar',mesh);bpy.context.collection.objects.link(far);export(far,'PineFar')
for r in records:
 old=next((x for x in report['models'] if x['file']==r['file']),{});old.update(r);report['models']=[x for x in report['models'] if x['file']!=r['file']]+[old]
report['forest_lods']={'pine_triangles':[r['triangles'] for r in records],'screens':[1,.65,.24],'impostor_resolution':[512,512],'needle_resolution':[256,512],'baked_lighting':False,'impostor_albedo_gain':1.65,'impostor_views':2,'far_casts_shadows':False,'mature_scan':False,'unreal_verified':False}
(PACK/'conditioning.json').write_text(json.dumps(report,indent=2)+'\n');(PACK/'forest-lods.json').write_text(json.dumps(report['forest_lods'],indent=2)+'\n')
with (PACK/'CREDITS.md').open('a') as f:f.write('\nForest LOD revision: original conifer retained nearby; selected and enlarged photographed sprigs at middle distance; two crossed albedo views at long distance. Far albedo compensated by 1.65; no baked scene lighting.\n')
print('FOREST_LODS_READY',json.dumps(report['forest_lods']),flush=True)
