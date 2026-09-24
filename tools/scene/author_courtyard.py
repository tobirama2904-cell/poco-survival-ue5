"""Blender: authored waterworks courtyard, CC0 modular art + original geometry.
Exports identical baked geometry for UE import and a layout-only Cycles check.
Not a game renderer, not final environment art, not a gameplay/FPS test.
"""
import bpy,json,math,random,sys,argparse,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ap=argparse.ArgumentParser();ap.add_argument('--assets',required=True);ap.add_argument('--textures',required=True);ap.add_argument('--output',required=True);ap.add_argument('--render',action='store_true')
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);assets=Path(a.assets);textures=Path(a.textures);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);random.seed(731)
scene=bpy.context.scene
library=bpy.data.collections.new('SOURCE_LIBRARY');scene.collection.children.link(library)
world=bpy.data.collections.new('COURTYARD');scene.collection.children.link(world)
created=[];sources={}
def move_collection(o,collection):
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o)
def material(name,color,metal=0,rough=.85):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
def source(asset):
 if asset in sources:return sources[asset]
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(assets/(asset+'.glb')))
 meshes=[]
 for o in set(bpy.data.objects)-before:
  if o.type=='MESH':
   transform=o.matrix_world.copy();o.parent=None;o.matrix_world=transform;meshes.append(o)
  move_collection(o,library)
 sources[asset]=meshes;return meshes
source('modular_urban_apartments_facade');kit={o.name:o for o in sources['modular_urban_apartments_facade']}
def module(name,anchor,yaw=0):
 original=kit[name];o=bpy.data.objects.new('architecture_'+name,original.data);world.objects.link(o)
 # Kit members have separate catalogue placements but share local building pivots.
 o.matrix_world=Matrix.Translation(Vector(anchor))@Matrix.Rotation(yaw,4,'Z');created.append(o);return o
stone=material('cast_concrete',(.23,.24,.21));iron=material('oxidized_steel',(.13,.105,.07),.6,.8)
paint=material('warning_ochre',(.47,.28,.065),.05,.9);ink=material('sign_lettering',(.76,.72,.57));dark=material('sign_enamel',(.035,.08,.08),.25,.6)
water=material('canal_water',(.035,.085,.08),.25,.18);leaf=material('ivy_leaf',(.055,.11,.025),0,.93)
ground=material('weathered_asphalt',(.16,.17,.15));nt=ground.node_tree;bsdf=nt.nodes.get('Principled BSDF')
for file,input_name,kind in [('asphalt-base.jpg','Base Color','color'),('asphalt-rough.jpg','Roughness','data'),('asphalt-normal.jpg','Normal','normal')]:
 n=nt.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(textures/file));n.image.colorspace_settings.name='sRGB' if kind=='color' else 'Non-Color'
 if kind=='normal':
  normal=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(n.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bsdf.inputs[input_name])
 else:nt.links.new(n.outputs['Color'],bsdf.inputs[input_name])
def cube(name,center,size,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.scale=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('edge wear','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
 o.data.materials.append(mat);move_collection(o,world);created.append(o);return o
def slab(name,x0,x1,y0,y1,z=0):
 o=cube(name,((x0+x1)/2,(y0+y1)/2,z-.12),(x1-x0,y1-y0,.24),ground)
 # Ground UVs use consistent four-metre texel density, not one stretched tile.
 uv=o.data.uv_layers.active
 for poly in o.data.polygons:
  for i in poly.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(v.x/4,v.y/4)
 return o
def pipe(name,a,b,r,mat=iron):
 midpoint=(Vector(a)+Vector(b))*.5;d=Vector(b)-Vector(a)
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=midpoint);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);move_collection(o,world);created.append(o);return o
fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');font=bpy.data.fonts.load(str(fontpath)) if fontpath.exists() else None
def sign(text,pos,width,yaw=0):
 # Text local X right, Y up; board faces local -Y in world.
 panel=cube('sign_panel',pos,(width,.06,.85),dark,.02);panel.rotation_euler.z=yaw
 curve=bpy.data.curves.new('authored_sign','FONT');curve.body=text;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=min(.48,(width-.35)/(max(len(text),1)*.62));curve.extrude=.001
 if font:curve.font=font
 ob=bpy.data.objects.new('authored_sign_text',curve);world.objects.link(ob);ob.location=Vector(pos)+Matrix.Rotation(yaw,3,'Z')@Vector((0,-.038,0));ob.rotation_euler=(math.pi/2,0,yaw);curve.materials.append(ink)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);panel.select_set(False);bpy.ops.object.convert(target='MESH');ob.select_set(False);created.append(ob)
slab('south_approach',-23,28,-22,-13)
slab('courtyard_ground',-23,28,-10,32)
cube('channel_water',(2.5,-11.5,-.83),(51,3,.05),water)
cube('channel_bed',(2.5,-11.5,-1.15),(51,3,.3),stone)
cube('canal_crossing',(0,-11.5,-.12),(4.2,3.15,.24),stone,.035)
for y in [-13,-10]:
 for x0,x1 in [(-23,-2.5),(2.5,28)]:
  cube('canal_lip',((x0+x1)/2,y,-.28),(x1-x0,.22,.55),stone,.02)
  pipe('canal_railing',(x0,y,.95),(x1,y,.95),.045)
  for x in range(math.ceil(x0),int(x1),3):pipe('railing_post',(x,y,0),(x,y,1.02),.04)
# North municipal residential block: actual matching wall/window modules.
for floor in range(3):
 for col in range(10):
  x=-12+3*col;z=3*floor
  wall='wall_window_centered_large_01';insert='window_centered_large_01'
  if floor==0 and col in [2,7]:wall='wall_door_centered_large_01';insert='door_centered_large_01'
  module(wall,(x,19,z));module(insert,(x,19,z))
  module('cornice_standard_standard_01',(x,19,z+2.8))
  if floor==0:module('base_standard_01',(x,19,0))
  if floor==2:module('crown_standard_standard_01',(x,19,9))
# Opaque structural backing prevents empty facade silhouettes; front modules
# retain their real photographed material and window geometry.
cube('north_volume',(1.5,24,4.5),(30,9.8,9),kit['wall_standard_standard_01'].data.materials[0])
cube('north_roof',(1.5,23.5,9.02),(30.5,10.5,.22),stone,.02)
# Eastern housing wing faces the yard; west workshop is lower and sheltered.
for side,yaw,anchor_x,floors in [('east',-math.pi/2,20,3),('west',math.pi/2,-18,1)]:
 for floor in range(floors):
  for col in range(8):
   anchor_y=(-6+col*3) if side=='east' else (18-col*3)
   module('wall_window_centered_small_01',(anchor_x,anchor_y,3*floor),yaw)
   module('window_centered_small_01',(anchor_x,anchor_y,3*floor),yaw)
   if floor==floors-1:module('crown_standard_standard_01',(anchor_x,anchor_y,3*floors),yaw)
 if side=='east':cube('east_volume',(24.5,6,4.5),(8.8,24,9),kit['wall_standard_standard_01'].data.materials[0])
 else:cube('workshop_volume',(-22.5,6,1.5),(8.8,24,3),stone)
cube('workshop_canopy',(-16.6,5,3.1),(3.8,10,.18),iron,.01)
for y in [0,10]:pipe('canopy_post',(-14.85,y,0),(-14.85,y,3.1),.055)
sign('ВОДОЗАБОР  /  СЕКТОР 04',(1.5,18.86,7.7),7)
sign('ЛАЗАРЕТ',(-6,18.73,3.2),3)
sign('МАСТЕРСКАЯ',(-17.87,5,2.6),3,math.pi/2)
sign('ВОДА НЕ ДЛЯ ПИТЬЯ',(6,-13.1,1.6),4)
pipe('warning_sign_post',(6,-13.07,0),(6,-13.07,1.6),.04)
def prop(asset,pos,yaw=0,scale=1):
 originals=source(asset);vs=[o.matrix_world@Vector(c) for o in originals for c in o.bound_box]
 lo=Vector(tuple(min(v[i] for v in vs) for i in range(3)));hi=Vector(tuple(max(v[i] for v in vs) for i in range(3)));center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 placement=Matrix.Translation(Vector(pos))@Matrix.Rotation(yaw,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-center)
 result=[]
 for original in originals:
  o=bpy.data.objects.new(asset,original.data);world.objects.link(o);o.matrix_world=placement@original.matrix_world;created.append(o);result.append(o)
 return result
prop('portable_generator',(-13,8,0),math.pi/2)
prop('metal_tool_chest',(-16,3,0),math.pi/2)
prop('industrial_storage_cart',(-13,4,0),.3)
prop('utility_box_01',(-16,9,0),math.pi/2)
prop('barrel_stove',(8,-7,0));prop('industrial_storage_cart',(10,-7,0),.7)
prop('sofa_02',(-7,17,0));prop('painted_wooden_cabinet',(-3,17.2,0),math.pi)
prop('metal_tool_chest',(14,16.5,0),math.pi)
for x,y in [(-11,-6),(13,-6),(-10,14),(16,12)]:prop('street_lamp_01',(x,y,0))
for x in [-10,-9.5,-9]:
 pipe('pump_risers',(x,18.4,.15),(x,18.4,3.1),.14)
 pipe('pump_elbows',(x,18.4,3.1),(x,17.6,3.1),.14)
# Two planted islands divide the initial empty apron into readable approaches.
soil=material('exposed_soil',(.085,.065,.035))
for x,y in [(-5,4),(12,9)]:
 cube('old_planter',(x,y,.17),(3.4,5.4,.34),stone,.045)
 cube('planter_soil',(x,y,.35),(3.04,5.04,.05),soil)
 prop('tree_small_02',(x,y,.38),random.uniform(0,math.tau),1.12)
 for i in range(8):prop('grass_medium_02',(x+random.uniform(-1.3,1.3),y+random.uniform(-2.2,2.2),.39),random.uniform(0,math.tau),random.uniform(.6,1))
for i in range(16):
 x=random.choice([-17.1,18.8]);y=random.uniform(-7,16)
 prop('grass_medium_02',(x,y,.01),random.uniform(0,math.tau),random.uniform(.5,.8))
# Original rubble, repairs, warning stripes, and ivy concentrate at edges;
# the main crossing and the three interaction approaches remain traversable.
for i in range(45):
 x=random.choice([-17.4,18.6])+random.uniform(-.3,.3);y=random.uniform(-6,18)
 o=cube('edge_rubble',(x,y,.045),(random.uniform(.12,.40),random.uniform(.14,.36),random.uniform(.06,.14)),stone);o.rotation_euler.z=random.random()*math.tau
for i in range(11):cube('crossing_warning',(i*.34-1.7,-9.84,.016),(.20,.27,.025),paint)
verts=[];faces=[]
for rootx in [-11.5,12.5,15.5]:
 for branch in range(3):
  for i in range(55):
   z=.08+i*.10;x=rootx+math.sin(i*.21+branch)*.35+branch*.12;y=18.64+random.uniform(-.07,.02)
   s=random.uniform(.08,.17);start=len(verts)
   verts.extend([(x-s,y,z),(x,y-.07,z+s*.55),(x+s,y,z+s*.1),(x,y+.015,z-s)])
   faces.extend([(start,start+1,start+3),(start+1,start+2,start+3)])
mesh=bpy.data.meshes.new('ivy_cluster');mesh.from_pydata(verts,[],faces);mesh.materials.append(leaf);ivy=bpy.data.objects.new('ivy_growth',mesh);world.objects.link(ivy);created.append(ivy)
# Calibration geometry makes Unreal conversion measured, not an axis guess.
for label,pos in [('ORIGIN',(0,0,0)),('X',(1,0,0)),('Y',(0,1,0)),('Z',(0,0,1))]:cube('FRAME_'+label,pos,(.04,.04,.04),stone)
# Group static scenery by spatial sector to reduce actor/draw overhead while
# keeping the calibration meshes separate. No source catalogue objects export.
for o in created:
 if o.type=='MESH':o.data=o.data.copy()
bpy.ops.object.select_all(action='DESELECT')
for o in created:o.select_set(True)
bpy.context.view_layer.objects.active=created[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# Join into eight spatial chunks, preserving material assignments and UVs.
groups={}
for o in created:
 if o.name.startswith('FRAME_'):continue
 center=sum((v.co for v in o.data.vertices),Vector())/max(1,len(o.data.vertices))
 key=('north' if center.y>18 else 'west' if center.x<-13 else 'east' if center.x>18 else 'south' if center.y<-9 else 'yard')
 groups.setdefault(key,[]).append(o)
for key,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='district_'+key
bpy.ops.object.select_all(action='DESELECT')
for o in world.objects:
 if o.type=='MESH':o.data.name=o.name
 o.select_set(o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(out/'courtyard.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
recipe={'schema':1,'name':'CanalDistrict','stage':'internal gameplay gate; not complete campaign','coordinate_frame':'baked Blender metres; imported FRAME meshes calibrate UE axes and units','spawn':[0,-17,1.05],'look_at':[0,10,1.6],'intro_camera':[-14,-17,7],'intro_look_at':[0,11,3.2],'interactions':[{'action':'search_depot','position':[-16,3,0]},{'action':'recover_fuel','position':[8,-7,0]},{'action':'repair_generator','position':[-13,8,0]}],'infected':[{'position':[15,9,1.05],'patrol':[[15,5,1.05],[16,14,1.05]]}],'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in world.objects if o.type=='MESH'),'static_chunks':len(groups),'glb_sha256':hashlib.sha256((out/'courtyard.glb').read_bytes()).hexdigest(),'assets_used':sorted(sources)}
(out/'courtyard.json').write_text(json.dumps(recipe,indent=2,ensure_ascii=False)+'\n')
library.hide_render=True;library.hide_viewport=True
for o in world.objects:
 if o.name.startswith('FRAME_'):o.hide_render=True
scene.world=bpy.data.worlds.new('layout_sky');scene.world.use_nodes=True;nodes=scene.world.node_tree.nodes;env=nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(textures/'sky.hdr'));scene.world.node_tree.links.new(env.outputs['Color'],nodes.get('Background').inputs['Color']);nodes.get('Background').inputs['Strength'].default_value=.4
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(48),math.radians(-28),math.radians(-32)));bpy.context.object.data.energy=2.1;bpy.context.object.data.color=(1,.83,.63);bpy.context.object.data.angle=math.radians(4)
bpy.ops.object.camera_add(location=(-5,-18,2.7));cam=bpy.context.object;cam.rotation_euler=(Vector((0,12,3.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=bool(getattr(bpy.app.build_options,"openimagedenoise",False));scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'layout.blend'))
if a.render:
 scene.render.filepath=str(out/'layout-check.png');bpy.ops.render.render(write_still=True)
print('COURTYARD_AUTHORED',json.dumps(recipe,ensure_ascii=False))
