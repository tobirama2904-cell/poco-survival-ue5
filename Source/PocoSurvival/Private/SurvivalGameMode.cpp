#include "SurvivalGameMode.h"
#include "SurvivalCharacter.h"
#include "SurvivalPlayerController.h"
#include "SurvivalHUD.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Camera/CameraActor.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/PlatformMisc.h"
ASurvivalGameMode::ASurvivalGameMode()
{
    DefaultPawnClass=ASurvivalCharacter::StaticClass();PlayerControllerClass=ASurvivalPlayerController::StaticClass();HUDClass=ASurvivalHUD::StaticClass();
}
void ASurvivalGameMode::StartPlay()
{
    Super::StartPlay();FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::Intro,0.3f,false);
    if (FParse::Param(FCommandLine::Get(),TEXT("SurvivalSmokeScreenshot"))) { FTimerHandle Capture;GetWorldTimerManager().SetTimer(Capture,this,&ASurvivalGameMode::CaptureProof,7.0f,false); }
}
void ASurvivalGameMode::Intro()
{
    auto* PC=GetWorld()->GetFirstPlayerController();if (!PC) return;
    TArray<AActor*> Cameras;UGameplayStatics::GetAllActorsWithTag(this,TEXT("intro_camera"),Cameras);
    if (!Cameras.Num()) return;
    PC->SetViewTargetWithBlend(Cameras[0],0.4f);
    if (auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())) Player->GetCharacterMovement()->DisableMovement();
    FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::EndIntro,3.8f,false);
}
void ASurvivalGameMode::EndIntro()
{
    if (auto* PC=GetWorld()->GetFirstPlayerController()) if (auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())) { PC->SetViewTargetWithBlend(Player,0.8f);Player->GetCharacterMovement()->SetMovementMode(MOVE_Walking); }
}
void ASurvivalGameMode::CaptureProof()
{
    if (auto* PC=GetWorld()->GetFirstPlayerController()) PC->ConsoleCommand(TEXT("HighResShot 1"));
    FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::ExitProof,4.0f,false);
}
void ASurvivalGameMode::ExitProof() { FPlatformMisc::RequestExit(false); }
