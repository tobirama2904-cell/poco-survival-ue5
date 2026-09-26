"""Retarget pinned CMU boxing onto the actual conditioned Rocketbox bind skeleton.
Original conversion, in-place clips, foot-height correction and authored fist closure.
No claim of final animation or engine compatibility until runtime inspection.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from cmu_motion import read_asf,read_amc,pose,select_punch
source=ROOT/'.cache/cmu-motion';skeleton=read_asf(source/'13.asf');frames=read_amc(source/'13_17.amc');peak,_=select_punch(skeleton,frames)
H=Matrix(((1,0,0),(0,0,-1),(0,1,0)));Hi=H.inverted();R0,_=pose(skeleton,frames[peak]);forward=H@Vector(R0['root']@__import__('numpy').array([0.,0.,1.]));align=Matrix.Rotation(-math.pi/2-math.atan2(forward.y,forward.x),3,'Z')
OUT=ROOT/'.cache/melee-characters';OUT.mkdir(parents=True,exist_ok=True)
roles=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['Arsen','Infected'];reports=[]
for role in roles:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'.cache/characters'/(role+'.glb')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)];assert meshes;body=max(meshes,key=lambda o:len(o.data.vertices))
 assert all(abs(x-1)<1e-5 for x in rig.scale)
 oldfps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
 actions={key:next(a for a in bpy.data.actions if a.name.startswith(key+'_')) for key in ['Idle','Walk','Run','Crouch','Talk']}
 for a in actions.values():
  for fc in a.fcurves:
   for k in fc.keyframe_points:
    for v in [k.co,k.handle_left,k.handle_right]:v.x*=30/oldfps

 for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
 bpy.context.scene.render.fps=30
 rest={b.name:b.matrix_local.to_quaternion() for b in rig.data.bones};mapping={'Bip01 Pelvis':('root',None),'Bip01 Spine':('lowerback','Bip01 Spine1'),'Bip01 Spine1':('upperback','Bip01 Spine2'),'Bip01 Spine2':('thorax','Bip01 Neck'),'Bip01 Neck':('lowerneck','Bip01 Head'),'Bip01 Head':('head',None)}
 for side,cmu in [('L','l'),('R','r')]:
  for target,bone,child in [('Clavicle','clavicle','UpperArm'),('UpperArm','humerus','Forearm'),('Forearm','radius','Hand'),('Hand','radius','Finger2'),('Thigh','femur','Calf'),('Calf','tibia','Foot'),('Foot','foot','Toe0')]:mapping[f'Bip01 {side} {target}']=(cmu+bone,f'Bip01 {side} {child}')
 corrections={}
 for name,(src,child) in mapping.items():
  if child and child in rig.data.bones:
   target_dir=(rig.data.bones[child].head_local-rig.data.bones[name].head_local).normalized();source_dir=(H@Vector(skeleton[0][src]['direction'])).normalized();corrections[name]=target_dir.rotation_difference(source_dir)
  else:corrections[name]=Quaternion()
 foot_ids=[v.index for v in body.data.vertices if (body.matrix_world@v.co).z<.11];assert foot_ids
 # Ground the existing crouch loop too, so entering/leaving the crouched strike
 # does not jump vertically and civilian companions benefit from the same fix.
 raw_crouch=actions['Crouch'];fixed=bpy.data.actions.new(role+'_CrouchGrounded');fixed.use_fake_user=True
 for frame in range(round(raw_crouch.frame_range[0]),round(raw_crouch.frame_range[1])+1):
  rig.animation_data.action=raw_crouch;bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
  snapshot={b.name:(b.rotation_quaternion.copy(),b.location.copy(),b.scale.copy()) for b in rig.pose.bones}
  evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();low=min((evaluated.matrix_world@mesh.vertices[i].co).z for i in foot_ids);evaluated.to_mesh_clear()
  rig.animation_data.action=fixed
  for b in rig.pose.bones:
   b.rotation_mode='QUATERNION';b.rotation_quaternion,b.location,b.scale=snapshot[b.name]
   if b.name=='Bip01 Pelvis':b.location+=rest[b.name].inverted()@Vector((0,0,-low))
   for channel in ['rotation_quaternion','location','scale']:b.keyframe_insert(channel,frame=frame)
 actions['Crouch']=fixed
 for clip,base_name in ([('Punch','Idle'),('PunchCrouch','Crouch')] if role in ('Arsen','Infected') else []):
  rig.animation_data.action=actions[base_name];bpy.context.scene.frame_set(int(actions[base_name].frame_range[0]));bpy.context.view_layer.update()
  base={b.name:(b.rotation_quaternion.copy(),b.location.copy()) for b in rig.pose.bones};base_world={b.name:b.matrix.to_quaternion() for b in rig.pose.bones}
  rig.animation_data.action=None;action=bpy.data.actions.new(role+'_'+clip);rig.animation_data.action=action;action.use_fake_user=True
  metrics=[]
  for n in range(25):
   bpy.context.scene.frame_set(n+1);Rs,Ps=pose(skeleton,frames[peak-36+n*4]);t=n/30;blend=min(1.,t/.10,max(0.,(.8-t)/.18));world={}
   for b in rig.pose.bones:
    parent=b.parent;local_rest=rest[parent.name].inverted()@rest[b.name] if parent else rest[b.name]
    if b.name in mapping and not(clip=='PunchCrouch' and ('Pelvis' in b.name or any(v in b.name for v in ['Thigh','Calf','Foot']))):
     src=mapping[b.name][0];q=(align@H@Matrix(Rs[src].tolist())@Hi).to_quaternion()@corrections[b.name]@rest[b.name]
     local=local_rest.inverted()@(world[parent.name].inverted() if parent else Quaternion())@q
    else:local=base[b.name][0]
    b.rotation_mode='QUATERNION';b.rotation_quaternion=base[b.name][0].slerp(local,blend);b.location=base[b.name][1];b.scale=(1,1,1)
    world[b.name]=(world[parent.name] if parent else Quaternion())@local_rest@b.rotation_quaternion
   # Close fingers around the palm using anatomical child positions, not imported display tails.
   for b in rig.pose.bones:
    if ' Finger' not in b.name:continue
    side='L' if ' L ' in b.name else 'R';suffix=b.name.split('Finger')[-1]
    child=next(iter(b.bone.children),None)
    direction=(child.head_local-b.bone.head_local) if child else (b.bone.head_local-b.bone.parent.head_local)
    hand=rig.data.bones[f'Bip01 {side} Hand'].head_local;index=rig.data.bones[f'Bip01 {side} Finger1'].head_local;pinky=rig.data.bones[f'Bip01 {side} Finger4'].head_local
    palm=(index-hand).cross(pinky-hand).normalized()
    if palm.dot(Vector((-1 if side=='L' else 1,0,0)))<0:palm=-palm
    curl=(rig.data.bones[f'Bip01 {side} Finger2'].head_local-b.bone.head_local).normalized() if suffix=='0' else palm
    axis=direction.normalized().cross(curl)
    if axis.length<.1:continue
    axis=rest[b.name].inverted()@axis.normalized();angle=math.radians(45 if suffix=='0' else 20 if suffix.startswith('0') else 60 if len(suffix)==1 else 72 if suffix.endswith('1') else 48)
    b.rotation_quaternion=base[b.name][0]@Quaternion(axis,angle*blend)
   bpy.context.view_layer.update()
   evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=evaluated.to_mesh();low=min((evaluated.matrix_world@m.vertices[i].co).z for i in foot_ids);evaluated.to_mesh_clear()
   root=rig.pose.bones['Bip01 Pelvis'];root.location+=rest[root.name].inverted()@Vector((0,0,-low));bpy.context.view_layer.update()
   for b in rig.pose.bones:
    b.keyframe_insert('rotation_quaternion',frame=n+1);b.keyframe_insert('location',frame=n+1);b.keyframe_insert('scale',frame=n+1)
   wrist=rig.pose.bones['Bip01 R Hand'].head.copy();metrics.append({'frame':n+1,'wrist':list(wrist),'foot_shift_m':-low})
  actions[clip]=action;(OUT/(role+'-'+clip+'-pose.json')).write_text(json.dumps(metrics,indent=2))
 # Each export retains all previously used motions and the exact bone bind transforms.
 rig.animation_data.action=None
 for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
 for key,a in actions.items():
  track=rig.animation_data.nla_tracks.new();track.name=key;track.strips.new(key,1,a);track.mute=True
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for m in meshes:m.select_set(True)
 bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.gltf(filepath=str(OUT/(role+'.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True)
 reports.append({'role':role,'file':role+'.glb','sha256':hashlib.sha256((OUT/(role+'.glb')).read_bytes()).hexdigest(),'bytes':(OUT/(role+'.glb')).stat().st_size,'source_motion':'CMU 13_17' if role in ('Arsen','Infected') else 'Rocketbox crouch (ground-height correction only)','source_frames':[peak-36+1,peak+60+1] if role in ('Arsen','Infected') else None,'source_fps':120,'duration_seconds':.8 if role in ('Arsen','Infected') else None,'impact_seconds':.3 if role in ('Arsen','Infected') else None,'clips':list(actions),'retargeted':role in ('Arsen','Infected'),'grounded_crouch':True,'in_game_verified':False})
 if role=='Arsen':
  # Save an inspection scene with exact baked clips; render separate key poses.
  rig.animation_data.action=actions['Punch'];bpy.context.scene.frame_set(10)
  bpy.ops.object.camera_add(location=(2.8,-4.2,1.6));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=2.3;bpy.context.scene.camera=camera
  for pos,power in [((2,-3,4),500),((-2,-1,3),260),((0,3,4),420)]:
   bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=3;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
  scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Review');scene.world.color=(.10,.12,.14);scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=480;scene.render.resolution_y=560;scene.render.resolution_percentage=100
  for frame in [1,6,10,18,25]:scene.frame_set(frame);scene.render.filepath=str(OUT/f'punch-{frame}.png');bpy.ops.render.render(write_still=True)
  rig.animation_data.action=actions['PunchCrouch'];scene.frame_set(10);scene.render.filepath=str(OUT/'crouch-impact.png');bpy.ops.render.render(write_still=True)
 (OUT/'motion-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print('MELEE_MOTION_AUTHORED',json.dumps(reports),flush=True)
