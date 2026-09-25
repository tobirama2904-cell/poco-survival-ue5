#pragma once
#include "CoreMinimal.h"
#include "SurvivalCharacter.h"
#include "Core/CompanionSupport.h"
#include "SurvivalCompanion.generated.h"
// Protected narrative escort/companion: following, hold, conversation and bandage aid.
// Not yet tactical combat, relationships/permanent-death AI or global navigation.
UCLASS()
class POCOSURVIVAL_API ASurvivalCompanion : public ASurvivalCharacter
{
 GENERATED_BODY()
public:
 ASurvivalCompanion();
 virtual void BeginPlay() override;
 virtual void Tick(float Delta) override;
 virtual void FellOutOfWorld(const UDamageType&) override;
 virtual float TakeDamage(float,const FDamageEvent&,AController*,AActor*) override { return 0; }
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Companion") bool RuthRole=false;
 UFUNCTION(BlueprintPure,Category="Companion") bool IsAvailable() const { return bAvailable; }
 float Travelled=0;
 bool ToggleHold(ASurvivalCharacter* Player);
 bool RequestAid(ASurvivalCharacter* Player);
 bool IsHelping() const { return Aid.Active(); }
 float HelpProgress() const { return Aid.Progress(); }
private:
 survival::CompanionAid Aid;
 float AidStarted=-1000;
 uint32 SupportEpoch=MAX_uint32;
 bool RestoreHold(class USurvivalGameInstance* Game);
 void UpdateAid(float Delta,ASurvivalCharacter* Player,class USurvivalGameInstance* Game);
 bool bAvailable=false,bSettled=false,bProxyStateApplied=false,bProxyActive=false;
 FVector Refuge=FVector::ZeroVector;
 FVector Direction=FVector::ZeroVector,Last=FVector::ZeroVector;
 float SteerDelay=0,RecoveryDelay=0;
 bool PlaceNear(ASurvivalCharacter* Player);
};
