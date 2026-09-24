#include "SurvivalGameInstance.h"
#include "SurvivalSaveGame.h"
#include "SurvivalCharacter.h"
#include "Engine/World.h"
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
    Save->SaveGeneration = SaveGeneration + 1;
    Save->StateRevision = static_cast<int64>(Runtime.State().revision);
    for (const auto& Id : Runtime.State().journal) Save->ActionJournal.Add(UTF8_TO_TCHAR(Id.c_str()));
    if (GetWorld()) if (auto* Player = Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(GetWorld(),0)))
    {
        if (!Player->IsAlive()) return false;
        Save->bHasPlayerState=true;Save->MapName=UGameplayStatics::GetCurrentLevelName(GetWorld(),true);
        Save->PlayerLocation=Player->GetActorLocation();Save->PlayerRotation=Player->GetActorRotation();
        Save->Health=Player->GetHealth();Save->Stamina=Player->GetStamina();
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
        if (!Save || (Save->FormatVersion != 1 && Save->FormatVersion != 2) || Save->CampaignVersion != TEXT("foundation-1") ||
            Save->StateRevision < 0 || Save->StateRevision != Save->ActionJournal.Num() || Save->SaveGeneration<0) continue;
        if (Save->bHasPlayerState && (Save->MapName.IsEmpty() || Save->PlayerLocation.ContainsNaN() ||
            Save->PlayerLocation.GetAbsMax()>1000000 || Save->PlayerRotation.ContainsNaN() ||
            !FMath::IsFinite(Save->Health) || Save->Health<=0 || Save->Health>100 ||
            !FMath::IsFinite(Save->Stamina) || Save->Stamina<0 || Save->Stamina>100)) continue;
        survival::Runtime Candidate;
        if (static_cast<size_t>(Save->ActionJournal.Num()) > Candidate.Definition().actions.size()) continue;
        bool bValid = true;
        for (const auto& Id : Save->ActionJournal)
        {
            if (Candidate.TryAction(std::string(TCHAR_TO_UTF8(*Id))) != survival::Error::None)
            { bValid = false; break; }
        }
        const int64 Generation = Save->FormatVersion>=2 ? Save->SaveGeneration : Save->StateRevision;
        if (bValid && (!bFound || Generation > BestGeneration))
        { bFound = true; Best = Candidate.State(); BestSlot = Index; BestGeneration=Generation;BestSave=Save; }
    }
    if (!bFound || Runtime.Restore(Best) != survival::Error::None) return false;
    SaveGeneration=BestGeneration;PendingPlayerSave=BestSave;
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
    return Player->RestoreVitals(PendingPlayerSave->Health,PendingPlayerSave->Stamina);
}
