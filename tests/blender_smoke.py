"""Blender-only integration test. Synthetic fixture never enters release packages."""
import bpy,json,runpy,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='poco-art-smoke-') as temp:
 work=Path(temp);source=work/'source';asset=source/'portable_generator';asset.mkdir(parents=True)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.mesh.primitive_cube_add(size=2)
 bpy.ops.export_scene.gltf(filepath=str(asset/'fixture.gltf'),export_format='GLTF_SEPARATE')
 (source/'CREDITS.md').write_text('Synthetic integration-test fixture; not a released game asset.')
 lock=work/'fixture-lock.json';lock.write_text(json.dumps({'assets':[{'id':'portable_generator','entrypoint':'fixture.gltf'}]}))
 sys.argv=['blender','--',str(work),str(lock)]
 runpy.run_path(str(root/'tools/condition_assets.py'),run_name='__main__')
 report=json.loads((work/'mobile/conditioning-report.json').read_text())
 assert len(report['assets'])==1 and report['assets'][0]['candidate_triangles']==12
 image=work/'previews/portable_generator.png';assert image.exists() and image.stat().st_size>2000
 assert image.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
 print('BLENDER_SMOKE_PASS: glTF import, GLB export, CPU rendering, report and image output',flush=True)
