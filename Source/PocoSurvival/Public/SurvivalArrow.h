#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalArrow.generated.h"
class USphereComponent;class UStaticMeshComponent;class UProjectileMovementComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalArrow:public AActor {
 GENERATED_BODY()
public:
 ASurvivalArrow();
 void Launch(FVector Direction,float Power,AController* Shooter);
private:
 UPROPERTY() TObjectPtr<USphereComponent> Collision;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> Shaft;
 UPROPERTY() TObjectPtr<UProjectileMovementComponent> Movement;
 UPROPERTY() TObjectPtr<AController> ShooterController;
 float Damage=45;bool bLanded=false;
 UFUNCTION() void Impact(UPrimitiveComponent* Component,AActor* Other,UPrimitiveComponent* OtherComponent,FVector Normal,const FHitResult& Hit);
};
