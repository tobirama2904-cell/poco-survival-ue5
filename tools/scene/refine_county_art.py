"""Blender: original conifer geometry with CC0 photographic textures; upgraded shelter.
Consumes the pinned previous pack. Does not relabel a procedural tree as a scan.
"""
import bpy,sys,json,math,random,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/scene'))
from county_layout import placements,height,POIS
PACK=ROOT/'.cache/county-pack';SRC=ROOT/'.cache/conifer-sources';GROUND=ROOT/'.cache/nature-sources/ground';R=random.Random(71943)
report=json.loads((PACK/'conditioning.json').read_text())
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.data.orphans_purge(do_recursive=True)
def material(name,color=(1,1,1),diffuse=None,normal=None,rough=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.86
 if diffuse:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(diffuse),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if normal:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(normal),check_existing=True);t.image.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.65;m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
 if rough:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(rough),check_existing=True);t.image.colorspace_settings.name='Non-Color';m.node_tree.links.new(t.outputs['Color'],p.inputs['Roughness'])
 return m

def export(name,**metadata):
 path=PACK/(name+'.glb');bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False)
 if name=='Pine':
  # Explicit glTF cutout; exporter surface-method names changed between Blender versions.
  raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[20+n:]
  for m in doc['materials']:
   if m['name']=='PhotographedNeedles':m.update(alphaMode='MASK',alphaCutoff=.28,doubleSided=True)
  text=json.dumps(doc,separators=(',',':')).encode();text+=b' '*((-len(text))%4);path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+binary)
 item={'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**metadata}
 report['models']=[m for m in report['models'] if m['file']!=path.name]+[item]
 print('ART_REFINED',name,item,flush=True)

clear();bark=material('PhotographedBark',diffuse=SRC/'pine_tree_01_bark_diff_1k.jpg',normal=SRC/'pine_tree_01_bark_nor_gl_1k.jpg')
needle=material('PhotographedNeedles');p=needle.node_tree.nodes.get('Principled BSDF');t=needle.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(SRC/'pine_needles_rgba.png'));needle.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);needle.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha']);needle.use_backface_culling=False
if hasattr(needle,'surface_render_method'):needle.surface_render_method='DITHERED'
verts=[];faces=[];uvs=[];mats=[]
def face(points,uv,mat):
 i=len(verts);verts.extend([tuple(v) for v in points]);uvs.extend(uv);faces.append(tuple(range(i,i+len(points))));mats.append(mat)
def tube(a,b,r0,r1,sides=7):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u).normalized()
 for j in range(sides):
  t0=j*math.tau/sides;t1=(j+1)*math.tau/sides;v0=u*math.cos(t0)+v*math.sin(t0);v1=u*math.cos(t1)+v*math.sin(t1)
  face([a+v0*r0,a+v1*r0,b+v1*r1,b+v0*r1],[(j/sides,0),((j+1)/sides,0),((j+1)/sides,(b-a).length/1.5),(j/sides,(b-a).length/1.5)],0)
for i in range(16):
 z=i*12.6/16;z1=(i+1)*12.6/16;tube((.055*math.sin(z),.04*math.cos(z)-.04,z),(.055*math.sin(z1),.04*math.cos(z1)-.04,z1),.22*(1-z/13)**1.2+.01,.22*(1-z1/13)**1.2+.01,10)
# Whorls with asymmetry and genuine photographed twig silhouettes, not triangle collapse.
sprigs=0
for tier in range(17):
 z=2.2+tier*.59;radius=3.2*max(.08,1-(z-2.2)/10.9)**.72
 count=6 if tier<13 else 5
 for j in range(count):
  angle=j*math.tau/count+tier*2.399+R.uniform(-.18,.18);out=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-out.y,out.x,0));length=radius*R.uniform(.8,1.17);base=Vector((0,0,z));end=base+out*length+Vector((0,0,R.uniform(-.5,.3)))
  tube(base,end,.055*(1-tier/22),.008,6)
  for k in range(1,8):
   t=k/8;centre=base.lerp(end,t)
   for sign in [-1,0,1]:
    direction=(out*.5+side*sign*.9+Vector((0,0,.4+R.uniform(-.2,.45)))).normalized();twig_len=R.uniform(.48,.88)*(1-tier*.018);across=direction.cross(Vector((0,0,1))).normalized();normal=direction.cross(across).normalized()
    for cross in [across,normal]:
     w=twig_len*.52;face([centre+cross*(-.58*w),centre+cross*(.42*w),centre+direction*twig_len+cross*(.42*w),centre+direction*twig_len+cross*(-.58*w)],[(0,0),(1,0),(1,1),(0,1)],1)
    sprigs+=1
mesh=bpy.data.meshes.new('Pine');mesh.from_pydata(verts,[],faces);mesh.materials.append(bark);mesh.materials.append(needle);uv=mesh.uv_layers.new()
for f,mi in zip(mesh.polygons,mats):
 f.material_index=mi
 for li in f.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
o=bpy.data.objects.new('Pine',mesh);bpy.context.collection.objects.link(o);o.select_set(True)
export('Pine',source='Original procedural conifer; Poly Haven pine_tree_01 textures only',triangles=sum(len(f.vertices)-2 for f in mesh.polygons),height_m=12.6,photographed_sprigs=sprigs,license='Original geometry / CC0 textures',mature_tree_scan=False)

# Keep terrain geometry and import-basis compensation unchanged; refine UV scale/PBR.
clear();bpy.ops.import_scene.gltf(filepath=str(PACK/'Terrain.glb'))
ground=material('ForestFloorPBR',diffuse=GROUND/'forest_ground_04_diff_1k.jpg',normal=GROUND/'forest_ground_04_nor_gl_1k.jpg',rough=GROUND/'forest_ground_04_rough_1k.jpg')
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ob.data.materials.clear();ob.data.materials.append(ground)
 # Idempotent UV coordinates from positions, not repeated multiplication.
 for layer in ob.data.uv_layers:
  for loop in ob.data.loops:
   v=ob.data.vertices[loop.vertex_index].co;layer.data[loop.index].uv=(v.x/3,-v.y/3)
export('Terrain',source='Original terrain; CC0 forest_ground_04 PBR',uv_tile_m=3,geometry_basis_preserved=True)

# Original open shelter: keep desk/cot positions used by actual story objects.
clear();wood=material('ShelterWoodWeathered',diffuse=ROOT/'BuildData/surfaces/wood_planks_grey_Diffuse.jpg');steel=material('RoofSteelWeathered',diffuse=ROOT/'BuildData/surfaces/rusty_metal_04_Diffuse.jpg');canvas=material('CanvasCot',(.29,.31,.25));dark=material('AgedIron',(.055,.06,.05))
def box(name,pos,size,mat,rotation=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);o.rotation_euler.z=rotation
 for f in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(v[axes[0]]/2.1,v[axes[1]]/2.1)
 return o
for x in [-3,3]:
 # Window opening y=-.7..1.1, z=1.05..2.10, not a painted-on window.
 for y,sy in [(-2.1,2.8),(2.3,2.4)]:box('wall',(x,y,1.5),(.18,sy,3),wood)
 box('window_lower',(x,.2,.525),(.18,1.8,1.05),wood);box('window_upper',(x,.2,2.55),(.18,1.8,.9),wood)
 for y in [-.76,1.16]:box('window_jamb',(x,y,1.575),(.28,.09,1.2),wood)
 for z in [1.01,2.14]:box('window_frame',(x,.2,z),(.32,2,.10),wood)
 box('window_divider',(x,.2,1.58),(.12,.05,1.05),dark)
box('back',(0,3.5,1.5),(6,.18,3),wood)
for x in [-2.1,2.1]:box('front',(x,-3.5,1.5),(1.8,.18,3),wood)
box('lintel',(0,-3.5,2.7),(2.4,.18,.6),wood);box('floor',(0,-.5,.08),(6.4,8.6,.16),wood)
for side in [-1,1]:o=box('roof',(side*1.8,0,3.5),(3.85,8.6,.16),steel);o.rotation_euler.y=side*math.radians(18)
for x in [-2.8,2.8]:box('porch_post',(x,-4.25,1.5),(.14,.14,3),wood)
box('cot',(-2,1.9,.45),(1.4,2.4,.22),canvas)
for x in [-2.5,-1.5]:
 for y in [1,2.8]:box('cot_leg',(x,y,.2),(.09,.09,.4),steel)
box('desk',(2,1,.8),(1.5,2,.13),wood)
for x in [1.4,2.6]:
 for y in [.2,1.8]:box('desk_leg',(x,y,.4),(.1,.1,.8),wood)
for z in [.8,1.4,2]:box('shelf',(0,3.2,z),(2.4,.45,.09),wood)
box('porch_bench',(-2,-3.98,.48),(1.4,.4,.12),wood)
for x in [-2.55,-1.45]:box('bench_leg',(x,-3.98,.23),(.12,.32,.46),wood)
for i in range(7):box('stacked_timber',(3.65,1.3,(i//2)*.13+.07),(.16,2,.12),wood,(-1)**i*.03)
for x in [-5,5]:
 for y in [2,4.3,6.6]:box('old_fence_post',(x,y,.65),(.14,.14,1.3),wood)
 for y in [3.15,5.45]:
  for z in [.5,1.05]:box('old_fence_rail',(x,y,z),(.09,2.35,.12),wood)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='Shelter';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.transform(Matrix.Diagonal((1,-1,1,1)));o.data.flip_normals()
export('Shelter',source='Original windowed shelter / porch / furniture / fence',triangles=sum(len(p.vertices)-2 for p in o.data.polygons),windows=2,story_tabletop_preserved=True)
(PACK/'conditioning.json').write_text(json.dumps(report,indent=2)+'\n')
(PACK/'conifer-source.json').write_bytes((SRC/'license-lock.json').read_bytes());(PACK/'ground-source.json').write_bytes((GROUND/'license-lock.json').read_bytes())
(PACK/'county.json').write_text(json.dumps({'schema':1,'extent_m':2400,'terrain_tiles':16,'pois':[{**p,'z':height(p['x'],p['y'])} for p in POIS],'instances':placements()},indent=2))
with (PACK/'CREDITS.md').open('a') as f:f.write('\nConifer revision: original procedural geometry with CC0 pine_tree_01 twig/bark photographs (https://polyhaven.com/a/pine_tree_01); not a scanned mature-tree mesh. Ground PBR and windowed shelter revised.\n')
print('COUNTY_ART_REFINEMENT_COMPLETE',flush=True)
