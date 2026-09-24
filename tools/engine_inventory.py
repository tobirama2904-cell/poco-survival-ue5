#!/usr/bin/env python3
"""Report metadata only; never copy licensed engine source into artifacts."""
import json,os,shutil
from pathlib import Path
engine=Path('/home/ue4/UnrealEngine/Engine')
base=engine/'Config/BaseEngine.ini'
text=base.read_text(errors='replace') if base.exists() else ''
report={
 'phase':'official-engine-inventory',
 'version':json.loads((engine/'Build/Build.version').read_text()),
 'installed_build_marker':(engine/'Build/InstalledBuild.txt').exists(),
 'editor_binary_exists':(engine/'Binaries/Linux/UnrealEditor-Cmd').exists(),
 'android_target_platform_module_exists':(engine/'Binaries/Linux/libUnrealEditor-AndroidTargetPlatform.so').exists(),
 'android_binary_directory_exists':(engine/'Binaries/Android').is_dir(),
 'android_installed_platform_declared':any('PlatformName="Android"' in line for line in text.splitlines() if 'InstalledPlatformConfigurations' in line),
 'android_sdk_environment_present':bool(os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')),
 'linux_toolchain_directory_exists':(engine/'Extras/ThirdPartyNotUE/SDKs/HostLinux').is_dir(),
 'container_free_disk_bytes':shutil.disk_usage('/project').free,
 'android_package_tested':False,
 'visual_render_tested':False,
 'physical_device_tested':False,
}
output=Path('/project/artifacts/engine-probe');output.mkdir(parents=True,exist_ok=True)
(output/'engine-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
print('ENGINE_INVENTORY',json.dumps(report),flush=True)
