#include "SurvivalSceneryCluster.h"
#include "Core/SceneryLOD.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/Pawn.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
ASurvivalSceneryCluster::ASurvivalSceneryCluster()
{
 PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.bStartWithTickEnabled=false;PrimaryActorTick.TickInterval=.4f;
 SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));RootComponent->SetMobility(EComponentMobility::Static);
 Visuals=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("Vegetation"));Visuals->SetupAttachment(RootComponent);Visuals->SetMobility(EComponentMobility::Static);Visuals->SetCollisionProfileName(TEXT("NoCollision"));
 Trunks=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("TrunkCollision"));Trunks->SetupAttachment(RootComponent);Trunks->SetMobility(EComponentMobility::Static);Trunks->SetCollisionProfileName(TEXT("BlockAll"));Trunks->SetVisibility(false);Trunks->SetHiddenInGame(true);Trunks->SetCastShadow(false);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));Trunks->SetStaticMesh(Cylinder.Object);
}
void ASurvivalSceneryCluster::Configure(UStaticMesh* Mesh,float CullDistance,bool TreeTrunks,bool SolidObjects)
{
 if(!Mesh)return;
 EndRange=FMath::Max(20000.f,CullDistance);
 Visuals->SetStaticMesh(Mesh);Visuals->SetCollisionProfileName(SolidObjects?TEXT("BlockAll"):TEXT("NoCollision"));Visuals->SetCullDistances(FMath::Max(1000.f,CullDistance*.85f),FMath::Max(1200.f,CullDistance));
 Visuals->SetCastShadow(TreeTrunks);bTreeTrunks=TreeTrunks;
}
void ASurvivalSceneryCluster::AddScenery(FVector Position,float Yaw,float Scale)
{
 if(Position.ContainsNaN()||!FMath::IsFinite(Yaw)||!FMath::IsFinite(Scale)||Scale<=0||Scale>10)return;
 Visuals->AddInstance(FTransform(FRotator(0,Yaw,0),Position,FVector(Scale)),false);
 if(bTreeTrunks)Trunks->AddInstance(FTransform(FRotator::ZeroRotator,Position+FVector(0,0,130*Scale),FVector(.30f*Scale,.30f*Scale,2.6f*Scale)),false);
}

void ASurvivalSceneryCluster::ConfigureDistanceLevels(UStaticMesh* NearMesh,UStaticMesh* MidMesh,UStaticMesh* FarMesh)
{
 if(!NearMesh||!MidMesh||!FarMesh||!bTreeTrunks)return;
 DistanceMeshes={NearMesh,MidMesh,FarMesh};bDistanceLODs=true;
 // Runtime mesh swaps affect visuals only. Static trunk blockers never change.
 Visuals->SetMobility(EComponentMobility::Movable);
}
void ASurvivalSceneryCluster::BeginPlay()
{
 Super::BeginPlay();SetActorTickEnabled(bDistanceLODs);if(bDistanceLODs){Visuals->SetVisibility(false);UpdateDistanceLOD();}
}
void ASurvivalSceneryCluster::Tick(float Delta)
{
 Super::Tick(Delta);if(bDistanceLODs)UpdateDistanceLOD();
}
void ASurvivalSceneryCluster::UpdateDistanceLOD()
{
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);if(!Player||DistanceMeshes.Num()!=3)return;
 survival::SceneryLODPolicy Policy;Policy.endRange=EndRange;
 const int32 LOD=Policy.Choose(FVector::Dist2D(GetActorLocation(),Player->GetActorLocation()),CurrentLOD);
 if(LOD==CurrentLOD)return;CurrentLOD=LOD;
 if(LOD==3){Visuals->SetVisibility(false);return;}
 Visuals->SetStaticMesh(DistanceMeshes[LOD]);Visuals->SetCastShadow(LOD==0);Visuals->SetVisibility(true);
}
