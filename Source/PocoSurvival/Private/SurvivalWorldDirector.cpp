#include "SurvivalWorldDirector.h"
#include "Core/AmericanStory.h"
#include "SurvivalGameInstance.h"
#include "SurvivalCharacter.h"
#include "SurvivalCompanion.h"
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
#include "Components/PointLightComponent.h"
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
 FloodWater=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FloodWater"));FloodWater->SetupAttachment(RootComponent);FloodWater->SetCollisionEnabled(ECollisionEnabled::NoCollision);FloodWater->SetCastShadow(false);
 Rain=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("LocalRain"));Rain->SetupAttachment(RootComponent);Rain->SetCollisionEnabled(ECollisionEnabled::NoCollision);Rain->SetCastShadow(false);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));Rain->SetStaticMesh(Cube.Object);FloodWater->SetStaticMesh(Cube.Object);FloodWater->SetRelativeLocation(FVector(-15000,11000,35));FloodWater->SetRelativeScale3D(FVector(140,120,.1));FloodWater->SetVisibility(false);
}
void ASurvivalWorldDirector::BeginPlay()
{
 Super::BeginPlay();
 if(auto* M=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Story/Materials/M_City3.M_City3")))FloodWater->SetMaterial(0,M);
 for(const TCHAR* Name:{TEXT("ScoreExplore"),TEXT("ScoreStealth"),TEXT("ScoreCombat"),TEXT("ScoreMemory")}){const FString P=FString(TEXT("/Game/Story/Audio/"))+Name+TEXT(".")+Name;auto* W=LoadObject<USoundBase>(nullptr,*P);Score.Add(W?UGameplayStatics::SpawnSound2D(this,W,0):nullptr);}
 for(TActorIterator<ADirectionalLight> It(GetWorld());It;++It){Sun=*It;break;}
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
 MixScore(Player,Delta);FloodWater->SetVisibility(Game->FilmDecision==1);
 const bool Paused=Player->IsCinematicLocked()||Player->bEditingControls;Game->StepWorldClock(Delta,Paused);
 if(Paused)return;const auto Climate=Game->WorldClimate();EnvironmentTimer-=Delta;StoryTimer-=Delta;
 if(EnvironmentTimer<=0){EnvironmentTimer=1;
  for(TActorIterator<AActor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("county_story_lamp"))){
   for(int32 I=0;I<survival::CountyState::Count;++I)if(It->ActorHasTag(FName(*FString::Printf(TEXT("county_arc_%d"),I))))if(auto* Light=It->FindComponentByClass<UPointLightComponent>())Light->SetVisibility(Game->County.stages[I]==3);
  }
  for(TActorIterator<AActor> It(GetWorld());It;++It){
   if(It->ActorHasTag(TEXT("main_route_barrier"))){const bool Open=Game->MainStory.Has(8);It->SetActorHiddenInGame(Open);It->SetActorEnableCollision(!Open);}
   if(It->ActorHasTag(TEXT("main_repair_spares"))){const bool Taken=Game->MainStory.spareRecovered||Game->MainStory.Has(1);It->SetActorHiddenInGame(Taken);It->SetActorEnableCollision(!Taken);}
   if(It->ActorHasTag(TEXT("main_medical_pack"))){const bool Taken=Game->MainStory.Has(2);It->SetActorHiddenInGame(Taken);It->SetActorEnableCollision(!Taken);}
   if(It->ActorHasTag(TEXT("main_refuge_lamp")))if(auto* L=It->FindComponentByClass<UPointLightComponent>())L->SetVisibility(Game->MainStory.Has(16));
  }
  const float Day=Climate.daylight;
  if(Sun){Sun->SetActorRotation(FRotator(-FMath::Max(12.f,Day*72),Game->WorldHour()*15-90,0));auto* Light=Cast<UDirectionalLightComponent>(Sun->GetLightComponent());if(Light){Light->SetIntensity((.16f+FMath::Sqrt(Day)*2.65f)*(1-Climate.cloud*.60f));Light->SetLightColor(FLinearColor::LerpUsingHSV(FLinearColor(.40,.55,.95),FLinearColor(1,.87,.69),FMath::Min(1.f,Day*3)));}}
  if(Fill)Fill->GetLightComponent()->SetIntensity(.55f+FMath::Sqrt(Day)*2.15f);
  if(Fog){auto* C=Fog->GetComponent();C->SetFogDensity(.003f+Climate.fog*.025f);C->SetFogInscatteringColor(FLinearColor::LerpUsingHSV(FLinearColor(.025,.04,.065),FLinearColor(.32,.38,.40),Day));C->SetStartDistance(1500);}
  if(Sky)Sky->SetActorLocation(Player->GetActorLocation());
  if(SkyMaterial)SkyMaterial->SetVectorParameterValue(TEXT("SkyColor"),FLinearColor::LerpUsingHSV(FLinearColor(.016,.028,.06),FLinearColor(1,.98,.94),FMath::Min(1.f,Day*2))*(1-Climate.cloud*.4f));
  for(const auto& M:WetMaterials)if(M)M->SetScalarParameterValue(TEXT("Wetness"),Climate.rain);
  FHitResult Shelter;FCollisionQueryParams Params(SCENE_QUERY_STAT(RainShelter),false,Player);Params.AddIgnoredActor(this);
  bSheltered=GetWorld()->LineTraceSingleByChannel(Shelter,Player->GetActorLocation()+FVector(0,0,80),Player->GetActorLocation()+FVector(0,0,2500),ECC_Visibility,Params);
  if(RainSound)RainSound->SetVolumeMultiplier(Climate.rain*(bSheltered?.055f:.18f));
 }
 const int32 Count=bSheltered?0:FMath::RoundToInt(Climate.rain*(USurvivalControlSettings::Get()->bPerformanceMode?64:128));Rain->SetVisibility(Count>0);RainPhase=FMath::Fmod(RainPhase+Delta*1000,1600.f);
 if(Count>0){const FVector Origin=Player->GetActorLocation();for(int32 I=0;I<128;++I){const float X=static_cast<float>((I*317)%1600)-800,Y=static_cast<float>((I*593)%1600)-800,Z=FMath::Fmod(I*73.f+1600-RainPhase,1600.f);const FVector P=I<Count?Origin+FVector(X,Y,Z):Origin-FVector(0,0,10000);Rain->UpdateInstanceTransform(I,FTransform(FRotator(0,0,-12),P,FVector(.013,.013,.85)),true,I==127,true);}}
 if(StoryTimer<=0&&GetWorld()->GetTimeSeconds()>12){StoryTimer=.5f;AdvanceStory(Player,Game);}
 TryJourneyConversation(Player,Game,Delta);
}
void ASurvivalWorldDirector::AdvanceStory(ASurvivalCharacter* Player,USurvivalGameInstance* Game)
{
 if(!Player->IsAlive()||Player->bStoryActive||Player->bJournalOpen||Player->bEditingControls||!Player->GetCharacterMovement()->IsMovingOnGround())return;
 const auto& Scenes=survival::FilmScenes();if(Game->FilmProgress<0||Game->FilmProgress>=static_cast<int32>(Scenes.size()))return;const auto& Scene=Scenes[Game->FilmProgress];
 const FVector Target(Scene.x*100,Scene.y*100,Scene.z*100);
 if(!Game->MainStory.Has(Scene.requiredEvents))return;
 if(Scene.escort>0){bool Near=false;for(TActorIterator<ASurvivalCompanion> Friend(GetWorld());Friend;++Friend)if(Friend->RuthRole==(Scene.escort==2)&&Friend->IsAvailable()&&FVector::DistSquared2D(Friend->GetActorLocation(),Player->GetActorLocation())<FMath::Square(950.f))Near=true;if(!Near)return;}

 if(FVector::DistSquared2D(Target,Player->GetActorLocation())>FMath::Square(480.f))return;
 if(Scene.gate==1&&Game->FieldInventory.Get(survival::Supply::Bow)==0){Player->StatusMessage=TEXT("Возьми снаряжение из ящика у лестницы депо.");return;}
 if(Scene.gate==2&&Game->FilmDecision==0){Player->StatusMessage=TEXT("Красный рычаг: открыть канал. Синий: удержать затвор.");return;}
 for(TActorIterator<ASurvivalInfected> Enemy(GetWorld());Enemy;++Enemy)if(Enemy->IsAlive()&&FVector::DistSquared(Enemy->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1300.f))return;
 AActor* Speaker=nullptr;float Best=FMath::Square(1200.f);for(TActorIterator<AActor> It(GetWorld());It;++It)if(!It->IsHidden()&&It->ActorHasTag(TEXT("american_cast"))&&(Scene.focus.empty()||It->ActorHasTag(FName(UTF8_TO_TCHAR(Scene.focus.c_str()))))){const float D=FVector::DistSquared(It->GetActorLocation(),Target);if(D<Best){Best=D;Speaker=*It;}}
 Player->BeginFilm(Game->FilmProgress,Speaker);

}
FString ASurvivalWorldDirector::Chapter(USurvivalGameInstance* G){if(!G)return TEXT("Беллуэзер");const auto& S=survival::FilmScenes();return G->FilmProgress<static_cast<int32>(S.size())?UTF8_TO_TCHAR(S[G->FilmProgress].title.c_str()):TEXT("БЕЛЛУЭЗЕР • ПОСЛЕ НАВОДНЕНИЯ");}
FString ASurvivalWorldDirector::Intention(USurvivalGameInstance* G)
{
 if(!G)return TEXT("");const auto& Scenes=survival::FilmScenes();const bool English=USurvivalControlSettings::Get()->bEnglishStory;
 if(G->FilmProgress>=0&&G->FilmProgress<static_cast<int32>(Scenes.size())){
  const auto& S=Scenes[G->FilmProgress];
  if(S.escort>0&&G->MainStory.Has(S.requiredEvents))if(auto* Player=UGameplayStatics::GetPlayerPawn(G,0)){
   bool Near=false;for(TActorIterator<ASurvivalCompanion> Friend(G->GetWorld());Friend;++Friend)if(Friend->RuthRole==(S.escort==2)&&Friend->IsAvailable()&&FVector::DistSquared2D(Friend->GetActorLocation(),Player->GetActorLocation())<FMath::Square(950.f))Near=true;
   if(!Near)return English?(S.escort==2?TEXT("Wait for Ruth somewhere safe. Stay close to her."):TEXT("Wait for Mara somewhere safe.")):(S.escort==2?TEXT("Дождитесь Рут в безопасном месте. Не уходите далеко."):TEXT("Дождитесь Мары в безопасном месте."));
  }
  return UTF8_TO_TCHAR((English?S.intentEn:S.intentRu).c_str());
 }
 return English?TEXT("Bellwether stays open. The orchard shelter remains available."):TEXT("Беллуэзер открыт для исследования. Убежище в саду остаётся доступным.");
}


void ASurvivalWorldDirector::MixScore(ASurvivalCharacter* Player,float Delta){
 int32 Mode=-1;bool Threat=false,Fight=false;
 for(TActorIterator<ASurvivalInfected> It(GetWorld());It;++It)if(It->IsAlive()&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1900.f)){Threat=true;Fight|=It->State==EInfectedState::Chase||It->State==EInfectedState::Attack;}
 bool AidBusy=false;for(TActorIterator<ASurvivalCompanion> It(GetWorld());It;++It)if(It->IsHelping())AidBusy=true;
 Player->PauseBanter((Fight||AidBusy||(Threat&&Player->IsJourneyConversation()))&&!Player->IsCinematicLocked());
 const float Cycle=FMath::Fmod(GetWorld()->GetTimeSeconds(),160.f);if(Fight&&!Player->IsCinematicLocked())Mode=2;else if(Player->bStoryActive&&!Player->IsJourneyConversation())Mode=3;else if(Threat)Mode=1;else if(!Player->IsJourneyConversation()&&Cycle<42)Mode=0;
 if(Player->bEditingControls||!Player->IsAlive())Mode=-1;
 for(int32 I=0;I<Score.Num();++I){const float Target=I==Mode?(Player->bStoryActive?.10f:.20f):0;ScoreLevels[I]=FMath::FInterpTo(ScoreLevels[I],Target,Delta,.6f);if(Score[I])Score[I]->SetVolumeMultiplier(ScoreLevels[I]);}
}

void ASurvivalWorldDirector::TryJourneyConversation(ASurvivalCharacter* Player,USurvivalGameInstance* Game,float Delta)
{
 JourneyDelay=FMath::Max(0.f,JourneyDelay-Delta);
 const bool Walking=Player->GetVelocity().Size2D()>30;
 RestSeconds=Walking?0:RestSeconds+Delta;
 if(Player->bStoryActive){JourneyDelay=FMath::Max(JourneyDelay,75.f);return;}
 if(JourneyDelay>0||!Player->IsAlive()||Player->bJournalOpen||Player->bEditingControls||Player->bAiming||!Player->GetCharacterMovement()->IsMovingOnGround())return;
 const auto& Film=survival::FilmScenes();if(Game->FilmProgress>=0&&Game->FilmProgress<static_cast<int32>(Film.size())){
  const auto& Next=Film[Game->FilmProgress];if(FVector::DistSquared2D(Player->GetActorLocation(),FVector(Next.x*100,Next.y*100,0))<FMath::Square(1800.f))return;
 }
 bool Nearby=false;for(TActorIterator<ASurvivalCompanion> It(GetWorld());It;++It)if(!It->RuthRole&&!It->IsHidden()&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(800.f)){if(It->IsHelping())return;Nearby=true;break;}
 if(!Nearby)return;
 // Carrying Ruth's emergency pack is not a moment for casual conversations.
 if(Game->MainStory.Has(2)&&!Game->MainStory.Has(4))return;
 for(TActorIterator<ASurvivalInfected> It(GetWorld());It;++It)if(It->IsAlive()&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(2000.f))return;
 const auto C=Game->WorldClimate();const FVector P=Player->GetActorLocation();const float RiverX=47000+6500*FMath::Sin(P.Y/24000);
 survival::JourneyContext Context;Context.scene=Game->FilmProgress;Context.walking=Walking;Context.rest=RestSeconds>15;Context.rain=C.rain>.25f;Context.night=C.daylight<.2f;Context.hurt=Player->GetHealth()<70;Context.water=FMath::Abs(P.Y)<110000&&FMath::Abs(P.X-RiverX)<3500;Context.quiet=true;Context.companion=true;
 const int32 Id=Game->Journey.Pick(Context);if(Id>=0){Player->BeginJourneyConversation(Id);JourneyDelay=110;RestSeconds=0;}
}
