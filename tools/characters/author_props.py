"""Original small gameplay props; metres, joined meshes, PBR materials."""
import bpy,math
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'BuildData/props';out.mkdir(exist_ok=True)
def mat(name,color,metal=0,rough=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def cube(pos,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('RoundedEdges','BEVEL');b.width=.002;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name);return o
def cyl(pos,r,depth,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=depth,location=pos,rotation=rot);o=bpy.context.object;o.data.materials.append(m);return o
def export(name):
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(o for o in bpy.data.objects if o.type=='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name;o.data.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',export_animations=False)
for name in ['Pistol','Pipe','Bottle']:
 bpy.ops.wm.read_factory_settings(use_empty=True);steel=mat(name+'_Steel',(.065,.075,.08),.8,.42);grip=mat(name+'_Grip',(.075,.09,.065),.05,.9)
 if name=='Pistol':
  cube((.06,0,.07),(.21,.028,.032),steel);cube((.015,0,.04),(.13,.027,.025),steel);g=cube((-.015,0,-.003),(.04,.033,.095),grip);g.rotation_euler.y=-.22
  for x in [-.035,-.028,-.021,-.014]:cube((x,0,.087),(.002,.03,.0015),grip)
  cube((.037,0,.007),(.044,.014,.006),steel);cube((.06,0,.021),(.006,.014,.028),steel);cube((.132,0,.09),(.008,.006,.007),steel)
  cyl((.158,0,.07),.009,.003,grip,(0,math.pi/2,0));cube((.025,0,.025),(.007,.006,.025),steel)
 elif name=='Pipe':
  cyl((0,0,.2),.018,.52,steel);cyl((0,0,.015),.022,.11,grip)
  for z in [-.035,-.015,.005,.025,.045]:cyl((0,0,z),.024,.01,grip)
  cyl((0,0,.46),.024,.025,steel)
 else:
  glass=mat('Bottle_GreenGlass',(.03,.12,.08),.15,.22);cyl((0,0,.015),.028,.12,glass);cyl((0,0,.102),.012,.06,glass);cyl((0,0,.075),.019,.025,glass);cyl((0,0,.131),.014,.008,steel)
 export(name)
print('ORIGINAL_PROPS_READY')
