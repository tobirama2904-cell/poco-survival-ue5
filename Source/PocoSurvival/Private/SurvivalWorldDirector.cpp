#include "SurvivalWorldDirector.h"
#include "SurvivalGameInstance.h"
#include "SurvivalCharacter.h"
#include "SurvivalInteraction.h"
#include "SurvivalInfected.h"
#include "SurvivalCityGeometry.h"
#include "SurvivalControlSettings.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/StaticMesh.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Sound/SoundBase.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
ASurvivalWorldDirector::ASurvivalWorldDirector()
{
 PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=.1f;
 SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
 Rain=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("LocalRain"));Rain->SetupAttachment(RootComponent);Rain->SetCollisionEnabled(ECollisionEnabled::NoCollision);Rain->SetCastShadow(false);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));Rain->SetStaticMesh(Cube.Object);
}
void ASurvivalWorldDirector::BeginPlay()
{
 Super::BeginPlay();for(TActorIterator<ADirectionalLight> It(GetWorld());It;++It){Sun=*It;break;}
 for(TActorIterator<ASkyLight> It(GetWorld());It;++It){Fill=*It;break;}
 Fog=GetWorld()->SpawnActor<AExponentialHeightFog>();
 for(TActorIterator<AActor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("environment_sky"))){Sky=*It;if(auto* C=It->FindComponentByClass<UStaticMeshComponent>())SkyMaterial=C->CreateDynamicMaterialInstance(0);break;}
 for(TActorIterator<ASurvivalCityGeometry> It(GetWorld());It;++It){TArray<UHierarchicalInstancedStaticMeshComponent*> Parts;It->GetComponents(Parts);for(auto* C:Parts)if(auto* M=C->CreateDynamicMaterialInstance(0))WetMaterials.Add(M);}
 if(auto* M=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Story/Materials/M_Rain.M_Rain")))Rain->SetMaterial(0,M);
 for(int32 I=0;I<128;++I)Rain->AddInstance(FTransform(FVector(0,0,-10000)));Rain->SetVisibility(false);
 if(auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Story/Audio/Rain.Rain")))RainSound=UGameplayStatics::SpawnSound2D(this,Sound,0.0f);
}
void ASurvivalWorldDirector::Tick(float Delta)
{
 Super::Tick(Delta);auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());auto* Player=Cast<ASurvivalCharacter>(UGameplayStatics::GetPlayerPawn(this,0));if(!Game||!Player)return;
 const bool Paused=Player->IsCinematicLocked()||Player->bEditingControls;Game->StepWorldClock(Delta,Paused);
 if(Paused)return;const auto Climate=Game->WorldClimate();EnvironmentTimer-=Delta;StoryTimer-=Delta;
 if(EnvironmentTimer<=0){EnvironmentTimer=1;
  const float Day=Climate.daylight;
  if(Sun){Sun->SetActorRotation(FRotator(-FMath::Max(12.f,Day*72),Game->WorldHour()*15-90,0));auto* Light=Cast<UDirectionalLightComponent>(Sun->GetLightComponent());if(Light){Light->SetIntensity((.10f+Day*2.9f)*(1-Climate.cloud*.60f));Light->SetLightColor(FLinearColor::LerpUsingHSV(FLinearColor(.40,.55,.95),FLinearColor(1,.87,.69),FMath::Min(1.f,Day*3)));}}
  if(Fill)Fill->GetLightComponent()->SetIntensity(.13f+Day*.67f);
  if(Fog){auto* C=Fog->GetComponent();C->SetFogDensity(.003f+Climate.fog*.025f);C->SetFogInscatteringColor(FLinearColor::LerpUsingHSV(FLinearColor(.025,.04,.065),FLinearColor(.32,.38,.40),Day));C->SetStartDistance(1500);}
  if(Sky)Sky->SetActorLocation(Player->GetActorLocation());
  if(SkyMaterial)SkyMaterial->SetVectorParameterValue(TEXT("SkyColor"),FLinearColor::LerpUsingHSV(FLinearColor(.004,.009,.025),FLinearColor(.12,.22,.36),FMath::Min(1.f,Day*2))*(1-Climate.cloud*.4f));
  for(const auto& M:WetMaterials)if(M)M->SetScalarParameterValue(TEXT("Wetness"),Climate.rain);
  FHitResult Shelter;FCollisionQueryParams Params(SCENE_QUERY_STAT(RainShelter),false,Player);Params.AddIgnoredActor(this);
  bSheltered=GetWorld()->LineTraceSingleByChannel(Shelter,Player->GetActorLocation()+FVector(0,0,80),Player->GetActorLocation()+FVector(0,0,2500),ECC_Visibility,Params);
  if(RainSound)RainSound->SetVolumeMultiplier(Climate.rain*(bSheltered?.055f:.18f));
 }
 const int32 Count=bSheltered?0:FMath::RoundToInt(Climate.rain*(USurvivalControlSettings::Get()->bPerformanceMode?64:128));Rain->SetVisibility(Count>0);RainPhase=FMath::Fmod(RainPhase+Delta*1000,1600.f);
 if(Count>0){const FVector Origin=Player->GetActorLocation();for(int32 I=0;I<128;++I){const float X=static_cast<float>((I*317)%1600)-800,Y=static_cast<float>((I*593)%1600)-800,Z=FMath::Fmod(I*73.f+1600-RainPhase,1600.f);const FVector P=I<Count?Origin+FVector(X,Y,Z):Origin-FVector(0,0,10000);Rain->UpdateInstanceTransform(I,FTransform(FRotator(0,0,-12),P,FVector(.013,.013,.85)),true,I==127,true);}}
 if(StoryTimer<=0&&GetWorld()->GetTimeSeconds()>12){StoryTimer=.5f;AdvanceStory(Player,Game);}
}
void ASurvivalWorldDirector::AdvanceStory(ASurvivalCharacter* Player,USurvivalGameInstance* Game)
{
 if(!Player->IsAlive()||Player->bStoryActive||Player->bJournalOpen||Player->bEditingControls||!Player->GetCharacterMovement()->IsMovingOnGround())return;
 const auto Objectives=Game->GetObjectives();
 for(const auto& Objective:Objectives){if(!Objective.bAvailable)continue;
  const bool Radio=Objective.Id==TEXT("meet_dispatch")||Objective.Id==TEXT("radio_brother");const bool Person=Objective.Id==TEXT("meet_doctor")||Objective.Id==TEXT("speak_guard");if(!Radio&&!Person)continue;
  for(TActorIterator<ASurvivalInteraction> It(GetWorld());It;++It)if(It->ActionId==Objective.Id&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(Radio?450.f:280.f)){
   if(Person){if(Player->GetVelocity().Size2D()>40)continue;bool Threat=false;for(TActorIterator<ASurvivalInfected> Enemy(GetWorld());Enemy;++Enemy)if(Enemy->IsAlive()&&FVector::DistSquared(Enemy->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1600.f)){Threat=true;break;}if(Threat)continue;}
   FCollisionQueryParams Params(SCENE_QUERY_STAT(StoryTriggerSight),false,Player);FHitResult Hit;const FVector Start=Player->GetActorLocation()+FVector(0,0,50);
   if(GetWorld()->LineTraceSingleByChannel(Hit,Start,It->GetActorLocation()+FVector(0,0,50),ECC_Visibility,Params)&&Hit.GetActor()!=*It)continue;
   FString Error;if(Game->TryAction(Objective.Id,Error)){Player->BeginStory(Objective.Id,*It,Person);Player->Save();}return;
  }
 }
}
FString ASurvivalWorldDirector::Chapter(USurvivalGameInstance* G)
{
 if(!G)return TEXT("Нижний Берег");
 if(G->HasWorldFlag(TEXT("campaign_resolution")))return TEXT("ПОСЛЕ РАССВЕТА");
 if(G->HasWorldFlag(TEXT("brother_rescued")))return TEXT("V • НАЗЫВАТЬ ИМЕНА");
 if(G->HasWorldFlag(TEXT("clean_water")))return TEXT("IV • ЗНАКОМЫЙ СТУК");
 if(G->HasWorldFlag(TEXT("logbook_found")))return TEXT("III • ЧТО ОСТАЛОСЬ ВНИЗУ");
 if(G->HasWorldFlag(TEXT("medical_plan")))return TEXT("II • ТЕ, КТО ОСТАЛСЯ");
 return TEXT("I • ВОЗВРАЩЕНИЕ");
}
FString ASurvivalWorldDirector::Intention(USurvivalGameInstance* G)
{
 if(!G)return TEXT("");if(G->HasWorldFlag(TEXT("campaign_resolution")))return TEXT("Можно остаться. Незаконченные истории не исчезли.");
 if(G->HasWorldFlag(TEXT("brother_rescued")))return TEXT("Ильяс найден. Теперь решить, что делать с правдой — и с живыми.");
 if(G->HasWorldFlag(TEXT("clean_water")))return TEXT("На вышке ответил знакомый голос. Не включать прожекторы.");
 if(G->HasWorldFlag(TEXT("logbook_found")))return TEXT("В журнале есть имя брата. И след того, что скрыли от города.");
 if(G->HasWorldFlag(TEXT("medical_plan")))return TEXT("Наргис видела Ильяса. Вода и закрытые шлюзы связаны с его исчезновением.");
 return TEXT("Арсен вернулся за братом. В депо ещё работает радио.");
}
