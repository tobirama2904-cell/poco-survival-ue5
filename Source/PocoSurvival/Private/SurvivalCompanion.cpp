#include "SurvivalCompanion.h"
#include "SurvivalGameInstance.h"
#include "SurvivalInfected.h"
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
  if(GetWorld()->OverlapBlockingTestByChannel(Spot,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(37,FMath::Max(37.f,GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-1)),Params))continue;
  if(TeleportTo(Spot,Player->GetActorRotation(),false,false)){Last=Spot;return true;}
 }
 return false;
}
void ASurvivalCompanion::Tick(float Delta)
{
 auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());auto* Player=Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
 if(!Game||!Player||Player==this){Super::Tick(Delta);return;}
 if(!RuthRole&&SupportEpoch!=Game->SupportLoadRevision){SupportEpoch=Game->SupportLoadRevision;Aid.Cancel();bAvailable=false;}
 const bool Active=Game->FilmProgress>=(RuthRole?25:18);bSettled=RuthRole&&Game->FilmProgress>=30;
 const FName Role=RuthRole?TEXT("Ruth"):TEXT("Mara");
 // Replace the stationary staging proxies rather than show duplicate people.
 if(!bProxyStateApplied||bProxyActive!=Active){
  for(TActorIterator<AActor> It(GetWorld());It;++It)if(!Cast<ASurvivalCompanion>(*It)&&It->ActorHasTag(Role))It->SetActorHiddenInGame(Active);
  bProxyStateApplied=true;bProxyActive=Active;
 }
 if(!Active){Aid.Cancel();bAvailable=false;bSettled=false;SetActorHiddenInGame(true);SetActorEnableCollision(false);GetCharacterMovement()->DisableMovement();Super::Tick(Delta);return;}
 if(!bAvailable){
  if(!RuthRole&&Game->bMaraHolding&&RestoreHold(Game)){}
  else if(RuthRole&&Game->FilmProgress>=30&&Refuge!=FVector::ZeroVector){if(!TeleportTo(Refuge,FRotator::ZeroRotator,false,false))return;Last=GetActorLocation();}
  else if(!PlaceNear(Player))return;
  bAvailable=true;SetActorHiddenInGame(false);SetActorEnableCollision(true);GetCharacterMovement()->SetMovementMode(MOVE_Walking);
 }
 bConversing=Player->bStoryActive&&!Player->IsBanterPaused()&&(Player->StorySpeaker==(RuthRole?TEXT("Рут"):TEXT("Мара"))||Player->StorySpeaker==(RuthRole?TEXT("Ruth"):TEXT("Mara")));
 Super::Tick(Delta);Travelled+=FVector::Dist2D(Last,GetActorLocation());Last=GetActorLocation();
 if(!RuthRole)UpdateAid(Delta,Player,Game);
 FVector Goal=Player->GetActorLocation()-Player->GetActorForwardVector()*(RuthRole?180:40)+Player->GetActorRightVector()*(RuthRole?115:-115);
 if(!RuthRole&&Game->bMaraHolding)Goal=Game->MaraHoldLocation;
 if(Aid.Active())Goal=Player->GetActorLocation()-Player->GetActorForwardVector()*100;
 if(RuthRole&&Game->FilmProgress>=30){
  if(Refuge!=FVector::ZeroVector)Goal=Refuge;
  bSettled=true;
 }
 FCollisionQueryParams FormationParams(SCENE_QUERY_STAT(CompanionFormation),false,this);FormationParams.AddIgnoredActor(Player);FHitResult FormationBlock;
 if(!bSettled&&!(Game->bMaraHolding&&!RuthRole)&&!Aid.Active()&&GetWorld()->SweepSingleByChannel(FormationBlock,Player->GetActorLocation()+FVector(0,0,20),Goal+FVector(0,0,20),FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(40,survival::CompanionProbeHalf(Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight())),FormationParams))Goal=Player->GetActorLocation()-Player->GetActorForwardVector()*180;
 const float Distance=FVector::Dist2D(Goal,GetActorLocation());
 const bool KneelForAid=Aid.Active()&&FVector::DistSquared2D(GetActorLocation(),Player->GetActorLocation())<FMath::Square(220.f);
 if(!RuthRole&&((Game->bMaraHolding&&!Aid.Active())||KneelForAid||Player->GetCharacterMovement()->IsCrouching()))Crouch();else UnCrouch();
 if(Player->IsCinematicLocked()||!Player->IsAlive()||Distance<(Aid.Active()?35.f:95.f)){GetCharacterMovement()->StopMovementImmediately();Direction=FVector::ZeroVector;return;}
 GetCharacterMovement()->MaxWalkSpeed=RuthRole?190:Distance>450?540:340;
 GetCharacterMovement()->MaxWalkSpeedCrouched=150;
 SteerDelay-=Delta;RecoveryDelay-=Delta;
 if(SteerDelay<=0){
  SteerDelay=.2f;const FVector Desired=(Goal-GetActorLocation()).GetSafeNormal2D();float Best=-10000;Direction=FVector::ZeroVector;
  FCollisionQueryParams Params(SCENE_QUERY_STAT(CompanionSteering),false,this);Params.AddIgnoredActor(Player);
  for(float Angle:{0.f,30.f,-30.f,65.f,-65.f,100.f,-100.f}){
   const FVector Candidate=Desired.RotateAngleAxis(Angle,FVector::UpVector);const FVector Start=GetActorLocation()+FVector(0,0,20),End=Start+Candidate*170;FHitResult Block,Floor;
   if(GetWorld()->SweepSingleByChannel(Block,Start,End,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(40,survival::CompanionProbeHalf(GetCapsuleComponent()->GetScaledCapsuleHalfHeight())),Params))continue;
   if(!GetWorld()->LineTraceSingleByChannel(Floor,End+FVector(0,0,80),End-FVector(0,0,450),ECC_WorldStatic,Params)||Floor.ImpactNormal.Z<.6f)continue;
   const float Score=FVector::DotProduct(Candidate,Desired)-FMath::Abs(Angle)*.001f;if(Score>Best){Best=Score;Direction=Candidate;}
  }
 }
 // Off-screen recovery is an explicit bounded fallback, not global pathfinding.
 if(!bSettled&&!(Game->bMaraHolding&&!RuthRole)&&!Aid.Active()&&Distance>2200&&RecoveryDelay<=0){
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
 Aid.Cancel();bAvailable=false;SetActorHiddenInGame(true);SetActorEnableCollision(false);GetCharacterMovement()->DisableMovement();
}

bool ASurvivalCompanion::ToggleHold(ASurvivalCharacter* Player)
{
 auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());if(!Game||RuthRole||!bAvailable||!Player)return false;
 Aid.Cancel();
 if(Game->bMaraHolding){Game->bMaraHolding=false;Player->StatusMessage=TEXT("Мара идёт за тобой.");}
 else {
  if(!GetCharacterMovement()->IsMovingOnGround())return false;
  Game->bMaraHolding=true;Game->MaraHoldLocation=GetActorLocation()+FVector(0,0,96.f*GetActorScale3D().Z-GetCapsuleComponent()->GetScaledCapsuleHalfHeight());Game->MaraHoldMap=UGameplayStatics::GetCurrentLevelName(this,true);Player->StatusMessage=TEXT("Мара останется здесь. Позвать её можно из панели напарника.");
 }
 if(!Game->SaveProgress())Player->StatusMessage+=TEXT(" Приказ действует, но сохранение сейчас недоступно.");
 return true;
}
bool ASurvivalCompanion::RestoreHold(USurvivalGameInstance* Game)
{
 FHitResult Floor;FCollisionQueryParams Params(SCENE_QUERY_STAT(CompanionHoldRestore),false,this);const FVector P=Game->MaraHoldLocation;
 if(Game->MaraHoldMap==UGameplayStatics::GetCurrentLevelName(this,true)&&GetWorld()->LineTraceSingleByChannel(Floor,P+FVector(0,0,50),P-FVector(0,0,300),ECC_WorldStatic,Params)&&Floor.ImpactNormal.Z>.65f){
  const float Half=GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
  const FVector Spot=Floor.ImpactPoint+FVector(0,0,Half+3);
  if(!GetWorld()->OverlapBlockingTestByChannel(Spot,FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(40,Half),Params)&&TeleportTo(Spot,GetActorRotation(),false,false)){Last=Spot;return true;}
 }
 Game->bMaraHolding=false;return false;
}
bool ASurvivalCompanion::RequestAid(ASurvivalCharacter* Player)
{
 auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());if(!Game||!Player||RuthRole||!bAvailable||Player->IsCinematicLocked()||FVector::DistSquared(GetActorLocation(),Player->GetActorLocation())>FMath::Square(1400.f))return false;
 for(TActorIterator<ASurvivalInfected> It(GetWorld());It;++It)if(It->IsAlive()&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1500.f))return false;
 if(!Aid.Begin(Player->GetHealth(),Player->Wounds(),Game->FieldInventory))return false;
 AidStarted=GetWorld()->GetTimeSeconds();Player->StatusMessage=TEXT("Мара подходит помочь. Остановись; нужен один обычный бинт.");return true;
}
void ASurvivalCompanion::UpdateAid(float Delta,ASurvivalCharacter* Player,USurvivalGameInstance* Game)
{
 if(!Aid.Active())return;
 survival::AidContext Context;Context.near=FVector::DistSquared(GetActorLocation(),Player->GetActorLocation())<FMath::Square(180.f);Context.still=Player->GetVelocity().Size2D()<40&&GetVelocity().Size2D()<40;Context.allowed=!Player->IsCinematicLocked()&&!Player->IsMeleeActive()&&!Player->bJournalOpen&&!Player->bEditingControls;Context.safe=Player->LastImpactTime<=AidStarted;
 for(TActorIterator<ASurvivalInfected> It(GetWorld());It;++It)if(It->IsAlive()&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1500.f))Context.safe=false;
 FCollisionQueryParams Params(SCENE_QUERY_STAT(CompanionAidSight),false,this);Params.AddIgnoredActor(Player);FHitResult Hit;
 Context.clear=!GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation()+FVector(0,0,35),Player->GetActorLocation()+FVector(0,0,35),ECC_Visibility,Params);
 float Health=Player->GetHealth();auto Wounds=Player->Wounds();const auto Result=Aid.Step(Delta,Context,Health,Wounds,Game->FieldInventory);
 if(Result==survival::AidResult::Completed){
  Player->ApplySupportResult(Health,Wounds);const bool Saved=Game->SaveProgress();Player->StatusMessage=Saved?TEXT("Мара остановила кровотечение и помогла перевязаться. Использован один бинт."):TEXT("Перевязка завершена; сохранить прогресс сейчас не удалось.");
 }else if(Result==survival::AidResult::Cancelled&&!Player->bStoryActive)Player->StatusMessage=TEXT("Помощь прервана. Бинт не потрачен.");
}
