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
 virtual void BeginPlay() override;
 virtual void Tick(float Delta) override;
 UFUNCTION(BlueprintCallable,Category="County") void ConfigureDistanceLevels(UStaticMesh* NearMesh,UStaticMesh* MidMesh,UStaticMesh* FarMesh);
 UFUNCTION(BlueprintPure,Category="County") int32 GetVisualLOD() const { return CurrentLOD; }
 UFUNCTION(BlueprintCallable,Category="County") void Configure(UStaticMesh* Mesh,float CullDistance,bool TreeTrunks,bool SolidObjects=false);
 UFUNCTION(BlueprintCallable,Category="County") void AddScenery(FVector Position,float Yaw,float Scale);
private:
 UPROPERTY() TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Visuals;
 UPROPERTY() TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Trunks;
 UPROPERTY() bool bTreeTrunks=false;
 UPROPERTY() bool bDistanceLODs=false;
 UPROPERTY() TArray<TObjectPtr<UStaticMesh>> DistanceMeshes;
 UPROPERTY() float EndRange=47000;
 int32 CurrentLOD=-1;
 void UpdateDistanceLOD();
};
