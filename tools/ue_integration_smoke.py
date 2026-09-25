"""Run inside UnrealEditor-Cmd. Headless native integration, NOT visual gameplay."""
import json
from pathlib import Path
import unreal

output=Path('/project/artifacts/engine-probe')
cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalGameInstance')
assert cls is not None, 'Native GameInstance class failed to load'
assert unreal.load_class(None,'/Script/PocoSurvival.SurvivalInteraction') is not None
assert unreal.load_class(None,'/Script/PocoSurvival.SurvivalSaveGame') is not None
assert unreal.load_class(None,'/Script/PocoSurvival.SurvivalCompanion') is not None

def instance():
    return unreal.new_object(cls)
def apply(game, action, expected=True):
    result=game.try_action(unreal.Name(action))
    success=result[0] if isinstance(result,tuple) else result
    assert bool(success)==expected, (action,result)

game=instance()
assert len(game.get_objectives())==61
assert game.get_carried_weight_kg()==0.0
apply(game,'repair_generator',False)
for action in ['search_depot','recover_fuel','repair_generator']:
    apply(game,action)
assert game.has_world_flag(unreal.Name('generator_running'))
assert game.get_item_count(unreal.Name('fuel'))==0
assert game.save_progress(), 'First slot write failed'
apply(game,'power_clinic')
assert game.save_progress(), 'Second slot write failed'
loaded=instance()
assert loaded.load_progress()
assert loaded.has_world_flag(unreal.Name('clinic_power'))
apply(loaded,'power_pumps',False)
# Only the two test slots in this disposable CI checkout are touched.
save_dir=Path(unreal.Paths.project_saved_dir())/'SaveGames'
latest=save_dir/'Survival_B.sav'
assert latest.exists(), 'Cannot locate actual save file for corruption test'
latest.write_bytes(b'')  # Interrupted write: empty newest slot.
recovered=instance()
assert recovered.load_progress(), 'Older valid slot was not recovered'
assert recovered.has_world_flag(unreal.Name('generator_running'))
assert not recovered.has_world_flag(unreal.Name('clinic_power'))
# Equal quest revisions must be ordered by successful save generation, not
# action count. This matters once position/vitals can change between quests.
save_cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalSaveGame')
for slot,generation,action in [('Survival_A',10,'search_depot'),('Survival_B',11,'recover_fuel')]:
    save=unreal.GameplayStatics.create_save_game_object(save_cls)
    save.set_editor_property('format_version',2)
    save.set_editor_property('save_generation',generation)
    save.set_editor_property('state_revision',1)
    save.set_editor_property('action_journal',[action])
    assert unreal.GameplayStatics.save_game_to_slot(save,slot,0)
same_revision=instance();assert same_revision.load_progress()
assert same_revision.get_item_count(unreal.Name('fuel'))==1
assert same_revision.get_item_count(unreal.Name('starter_coil'))==0
# Encounter persistence: damaged/dead enemies survive reload; malformed newest
# encounter snapshots fall back to the previous valid save, never resurrecting
# everything merely because the application restarted.
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
enemy_class=unreal.load_class(None,'/Script/PocoSurvival.SurvivalInfected')
enemy=actors.spawn_actor_from_class(enemy_class,unreal.Vector(10000,10000,500))
enemy.set_editor_property('persistent_id',unreal.Name('smoke_enemy'))
map_name=unreal.GameplayStatics.get_current_level_name(world,True)
def encounter_save(slot,generation,health,duplicate=False):
    save=unreal.GameplayStatics.create_save_game_object(save_cls)
    save.set_editor_property('format_version',3)
    save.set_editor_property('save_generation',generation)
    save.set_editor_property('state_revision',1)
    save.set_editor_property('action_journal',['search_depot'])
    save.set_editor_property('view_rotation',unreal.Rotator(pitch=-20,yaw=42,roll=0))
    state=unreal.SurvivalInfectedSnapshot()
    state.set_editor_property('persistent_id',unreal.Name('smoke_enemy'))
    state.set_editor_property('map_name',map_name)
    state.set_editor_property('location',enemy.get_actor_location())
    state.set_editor_property('rotation',enemy.get_actor_rotation())
    state.set_editor_property('health',health)
    state.set_editor_property('stamina',60)
    save.set_editor_property('infected_states',[state,state] if duplicate else [state])
    assert unreal.GameplayStatics.save_game_to_slot(save,slot,0)
encounter_save('Survival_A',20,45)
encounter_save('Survival_B',21,0)
encounters=instance();assert encounters.load_progress()
assert encounters.apply_loaded_infected_state(enemy)
assert enemy.get_health()==0 and not enemy.is_alive()
assert enemy.get_editor_property('state')==unreal.InfectedState.DEAD
for bad_health,duplicate in [(101,False),(45,True)]:
    encounter_save('Survival_B',22,bad_health,duplicate)
    fallback=instance();assert fallback.load_progress()
    assert fallback.apply_loaded_infected_state(enemy)
    assert enemy.get_health()==45 and enemy.is_alive()
    assert enemy.get_editor_property('state')==unreal.InfectedState.PATROL
saved=unreal.GameplayStatics.load_game_from_slot('Survival_A',0)
assert saved.get_editor_property('view_rotation').pitch==-20
assert not enemy.restore_encounter(enemy.get_actor_location(),enemy.get_actor_rotation(),101,50)
actors.destroy_actor(enemy)
# Native UObject serialization/replay of version-5 climate, including corrupt
# newest-save fallback and legacy version-4 migration to authored arrival time.
for slot in ['Survival_A','Survival_B']:unreal.GameplayStatics.delete_game_in_slot(slot,0)
clock=instance();clock.step_world_clock(.5,False);assert abs(clock.world_seconds()-61212)<.01
clock.step_world_clock(1,True);assert abs(clock.world_seconds()-61212)<.01
assert clock.save_progress()
restored=instance();assert restored.load_progress();assert abs(restored.world_seconds()-61212)<.01
for bad_time,bad_seed in [(-1,731),(315360001,731),(61200,-1),(61200,4294967296)]:
    broken=unreal.GameplayStatics.create_save_game_object(save_cls)
    broken.set_editor_property('save_generation',999)
    broken.set_editor_property('world_elapsed_seconds',bad_time);broken.set_editor_property('weather_seed',bad_seed)
    assert unreal.GameplayStatics.save_game_to_slot(broken,'Survival_B',0)
    recovered=instance();assert recovered.load_progress();assert abs(recovered.world_seconds()-61212)<.01
legacy=unreal.GameplayStatics.create_save_game_object(save_cls);legacy.set_editor_property('format_version',4);legacy.set_editor_property('save_generation',1000)
legacy.set_editor_property('world_elapsed_seconds',-1)
assert unreal.GameplayStatics.save_game_to_slot(legacy,'Survival_B',0)
migrated=instance();assert migrated.load_progress();assert migrated.world_hour()==17
# Version-6 field state roundtrip and corrupt-newest-slot recovery. Native
# property serialization, NOT a substitute for firing/rendering/device tests.
for slot in ['Survival_A','Survival_B']:unreal.GameplayStatics.delete_game_in_slot(slot,0)
field=unreal.GameplayStatics.create_save_game_object(save_cls)
field.set_editor_property('format_version',6);field.set_editor_property('save_generation',40)
field.set_editor_property('field_items',[3,1,2,1,6,2,1,1,8]);field.set_editor_property('looted_caches',1)
field.set_editor_property('open_doors',3);field.set_editor_property('wound_state',unreal.Vector4(1,.4,.6,1))
field.set_editor_property('film_progress',14);field.set_editor_property('film_decision',1)
assert unreal.GameplayStatics.save_game_to_slot(field,'Survival_A',0)
f=instance();assert f.load_progress();assert f.save_progress()
roundtrip=unreal.GameplayStatics.load_game_from_slot('Survival_B',0)
assert list(roundtrip.get_editor_property('field_items'))==[3,1,2,1,6,2,1,1,8]
assert roundtrip.get_editor_property('open_doors')==3
assert roundtrip.get_editor_property('film_progress')==14 and roundtrip.get_editor_property('film_decision')==1
for prop,value in [('field_items',[-1]*9),('looted_caches',1<<24),('open_doors',1<<24),('film_progress',99)]:
    broken=unreal.GameplayStatics.load_game_from_slot('Survival_A',0);broken.set_editor_property('save_generation',99);broken.set_editor_property(prop,value)
    assert unreal.GameplayStatics.save_game_to_slot(broken,'Survival_B',0)
    recovery=instance();assert recovery.load_progress();assert recovery.save_progress()
    fixed=unreal.GameplayStatics.load_game_from_slot('Survival_B',0);assert fixed.get_editor_property('film_progress')==14
# Version 7: real UObject county choice replay, transactional repair and save
# recovery. Physical props/audio/cinematics require separate rendered tests.
for slot in ['Survival_A','Survival_B']:unreal.GameplayStatics.delete_game_in_slot(slot,0)
county_save=unreal.GameplayStatics.create_save_game_object(save_cls)
county_save.set_editor_property('format_version',7);county_save.set_editor_property('save_generation',50)
county_save.set_editor_property('field_items',[0,0,6,6,0,0,0,0,0]);county_save.set_editor_property('county_stages',[0]*6)
assert unreal.GameplayStatics.save_game_to_slot(county_save,'Survival_A',0)
county_game=instance();assert county_game.load_progress()
for arc in range(6):
 assert county_game.try_county_action(arc,2)==3
 assert county_game.try_county_action(arc,0)==0
 assert county_game.try_county_action(arc,1)==0
 assert county_game.try_county_action(arc,1)==1
 choice=2 if arc%2==0 else 3
 assert county_game.try_county_action(arc,choice)==0
 assert county_game.try_county_action(arc,choice)==1
 assert county_game.try_county_action(arc,3 if choice==2 else 2)==3
assert county_game.save_progress()
county_roundtrip=unreal.GameplayStatics.load_game_from_slot('Survival_B',0)
assert list(county_roundtrip.get_editor_property('county_stages'))==[3,4,3,4,3,4]
assert list(county_roundtrip.get_editor_property('field_items'))==[0,0,0,0,0,3,0,0,0]
for bad in [[0]*5,[5,0,0,0,0,0],[-1,0,0,0,0,0]]:
 broken=unreal.GameplayStatics.load_game_from_slot('Survival_B',0);broken.set_editor_property('save_generation',100);broken.set_editor_property('county_stages',bad)
 assert unreal.GameplayStatics.save_game_to_slot(broken,'Survival_A',0)
 good=instance();assert good.load_progress();assert good.get_county_stage(0)==3 and good.get_county_stage(1)==4
county_save.set_editor_property('format_version',6);county_save.set_editor_property('save_generation',101);county_save.set_editor_property('county_stages',[-1]*6)
assert unreal.GameplayStatics.save_game_to_slot(county_save,'Survival_A',0)
legacy_county=instance();assert legacy_county.load_progress();assert all(legacy_county.get_county_stage(i)==0 for i in range(6))
# Version 8: one main rescue chain, independent of all optional county choices.
for slot in ['Survival_A','Survival_B']:unreal.GameplayStatics.delete_game_in_slot(slot,0)
main_save=unreal.GameplayStatics.create_save_game_object(save_cls)
main_save.set_editor_property('format_version',8);main_save.set_editor_property('save_generation',200)
main_save.set_editor_property('film_decision',2);main_save.set_editor_property('field_items',[0,0,1,1,0,0,0,0,0])
for action,progress in enumerate([20,22,24,26,29]):
 for slot in ['Survival_A','Survival_B']:unreal.GameplayStatics.delete_game_in_slot(slot,0)
 main_save.set_editor_property('film_progress',progress)
 assert unreal.GameplayStatics.save_game_to_slot(main_save,'Survival_A',0)
 main_game=instance();assert main_game.load_progress();assert main_game.try_main_action(action)==0
 assert main_game.try_main_action(action)==1
 assert main_game.save_progress()
 main_save=unreal.GameplayStatics.load_game_from_slot('Survival_B',0)
 assert main_save.get_editor_property('main_story_events')==(1<<(action+1))-1
 assert list(main_save.get_editor_property('county_stages'))==[0]*6
 assert main_save.get_editor_property('field_items')[5]==0
for broken_mask in [-1,2,5,63,0]:
 broken=unreal.GameplayStatics.load_game_from_slot('Survival_B',0);broken.set_editor_property('save_generation',9999);broken.set_editor_property('main_story_events',broken_mask)
 assert unreal.GameplayStatics.save_game_to_slot(broken,'Survival_A',0)
 fallback=instance();assert fallback.load_progress();assert fallback.save_progress()
 fixed=unreal.GameplayStatics.load_game_from_slot('Survival_A',0);assert fixed.get_editor_property('main_story_events')==31
legacy_main=unreal.GameplayStatics.create_save_game_object(save_cls);legacy_main.set_editor_property('format_version',7);legacy_main.set_editor_property('save_generation',20000)
legacy_main.set_editor_property('film_progress',18);legacy_main.set_editor_property('film_decision',2);legacy_main.set_editor_property('field_items',[0]*9)
legacy_main.set_editor_property('main_story_events',-1)
assert unreal.GameplayStatics.save_game_to_slot(legacy_main,'Survival_A',0)
migrated_main=instance();assert migrated_main.load_progress();assert migrated_main.save_progress()
migrated_save=unreal.GameplayStatics.load_game_from_slot('Survival_B',0);assert migrated_save.get_editor_property('main_story_events')==0
# A player who spent all ordinary crafting materials can still repair the
# required receiver using the protected spare kit placed beside it.
for slot in ['Survival_A','Survival_B']:unreal.GameplayStatics.delete_game_in_slot(slot,0)
spare=unreal.GameplayStatics.create_save_game_object(save_cls);spare.set_editor_property('format_version',8)
spare.set_editor_property('film_progress',20);spare.set_editor_property('film_decision',2);spare.set_editor_property('field_items',[0]*9)
assert unreal.GameplayStatics.save_game_to_slot(spare,'Survival_A',0)
g=instance();assert g.load_progress();assert g.try_main_action(0)==3;assert g.try_main_action(5)==0;assert g.save_progress()
spare_roundtrip=unreal.GameplayStatics.load_game_from_slot('Survival_B',0);assert spare_roundtrip.get_editor_property('main_repair_kit_recovered')
g=instance();assert g.load_progress();assert g.try_main_action(0)==0;assert g.save_progress()
report={'phase' :'unreal-headless-native-integration','native_classes_loaded':4,
 'version8_main_rescue_and_legacy_migration_tested':True,'version7_county_choices_and_legacy_migration_tested':True,'version6_field_and_film_serialization_fallback_tested':True,'version5_world_clock_serialization_and_fallback_tested':True,'version4_clock_migration_tested':True,'same_revision_save_generation_tested':True,'damaged_and_dead_encounters_restored':True,'invalid_and_duplicate_encounter_fallback_tested':True,'view_rotation_serialization_tested':True,
 'objective_count':61,'native_inventory_and_choices_tested':True,
 'save_write_and_load_tested':True,'truncated_newest_slot_recovery_tested':True,
 'unreal_editor_version':unreal.SystemLibrary.get_engine_version(),
 'visual_render_tested':False,'android_package_tested':False,'physical_device_tested':False}
output.mkdir(parents=True,exist_ok=True)
(output/'unreal-integration.json').write_text(json.dumps(report,indent=2)+'\n')
print('UNREAL_INTEGRATION_PASS',json.dumps(report))
