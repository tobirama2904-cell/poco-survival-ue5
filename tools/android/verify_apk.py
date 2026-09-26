#!/usr/bin/env python3
"""Structural/signature checks are NOT installation, gameplay or phone-FPS tests."""
import hashlib,json,struct,subprocess,zipfile,os
from pathlib import Path
p=Path('artifacts/apk/NulevayaOtmetka-internal-arm64.apk');sdk=Path(os.environ['ANDROID_HOME'])/'build-tools/35.0.1'
cert=subprocess.check_output([str(sdk/'apksigner'),'verify','--verbose','--print-certs',str(p)],text=True)
identity=json.loads(Path('BuildData/android-signing.public.json').read_text());allowed=[identity['certificate_sha256']]
if os.environ.get('ALLOW_HISTORIC_APK_SIGNER')=='1':allowed+=identity.get('historical_internal_certificate_sha256',[])
expected=next((value for value in allowed if value in cert.lower().replace(':','')),None)
if expected is None:raise ValueError('Unexpected APK signing certificate')
with zipfile.ZipFile(p) as z:
    if z.testzip():raise ValueError('Corrupt APK ZIP')
    names=z.namelist();libs=[n for n in names if n.startswith('lib/arm64-v8a/') and n.endswith('.so')]
    assert libs and 'AndroidManifest.xml' in names
    unreal=[n for n in libs if n.endswith('/libUnreal.so')];assert len(unreal)==1
    with z.open(unreal[0]) as f:h=f.read(64)
    assert h[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',h,18)[0]==183
    data=[n for n in names if n.startswith('assets/') and any(t in n.lower() for t in ['.obb','.pak','.utoc','.ucas'])]
    assert data,'No embedded cooked game archive; do not publish a native-only APK'
    assert any(z.getinfo(n).file_size>1024**2 for n in data)
badging=subprocess.check_output([str(sdk/'aapt'),'dump','badging',str(p)],text=True)
assert "package: name='com.pocosurvival.game'" in badging
h=hashlib.sha256()
with p.open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
r={'package_run':os.environ.get('APK_RUN',os.environ.get('GITHUB_RUN_ID','')),'phase':'signed internal APK verification','file':p.name,'bytes':p.stat().st_size,'sha256':h.hexdigest(),'signature_verified':True,'certificate_sha256':expected,'arm64_library_verified':True,'embedded_game_archives':data,'installation_tested':False,'physical_device_tested':False,'final_game':False}
Path('artifacts/android-build/apk-verification.json').write_text(json.dumps(r,indent=2)+'\n');Path('artifacts/apk/SHA256SUMS').write_text(h.hexdigest()+'  '+p.name+'\n');print(json.dumps(r),flush=True)
Path('artifacts/android-build/apk-badging.log').write_text(badging)
