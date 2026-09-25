#include "SurvivalCityGeometry.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
ASurvivalCityGeometry::ASurvivalCityGeometry()
{
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
    RootComponent->SetMobility(EComponentMobility::Static);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    for (int32 I=0;I<6;++I) {
        auto* C=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(*FString::Printf(TEXT("Surface%d"),I));
        C->SetupAttachment(RootComponent);C->SetMobility(EComponentMobility::Static);C->SetStaticMesh(Cube.Object);
        C->SetCollisionProfileName(I==3?TEXT("NoCollision"):TEXT("BlockAll"));
        const FString Path=FString::Printf(TEXT("/Game/Story/Materials/M_City%d.M_City%d"),I,I);
        if (auto* M=LoadObject<UMaterialInterface>(nullptr,*Path)) C->SetMaterial(0,M);
        C->SetCullDistances(0,I==3?22000:75000);Surfaces.Add(C);
    }
}
void ASurvivalCityGeometry::AddBox(FVector Center,FVector Size,int32 Surface)
{
    if (!Surfaces.IsValidIndex(Surface) || Size.GetMin()<=0) return;
    Surfaces[Surface]->AddInstance(FTransform(FQuat::Identity,Center,Size/100),false);
}
