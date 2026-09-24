"""Blender conversion of pinned CC0 vegetation; no triangle-count claims hidden."""
import bpy,sys,json
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);out.mkdir(parents=True,exist_ok=True)
# Tree is simplified with gltfpack before Blender; importing/exporting its
# 2,062,487-triangle source exceeded the local 2 GiB memory budget.
for name in ['grass_medium_02']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(root/name/(name+'.gltf')))
 meshes=[o for o in bpy.data.objects if o.type=='MESH']
 print('EXTRA_MODEL',name,[(o.name,tuple(round(x,2) for x in o.dimensions)) for o in meshes])
 if name=='grass_medium_02':
  # Catalogue contains variants; export one actual grass clump, not its gallery.
  for o in meshes[1:]:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',export_animations=False)
