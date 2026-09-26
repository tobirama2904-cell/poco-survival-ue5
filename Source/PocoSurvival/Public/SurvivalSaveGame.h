#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "SurvivalSaveGame.generated.h"

USTRUCT(BlueprintType)
struct FSurvivalInfectedSnapshot
{
    GENERATED_BODY()
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FName PersistentId;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FString MapName;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FVector Location = FVector::ZeroVector;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FRotator Rotation = FRotator::ZeroRotator;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") float Health = 100;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") float Stamina = 100;
};

// Persist the ordered event journal. World facts are reconstructed by validated
// replay; edits to arbitrary inventory counters are never silently accepted.
UCLASS()
class POCOSURVIVAL_API USurvivalSaveGame : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 FormatVersion = 0; // Sentinel default; SaveProgress writes explicit version 8.
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FString CampaignVersion = TEXT("city-1");
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 SaveGeneration = 0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") bool bHasPlayerState = false;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FString MapName;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FVector PlayerLocation = FVector::ZeroVector;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FRotator PlayerRotation = FRotator::ZeroRotator;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FRotator ViewRotation = FRotator::ZeroRotator;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") TArray<FSurvivalInfectedSnapshot> InfectedStates;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") float Health = 100;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") float Stamina = 100;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") TArray<int32> FieldItems;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 LootedCaches=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 OpenDoors=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FVector4 WoundState=FVector4(0,0,0,0);
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") bool bBowEquipped=false;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 FilmProgress=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 JourneyHeard=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") bool bMaraHolding=false;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FVector MaraHoldLocation=FVector::ZeroVector;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") FString MaraHoldMap;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") TArray<int32> CountyStages={0,0,0,0,0,0};
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 FilmDecision=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 MainStoryEvents=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") bool MainRepairKitRecovered=false;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") double WorldElapsedSeconds=61200;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 WeatherSeed=731;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 LoadedRounds=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 RoundsSpent=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int32 BottlesUsed=0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") bool bPistolEquipped=false;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") int64 StateRevision = 0;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="Save") TArray<FString> ActionJournal;
};
