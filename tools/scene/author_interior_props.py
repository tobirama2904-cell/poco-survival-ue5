"""Blender conditioning of small CC0 props; retain source topology and materials."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'.cache/interior-sources';OUT=ROOT/'.cache/interior-pack';OUT.mkdir(parents=True,exist_ok=True)
NAMES={'medical_box':'MedicalBox','medical_tape':'MedicalTape','wheelchair_01':'Wheelchair','old_bed_frame':'BedFrame','wooden_bookshelf_worn':'Bookshelf','metal_office_desk':'OfficeDesk','SchoolChair_01':'SchoolChair','SchoolDesk_01':'SchoolDesk','portable_cassette_player':'CassettePlayer'}
report=[]
for source,name in NAMES.items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.data.orphans_purge(do_recursive=True)
 bpy.ops.import_scene.gltf(filepath=str(SRC/source/(source+'.gltf')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes,name
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:
  world=o.matrix_world.copy();o.parent=None;o.matrix_world=world;o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bbox=[Vector(v) for v in o.bound_box];lo=Vector(tuple(min(v[i] for v in bbox) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bbox) for i in range(3)));offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for v in o.data.vertices:v.co-=offset
 o.name=name;o.data.name=name;o.data.update();bpy.context.view_layer.update()
 triangles=sum(len(f.vertices)-2 for f in o.data.polygons);assert triangles<80000,(name,triangles)
 dimensions=[float(x) for x in o.dimensions];assert max(dimensions)<5 and min(dimensions)>0,(name,dimensions)
 for image in bpy.data.images:
  if image.size[0]>1024 or image.size[1]>1024:image.scale(min(1024,image.size[0]),min(1024,image.size[1]))
 path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False)
 item={'name':name,'source':source,'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':triangles,'dimensions_m':dimensions,'mesh_parts_joined':len(meshes),'origin':'XY centre, bottom Z; source metre scale retained','geometry_decimated':False,'license':'CC0-1.0'};report.append(item);print('INTERIOR_PROP_READY',json.dumps(item),flush=True)
(OUT/'conditioning.json').write_text(json.dumps({'schema':1,'models':report,'unreal_render_verified':False,'physical_device_performance_verified':False},indent=2)+'\n')
(OUT/'source-lock.json').write_bytes((ROOT/'BuildData/interior-sources.lock.json').read_bytes())
(OUT/'CREDITS.md').write_text('# Interior props\n\nCC0 model/textures from Poly Haven, https://polyhaven.com/license .\nOrigin conditioning and source-mesh joining by this project. No final device-performance claim.\n\n'+''.join('- '+s+' — https://polyhaven.com/a/'+s+'\n' for s in NAMES))
