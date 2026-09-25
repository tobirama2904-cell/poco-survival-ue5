#pragma once
#include "CoreMinimal.h"
#include "SurvivalCharacter.h"
#include "SurvivalCompanion.generated.h"
// Protected narrative escort foundation: following, crouching and conversation.
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
private:
 bool bAvailable=false,bSettled=false,bProxyStateApplied=false,bProxyActive=false;
 FVector Refuge=FVector::ZeroVector;
 FVector Direction=FVector::ZeroVector,Last=FVector::ZeroVector;
 float SteerDelay=0,RecoveryDelay=0;
 bool PlaceNear(ASurvivalCharacter* Player);
};
