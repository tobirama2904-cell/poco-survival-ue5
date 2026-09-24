#!/usr/bin/env python3
"""Install/launch an actual signed ARM64 APK on a development emulator.
Records its ABI/native bridge and images. Never substitutes this for POCO testing.
"""
import json,os,subprocess,time
from pathlib import Path
ROOT=Path('artifacts/android-emulator');ROOT.mkdir(parents=True,exist_ok=True)
SDK=Path(os.environ['ANDROID_HOME']);ADB=str(SDK/'platform-tools/adb');PACKAGE='com.pocosurvival.game'
def adb(*args,timeout=45,check=True):
    return subprocess.run([ADB,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout,check=check)
def text(*args,**kwargs):return adb(*args,**kwargs).stdout.decode('utf-8',errors='replace').strip()
def screenshot(name):
    p=ROOT/name;p.write_bytes(adb('exec-out','screencap','-p').stdout)
    data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    return {'file':name,'width':int.from_bytes(data[16:20],'big'),'height':int.from_bytes(data[20:24],'big')}
def launch():
    activity=text('shell','cmd','package','resolve-activity','--brief',PACKAGE).splitlines()[-1]
    if '/' not in activity:raise RuntimeError('No launcher activity')
    result=text('shell','am','start','-W','-n',activity,timeout=90);(ROOT/'launch.log').write_text(result)
    if 'Error:' in result:raise RuntimeError('Activity launch failed')
    return activity
emulator_log=(ROOT/'emulator.log').open('wb');process=None
report={'physical_device_tested':False,'poco_f4_tested':False,'fps_claimed':False,'arm_translation_emulator_only':True,'installed':False,'launch_survived':False,'visual_quality_review_required':True}
try:
    process=subprocess.Popen([str(SDK/'emulator/emulator'),'-avd','GameInstallCheck','-no-window','-no-audio','-no-boot-anim','-no-snapshot','-gpu','swiftshader_indirect','-memory','4096','-cores','2','-camera-back','none','-camera-front','none','-no-metrics'],stdout=emulator_log,stderr=subprocess.STDOUT)
    deadline=time.monotonic()+600
    while time.monotonic()<deadline:
        if process.poll() is not None:raise RuntimeError('Emulator exited before boot')
        if text('shell','getprop','sys.boot_completed',timeout=10,check=False)=='1':break
        time.sleep(5)
    else:raise TimeoutError('Emulator boot timeout')
    report['abis']=text('shell','getprop','ro.product.cpu.abilist')
    report['native_bridge']=text('shell','getprop','ro.dalvik.vm.native.bridge')
    report['android_version']=text('shell','getprop','ro.build.version.release')
    report['build_fingerprint']=text('shell','getprop','ro.build.fingerprint')
    if 'arm64-v8a' not in report['abis']:raise RuntimeError('Image does not advertise ARM64 translation; cannot claim ARM install coverage')
    adb('shell','input','keyevent','82');adb('logcat','-c')
    install=text('install','-r','artifacts/apk/NulevayaOtmetka-internal-arm64.apk',timeout=180)
    (ROOT/'install.log').write_text(install)
    if 'Success' not in install:raise RuntimeError('APK installation failed')
    report['installed']=True;report['activity']=launch()
    # Native translation + first Android shader initialization can be slow.
    time.sleep(150)
    report['pid_after_start']=text('shell','pidof',PACKAGE,check=False)
    report['screenshots']=[screenshot('android-start.png')]
    logs=text('logcat','-d',timeout=60);(ROOT/'android-logcat.log').write_text(logs)
    if not report['pid_after_start']:raise RuntimeError('Game process did not survive startup')
    if 'CanalDistrict' not in logs:raise RuntimeError('No real district-load evidence in Android logs')
    report['launch_survived']=True
    width,height=report['screenshots'][0]['width'],report['screenshots'][0]['height']
    adb('shell','input','swipe',str(round(width*.13)),str(round(height*.8)),str(round(width*.13)),str(round(height*.62)),'1500')
    time.sleep(5);report['screenshots'].append(screenshot('android-after-input.png'))
    adb('shell','input','tap',str(round(width*.75)),str(round(height*.08)))
    time.sleep(3)
    report['save_file_search']=text('shell','find','/sdcard/Android/data/'+PACKAGE+'/files','-name','Survival_*.sav',check=False)
    adb('shell','am','force-stop',PACKAGE);launch();time.sleep(90)
    report['pid_after_restart']=text('shell','pidof',PACKAGE,check=False)
    report['screenshots'].append(screenshot('android-restart.png'))
    (ROOT/'android-restart-logcat.log').write_text(text('logcat','-d',timeout=60))
    if not report['pid_after_restart']:raise RuntimeError('Game failed to survive relaunch')
    report['restart_survived']=True
except Exception as e:
    report['failure']=type(e).__name__+': '+str(e)
    try:(ROOT/'failure-logcat.log').write_text(text('logcat','-d',timeout=15,check=False))
    except Exception:pass
    raise
finally:
    (ROOT/'install-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
    if process is not None:
        process.terminate()
        try:process.wait(timeout=15)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    emulator_log.close()
