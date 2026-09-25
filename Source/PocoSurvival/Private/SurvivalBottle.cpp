#include "SurvivalBottle.h"
#include "SurvivalInfected.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Sound/SoundBase.h"
#include "Kismet/GameplayStatics.h"
ASurvivalBottle::ASurvivalBottle()
{
    Physics=CreateDefaultSubobject<USphereComponent>(TEXT("Physics"));SetRootComponent(Physics);Physics->InitSphereRadius(5);Physics->SetCollisionProfileName(TEXT("PhysicsActor"));Physics->SetSimulatePhysics(true);Physics->SetNotifyRigidBodyCollision(true);
    Physics->OnComponentHit.AddDynamic(this,&ASurvivalBottle::Impact);
    Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Bottle"));Visual->SetupAttachment(Physics);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    InitialLifeSpan=8;
}
void ASurvivalBottle::Launch(FVector Velocity)
{
    Visual->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Story/Props/Bottle.Bottle")));Physics->SetPhysicsLinearVelocity(Velocity);
}
void ASurvivalBottle::Impact(UPrimitiveComponent* HitComponent,AActor* OtherActor,UPrimitiveComponent* OtherComponent,FVector Impulse,const FHitResult& Hit)
{
    if (bBroken || !OtherActor || OtherActor==this) return;bBroken=true;
    for (TActorIterator<ASurvivalInfected> It(GetWorld());It;++It) It->HearNoise(Hit.ImpactPoint,2200);
    if (auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Story/Audio/Glass.Glass"))) UGameplayStatics::PlaySoundAtLocation(this,Sound,Hit.ImpactPoint,.8f);
    Destroy();
}
