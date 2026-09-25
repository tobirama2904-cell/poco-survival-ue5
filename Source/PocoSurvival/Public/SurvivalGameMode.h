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
    void BeginCountyProof();void EndCountyMovement();void CaptureCountyProof();
    void BeginCompanionFilmProof();
    void CaptureCompanionFilmProof();
    void BeginSupportProof();void BeginAidProof();void CaptureSupportProof();
    FVector SupportMaraStart=FVector::ZeroVector,SupportPlayerStart=FVector::ZeroVector;
    bool bSupportHeld=false,bSupportRequested=false;
    bool bCompanionAvailable=false,bCompanionHuman=false,bCompanionGrounded=false;
    float CompanionTravel=0,CompanionDistance=0;
    FVector CountyMovementStart=FVector::ZeroVector;
    int32 CountyFloors=0;
    int32 CountyAnchors=0;
    FVector MovementProofStart=FVector::ZeroVector;
    bool bMovementProofStarted=false;
};
