#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "SurvivalGameMode.generated.h"
UCLASS()
class POCOSURVIVAL_API ASurvivalGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ASurvivalGameMode();
    virtual void StartPlay() override;
private:
    void Intro();void EndIntro();void CaptureProof();void ExitProof();
    void BeginMovementProof();void EndMovementProof();
    FVector MovementProofStart=FVector::ZeroVector;
    bool bMovementProofStarted=false;
};
