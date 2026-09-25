"""Blender 4.3: resolve source textures and bake compatible Rocketbox animation clips.
Input and resulting derivatives are MIT (Microsoft 2020). No Epic assets involved.
"""
import bpy,json,sys,argparse,math,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--role',default='all');p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[2];lock=json.loads((root/'BuildData/characters/rocketbox.lock.json').read_text());source=Path(a.source);out=Path(a.output);out.mkdir(parents=True,exist_ok=True);report=[]
for role,sub in lock['characters'].items():
 if a.role!='all' and role!=a.role:continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 folder=source/'Assets/Avatars'/sub;file=folder/'Export'/(sub.split('/')[-1]+'.fbx');bpy.ops.import_scene.fbx(filepath=str(file))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert meshes
 keep=set(meshes+[rig]);tex={p.name.lower():p for p in folder.rglob('*.tga')}
 for o in list(bpy.data.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 for im in list(bpy.data.images):
  base=Path(im.filepath.replace('\\','/')).name.lower();assert base in tex,base
  im.filepath=str(tex[base]);im.reload();assert im.size[0]>0,base
  if max(im.size)>1024:im.scale(1024,1024)
  im.pack()
 for m in bpy.data.materials:
  nodes=m.node_tree.nodes;old=[n for n in nodes if n.type=='TEX_IMAGE'];color=next((n.image for n in old if '_color' in n.image.filepath.lower()),None);normal=next((n.image for n in old if '_normal' in n.image.filepath.lower()),None);assert color,m.name
  opaque='opacity' not in m.name.lower();m.name=role+'_'+m.name;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');bs=nodes.new('ShaderNodeBsdfPrincipled');m.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface']);bs.inputs['Roughness'].default_value=.84
  color.colorspace_settings.name='sRGB';n=nodes.new('ShaderNodeTexImage');n.image=color;m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
  if not opaque:m.node_tree.links.new(n.outputs['Alpha'],bs.inputs['Alpha']);m.surface_render_method='DITHERED';m.use_transparency_overlap=False
  if normal:
   normal.colorspace_settings.name='Non-Color';nt=nodes.new('ShaderNodeTexImage');nt.image=normal;nm=nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(nt.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 rig.name=role+'_Rig'
 for i,o in enumerate(meshes):o.name=role+'_Body'+('' if i==0 else str(i));o.data.name=o.name
 rig.animation_data_clear();clips={};rest_errors=[]
 for clip,rel in lock['animations'].items():
  before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(source/'Assets/Animations'/rel));new=set(bpy.data.objects)-before;src=next(o for o in new if o.type=='ARMATURE');original=src.animation_data.action
  errors=[(rig.data.bones[n].matrix_local.to_quaternion().rotation_difference(src.data.bones[n].matrix_local.to_quaternion()).angle) for n in rig.data.bones.keys() if n in src.data.bones];rest_errors.append(max(errors))
  # Animation FBXs store a different bind pose. Copying local fcurves leaves arms
  # in A-pose; bake world-space rotations onto the actual avatar's rest skeleton.
  rig.animation_data_clear()
  for bone in rig.pose.bones:
   bone.matrix_basis.identity()
   if bone.name in src.pose.bones:
    c=bone.constraints.new('COPY_ROTATION');c.target=src;c.subtarget=bone.name;c.owner_space='WORLD';c.target_space='WORLD'
  bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
  bpy.ops.nla.bake(frame_start=int(original.frame_range[0]),frame_end=int(original.frame_range[1]),step=1,only_selected=False,visual_keying=True,clear_constraints=True,clear_parents=False,use_current_action=False,bake_types={'POSE'})
  action=rig.animation_data.action;action.name=role+'_'+clip;action.use_fake_user=True;clips[clip]=action
  for o in new:bpy.data.objects.remove(o,do_unlink=True)
 rig.animation_data_clear()
 rig.animation_data_create()
 for clip,action in clips.items():
  track=rig.animation_data.nla_tracks.new();track.name=clip;track.strips.new(clip,1,action)
  track.mute=True
 # NLA exporter exports muted tracks; solo individual strips during export sampling.
 bpy.ops.object.select_all(action='DESELECT')
 for o in keep:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.gltf(filepath=str(out/(role+'.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_yup=True,export_image_format='AUTO')
 triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 report.append({'role':role,'triangles':triangles,'bones':len(rig.data.bones),'clips':list(clips),'max_bind_rotation_difference_radians':max(rest_errors),'file':role+'.glb','bytes':(out/(role+'.glb')).stat().st_size,'sha256':hashlib.sha256((out/(role+'.glb')).read_bytes()).hexdigest()})
 if a.render and role=='Arsen':
  for track in rig.animation_data.nla_tracks:track.mute=True
  rig.animation_data.action=clips['Walk'];bpy.context.scene.frame_set(12)
  bpy.ops.object.camera_add(location=(3,-4,2.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.3;bpy.context.scene.camera=cam
  for pos,power,size in [((2,-3,4),350,4),((-2,-1,2),220,3),((0,3,4),500,3)]:
   bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
  scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.09,.09,.09);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=600;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.render.filepath=str(out/'Arsen-asset-check.png');bpy.ops.render.render(write_still=True)
 (out/'conditioning-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('CHARACTER_CONDITIONING_PASS',json.dumps(report))
