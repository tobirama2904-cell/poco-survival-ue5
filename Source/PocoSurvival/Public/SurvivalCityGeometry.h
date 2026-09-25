#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalCityGeometry.generated.h"
class UHierarchicalInstancedStaticMeshComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalCityGeometry : public AActor
{
    GENERATED_BODY()
public:
    ASurvivalCityGeometry();
    UFUNCTION(BlueprintCallable,Category="City") void AddBox(FVector Center,FVector Size,int32 Surface);
private:
    UPROPERTY() TArray<TObjectPtr<UHierarchicalInstancedStaticMeshComponent>> Surfaces;
};
