#!/usr/bin/env python3
"""Install/launch an actual signed ARM64 APK on a development emulator.
Records its ABI/native bridge and images. Never substitutes this for POCO testing.
"""
import json,os,subprocess,time,shlex,hashlib
from pathlib import Path
from frame_quality import metrics
from device_save_probe import DeviceSaveProbe
from save_state_probe import compare_saves
ROOT=Path('artifacts/android-emulator');ROOT.mkdir(parents=True,exist_ok=True)
SDK=Path(os.environ['ANDROID_HOME']);ADB=str(SDK/'platform-tools/adb');PACKAGE='com.pocosurvival.game'
def adb(*args,timeout=45,check=True):
    return subprocess.run([ADB,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout,check=check)
def text(*args,**kwargs):return adb(*args,**kwargs).stdout.decode('utf-8',errors='replace').strip()
def screenshot(name):
    p=ROOT/name;p.write_bytes(adb('exec-out','screencap','-p').stdout)
    data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    return {'file':name,'width':int.from_bytes(data[16:20],'big'),'height':int.from_bytes(data[20:24],'big')}
def wait_visible_frame(name,timeout=300):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if not text('shell','pidof',PACKAGE,check=False):raise RuntimeError('Game died while awaiting first visible frame')
        image=screenshot(name);image['pixel_regression_checks']=metrics(ROOT/name)
        if image['pixel_regression_checks']['not_black']:
            if not image['pixel_regression_checks']['no_strong_magenta_regression']:raise RuntimeError('Strong magenta rendering regression; frame rejected')
            return image
        time.sleep(15)
    raise TimeoutError('Map loaded but no visible frame arrived')
def launch():
    activity=text('shell','cmd','package','resolve-activity','--brief',PACKAGE).splitlines()[-1]
    if '/' not in activity:raise RuntimeError('No launcher activity')
    result=text('shell','am','start','-W','-n',activity,'--es','cmdline',shlex.quote('-project="../../../PocoSurvival/PocoSurvival.uproject" -AllowSoftwareRendering'),timeout=90);(ROOT/'launch.log').write_text(result)
    if 'Error:' in result:raise RuntimeError('Activity launch failed')
    return activity
emulator_log=(ROOT/'emulator.log').open('wb');process=None;probe=None;video_process=None;video_log=None
report={'physical_device_tested':False,'poco_f4_tested':False,'fps_claimed':False,'arm_translation_emulator_only':True,'installed':False,'launch_survived':False,'visual_quality_review_required':True,'emulator_only_commandline':'-AllowSoftwareRendering','requested_emulator_portrait_resolution':'540x960'}
def start_video(width,height):
    global video_process,video_log
    video_log=(ROOT/'screenrecord.log').open('wb')
    video_process=subprocess.Popen([ADB,'shell','screenrecord','--size',str(width)+'x'+str(height),'--bit-rate','1200000','--time-limit','120','/sdcard/Download/low-water-actual.mp4'],stdout=video_log,stderr=subprocess.STDOUT)
    report['video_capture']={'kind':'actual Android emulator screen recording','audio_recorded':False,'physical_device_fps_claimed':False,'contains_keyboard_diagnostic':False}
def stop_video():
    global video_process,video_log
    if video_process is None:return
    try:
        if video_process.poll() is None:
            adb('shell','pkill','-2','screenrecord',timeout=15,check=False)
            try:video_process.wait(timeout=25)
            except subprocess.TimeoutExpired:video_process.terminate();video_process.wait(timeout=10)
        dest=ROOT/'android-actual-recording.mp4'
        pull=adb('pull','/sdcard/Download/low-water-actual.mp4',str(dest),timeout=60,check=False)
        if pull.returncode or not dest.exists() or dest.stat().st_size<4096:raise RuntimeError('No finalized Android recording')
        with dest.open('rb') as f:header=f.read(32)
        if b'ftyp' not in header:raise RuntimeError('Recording is not an MP4 container')
        report['video_capture'].update(file=dest.name,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    except Exception as e:report['video_capture_error']=type(e).__name__+': '+str(e)
    finally:
        if video_log:video_log.close()
        video_process=None
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
    adb('shell','input','keyevent','82')
    adb('shell','settings','put','secure','immersive_mode_confirmations','confirmed')
    adb('shell','settings','put','system','screen_off_timeout','1800000')
    adb('shell','wm','size','540x960');adb('logcat','-c')
    install=text('install','-r','artifacts/apk/NulevayaOtmetka-internal-arm64.apk',timeout=180)
    (ROOT/'install.log').write_text(install)
    if 'Success' not in install:raise RuntimeError('APK installation failed')
    verified=json.loads(Path('artifacts/android-build/apk-verification.json').read_text())
    digest=hashlib.sha256()
    with Path('artifacts/apk/NulevayaOtmetka-internal-arm64.apk').open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    assert digest.hexdigest()==verified['sha256'],'APK changed after signature/structure verification'
    report['apk_sha256']=digest.hexdigest();report['apk_package_run']=os.environ.get('APK_RUN','')
    report['installed']=True;report['activity']=launch()
    # Wait for an actual map, not merely a surviving error-dialog process.
    deadline=time.monotonic()+600;time.sleep(15)
    while time.monotonic()<deadline:
        logs=text('logcat','-d',timeout=60)
        if 'CanalDistrict' in logs and 'Bringing World' in logs:break
        if not text('shell','pidof',PACKAGE,check=False):break
        if 'None of the 1 devices meet all the criteria!' in logs:break
        time.sleep(10)
    time.sleep(15)
    report['pid_after_start']=text('shell','pidof',PACKAGE,check=False)
    report['screenshots']=[wait_visible_frame('android-start.png')]
    logs=text('logcat','-d',timeout=60);(ROOT/'android-logcat.log').write_text(logs)
    if not report['pid_after_start']:raise RuntimeError('Game process did not survive startup')
    if 'CanalDistrict' not in logs or 'Bringing World' not in logs:raise RuntimeError('No real district-load evidence in Android logs')
    report['launch_survived']=True
    width,height=report['screenshots'][0]['width'],report['screenshots'][0]['height']
    time.sleep(35)
    start_video(width,height)
    probe=DeviceSaveProbe(adb,text,screenshot,ROOT,width,height)
    report['journal_close_touch_diagnostic']=probe.journal_close_by_touch() # diagnostic only; not gate evidence
    before=probe.save('before')
    # Actual touchscreen gesture; no diagnostic teleport or game-state injection.
    adb('shell','input','swipe',str(round(width*.13)),str(round(height*.8)),str(round(width*.13)),str(round(height*.62)),'1500')
    time.sleep(8);report['screenshots'].append(wait_visible_frame('android-after-input.png'))
    moved=probe.save('after-move',before['generation'])
    stop_video()
    adb('shell','am','force-stop',PACKAGE);adb('logcat','-c');launch()
    # Wait for the actual map, not a fixed 90-second interval during which a
    # correctly restored story could naturally progress and confuse comparison.
    deadline=time.monotonic()+600
    while time.monotonic()<deadline:
        restart_logs=text('logcat','-d',timeout=60)
        if 'CanalDistrict' in restart_logs and 'Bringing World' in restart_logs:break
        if not text('shell','pidof',PACKAGE,check=False):raise RuntimeError('Game died during restart load')
        time.sleep(5)
    else:raise TimeoutError('No real map-load evidence after restart')
    probe.journal(True) # Real UI pauses ordinary story dialogue before sampling.

    report['pid_after_restart']=text('shell','pidof',PACKAGE,check=False)
    report['screenshots'].append(wait_visible_frame('android-restart.png'))
    (ROOT/'android-restart-logcat.log').write_text(text('logcat','-d',timeout=60))
    if not report['pid_after_restart']:raise RuntimeError('Game failed to survive relaunch')
    report['restart_survived']=True
    restored=probe.save('after-restart',moved['generation'])
    report['save_snapshots']={'before':before,'after_move':moved,'after_restart':restored}
    report['save_files_present']=True;report['save_button_input_injected']=True
    report['menu_press_duration_ms']=probe.press_ms;report['short_tap_responsiveness_verified']=False
    report['journal_touch_confirmed']=True;report['fresh_save_after_touch_verified']=True
    report['visible_frames_verified']=True;report['touch_input_injected']=True
    comparison=compare_saves(before,moved,restored);report.update(comparison)
    report['save_restore_equality_verified']=False # Only the specified player-state subset is compared.
    assert comparison['touch_movement_verified'],'Actual saved player positions did not establish touch movement'
    assert comparison['player_position_inventory_progress_restore_verified'],'Restored player-state subset differs or no fresh save was captured'
except Exception as e:
    report['failure']=type(e).__name__+': '+str(e)
    stop_video() # Preserve only actual touch attempts, before keyboard diagnosis.
    # Failure-only diagnosis. Keyboard Tab must NEVER satisfy the touch gate.
    if probe is not None:
        try:
            for service in ['input','window','display']:
                (ROOT/('failure-'+service+'.log')).write_text(text('shell','dumpsys',service,timeout=25,check=False))
            adb('shell','input','keyevent','61',check=False);time.sleep(12)
            report['keyboard_only_journal_diagnostic']=probe.journal_visible('android-keyboard-diagnostic.png')
            report['keyboard_diagnostic_is_touch_proof']=False
        except Exception as diagnostic_error:report['input_diagnostic_failure']=str(diagnostic_error)
    try:(ROOT/'failure-logcat.log').write_text(text('logcat','-d',timeout=15,check=False))
    except Exception:pass
    raise
finally:
    stop_video()
    if probe is not None:probe.persist()
    (ROOT/'install-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
    if process is not None:
        process.terminate()
        try:process.wait(timeout=15)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    emulator_log.close()
