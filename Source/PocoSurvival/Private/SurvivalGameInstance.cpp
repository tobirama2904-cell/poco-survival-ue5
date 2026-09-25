#include "SurvivalGameInstance.h"
#include "Sound/SoundAttenuation.h"
#include "SurvivalSaveGame.h"
#include "Core/AmericanStory.h"
#include "SurvivalInteraction.h"
#include "SurvivalCharacter.h"
#include "SurvivalInfected.h"
#include "GameFramework/Controller.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"

namespace {
std::string NativeId(FName Name) { return std::string(TCHAR_TO_UTF8(*Name.ToString())); }
FString SlotName(int32 Index) { return Index == 0 ? TEXT("Survival_A") : TEXT("Survival_B"); }
}
void USurvivalGameInstance::Init()
{
    Super::Init();
    LoadProgress();
}
bool USurvivalGameInstance::TryAction(FName ActionId, FString& FailureReason)
{
    const survival::Error Result = Runtime.TryAction(NativeId(ActionId));
    FailureReason = UTF8_TO_TCHAR(survival::Explain(Result));
    if (Result != survival::Error::None) return false;
    OnWorldStateChanged.Broadcast();
    return true;
}
bool USurvivalGameInstance::HasWorldFlag(FName Flag) const { return Runtime.HasFlag(NativeId(Flag)); }
bool USurvivalGameInstance::HasCompletedAction(FName ActionId) const { return Runtime.State().completed.count(NativeId(ActionId)) != 0; }
int32 USurvivalGameInstance::GetItemCount(FName ItemId) const
{
    const auto It = Runtime.State().inventory.find(NativeId(ItemId));
    return It == Runtime.State().inventory.end() ? 0 : It->second;
}
float USurvivalGameInstance::GetCarriedWeightKg() const { return static_cast<float>(Runtime.CarriedGrams()) / 1000.0f; }
TArray<FSurvivalObjectiveView> USurvivalGameInstance::GetObjectives() const
{
    TArray<FSurvivalObjectiveView> Results;
    for (const auto& Action : Runtime.Definition().actions)
    {
        FSurvivalObjectiveView View;
        View.Id = FName(UTF8_TO_TCHAR(Action.id.c_str()));
        View.District = FName(UTF8_TO_TCHAR(Action.district.c_str()));
        View.Title = FText::FromString(UTF8_TO_TCHAR(Action.title.c_str()));
        const auto Status = Runtime.CanApply(Action.id);
        View.StatusCode = FName(UTF8_TO_TCHAR(survival::Explain(Status)));
        View.bAvailable = Status == survival::Error::None;
        View.bCompleted = Runtime.State().completed.count(Action.id) != 0;
        Results.Add(View);
    }
    return Results;
}
bool USurvivalGameInstance::SaveProgress()
{
    if (SaveGeneration == MAX_int64) return false;
    auto* Save = Cast<USurvivalSaveGame>(UGameplayStatics::CreateSaveGameObject(USurvivalSaveGame::StaticClass()));
    if (!Save) return false;
    Save->SaveGeneration = SaveGeneration + 1;Save->WorldElapsedSeconds=Clock.seconds;Save->WeatherSeed=Clock.seed;
    Save->MainRepairKitRecovered=MainStory.spareRecovered;Save->MainStoryEvents=MainStory.events;Save->FilmProgress=FilmProgress;Save->FilmDecision=FilmDecision;Save->LootedCaches=FieldInventory.looted;Save->OpenDoors=FieldInventory.doors;for(int32 N:FieldInventory.items)Save->FieldItems.Add(N);
    Save->CountyStages.Reset();for(int32 Stage:County.stages)Save->CountyStages.Add(Stage);
    Save->StateRevision = static_cast<int64>(Runtime.State().revision);
    for (const auto& Id : Runtime.State().journal) Save->ActionJournal.Add(UTF8_TO_TCHAR(Id.c_str()));
    if (GetWorld()) if (auto* Player = Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(GetWorld(),0)))
    {
        if (!Player->IsAlive() || !Player->GetCharacterMovement()->IsMovingOnGround()) return false;
        Save->bHasPlayerState=true;Save->MapName=UGameplayStatics::GetCurrentLevelName(GetWorld(),true);
        Save->PlayerLocation=Player->GetActorLocation();Save->PlayerRotation=Player->GetActorRotation();
        Save->ViewRotation=Player->GetController() ? Player->GetController()->GetControlRotation() : Save->PlayerRotation;
        Save->bBowEquipped=Player->bBowEquipped;const auto& W=Player->Wounds();Save->WoundState=FVector4(W.bleeding,W.arm,W.leg,W.concussion);
        Save->Health=Player->GetHealth();Save->Stamina=Player->GetStamina();
        const auto& Combat=Player->CombatState();Save->LoadedRounds=Combat.loaded;Save->RoundsSpent=Combat.spent;Save->BottlesUsed=Combat.bottlesUsed;Save->bPistolEquipped=Combat.pistol;
    }
    if (UWorld* World=GetWorld()) {
        const FString Map=UGameplayStatics::GetCurrentLevelName(World,true);
        if (PendingPlayerSave) for (const auto& Previous:PendingPlayerSave->InfectedStates)
            if (Previous.MapName!=Map) Save->InfectedStates.Add(Previous);
        TSet<FName> Ids;
        for (TActorIterator<ASurvivalInfected> It(World);It;++It) {
            if (It->PersistentId.IsNone()) continue;
            if (Ids.Contains(It->PersistentId)) return false;
            Ids.Add(It->PersistentId);
            FSurvivalInfectedSnapshot State;State.PersistentId=It->PersistentId;State.MapName=Map;
            State.Location=It->GetActorLocation();State.Rotation=It->GetActorRotation();
            State.Health=It->GetHealth();State.Stamina=It->GetStamina();Save->InfectedStates.Add(State);
        }
        if (Save->InfectedStates.Num()>256) return false;
    }
    if (!UGameplayStatics::SaveGameToSlot(Save, SlotName(NextSaveSlot), 0)) return false;
    SaveGeneration=Save->SaveGeneration;PendingPlayerSave=Save;
    NextSaveSlot = 1 - NextSaveSlot;
    return true;
}
bool USurvivalGameInstance::LoadProgress()
{
    bool bFound = false;
    survival::Snapshot Best;
    int32 BestSlot = 0;
    int64 BestGeneration = -1;
    USurvivalSaveGame* BestSave = nullptr;
    for (int32 Index = 0; Index < 2; ++Index)
    {
        if (!UGameplayStatics::DoesSaveGameExist(SlotName(Index), 0)) continue;
        auto* Save = Cast<USurvivalSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName(Index), 0));
        if (!Save || (Save->FormatVersion < 1 || Save->FormatVersion > 8) || (Save->CampaignVersion != TEXT("foundation-1") && Save->CampaignVersion != TEXT("city-1")) ||
            Save->StateRevision < 0 || Save->StateRevision != Save->ActionJournal.Num() || Save->SaveGeneration<0) continue;
        if (Save->bHasPlayerState && (Save->MapName.IsEmpty() || Save->PlayerLocation.ContainsNaN() ||
            Save->PlayerLocation.GetAbsMax()>1000000 || Save->PlayerRotation.ContainsNaN() ||
            !FMath::IsFinite(Save->Health) || Save->Health<=0 || Save->Health>100 ||
            !FMath::IsFinite(Save->Stamina) || Save->Stamina<0 || Save->Stamina>100)) continue;
        if (Save->FormatVersion>=3 && (Save->ViewRotation.ContainsNaN() || Save->InfectedStates.Num()>256)) continue;
        if(Save->FormatVersion>=5&&(!FMath::IsFinite(Save->WorldElapsedSeconds)||Save->WorldElapsedSeconds<0||Save->WorldElapsedSeconds>315360000||Save->WeatherSeed<0||Save->WeatherSeed>MAX_uint32))continue;
        if(Save->FormatVersion>=7){
            if(Save->CountyStages.Num()!=survival::CountyState::Count)continue;
            survival::CountyState Check;for(int32 I=0;I<survival::CountyState::Count;++I)Check.stages[I]=Save->CountyStages[I];
            if(!Check.Valid())continue;
        }
        if(Save->FormatVersion<8&&Save->FilmProgress>18)continue;
        if(Save->FormatVersion>=8){
            if(Save->MainStoryEvents<0||Save->MainStoryEvents>31)continue;
            survival::CampaignState Check;Check.events=static_cast<uint32>(Save->MainStoryEvents);if(!Check.Valid())continue;
            unsigned Required=0;const auto& Scenes=survival::FilmScenes();
            if(Save->FilmProgress<0||Save->FilmProgress>static_cast<int32>(Scenes.size()))continue;
            for(int32 I=0;I<Save->FilmProgress;++I)Required|=Scenes[I].requiredEvents;
            if(!Check.Has(Required))continue;
        }
        survival::FieldKit Field;
        if(Save->FormatVersion>=6){
            if(Save->FieldItems.Num()!=static_cast<int32>(survival::Supply::Count)||Save->LootedCaches<0||Save->LootedCaches>=(1ll<<24)||Save->OpenDoors<0||Save->OpenDoors>=(1ll<<24)||Save->FilmProgress<0||Save->FilmProgress>static_cast<int32>(survival::FilmScenes().size())||Save->FilmDecision<0||Save->FilmDecision>2||(Save->FilmProgress>=15&&Save->FilmDecision==0)||(Save->FilmProgress<14&&Save->FilmDecision!=0))continue;
            for(int32 I=0;I<Save->FieldItems.Num();++I)Field.items[I]=Save->FieldItems[I];Field.looted=static_cast<uint32>(Save->LootedCaches);Field.doors=static_cast<uint32>(Save->OpenDoors);
            const auto W=Save->WoundState;const survival::Trauma T{static_cast<float>(W.X),static_cast<float>(W.Y),static_cast<float>(W.Z),static_cast<float>(W.W)};
            if(!Field.Valid()||!T.Valid()||(Save->bBowEquipped&&(Field.Get(survival::Supply::Bow)==0||Save->bPistolEquipped)))continue;
        }
        bool EncountersValid=true;TSet<FString> EncounterKeys;
        for (const auto& State:Save->InfectedStates) {
            const FString Key=State.MapName+TEXT("/")+State.PersistentId.ToString();
            if (State.PersistentId.IsNone() || State.MapName.IsEmpty() || EncounterKeys.Contains(Key) ||
                State.Location.ContainsNaN() || State.Location.GetAbsMax()>1000000 || State.Rotation.ContainsNaN() ||
                !FMath::IsFinite(State.Health) || State.Health<0 || State.Health>100 ||
                !FMath::IsFinite(State.Stamina) || State.Stamina<0 || State.Stamina>100) { EncountersValid=false;break; }
            EncounterKeys.Add(Key);
        }
        if (!EncountersValid) continue;
        survival::Runtime Candidate{survival::MakeCityCampaign()};
        if (static_cast<size_t>(Save->ActionJournal.Num()) > Candidate.Definition().actions.size()) continue;
        bool bValid = true;
        for (const auto& Id : Save->ActionJournal)
        {
            if (Candidate.TryAction(std::string(TCHAR_TO_UTF8(*Id))) != survival::Error::None)
            { bValid = false; break; }
        }
        if (bValid && Save->FormatVersion>=4) {
            const auto& Inventory=Candidate.State().inventory;
            const auto Count=[&](const char* Name) { const auto It=Inventory.find(Name);return It==Inventory.end()?0:It->second; };
            bValid=survival::Combat::Valid({Save->LoadedRounds,Save->RoundsSpent,Save->BottlesUsed,Save->bPistolEquipped},Count("ammo_pack")*8+Field.Get(survival::Supply::Rounds),Count("bottle_pack"),Candidate.HasFlag("has_pistol"));
        }
        const int64 Generation = Save->FormatVersion>=2 ? Save->SaveGeneration : Save->StateRevision;
        if (bValid && (!bFound || Generation > BestGeneration))
        { bFound = true; Best = Candidate.State(); BestSlot = Index; BestGeneration=Generation;BestSave=Save; }
    }
    if (!bFound || Runtime.Restore(Best) != survival::Error::None) return false;
    SaveGeneration=BestGeneration;PendingPlayerSave=BestSave;FieldInventory={};MainStory={};if(BestSave->FormatVersion>=8){MainStory.events=static_cast<uint32>(BestSave->MainStoryEvents);MainStory.spareRecovered=BestSave->MainRepairKitRecovered;}County={};if(BestSave->FormatVersion>=7)for(int32 I=0;I<survival::CountyState::Count;++I)County.stages[I]=BestSave->CountyStages[I];FilmProgress=0;FilmDecision=0;
    if(BestSave->FormatVersion>=6){for(int32 I=0;I<BestSave->FieldItems.Num();++I)FieldInventory.items[I]=BestSave->FieldItems[I];FieldInventory.looted=static_cast<uint32>(BestSave->LootedCaches);FieldInventory.doors=static_cast<uint32>(BestSave->OpenDoors);FilmProgress=BestSave->FilmProgress;FilmDecision=BestSave->FilmDecision;}
    if(BestSave->FormatVersion>=5)Clock.Restore(BestSave->WorldElapsedSeconds,static_cast<uint32>(BestSave->WeatherSeed));else Clock.Restore(61200,731);
    if (UWorld* World=GetWorld()) for (TActorIterator<ASurvivalInfected> It(World);It;++It) ApplyLoadedInfectedState(*It);
    if(UWorld* World=GetWorld())for(TActorIterator<ASurvivalInteraction> It(World);It;++It){const FString Id=It->ActionId.ToString();if(Id.StartsWith(TEXT("__door_"))){const int32 I=FCString::Atoi(*Id.Mid(7));if(I>=0&&I<24)It->SetActorRotation(FRotator(0,(FieldInventory.doors&(1u<<I))?90:0,0));}if(Id.StartsWith(TEXT("__cache_"))){const int32 Index=FCString::Atoi(*Id.Mid(8));if(Index>=0&&Index<24){const bool Empty=(FieldInventory.looted&(1u<<Index))!=0;It->SetActorHiddenInGame(Empty);It->SetActorEnableCollision(!Empty);}}}
    NextSaveSlot = 1 - BestSlot;
    OnWorldStateChanged.Broadcast();
    return true;
}
bool USurvivalGameInstance::ApplyLoadedPlayerState(ASurvivalCharacter* Player)
{
    if (!Player || !PendingPlayerSave || !PendingPlayerSave->bHasPlayerState || !GetWorld()) return false;
    if (PendingPlayerSave->MapName != UGameplayStatics::GetCurrentLevelName(GetWorld(),true)) return false;
    // TeleportTo checks collision; an obstructed saved position must not force a
    // capsule into geometry. Vitals still recover at the current safe spawn.
    Player->TeleportTo(PendingPlayerSave->PlayerLocation,PendingPlayerSave->PlayerRotation,false,false);
    if (PendingPlayerSave->FormatVersion>=3) if (auto* Controller=Player->GetController()) Controller->SetControlRotation(PendingPlayerSave->ViewRotation);
    if (!Player->RestoreVitals(PendingPlayerSave->Health,PendingPlayerSave->Stamina)) return false;
    Player->bBowEquipped=PendingPlayerSave->FormatVersion>=6&&PendingPlayerSave->bBowEquipped;
    const FVector4 W=PendingPlayerSave->FormatVersion>=6?PendingPlayerSave->WoundState:FVector4(0,0,0,0);
    Player->RestoreWounds({static_cast<float>(W.X),static_cast<float>(W.Y),static_cast<float>(W.Z),static_cast<float>(W.W)});
    const survival::CombatSnapshot Combat=PendingPlayerSave->FormatVersion>=4 ? survival::CombatSnapshot{PendingPlayerSave->LoadedRounds,PendingPlayerSave->RoundsSpent,PendingPlayerSave->BottlesUsed,PendingPlayerSave->bPistolEquipped}:survival::CombatSnapshot{};
    return Player->RestoreCombat(Combat);
}

bool USurvivalGameInstance::ApplyLoadedInfectedState(ASurvivalInfected* Infected)
{
    if (!Infected || Infected->PersistentId.IsNone() || !PendingPlayerSave) return false;
    const FString Map=UGameplayStatics::GetCurrentLevelName(Infected,true);
    for (const auto& State:PendingPlayerSave->InfectedStates)
        if (State.MapName==Map && State.PersistentId==Infected->PersistentId)
            return Infected->RestoreEncounter(State.Location,State.Rotation,State.Health,State.Stamina);
    return false;
}

USoundAttenuation* USurvivalGameInstance::SpatialSound(){if(!SfxAttenuation){SfxAttenuation=NewObject<USoundAttenuation>(this);auto& S=SfxAttenuation->Attenuation;S.bAttenuate=true;S.bSpatialize=true;S.AttenuationShape=EAttenuationShape::Sphere;S.AttenuationShapeExtents=FVector(120,0,0);S.FalloffDistance=2600;}return SfxAttenuation;}
