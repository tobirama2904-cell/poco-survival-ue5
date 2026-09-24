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
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 FormatVersion = 2;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FString CampaignVersion = TEXT("foundation-1");
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 SaveGeneration = 0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") bool bHasPlayerState = false;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FString MapName;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FVector PlayerLocation = FVector::ZeroVector;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FRotator PlayerRotation = FRotator::ZeroRotator;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") float Health = 100;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") float Stamina = 100;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 StateRevision = 0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") TArray<FString> ActionJournal;
};
