#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalBottle.generated.h"
class USphereComponent;
class UPrimitiveComponent;
class UStaticMeshComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalBottle : public AActor
{
    GENERATED_BODY()
public:
    ASurvivalBottle();
    void Launch(FVector Velocity);
private:
    UPROPERTY() TObjectPtr<USphereComponent> Physics;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Visual;
    bool bBroken=false;
    UFUNCTION() void Impact(UPrimitiveComponent* HitComponent,AActor* OtherActor,UPrimitiveComponent* OtherComponent,FVector Impulse,const FHitResult& Hit);
};
