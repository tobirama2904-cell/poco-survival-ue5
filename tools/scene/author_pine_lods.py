"""Blender: retain full near tree, branch-card middle tree and eight-triangle far tree."""
import bpy,json,math,random,struct,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];pack=ROOT/'.cache/county-pack';folder=ROOT/'.cache/pine-lod';atlas=json.loads((folder/'atlas.json').read_text());report=json.loads((pack/'conditioning.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(pack/'Pine.glb'));high=next(o for o in bpy.context.scene.objects if o.type=='MESH');high.name='Pine'
materials=list(high.data.materials);leaf_index=next(i for i,m in enumerate(materials) if m.name.startswith('PhotographedNeedles'));bark_index=next(i for i,m in enumerate(materials) if m.name.startswith('PhotographedBark'))
leaf=materials[leaf_index];image=bpy.data.images.load(str(folder/'pine_lod_atlas.png'))
for node in leaf.node_tree.nodes:
 if node.type=='TEX_IMAGE' and node.image and 'pine_needles' in node.image.name:node.image=image
u0,v0,u1,v1=atlas['needle_uv']
for f in high.data.polygons:
 if f.material_index==leaf_index:
  for li in f.loop_indices:
   uv=high.data.uv_layers.active.data[li].uv.copy();high.data.uv_layers.active.data[li].uv=(u0+uv.x*(u1-u0),v0+uv.y*(v1-v0))
verts=[];faces=[];uvs=[];indices=[]
for f in high.data.polygons:
 if f.material_index!=bark_index:continue
 start=len(verts)
 for li in f.loop_indices:verts.append(tuple(high.data.vertices[high.data.loops[li].vertex_index].co));uvs.append(tuple(high.data.uv_layers.active.data[li].uv))
 faces.append(tuple(range(start,len(verts))));indices.append(bark_index)
def face(points,box,mat):
 start=len(verts);verts.extend(tuple(p) for p in points);a,b,c,d=box;uvs.extend([(a,b),(a,d),(c,d),(c,b)]);faces.append(tuple(range(start,start+4)));indices.append(mat)
rng=random.Random(71943)
for tier in range(17):
 z=2.2+tier*.59;radius=3.2*max(.08,1-(z-2.2)/10.9)**.72;count=6 if tier<13 else 5
 for j in range(count):
  a=j*math.tau/count+tier*2.399+rng.uniform(-.18,.18);length=radius*rng.uniform(.8,1.17);drop=rng.uniform(-.5,.3);axis=Vector((math.cos(a)*length,math.sin(a)*length,drop)).normalized();side=Vector((-math.sin(a),math.cos(a),0));base=Vector((0,0,z));width=length*.72
  # Consume the same sprig draws as the high-detail author's recipe, preserving
  # branch directions and extents instead of making a differently shaped tree.
  for k in range(21):rng.uniform(-.2,.45);rng.uniform(.48,.88)
  for tilt in [-math.pi/3,math.pi/3,math.pi/2]:
   cross=(side*math.cos(tilt)+Vector((0,0,math.sin(tilt)))).normalized();face([base-cross*width/2,base+cross*width/2,base+axis*length+cross*width/2,base+axis*length-cross*width/2],atlas['bough_uv'],leaf_index)
def mesh_object(name):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces)
 for m in materials:mesh.materials.append(m)
 layer=mesh.uv_layers.new()
 for f,index in zip(mesh.polygons,indices):
  f.material_index=index
  for li in f.loop_indices:layer.data[li].uv=uvs[mesh.loops[li].vertex_index]
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);return obj
mid=mesh_object('PineMid');verts=[];faces=[];uvs=[];indices=[]
w,h,x,z=atlas['tree_width'],atlas['tree_height'],atlas['tree_center_x'],atlas['tree_bottom_z'];a,b,c,d=atlas['tree_uv']
# UVs follow the vertical whole-tree photo; crossed planes prevent an edge-on disappearance.
for angle in [0,math.pi/4,math.pi/2,3*math.pi/4]:
 axis=Vector((math.cos(angle),math.sin(angle),0));points=[axis*(x-w/2)+Vector((0,0,z)),axis*(x+w/2)+Vector((0,0,z)),axis*(x+w/2)+Vector((0,0,z+h)),axis*(x-w/2)+Vector((0,0,z+h))]
 start=len(verts);verts.extend(tuple(p) for p in points);uvs.extend([(a,b),(c,b),(c,d),(a,d)]);faces.append(tuple(range(start,start+4)));indices.append(leaf_index)
far=mesh_object('PineFar')
for obj in [high,mid,far]:
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;path=pack/(obj.name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False)
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[20+n:]
 for m in doc['materials']:
  if 'PhotographedNeedles' in m['name']:m.update(alphaMode='MASK',alphaCutoff=.28,doubleSided=True)
 text=json.dumps(doc,separators=(',',':')).encode();text+=b' '*((-len(text))%4);path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+binary)
 previous=next((m for m in report['models'] if m['file']==path.name),{})
 item={**previous,'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':sum(len(f.vertices)-2 for f in obj.data.polygons),'source':'Original geometry and CC0-derived albedo atlas','lod_stage':obj.name}
 report['models']=[m for m in report['models'] if m['file']!=path.name]+[item];print('PINE_DISTANCE_MESH',obj.name,item['triangles'],flush=True)
(pack/'conditioning.json').write_text(json.dumps(report,indent=2)+'\n');(pack/'pine-lods.json').write_text(json.dumps({'meshes':['Pine','PineMid','PineFar'],'triangles':[sum(len(f.vertices)-2 for f in o.data.polygons) for o in [high,mid,far]],'cell_size_m':64,'near_range_m':90,'middle_range_m':180,'max_range_m':470,'hysteresis_m':6,'scope':'Spatial chunk LOD, not per-instance continuous LOD; near retains detail, far is an albedo billboard.','lighting_baked':False,'hardware_performance_verified':False},indent=2))
