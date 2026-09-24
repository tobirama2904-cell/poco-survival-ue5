#pragma once
#include "CoreMinimal.h"
#include "SurvivalCharacter.h"
#include "SurvivalInfected.generated.h"
UENUM(BlueprintType)
enum class EInfectedState : uint8 { Patrol, Investigate, Chase, Attack, Dead };
// Engineering enemy actor. Manny and unarmed motions are licensed test assets,
// NOT final infected art. Steering here is local, not district-scale navigation.
UCLASS()
class POCOSURVIVAL_API ASurvivalInfected : public ASurvivalCharacter
{
    GENERATED_BODY()
public:
    ASurvivalInfected();
    virtual void BeginPlay() override;
    virtual void Tick(float Delta) override;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Save") FName PersistentId;
    UFUNCTION(BlueprintCallable,Category="Save") bool RestoreEncounter(const FVector& Location,const FRotator& Rotation,float Health,float Stamina);
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="AI") TArray<FVector> PatrolPoints;
    UPROPERTY(BlueprintReadOnly,Category="AI") EInfectedState State=EInfectedState::Patrol;
private:
    FVector Destination=FVector::ZeroVector;
    FVector Direction=FVector::ZeroVector;
    float ThinkDelay=0,UnseenSeconds=100,AttackDelay=0;
    int32 PatrolIndex=0;
    void Think(float Delta);
};
