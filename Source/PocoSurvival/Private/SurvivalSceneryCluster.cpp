#include "SurvivalSceneryCluster.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
ASurvivalSceneryCluster::ASurvivalSceneryCluster()
{
 SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));RootComponent->SetMobility(EComponentMobility::Static);
 Visuals=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("Vegetation"));Visuals->SetupAttachment(RootComponent);Visuals->SetMobility(EComponentMobility::Static);Visuals->SetCollisionProfileName(TEXT("NoCollision"));
 Trunks=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("TrunkCollision"));Trunks->SetupAttachment(RootComponent);Trunks->SetMobility(EComponentMobility::Static);Trunks->SetCollisionProfileName(TEXT("BlockAll"));Trunks->SetVisibility(false);Trunks->SetHiddenInGame(true);Trunks->SetCastShadow(false);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));Trunks->SetStaticMesh(Cylinder.Object);
}
void ASurvivalSceneryCluster::Configure(UStaticMesh* Mesh,float CullDistance,bool TreeTrunks,bool SolidObjects)
{
 if(!Mesh)return;
 Visuals->SetStaticMesh(Mesh);Visuals->SetCollisionProfileName(SolidObjects?TEXT("BlockAll"):TEXT("NoCollision"));Visuals->SetCullDistances(FMath::Max(1000.f,CullDistance*.85f),FMath::Max(1200.f,CullDistance));
 Visuals->SetCastShadow(TreeTrunks);bTreeTrunks=TreeTrunks;
}
void ASurvivalSceneryCluster::AddScenery(FVector Position,float Yaw,float Scale)
{
 if(Position.ContainsNaN()||!FMath::IsFinite(Yaw)||!FMath::IsFinite(Scale)||Scale<=0||Scale>10)return;
 Visuals->AddInstance(FTransform(FRotator(0,Yaw,0),Position,FVector(Scale)),false);
 if(bTreeTrunks)Trunks->AddInstance(FTransform(FRotator::ZeroRotator,Position+FVector(0,0,130*Scale),FVector(.30f*Scale,.30f*Scale,2.6f*Scale)),false);
}
