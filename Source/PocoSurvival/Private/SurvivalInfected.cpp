#include "SurvivalInfected.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "SurvivalGameInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
ASurvivalInfected::ASurvivalInfected()
{
    AvatarRole=TEXT("Infected");GetCharacterMovement()->bRunPhysicsWithNoController=true;
}
void ASurvivalInfected::BeginPlay()
{
    Super::BeginPlay();Destination=GetActorLocation();
    if (!PatrolPoints.Num()) { PatrolPoints.Add(Destination);PatrolPoints.Add(Destination+FVector(250,0,0)); }
    if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->ApplyLoadedInfectedState(this);
}
void ASurvivalInfected::Tick(float Delta)
{
    if (auto* Player=Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(this,0))) if (Player->IsCinematicLocked() || Player->bEditingControls) {GetCharacterMovement()->StopMovementImmediately();CancelMelee();return;}
    Super::Tick(Delta);
    if (!IsAlive()) { State=EInfectedState::Dead;return; }
    AlertDelay=FMath::Max(0.f,AlertDelay-Delta);UnseenSeconds+=Delta;AttackDelay=FMath::Max(0.0f,AttackDelay-Delta);ThinkDelay-=Delta;
    if(IsMeleeActive()){GetCharacterMovement()->StopMovementImmediately();return;}
    if (ThinkDelay<=0) { Think(0.2f);ThinkDelay=0.2f; }
    GetCharacterMovement()->MaxWalkSpeed=(State==EInfectedState::Chase ? (Archetype==1?400:Archetype==2?230:290) : 135)*Wounds().WalkScale();
    AddMovementInput(Direction,1,true);
}
void ASurvivalInfected::Think(float Delta)
{
    auto* Player=Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
    if (!Player || !Player->IsAlive()) { Direction=FVector::ZeroVector;return; }
    const FVector Offset=Player->GetActorLocation()-GetActorLocation();const float Distance=Offset.Size2D();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(InfectedSight),false,this);FHitResult Hit;
    const bool Clear=!GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation()+FVector(0,0,60),Player->GetActorLocation()+FVector(0,0,60),ECC_Visibility,Params) || Hit.GetActor()==Player;
    const auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());const auto Climate=Game?Game->WorldClimate():survival::Climate{1,0,0,0};
    const float VisionRadius=(Archetype==2?450.f:1200.f)*(.55f+.45f*Climate.daylight)*(1-.3f*Climate.rain);
    const bool Seen=Distance<VisionRadius && Clear && (FVector::DotProduct(GetActorForwardVector(),Offset.GetSafeNormal2D())>0.20f || State==EInfectedState::Chase || Distance<160);
    const float HearingRadius=Player->bIsCrouched ? 90 : (Player->GetVelocity().Size2D()>400 ? 850 : 330);
    const bool Heard=Clear && Player->GetVelocity().Size2D()>80 && Distance<HearingRadius*(Archetype==2?2.3f:1.f)*(1-.3f*Climate.rain);
    if(Seen&&AlertDelay<=0){AlertDelay=8;for(TActorIterator<ASurvivalInfected> Ally(GetWorld());Ally;++Ally)if(*Ally!=this&&FVector::DistSquared(Ally->GetActorLocation(),GetActorLocation())<FMath::Square(1600.f))Ally->HearNoise(Player->GetActorLocation(),3000);}
    if (Seen || Heard) { LastKnown=Player->GetActorLocation();Destination=LastKnown;UnseenSeconds=0;State=Seen ? EInfectedState::Chase:EInfectedState::Investigate; }
    if (Distance<155 && Clear && UnseenSeconds<1)
    {
        State=EInfectedState::Attack;Direction=FVector::ZeroVector;
        SetActorRotation(FRotator(0,Offset.Rotation().Yaw,0));
        if (AttackDelay<=0) { Attack();AttackDelay=1.35f; }
        return;
    }
    if (UnseenSeconds>14) State=EInfectedState::Patrol;
    else if (UnseenSeconds>1) State=EInfectedState::Investigate;
    if (State==EInfectedState::Patrol && PatrolPoints.Num())
    {
        if (FVector::DistSquared2D(GetActorLocation(),PatrolPoints[PatrolIndex])<FMath::Square(90.0f)) PatrolIndex=(PatrolIndex+1)%PatrolPoints.Num();
        Destination=PatrolPoints[PatrolIndex];
    }
    if(State==EInfectedState::Investigate&&UnseenSeconds>2){const float Angle=UnseenSeconds*1.7f+static_cast<float>(GetTypeHash(PersistentId)%6);Destination=LastKnown+FVector(FMath::Cos(Angle),FMath::Sin(Angle),0)*FMath::Min(500.f,UnseenSeconds*40);}
    if(State==EInfectedState::Chase&&Distance>350&&Archetype==1){const float Side=(GetTypeHash(PersistentId)%2)?1.f:-1.f;const FVector Lateral=FVector::CrossProduct(Offset.GetSafeNormal2D(),FVector::UpVector)*Side*260;Destination=Player->GetActorLocation()+Lateral;}
    Direction=(Destination-GetActorLocation()).GetSafeNormal2D();
    if (FVector::DistSquared2D(Destination,GetActorLocation())<FMath::Square(70.0f)) Direction=FVector::ZeroVector;
    const FVector Start=GetActorLocation();
    if (!Direction.IsNearlyZero() && GetWorld()->SweepSingleByChannel(Hit,Start,Start+Direction*130,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeSphere(38),Params))
    {
        const FVector Left=Direction.RotateAngleAxis(70,FVector::UpVector);
        if (!GetWorld()->SweepSingleByChannel(Hit,Start,Start+Left*130,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeSphere(38),Params)) Direction=Left;
        else Direction=Direction.RotateAngleAxis(-70,FVector::UpVector);
    }
}

bool ASurvivalInfected::RestoreEncounter(const FVector& Location,const FRotator& Rotation,float Health,float Stamina)
{
    if (Location.ContainsNaN() || Location.GetAbsMax()>1000000 || Rotation.ContainsNaN() || !RestoreVitals(Health,Stamina)) return false;
    // Failed collision-aware teleport leaves a safe existing position, never a
    // capsule forced through a wall. Threat state restarts, health/death do not.
    TeleportTo(Location,Rotation,false,false);
    Destination=GetActorLocation();Direction=FVector::ZeroVector;
    UnseenSeconds=100;ThinkDelay=0;AttackDelay=0;PatrolIndex=0;
    State=IsAlive() ? EInfectedState::Patrol : EInfectedState::Dead;
    if (!IsAlive()) {
        GetCharacterMovement()->DisableMovement();
        if (!HasHumanAvatar()) if (auto* Death=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Death/MM_Death_Front_01.MM_Death_Front_01"))) {
            GetMesh()->PlayAnimation(Death,false);GetMesh()->SetPosition(Death->GetPlayLength(),false);
        }
    }
    return true;
}

void ASurvivalInfected::HearNoise(FVector Origin,float Radius)
{
    if (!IsAlive() || Origin.ContainsNaN() || !FMath::IsFinite(Radius) || Radius<=0 || FVector::DistSquared(Origin,GetActorLocation())>FMath::Square(Radius)) return;
    // A visible target is more important than a bottle behind it.
    if (State==EInfectedState::Chase || State==EInfectedState::Attack) return;
    LastKnown=Origin;Destination=Origin;UnseenSeconds=1.2f;State=EInfectedState::Investigate;
}
