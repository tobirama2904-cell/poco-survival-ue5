#include "SurvivalWorldDirector.h"
#include "Core/AmericanStory.h"
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
  const float Day=Climate.daylight;
  if(Sun){Sun->SetActorRotation(FRotator(-FMath::Max(12.f,Day*72),Game->WorldHour()*15-90,0));auto* Light=Cast<UDirectionalLightComponent>(Sun->GetLightComponent());if(Light){Light->SetIntensity((.12f+FMath::Sqrt(Day)*3.8f)*(1-Climate.cloud*.60f));Light->SetLightColor(FLinearColor::LerpUsingHSV(FLinearColor(.40,.55,.95),FLinearColor(1,.87,.69),FMath::Min(1.f,Day*3)));}}
  if(Fill)Fill->GetLightComponent()->SetIntensity(.25f+FMath::Sqrt(Day)*.9f);
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
 const auto& Scenes=survival::FilmScenes();if(Game->FilmProgress<0||Game->FilmProgress>=static_cast<int32>(Scenes.size()))return;const auto& Scene=Scenes[Game->FilmProgress];
 const FVector Target(Scene.x*100,Scene.y*100,Scene.z*100);
 if(FVector::DistSquared2D(Target,Player->GetActorLocation())>FMath::Square(480.f))return;
 if(Scene.gate==1&&Game->FieldInventory.Get(survival::Supply::Bow)==0){Player->StatusMessage=TEXT("Возьми снаряжение из ящика у лестницы депо.");return;}
 if(Scene.gate==2&&Game->FilmDecision==0){Player->StatusMessage=TEXT("Красный рычаг: открыть канал. Синий: удержать затвор.");return;}
 for(TActorIterator<ASurvivalInfected> Enemy(GetWorld());Enemy;++Enemy)if(Enemy->IsAlive()&&FVector::DistSquared(Enemy->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1300.f))return;
 AActor* Speaker=nullptr;float Best=FMath::Square(1200.f);for(TActorIterator<AActor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("american_cast"))){const float D=FVector::DistSquared(It->GetActorLocation(),Target);if(D<Best){Best=D;Speaker=*It;}}
 Player->BeginFilm(Game->FilmProgress,Speaker);

}
FString ASurvivalWorldDirector::Chapter(USurvivalGameInstance* G){if(!G)return TEXT("Беллуэзер");const auto& S=survival::FilmScenes();return G->FilmProgress<static_cast<int32>(S.size())?UTF8_TO_TCHAR(S[G->FilmProgress].title.c_str()):TEXT("БЕЛЛУЭЗЕР • ПОСЛЕ НАВОДНЕНИЯ");}
FString ASurvivalWorldDirector::Intention(USurvivalGameInstance* G){if(!G)return TEXT("");return G->FilmProgress>=18?TEXT("Свободное исследование. Помогай жителям, ищи припасы, вернись в нижний квартал."):TEXT("Дэниел Рид вернулся в Беллуэзер. Мара ждёт у следующей отметки.");}

void ASurvivalWorldDirector::MixScore(ASurvivalCharacter* Player,float Delta){
 int32 Mode=-1;bool Threat=false,Fight=false;
 for(TActorIterator<ASurvivalInfected> It(GetWorld());It;++It)if(It->IsAlive()&&FVector::DistSquared(It->GetActorLocation(),Player->GetActorLocation())<FMath::Square(1900.f)){Threat=true;Fight|=It->State==EInfectedState::Chase||It->State==EInfectedState::Attack;}
 const float Cycle=FMath::Fmod(GetWorld()->GetTimeSeconds(),160.f);if(Player->bStoryActive)Mode=3;else if(Fight)Mode=2;else if(Threat)Mode=1;else if(Cycle<42)Mode=0;
 if(Player->bEditingControls||!Player->IsAlive())Mode=-1;
 for(int32 I=0;I<Score.Num();++I){const float Target=I==Mode?(Player->bStoryActive?.10f:.20f):0;ScoreLevels[I]=FMath::FInterpTo(ScoreLevels[I],Target,Delta,.6f);if(Score[I])Score[I]->SetVolumeMultiplier(ScoreLevels[I]);}
}
