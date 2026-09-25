"""Run inside UnrealEditor-Cmd. Headless native integration, NOT visual gameplay."""
import json
from pathlib import Path
import unreal

output=Path('/project/artifacts/engine-probe')
cls=unreal.load_class(None,'/Script/PocoSurvival.SurvivalGameInstance')
assert cls is not None, 'Native GameInstance class failed to load'
assert unreal.load_class(None,'/Script/PocoSurvival.SurvivalInteraction') is not None
assert unreal.load_class(None,'/Script/PocoSurvival.SurvivalSaveGame') is not None

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
report={'phase' :'unreal-headless-native-integration','native_classes_loaded':3,
 'version6_field_and_film_serialization_fallback_tested':True,'version5_world_clock_serialization_and_fallback_tested':True,'version4_clock_migration_tested':True,'same_revision_save_generation_tested':True,'damaged_and_dead_encounters_restored':True,'invalid_and_duplicate_encounter_fallback_tested':True,'view_rotation_serialization_tested':True,
 'objective_count':61,'native_inventory_and_choices_tested':True,
 'save_write_and_load_tested':True,'truncated_newest_slot_recovery_tested':True,
 'unreal_editor_version':unreal.SystemLibrary.get_engine_version(),
 'visual_render_tested':False,'android_package_tested':False,'physical_device_tested':False}
output.mkdir(parents=True,exist_ok=True)
(output/'unreal-integration.json').write_text(json.dumps(report,indent=2)+'\n')
print('UNREAL_INTEGRATION_PASS',json.dumps(report))
