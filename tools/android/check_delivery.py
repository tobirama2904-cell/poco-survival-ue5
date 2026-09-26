#!/usr/bin/env python3
"""Bind an APK to its actual tests and manually reviewed images.
This checks evidence consistency; it is not a signature verifier, human reviewer,
physical-device benchmark or a declaration that the full game is finished.
"""
import argparse,hashlib,json,re
from pathlib import Path

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def validate(digest,size,apk,install,source,review,certificate,images):
 def need(condition,message):
  if not condition:raise ValueError(message)
 need(bool(re.fullmatch('[0-9a-f]{64}',digest)),'Invalid APK digest')
 need(apk.get('sha256')==digest and apk.get('bytes')==size,'APK does not match verified bytes')
 need(apk.get('signature_verified') is True and apk.get('arm64_library_verified') is True,'Missing signature/ABI evidence')
 need(apk.get('certificate_sha256')==certificate,'Not the current signing identity')
 need(bool(apk.get('embedded_game_archives')),'Missing packaged content evidence')
 need(str(source.get('package_run',''))==str(review.get('package_run','')) and str(apk.get('package_run',''))==str(review.get('package_run','')) and bool(review.get('package_run')),'Package/source/signature reports are from different runs')
 need(source.get('matching_game_source_verified') is True,'Unmatched native/cooked game source')
 for key in ['source_tree','engine_lock','project_descriptor']:
  values=[source.get(k,{}).get(key) for k in ['native','cooked','packaging']]
  need(all(values) and len(set(values))==1,'Source identity mismatch: '+key)
 need(source['cooked'].get('configuration_tree')==source['packaging'].get('configuration_tree') and bool(source['cooked'].get('configuration_tree')),'Cooked configuration mismatch')
 need(install.get('apk_sha256')==digest,'Install test belongs to a different/unbound APK')
 need(str(install.get('apk_package_run',''))==str(review.get('package_run','')) and bool(review.get('package_run')),'Package run mismatch')
 for key in ['installed','launch_survived','restart_survived','visible_frames_verified','touch_movement_verified','player_position_inventory_progress_restore_verified']:
  need(install.get(key) is True,'Missing real install/input/save proof: '+key)
 need(not install.get('failure'),'Install test reports failure')
 need(review.get('apk_sha256')==digest,'Visual review belongs to another APK')
 need(review.get('verdict')=='development-only','Explicit development-only review required; no final-game declaration supported')
 required={entry['file'] for entry in install.get('screenshots',[])}
 need(len(required)>=3,'Missing start/movement/restart images')
 reviewed=review.get('images',{})
 for name in required:
  need(name in images and reviewed.get(name)==images[name],'Unreviewed or mismatched image: '+name)
 return {'apk_sha256':digest,'package_run':review['package_run'],'development_candidate_evidence_bound':True,'final_game':False,'physical_poco_verified':False,'full_world_save_equality_verified':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--apk',type=Path,required=True);p.add_argument('--apk-report',type=Path,required=True);p.add_argument('--install-report',type=Path,required=True);p.add_argument('--source-report',type=Path,required=True);p.add_argument('--visual-review',type=Path,required=True);p.add_argument('--images',type=Path,required=True);a=p.parse_args()
 load=lambda f:json.loads(f.read_text())
 install=load(a.install_report);images={}
 for entry in install.get('screenshots',[]):
  name=Path(entry['file'])
  if name.is_absolute() or len(name.parts)!=1 or name.suffix!='.png':raise ValueError('Unsafe image name')
  image=a.images/name
  if image.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Image is not a PNG')
  images[name.name]=sha(image)
 root=Path(__file__).resolve().parents[2];cert=load(root/'BuildData/android-signing.public.json')['certificate_sha256']
 print(json.dumps(validate(sha(a.apk),a.apk.stat().st_size,load(a.apk_report),install,load(a.source_report),load(a.visual_review),cert,images),indent=2))
if __name__=='__main__':main()
