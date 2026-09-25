"""Blender: condition CC0 scanned assets and author original terrain/open shelter.
Heavy sources and generated GLBs live in excluded cache; a pinned public art pack
is what the scene worker downloads. Not a substitute for an Unreal screenshot.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from county_layout import height,POIS,placements,river_x
OUT=ROOT/'.cache/county-pack';OUT.mkdir(parents=True,exist_ok=True)
SOURCES=ROOT/'.cache/nature-sources';report=[]
previous={m['file']:m for m in json.loads((OUT/'conditioning.json').read_text()).get('models',[])} if (OUT/'conditioning.json').exists() else {}
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for m in list(bpy.data.meshes):
  if not m.users:bpy.data.meshes.remove(m)
 bpy.data.orphans_purge(do_recursive=True)
def export(name):
 if name in ('Terrain','Shelter','River'):
  # UE5.7.4's measured glTF basis is (X, -Y, Z), 100 cm/metre.
  # County recipes use native UE metres, so pre-reflect authored geometry.
  for ob in bpy.context.selected_objects:
   if ob.type=='MESH':ob.data.transform(Matrix.Diagonal((1,-1,1,1)));ob.data.flip_normals()
 path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_animations=False,export_cameras=False,export_lights=False,use_selection=True)
 return {'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def triangles(mesh):return sum(len(f.vertices)-2 for f in mesh.polygons)
for source,name,budget in [('pine_sapling_small','Pine',6000),('island_tree_02','Broadleaf',7500),('fern_02','Fern',1400),('rock_moss_set_01','MossRock',2600),('tree_stump_01','Stump',1800),('dead_tree_trunk','Deadwood',2000)]:
 prior=previous.get(name+'.glb');existing=OUT/(name+'.glb')
 if prior and existing.exists() and name!='Pine' and hashlib.sha256(existing.read_bytes()).hexdigest()==prior['sha256']:
  report.append(prior);print('VERIFIED_CONDITIONED_CACHE',name,flush=True);continue
 clear();bpy.ops.import_scene.gltf(filepath=str(SOURCES/source/(source+'.gltf')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 # Select a single actual specimen, not an entire scattered source set.
 ob=max(meshes,key=lambda o:len(o.data.vertices))
 for o in list(bpy.context.scene.objects):
  if o!=ob:bpy.data.objects.remove(o,do_unlink=True)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);ob.parent=None;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bounds=[Vector(v) for v in ob.bound_box];mid=Vector(((min(v.x for v in bounds)+max(v.x for v in bounds))/2,(min(v.y for v in bounds)+max(v.y for v in bounds))/2,min(v.z for v in bounds)))
 for v in ob.data.vertices:v.co-=mid
 before=triangles(ob.data)
 if before>budget:
  mod=ob.modifiers.new('Mobile geometry budget','DECIMATE');mod.ratio=budget/before;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 ob.name=name;ob.data.name=name
 if name=='Pine':
  # Artistic resizing of a scanned sapling, not a claim of a mature-tree scan.
  bpy.context.view_layer.update();factor=6.5/max(.01,ob.dimensions.z)
  for v in ob.data.vertices:v.co*=factor
  bpy.context.view_layer.update()
 for image in bpy.data.images:
  if image.size[0]>1024 or image.size[1]>1024:image.scale(min(1024,image.size[0]),min(1024,image.size[1]))
 item=export(name);item.update({'source':source,'source_triangles':before,'triangles':triangles(ob.data),'height_m':float(ob.dimensions.z),'license':'CC0-1.0'});report.append(item);print('CONDITIONED',json.dumps(item),flush=True)

def mat(name,color,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.88
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
clear();ground=mat('ForestFloor',(.18,.23,.11),SOURCES/'ground/forest_ground_04_diff_1k.jpg')
# Sixteen individually cullable 600 m collision tiles, 12.5 m sample spacing.
for ix in range(4):
 for iy in range(4):
  verts=[];faces=[];n=48
  for j in range(n+1):
   for i in range(n+1):
    x=-1200+ix*600+i*12.5;y=-1200+iy*600+j*12.5;verts.append((x,y,height(x,y)))
  for j in range(n):
   for i in range(n):
    q=j*(n+1)+i;faces.append((q,q+1,q+n+2,q+n+1))
  name=f'Terrain_{ix}_{iy}';mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(ground)
  uv=mesh.uv_layers.new()
  for f in mesh.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x/9,v.y/9)
  ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
bpy.ops.object.select_all(action='SELECT');report.append(export('Terrain'))
clear();wood=mat('ShelterWood',(.28,.18,.10),ROOT/'BuildData/surfaces/wood_planks_grey_Diffuse.jpg');metal=mat('RoofSteel',(.13,.19,.17),ROOT/'BuildData/surfaces/rusty_metal_04_Diffuse.jpg');plaster=mat('CanvasCot',(.32,.34,.27))
def box(name,pos,size,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);ob=bpy.context.object;ob.name=name;ob.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material)
 uv=ob.data.uv_layers.active
 for face in ob.data.polygons:
  axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in face.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2.5,v[axes[1]]/2.5)
 return ob
# Open doorway, covered porch, pitched roof and usable furnished interior.
for x in [-3,3]:box('side',(x,0,1.5),(.18,7,3),wood)
box('back',(0,3.5,1.5),(6,.18,3),wood)
for x in [-2.1,2.1]:box('front',(x,-3.5,1.5),(1.8,.18,3),wood)
box('lintel',(0,-3.5,2.7),(2.4,.18,.6),wood)
box('floor',(0,-.5,.08),(6.4,8.6,.16),wood)
for side in [-1,1]:o=box('roof',(side*1.8,0,3.5),(3.85,8.6,.16),metal);o.rotation_euler.y=side*math.radians(18)
for x in [-2.8,2.8]:box('porch_post',(x,-4.25,1.5),(.14,.14,3),wood)
box('cot',(-2,1.9,.45),(1.4,2.4,.22),plaster)
for x in [-2.5,-1.5]:
 for y in [1,2.8]:box('cot_leg',(x,y,.2),(.09,.09,.4),metal)
box('desk',(2,1,.8),(1.5,2,.13),wood)
for x in [1.4,2.6]:
 for y in [.2,1.8]:box('desk_leg',(x,y,.4),(.1,.1,.8),wood)
for z in [.8,1.4,2]:box('shelf',(0,3.2,z),(2.4,.45,.09),wood)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();bpy.context.object.name='Shelter';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);report.append(export('Shelter'))
clear();water=mat('RiverSurface',(.075,.18,.145));water.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.24
verts=[];faces=[]
for i in range(193):
 y=-1200+i*12.5;x=river_x(y);verts.extend([(x-10,y,-1.15),(x+10,y,-1.15)])
 if i:faces.append((2*i-2,2*i-1,2*i+1,2*i))
m=bpy.data.meshes.new('River');m.from_pydata(verts,[],faces);m.materials.append(water);o=bpy.data.objects.new('River',m);bpy.context.collection.objects.link(o);o.select_set(True);report.append(export('River'))
(OUT/'county.json').write_text(json.dumps({'schema':1,'extent_m':2400,'terrain_tiles':16,'pois':[{**p,'z':height(p['x'],p['y'])} for p in POIS],'instances':placements()},indent=2))
(OUT/'conditioning.json').write_text(json.dumps({'models':report,'unreal_visual_reviewed':False,'mobile_performance_measured':False},indent=2))
(OUT/'CREDITS.md').write_text('# County nature art\n\nCC0 model sources: Poly Haven — https://polyhaven.com/license\n\n'+''.join('- '+a+' — https://polyhaven.com/a/'+a+'\n' for a in ['pine_sapling_small','island_tree_02','fern_02','rock_moss_set_01','tree_stump_01','dead_tree_trunk','forest_ground_04'])+'\nTerrain, shelter and placement: original project authoring. Mobile decimation changes source geometry.\n')
(OUT/'sources.json').write_bytes((SOURCES/'sources.json').read_bytes())
(OUT/'ground-source.json').write_bytes((SOURCES/'ground/license-lock.json').read_bytes())
print('COUNTY_ASSETS_READY',flush=True)

# Separate reproducible foliage-coverage pass after simplification.
exec(compile((ROOT/'tools/scene/restore_leaf_silhouette.py').read_text(),str(ROOT/'tools/scene/restore_leaf_silhouette.py'),'exec'))
