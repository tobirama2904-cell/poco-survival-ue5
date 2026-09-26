"""Blender validation of exported animation files, not the authoring scene."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'.cache/melee-characters';report=[]
for role in ['Arsen','Infected','Leyla','Nargis','Ilyas']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(OUT/(role+'.glb')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers))
 for t in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(t)
 foot=[v.index for v in mesh.data.vertices if (mesh.matrix_world@v.co).z<.11];assert foot
 clips=['Crouch']+(['Punch','PunchCrouch'] if role in ('Arsen','Infected') else [])
 values=[]
 for clip in clips:
  action=next(a for a in bpy.data.actions if a.name.startswith(clip+'_'));rig.animation_data.action=action
  for frame in [action.frame_range[0],sum(action.frame_range)/2,action.frame_range[1]]:
   bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();low=min((ev.matrix_world@m.vertices[i].co).z for i in foot);ev.to_mesh_clear();assert abs(low)<.012,(role,clip,frame,low);values.append(abs(low))
 report.append({'role':role,'clips_checked':clips,'max_abs_floor_error_m':max(values),'blender_roundtrip_verified':True,'unreal_verified':False})
 if role=='Infected':
  rig.animation_data.action=next(a for a in bpy.data.actions if a.name.startswith('Punch_'));bpy.context.scene.frame_set(8)
  bpy.ops.object.camera_add(location=(2.8,-4.2,1.6));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.3;bpy.context.scene.camera=cam
  for pos,power in [((2,-3,4),500),((-2,-1,3),260),((0,3,4),420)]:
   bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=3;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
  s=bpy.context.scene;s.world=bpy.data.worlds.new('Review');s.world.color=(.1,.12,.14);s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=480;s.render.resolution_y=560;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'infected-impact.png');bpy.ops.render.render(write_still=True)
(OUT/'roundtrip-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('EXPORTED_MOTION_ROUNDTRIP_VERIFIED',json.dumps(report),flush=True)
