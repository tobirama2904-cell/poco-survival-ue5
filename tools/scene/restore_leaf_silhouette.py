"""Blender post-pass: preserve foliage coverage lost by aggressive whole-mesh collapse.
Sample the original CC0 leaf cloud, rebuild folded 6-triangle leaves with measured
atlas UVs. This is explicitly conditioned art, not untouched photogrammetry.
"""
import bpy,json,hashlib,random,numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];pack=ROOT/'.cache/county-pack';base=ROOT/'.cache/nature-sources/island_tree_02'
report=json.loads((pack/'conditioning.json').read_text());entry=next(m for m in report['models'] if m['file']=='Broadleaf.glb')
if not entry.get('foliage_restored'):
 doc=json.loads((base/'island_tree_02.gltf').read_text());raw=(base/'island_tree_02.bin').read_bytes()
 def access(idx):
  a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];return np.ndarray((a['count'],n),dtype='<f4',buffer=raw,offset=offset,strides=(v.get('byteStride',n*4),4)).copy()
 def xyz(p):return np.stack((p[:,0],-p[:,2],p[:,1]),axis=1)
 prim=doc['meshes'][0]['primitives'];allpos=np.concatenate([xyz(access(p['attributes']['POSITION'])) for p in prim]);mn=allpos.min(axis=0);mx=allpos.max(axis=0);offset=np.array([(mn[0]+mx[0])/2,(mn[1]+mx[1])/2,mn[2]])
 p=next(p for p in prim if p['material']==1);points=xyz(access(p['attributes']['POSITION']))-offset;normals=xyz(access(p['attributes']['NORMAL']))
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(pack/'Broadleaf.glb'));tree=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 rng=random.Random(4071);verts=[];faces=[];uvs=[]
 # UV outline of the first leaf in the source's 1k photographed atlas.
 outline=[(0,.53,.09,.975),(-.22,.25,.035,.86),(-.25,-.12,.02,.73),(0,-.5,.08,.60),(.22,-.12,.14,.73),(.20,.25,.13,.86)]
 for index in rng.sample(range(len(points)),900):
  c=Vector(points[index]);n=Vector(normals[index]).normalized();u=n.cross(Vector((0,0,1)))
  if u.length<.01:u=n.cross(Vector((1,0,0)))
  u.normalize();v=n.cross(u).normalized();size=rng.uniform(.21,.32);start=len(verts);verts.append(tuple(c+n*.008));uvs.append((.08,.79))
  for x,y,a,b in outline:verts.append(tuple(c+u*x*size+v*y*size));uvs.append((a,b))
  for i in range(6):faces.append((start,start+1+i,start+1+(i+1)%6))
 mesh=bpy.data.meshes.new('CoverageLeaves');mesh.from_pydata(verts,[],faces);uv=mesh.uv_layers.new()
 for face in mesh.polygons:
  for li in face.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
 material=bpy.data.materials.new('CC0 photographed leaf coverage');material.use_nodes=True;bs=material.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.78;t=material.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(base/'textures/island_tree_02_leaves_diff_1k.jpg'));material.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);material.use_backface_culling=False;mesh.materials.append(material)
 leaf=bpy.data.objects.new('CoverageLeaves',mesh);bpy.context.collection.objects.link(leaf);bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=tree;bpy.ops.object.join();tree.name='Broadleaf';bpy.ops.export_scene.gltf(filepath=str(pack/'Broadleaf.glb'),export_format='GLB',use_selection=True,export_animations=False)
 path=pack/'Broadleaf.glb';entry.update({'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':sum(len(p.vertices)-2 for p in tree.data.polygons),'foliage_restored':True,'rebuilt_leaves':900})
 (pack/'conditioning.json').write_text(json.dumps(report,indent=2)+'\n');print('LEAF_COVERAGE_RESTORED',entry,flush=True)
