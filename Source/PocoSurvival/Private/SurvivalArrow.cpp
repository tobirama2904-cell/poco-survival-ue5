#include "SurvivalArrow.h"
#include "SurvivalInfected.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "GameFramework/DamageType.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
ASurvivalArrow::ASurvivalArrow(){
 Collision=CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));SetRootComponent(Collision);Collision->InitSphereRadius(2);Collision->SetCollisionProfileName(TEXT("BlockAllDynamic"));Collision->OnComponentHit.AddDynamic(this,&ASurvivalArrow::Impact);
 Shaft=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Arrow"));Shaft->SetupAttachment(Collision);Shaft->SetCollisionEnabled(ECollisionEnabled::NoCollision);

 Movement=CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("Flight"));Movement->SetUpdatedComponent(Collision);Movement->bRotationFollowsVelocity=true;Movement->ProjectileGravityScale=.6f;Movement->bForceSubStepping=true;Movement->MaxSimulationTimeStep=.025f;InitialLifeSpan=25;
}
void ASurvivalArrow::Launch(FVector Direction,float Power,AController* Shooter){Shaft->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Story/Props/Arrow.Arrow")));ShooterController=Shooter;Damage=35+Power*45;Movement->Velocity=Direction.GetSafeNormal()*(2200+Power*4200);if(GetOwner())Collision->IgnoreActorWhenMoving(GetOwner(),true);}
void ASurvivalArrow::Impact(UPrimitiveComponent* Component,AActor* Other,UPrimitiveComponent* OtherComponent,FVector Normal,const FHitResult& Hit){
 if(bLanded||Other==GetOwner())return;bLanded=true;const FVector Direction=GetActorForwardVector();Movement->StopMovementImmediately();Collision->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 if(auto* Enemy=Cast<ASurvivalInfected>(Other)){UGameplayStatics::ApplyPointDamage(Enemy,Damage,Direction,Hit,ShooterController,this,UDamageType::StaticClass());if(OtherComponent)AttachToComponent(OtherComponent,FAttachmentTransformRules::KeepWorldTransform,Hit.BoneName);}
}
