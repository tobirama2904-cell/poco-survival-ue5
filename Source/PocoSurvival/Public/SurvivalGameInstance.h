#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "Core/SurvivalCore.h"
#include "SurvivalGameInstance.generated.h"

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
    UPROPERTY() TObjectPtr<USurvivalSaveGame> PendingPlayerSave;
    int64 SaveGeneration = 0;
    survival::Runtime Runtime;
    int32 NextSaveSlot = 0;
};
