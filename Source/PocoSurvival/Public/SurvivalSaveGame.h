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
    UPROPERTY(SaveGame) int32 FormatVersion = 1;
    UPROPERTY(SaveGame) FString CampaignVersion = TEXT("foundation-1");
    UPROPERTY(SaveGame) int64 StateRevision = 0;
    UPROPERTY(SaveGame) TArray<FString> ActionJournal;
};
