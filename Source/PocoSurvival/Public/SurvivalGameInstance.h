#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "Core/SurvivalCore.h"
#include "Core/CityContent.h"
#include "Core/Experience.h"
#include "Core/FieldSurvival.h"
#include "Core/CountyStories.h"
#include "Core/MainCampaign.h"
#include "Core/JourneyDialogue.h"
#include "SurvivalGameInstance.generated.h"

class USoundAttenuation;
class ASurvivalCharacter;
class ASurvivalInfected;
class USurvivalSaveGame;

USTRUCT(BlueprintType)
struct FSurvivalObjectiveView
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FName Id;
    UPROPERTY(BlueprintReadOnly) FName District;
    UPROPERTY(BlueprintReadOnly) FText Title;
    UPROPERTY(BlueprintReadOnly) FName StatusCode;
    UPROPERTY(BlueprintReadOnly) bool bAvailable = false;
    UPROPERTY(BlueprintReadOnly) bool bCompleted = false;
};
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FSurvivalStateChanged);

UCLASS()
class POCOSURVIVAL_API USurvivalGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;
    USoundAttenuation* SpatialSound();
    survival::FieldKit FieldInventory;
    survival::CountyState County;
    survival::CampaignState MainStory;
    survival::JourneyHistory Journey;
    bool bMaraHolding=false;
    FVector MaraHoldLocation=FVector::ZeroVector;
    FString MaraHoldMap;
    uint32 SupportLoadRevision=0;
    UFUNCTION(BlueprintCallable,Category="Story") bool FinishJourneyConversation(int32 Id) { return Journey.Finish(Id); }
    UFUNCTION(BlueprintPure,Category="Story") int64 GetJourneyHeard() const { return Journey.heard; }
    UFUNCTION(BlueprintCallable,Category="Story") int32 TryMainAction(int32 Action) { return static_cast<int32>(MainStory.Apply(Action,FilmProgress,FieldInventory)); }
    UFUNCTION(BlueprintCallable,Category="County") int32 TryCountyAction(int32 Arc,int32 Action) { return static_cast<int32>(County.Apply(Arc,Action,FieldInventory)); }
    UFUNCTION(BlueprintPure,Category="County") int32 GetCountyStage(int32 Arc) const { return Arc>=0&&Arc<survival::CountyState::Count?County.stages[Arc]:-1; }
    int32 FilmProgress=0,FilmDecision=0;
    UFUNCTION(BlueprintCallable,Category="World") void StepWorldClock(float Delta,bool Paused) { Clock.Step(Delta,Paused); }
    UFUNCTION(BlueprintPure,Category="World") float WorldHour() const { return Clock.Hour(); }
    UFUNCTION(BlueprintPure,Category="World") double WorldSeconds() const { return Clock.seconds; }
    survival::Climate WorldClimate() const { return Clock.Sample(); }
    UPROPERTY(BlueprintAssignable, Category="Survival") FSurvivalStateChanged OnWorldStateChanged;
    UFUNCTION(BlueprintCallable, Category="Survival") bool TryAction(FName ActionId, FString& FailureReason);
    UFUNCTION(BlueprintPure, Category="Survival") bool HasWorldFlag(FName Flag) const;
    UFUNCTION(BlueprintPure, Category="Survival") bool HasCompletedAction(FName ActionId) const;
    UFUNCTION(BlueprintPure, Category="Survival") int32 GetItemCount(FName ItemId) const;
    UFUNCTION(BlueprintPure, Category="Survival") float GetCarriedWeightKg() const;
    UFUNCTION(BlueprintPure, Category="Survival") TArray<FSurvivalObjectiveView> GetObjectives() const;
    UFUNCTION(BlueprintCallable, Category="Survival|Save") bool SaveProgress();
    UFUNCTION(BlueprintCallable, Category="Survival|Save") bool LoadProgress();
    UFUNCTION(BlueprintCallable, Category="Survival|Save") bool ApplyLoadedPlayerState(ASurvivalCharacter* Player);
    UFUNCTION(BlueprintCallable, Category="Survival|Save") bool ApplyLoadedInfectedState(ASurvivalInfected* Infected);
private:
    UPROPERTY() TObjectPtr<USoundAttenuation> SfxAttenuation;
    UPROPERTY() TObjectPtr<USurvivalSaveGame> PendingPlayerSave;
    int64 SaveGeneration = 0;
    survival::WorldClock Clock;
    survival::Runtime Runtime{survival::MakeCityCampaign()};
    int32 NextSaveSlot = 0;
};
