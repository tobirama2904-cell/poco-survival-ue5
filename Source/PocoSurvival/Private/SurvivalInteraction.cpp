#include "SurvivalInteraction.h"
#include "SurvivalGameInstance.h"
#include "SurvivalCharacter.h"
#include "SurvivalInfected.h"
#include "Core/CityContent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "EngineUtils.h"

ASurvivalInteraction::ASurvivalInteraction()
{
    PrimaryActorTick.bCanEverTick = true;PrimaryActorTick.bStartWithTickEnabled=false;
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    Mesh->SetCollisionProfileName(TEXT("BlockAll"));
    FocusVolume=CreateDefaultSubobject<USphereComponent>(TEXT("FocusVolume"));
    FocusVolume->SetupAttachment(Mesh);FocusVolume->InitSphereRadius(85);
    FocusVolume->SetRelativeLocation(FVector(0,0,65));
    FocusVolume->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    FocusVolume->SetCollisionResponseToAllChannels(ECR_Ignore);
    FocusVolume->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
bool ASurvivalInteraction::Interact(APawn* User, FString& FailureReason)
{
    if (!IsValid(User) || User->GetWorld() != GetWorld()) { FailureReason = TEXT("invalid_user"); return false; }
    if (FVector::DistSquared(User->GetActorLocation(), GetActorLocation()) > FMath::Square(FMath::Clamp(ReachCm, 1.0f, 500.0f)))
    { FailureReason = TEXT("out_of_reach"); return false; }
    FVector Eyes; FRotator Direction; User->GetActorEyesViewPoint(Eyes, Direction);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(SurvivalInteraction), false, User);
    FHitResult Hit;
    if (GetWorld()->LineTraceSingleByChannel(Hit, Eyes, GetActorLocation(), ECC_Visibility, Params) && Hit.GetActor() != this)
    { FailureReason = TEXT("occluded"); return false; }
    auto* Game = Cast<USurvivalGameInstance>(GetGameInstance());
    if (!Game) { FailureReason = TEXT("missing_game_instance"); return false; }
    auto* Player=Cast<ASurvivalCharacter>(User);
    const FString Id=ActionId.ToString();
    if(Id.StartsWith(TEXT("__door_"))){const int32 I=FCString::Atoi(*Id.Mid(7));if(I<0||I>=24)return false;Game->FieldInventory.doors^=1u<<I;TargetDoorYaw=(Game->FieldInventory.doors&(1u<<I))?90:0;SetActorTickEnabled(true);return true;}
    if(Id.StartsWith(TEXT("__cache_"))){const int32 Index=FCString::Atoi(*Id.Mid(8));if(!Game->FieldInventory.Loot(Index)){FailureReason=TEXT("Пусто или рюкзак полон");return false;}SetActorHiddenInGame(true);SetActorEnableCollision(false);if(Player)Player->SyncEquipment();return true;}
    if(Id==TEXT("__gate_open")||Id==TEXT("__gate_hold")){if(Game->FilmProgress!=14||Game->FilmDecision!=0){FailureReason=TEXT("Сначала поговорите с Марой у шлюза");return false;}Game->FilmDecision=Id==TEXT("__gate_open")?1:2;if(Game->FilmDecision==2){Game->FieldInventory.looted|=(1u<<9)|(1u<<10);for(TActorIterator<ASurvivalInteraction> It(GetWorld());It;++It)if(It->ActionId==TEXT("__cache_9")||It->ActionId==TEXT("__cache_10")){It->SetActorHiddenInGame(true);It->SetActorEnableCollision(false);}}return true;}
    if(Id.StartsWith(TEXT("__county_"))){
        TArray<FString> Parts;Id.Mid(9).ParseIntoArray(Parts,TEXT("_"));
        if(!Player||Parts.Num()!=2||!Parts[0].IsNumeric()||!Parts[1].IsNumeric()){FailureReason=TEXT("invalid_county_action");return false;}
        const int32 Arc=FCString::Atoi(*Parts[0]),Action=FCString::Atoi(*Parts[1]);
        if(Action==1)for(TActorIterator<ASurvivalInfected> Enemy(GetWorld());Enemy;++Enemy)if(Enemy->IsAlive()&&Enemy->State==EInfectedState::Chase&&FVector::DistSquared(Enemy->GetActorLocation(),User->GetActorLocation())<FMath::Square(1200.f)){FailureReason=TEXT("Сначала оторвитесь от преследования");return false;}
        const auto Result=static_cast<survival::CountyResult>(Game->TryCountyAction(Arc,Action));
        if(Result==survival::CountyResult::Resources){FailureReason=TEXT("Нужны дерево и деталь; для награды также нужно место в рюкзаке");return false;}
        if(Result==survival::CountyResult::WrongOrder||Result==survival::CountyResult::Invalid){FailureReason=TEXT("Изучите запись, восстановите устройство; принятый выбор изменить нельзя");return false;}
        if(Result==survival::CountyResult::Advanced&&Action==2)for(TActorIterator<ASurvivalInfected> Enemy(GetWorld());Enemy;++Enemy)Enemy->HearNoise(GetActorLocation(),4500);
        Player->BeginCountyStory(Arc,Action);return true;
    }
    const auto* Site=survival::FindCitySite(TCHAR_TO_UTF8(*ActionId.ToString()));
    if (Site && Site->kind=="heal" && (!Player || Player->GetHealth()>=100)) { FailureReason=TEXT("Здоровье уже полное");return false; }
    if (!Game->TryAction(ActionId,FailureReason)) return false;
    if (Player) {
        if (Site && Site->kind=="heal") Player->RestoreVitals(FMath::Min(100.0f,Player->GetHealth()+55),Player->GetStamina());
        Player->SyncEquipment();Player->BeginStory(ActionId,this);
    }
    return true;
}

void ASurvivalInteraction::BeginPlay(){Super::BeginPlay();const FString Id=ActionId.ToString();if(Id.StartsWith(TEXT("__door_")))if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance())){const int32 I=FCString::Atoi(*Id.Mid(7));if(I>=0&&I<24)SetActorRotation(FRotator(0,(G->FieldInventory.doors&(1u<<I))?90:0,0));}if(Id.StartsWith(TEXT("__cache_")))if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance())){const int32 I=FCString::Atoi(*Id.Mid(8));if(I>=0&&I<24&&(G->FieldInventory.looted&(1u<<I))){SetActorHiddenInGame(true);SetActorEnableCollision(false);}}}

void ASurvivalInteraction::Tick(float Delta){Super::Tick(Delta);const float Yaw=FMath::FInterpConstantTo(GetActorRotation().Yaw,TargetDoorYaw,Delta,150);SetActorRotation(FRotator(0,Yaw,0));if(FMath::IsNearlyEqual(Yaw,TargetDoorYaw,.1f))SetActorTickEnabled(false);}
