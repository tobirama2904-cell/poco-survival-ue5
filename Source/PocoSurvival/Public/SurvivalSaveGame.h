#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "SurvivalSaveGame.generated.h"

// Persist the ordered event journal. World facts are reconstructed by validated
// replay; edits to arbitrary inventory counters are never silently accepted.
UCLASS()
class POCOSURVIVAL_API USurvivalSaveGame : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 FormatVersion = 2;
    UPROPERTY(SaveGame) FString CampaignVersion = TEXT("foundation-1");
    UPROPERTY(SaveGame) int64 SaveGeneration = 0;
    UPROPERTY(SaveGame) bool bHasPlayerState = false;
    UPROPERTY(SaveGame) FString MapName;
    UPROPERTY(SaveGame) FVector PlayerLocation = FVector::ZeroVector;
    UPROPERTY(SaveGame) FRotator PlayerRotation = FRotator::ZeroRotator;
    UPROPERTY(SaveGame) float Health = 100;
    UPROPERTY(SaveGame) float Stamina = 100;
    UPROPERTY(SaveGame) int64 StateRevision = 0;
    UPROPERTY(SaveGame) TArray<FString> ActionJournal;
};
