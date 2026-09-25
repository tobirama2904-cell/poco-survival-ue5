#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalSceneryCluster.generated.h"
class UStaticMesh;
class UHierarchicalInstancedStaticMeshComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalSceneryCluster : public AActor
{
 GENERATED_BODY()
public:
 ASurvivalSceneryCluster();
 UFUNCTION(BlueprintCallable,Category="County") void Configure(UStaticMesh* Mesh,float CullDistance,bool TreeTrunks,bool SolidObjects=false);
 UFUNCTION(BlueprintCallable,Category="County") void AddScenery(FVector Position,float Yaw,float Scale);
private:
 UPROPERTY() TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Visuals;
 UPROPERTY() TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Trunks;
 UPROPERTY() bool bTreeTrunks=false;
};
