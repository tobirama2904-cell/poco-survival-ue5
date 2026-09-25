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
assert len(game.get_objectives())==55
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
report={'phase' :'unreal-headless-native-integration','native_classes_loaded':3,
 'same_revision_save_generation_tested':True,'damaged_and_dead_encounters_restored':True,'invalid_and_duplicate_encounter_fallback_tested':True,'view_rotation_serialization_tested':True,
 'objective_count':55,'native_inventory_and_choices_tested':True,
 'save_write_and_load_tested':True,'truncated_newest_slot_recovery_tested':True,
 'unreal_editor_version':unreal.SystemLibrary.get_engine_version(),
 'visual_render_tested':False,'android_package_tested':False,'physical_device_tested':False}
output.mkdir(parents=True,exist_ok=True)
(output/'unreal-integration.json').write_text(json.dumps(report,indent=2)+'\n')
print('UNREAL_INTEGRATION_PASS',json.dumps(report))
