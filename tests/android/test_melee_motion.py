import unittest,struct,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def glb(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def matrices(path):
 d,b=glb(path);skin=d['skins'][0];a=d['accessors'][skin['inverseBindMatrices']];v=d['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 return {d['nodes'][joint]['name']:struct.unpack_from('<16f',b,offset+i*v.get('byteStride',64)) for i,joint in enumerate(skin['joints'])}
class MeleeMotionTests(unittest.TestCase):
 def test_asset_binding_and_old_clip_durations_if_local(self):
  for role in ['Arsen','Infected','Leyla','Nargis','Ilyas']:
   old=ROOT/'.cache/character-base-002'/(role+'.glb');new=ROOT/'.cache/melee-characters'/(role+'.glb')
   if not(old.exists() and new.exists()):self.skipTest('Authoring outputs not present in this checkout')
   a,b=matrices(old),matrices(new);self.assertEqual(set(a),set(b))
   for bone in a:self.assertLess(max(abs(x-y) for x,y in zip(a[bone],b[bone])),.0001,bone)
   da,_=glb(old);db,_=glb(new)
   def span(d,n):
    anim=next(a for a in d['animations'] if a['name']==n);t=d['accessors'][anim['samplers'][0]['input']];return t['max'][0]-t['min'][0]
   for clip in ['Idle','Walk','Run','Crouch','Talk']:self.assertAlmostEqual(span(da,clip),span(db,clip),places=4)
   if role in ('Arsen','Infected'):
    for clip in ['Punch','PunchCrouch']:self.assertAlmostEqual(span(db,clip),.8,places=4)
 def test_published_role_coverage(self):
  records=json.loads((ROOT/'BuildData/characters/melee-motion-report.json').read_text());self.assertEqual(len(records),5)
  for r in records:self.assertTrue(r['grounded_crouch']);self.assertFalse(r['in_game_verified'])
  self.assertEqual({r['role'] for r in records if r['retargeted']},{'Arsen','Infected'})
 def test_action_clock_drives_pose_and_hit(self):
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalCharacter.cpp').read_text();self.assertIn('bMeleeImpactFrame=Melee.Step(Delta)',s);self.assertIn('RefreshBoneTransforms()',s);self.assertIn('GetPlayLength()-survival::MeleeAction::Duration',s);self.assertNotIn('HitTimer,this,&ASurvivalCharacter::DeliverMelee',s)
 def test_root_vertical_motion_is_retained(self):
  s=(ROOT/'tools/characters/import_unreal.py').read_text();self.assertIn("clip not in ('Punch','PunchCrouch','Crouch')",s);self.assertIn('other!=clip and len(other)>len(clip)',s)
 def test_actual_pose_and_damage_gate_not_just_clip_presence(self):
  s=(ROOT/'tools/scene/verify_render.py').read_text();self.assertIn("melee.get('passed') is True",s);self.assertIn('len(images)>=6',s)
  s=(ROOT/'Source/PocoSurvival/Private/SurvivalGameMode.cpp').read_text();self.assertIn('Player->Attack();Player->Attack()',s);self.assertIn('MeleeDummy->GetHealth(),75.f',s);self.assertIn('!Player->IsMeleePosePlaying()',s)
if __name__=='__main__':unittest.main()
