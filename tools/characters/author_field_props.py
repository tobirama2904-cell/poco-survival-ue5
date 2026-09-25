"""Original reusable field props. Deliberately modest geometry; not photogrammetry."""
import bpy,math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'BuildData/props'
def mat(name,color,rough=.65,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
wood=mat('Walnut',(.12,.055,.022));steel=mat('Steel',(.11,.13,.14),.36,.8);fiber=mat('Bowstring',(.32,.30,.23));canvas=mat('OliveCanvas',(.14,.17,.10))
def cube(name,pos,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('edge wear','BEVEL');b.width=.006;b.segments=2;return o

def rod(name,a,b,r,m):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o

def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def export(name):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.convert(target='MESH');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();bpy.context.object.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.export_scene.gltf(filepath=str(root/(name+'.glb')),export_format='GLB',export_animations=False)
clear()
points=[(.22*math.sin(math.pi*i/12),0,-.65+i*1.3/12) for i in range(13)]
for i in range(12):rod('laminated_limb',points[i],points[i+1],.018 if 4<i<8 else .012,wood)
rod('string',points[0],(-.09,0,0),.0018,fiber);rod('string',(-.09,0,0),points[-1],.0018,fiber);cube('grip',(.21,0,0),(.045,.055,.16),canvas)
# Grip is the attachment origin, not 21 cm away from the character's hand.
for o in bpy.context.scene.objects:o.location.x-=.21
export('Bow')
clear();rod('shaft',(-.62,0,0),(0,0,0),.0035,wood);rod('head',(0,0,0),(.065,0,0),.007,steel)
for a in [0,2.094,4.188]:o=cube('fletching',(-.54,0,.01),(.11,.002,.027),fiber);o.rotation_euler.x=a
export('Arrow')
clear()
for z in [.08,.24,.40,.56]:
 for y in [-.31,.31]:cube('slat',(0,y,z),(.92,.055,.13),wood)
 for x in [-.46,.46]:cube('slat',(x,0,z),(.055,.62,.13),wood)
for x in [-.4,.4]:
 for y in [-.25,.25]:cube('brace',(x,y,.33),(.06,.06,.66),steel)
for y in [-.24,-.08,.08,.24]:cube('lid',(0,y,.65),(.95,.145,.045),wood)
export('SupplyCrate')
clear()
for x in [.1,.3,.5,.7,.9,1.1]:cube('door_plank',(x,0,1.05),(.19,.055,2.1),wood)
for z in [.28,1.8]:cube('door_strap',(.6,-.04,z),(1.17,.025,.06),steel)
rod('handle',(1.05,-.05,1.05),(1.05,-.13,1.05),.022,steel);export('Door')
