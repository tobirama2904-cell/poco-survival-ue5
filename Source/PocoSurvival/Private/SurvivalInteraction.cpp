#include "SurvivalInteraction.h"
#include "SurvivalGameInstance.h"
#include "SurvivalCharacter.h"
#include "Core/CityContent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"

ASurvivalInteraction::ASurvivalInteraction()
{
    PrimaryActorTick.bCanEverTick = false;
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
    const auto* Site=survival::FindCitySite(TCHAR_TO_UTF8(*ActionId.ToString()));
    if (Site && Site->kind=="heal" && (!Player || Player->GetHealth()>=100)) { FailureReason=TEXT("Здоровье уже полное");return false; }
    if (!Game->TryAction(ActionId,FailureReason)) return false;
    if (Player) {
        if (Site && Site->kind=="heal") Player->RestoreVitals(FMath::Min(100.0f,Player->GetHealth()+55),Player->GetStamina());
        Player->BeginStory(ActionId,this);
    }
    return true;
}
