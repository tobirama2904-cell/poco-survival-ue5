#include "SurvivalGameInstance.h"
#include "SurvivalSaveGame.h"
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
    auto* Save = Cast<USurvivalSaveGame>(UGameplayStatics::CreateSaveGameObject(USurvivalSaveGame::StaticClass()));
    if (!Save) return false;
    Save->StateRevision = static_cast<int64>(Runtime.State().revision);
    for (const auto& Id : Runtime.State().journal) Save->ActionJournal.Add(UTF8_TO_TCHAR(Id.c_str()));
    // Alternate slots by successful writes, not revision parity. Even if several
    // actions occur between saves, the previous successfully written slot stays.
    if (!UGameplayStatics::SaveGameToSlot(Save, SlotName(NextSaveSlot), 0)) return false;
    NextSaveSlot = 1 - NextSaveSlot;
    return true;
}
bool USurvivalGameInstance::LoadProgress()
{
    bool bFound = false;
    survival::Snapshot Best;
    int32 BestSlot = 0;
    for (int32 Index = 0; Index < 2; ++Index)
    {
        if (!UGameplayStatics::DoesSaveGameExist(SlotName(Index), 0)) continue;
        const auto* Save = Cast<USurvivalSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName(Index), 0));
        if (!Save || Save->FormatVersion != 1 || Save->CampaignVersion != TEXT("foundation-1") ||
            Save->StateRevision < 0 || Save->StateRevision != Save->ActionJournal.Num()) continue;
        survival::Runtime Candidate;
        if (static_cast<size_t>(Save->ActionJournal.Num()) > Candidate.Definition().actions.size()) continue;
        bool bValid = true;
        for (const auto& Id : Save->ActionJournal)
        {
            if (Candidate.TryAction(std::string(TCHAR_TO_UTF8(*Id))) != survival::Error::None)
            { bValid = false; break; }
        }
        if (bValid && (!bFound || Candidate.State().revision > Best.revision))
        { bFound = true; Best = Candidate.State(); BestSlot = Index; }
    }
    if (!bFound || Runtime.Restore(Best) != survival::Error::None) return false;
    NextSaveSlot = 1 - BestSlot;
    OnWorldStateChanged.Broadcast();
    return true;
}
