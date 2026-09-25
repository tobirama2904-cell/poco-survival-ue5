#include "SurvivalCompanion.h"
#include "SurvivalGameInstance.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
ASurvivalCompanion::ASurvivalCompanion()
{
 AvatarRole=TEXT("Leyla");
 GetCharacterMovement()->bRunPhysicsWithNoController=true;
 GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Pawn,ECR_Ignore);
 GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore);
}
void ASurvivalCompanion::BeginPlay()
{
 AvatarRole=RuthRole?TEXT("Nargis"):TEXT("Leyla");Super::BeginPlay();
 Tags.AddUnique(FName(TEXT("american_cast")));Tags.AddUnique(FName(RuthRole?TEXT("Ruth"):TEXT("Mara")));
 for(TActorIterator<AActor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("main_refuge"))){Refuge=It->GetActorLocation();break;}
 SetActorHiddenInGame(true);SetActorEnableCollision(false);GetCharacterMovement()->DisableMovement();Last=GetActorLocation();
}
bool ASurvivalCompanion::PlaceNear(ASurvivalCharacter* Player)
{
 FCollisionQueryParams Params(SCENE_QUERY_STAT(CompanionRejoin),false,this);Params.AddIgnoredActor(Player);
 for(float Angle:{150.f,-150.f,180.f,90.f,-90.f,45.f,-45.f}){
  const FVector Offset=Player->GetActorForwardVector().RotateAngleAxis(Angle,FVector::UpVector)*(RuthRole?240:190);
  const FVector P=Player->GetActorLocation()+Offset;FHitResult Floor;
  if(!GetWorld()->LineTraceSingleByChannel(Floor,P+FVector(0,0,80),P-FVector(0,0,450),ECC_WorldStatic,Params)||Floor.ImpactNormal.Z<.65f)continue;
  const FVector Spot=Floor.ImpactPoint+FVector(0,0,GetCapsuleComponent()->GetScaledCapsuleHalfHeight()+3);
  if(GetWorld()->OverlapBlockingTestByChannel(Spot,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(37,95),Params))continue;
  if(TeleportTo(Spot,Player->GetActorRotation(),false,false)){Last=Spot;return true;}
 }
 return false;
}
void ASurvivalCompanion::Tick(float Delta)
{
 auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());auto* Player=Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
 if(!Game||!Player||Player==this){Super::Tick(Delta);return;}
 const bool Active=Game->FilmProgress>=(RuthRole?25:18);bSettled=RuthRole&&Game->FilmProgress>=30;
 const FName Role=RuthRole?TEXT("Ruth"):TEXT("Mara");
 // Replace the stationary staging proxies rather than show duplicate people.
 if(!bProxyStateApplied||bProxyActive!=Active){
  for(TActorIterator<AActor> It(GetWorld());It;++It)if(!Cast<ASurvivalCompanion>(*It)&&It->ActorHasTag(Role))It->SetActorHiddenInGame(Active);
  bProxyStateApplied=true;bProxyActive=Active;
 }
 if(!Active){bAvailable=false;bSettled=false;SetActorHiddenInGame(true);SetActorEnableCollision(false);GetCharacterMovement()->DisableMovement();Super::Tick(Delta);return;}
 if(!bAvailable){
  if(RuthRole&&Game->FilmProgress>=30&&Refuge!=FVector::ZeroVector){if(!TeleportTo(Refuge,FRotator::ZeroRotator,false,false))return;Last=GetActorLocation();}
  else if(!PlaceNear(Player))return;
  bAvailable=true;SetActorHiddenInGame(false);SetActorEnableCollision(true);GetCharacterMovement()->SetMovementMode(MOVE_Walking);
 }
 bConversing=Player->bStoryActive&&!Player->IsBanterPaused()&&(Player->StorySpeaker==(RuthRole?TEXT("Рут"):TEXT("Мара"))||Player->StorySpeaker==(RuthRole?TEXT("Ruth"):TEXT("Mara")));
 Super::Tick(Delta);Travelled+=FVector::Dist2D(Last,GetActorLocation());Last=GetActorLocation();
 FVector Goal=Player->GetActorLocation()-Player->GetActorForwardVector()*(RuthRole?180:40)+Player->GetActorRightVector()*(RuthRole?115:-115);
 if(RuthRole&&Game->FilmProgress>=30){
  if(Refuge!=FVector::ZeroVector)Goal=Refuge;
  bSettled=true;
 }
 FCollisionQueryParams FormationParams(SCENE_QUERY_STAT(CompanionFormation),false,this);FormationParams.AddIgnoredActor(Player);FHitResult FormationBlock;
 if(!bSettled&&GetWorld()->SweepSingleByChannel(FormationBlock,Player->GetActorLocation()+FVector(0,0,20),Goal+FVector(0,0,20),FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(35,70),FormationParams))Goal=Player->GetActorLocation()-Player->GetActorForwardVector()*180;
 const float Distance=FVector::Dist2D(Goal,GetActorLocation());
 if(Player->IsCinematicLocked()||!Player->IsAlive()||Distance<95){GetCharacterMovement()->StopMovementImmediately();Direction=FVector::ZeroVector;return;}
 if(Player->GetCharacterMovement()->IsCrouching()&&!RuthRole)Crouch();else UnCrouch();
 GetCharacterMovement()->MaxWalkSpeed=RuthRole?190:Distance>450?540:340;
 GetCharacterMovement()->MaxWalkSpeedCrouched=150;
 SteerDelay-=Delta;RecoveryDelay-=Delta;
 if(SteerDelay<=0){
  SteerDelay=.2f;const FVector Desired=(Goal-GetActorLocation()).GetSafeNormal2D();float Best=-10000;Direction=FVector::ZeroVector;
  FCollisionQueryParams Params(SCENE_QUERY_STAT(CompanionSteering),false,this);Params.AddIgnoredActor(Player);
  for(float Angle:{0.f,30.f,-30.f,65.f,-65.f,100.f,-100.f}){
   const FVector Candidate=Desired.RotateAngleAxis(Angle,FVector::UpVector);const FVector Start=GetActorLocation()+FVector(0,0,20),End=Start+Candidate*170;FHitResult Block,Floor;
   if(GetWorld()->SweepSingleByChannel(Block,Start,End,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(35,70),Params))continue;
   if(!GetWorld()->LineTraceSingleByChannel(Floor,End+FVector(0,0,80),End-FVector(0,0,450),ECC_WorldStatic,Params)||Floor.ImpactNormal.Z<.6f)continue;
   const float Score=FVector::DotProduct(Candidate,Desired)-FMath::Abs(Angle)*.001f;if(Score>Best){Best=Score;Direction=Candidate;}
  }
 }
 // Off-screen recovery is an explicit bounded fallback, not global pathfinding.
 if(!bSettled&&Distance>2200&&RecoveryDelay<=0){
  RecoveryDelay=3;auto* PC=Cast<APlayerController>(Player->GetController());FVector2D Screen;int32 W=0,H=0;if(PC)PC->GetViewportSize(W,H);
  const bool OnScreen=PC&&PC->ProjectWorldLocationToScreen(GetActorLocation(),Screen,true)&&Screen.X>-150&&Screen.Y>-150&&Screen.X<W+150&&Screen.Y<H+150;
  FHitResult Block;FCollisionQueryParams Params(SCENE_QUERY_STAT(CompanionOcclusion),false,this);Params.AddIgnoredActor(Player);
  const bool Occluded=GetWorld()->LineTraceSingleByChannel(Block,Player->GetActorLocation()+FVector(0,0,60),GetActorLocation()+FVector(0,0,60),ECC_Visibility,Params);
  if(!OnScreen&&(Occluded||Distance>4500))PlaceNear(Player);
 }
 if(!Direction.IsNearlyZero())AddMovementInput(Direction,1,true);
}

void ASurvivalCompanion::FellOutOfWorld(const UDamageType&)
{
 bAvailable=false;SetActorHiddenInGame(true);SetActorEnableCollision(false);GetCharacterMovement()->DisableMovement();
}
