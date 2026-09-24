#include "SurvivalGameMode.h"
#include "SurvivalGameInstance.h"
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
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
ASurvivalGameMode::ASurvivalGameMode()
{
    DefaultPawnClass=ASurvivalCharacter::StaticClass();PlayerControllerClass=ASurvivalPlayerController::StaticClass();HUDClass=ASurvivalHUD::StaticClass();
}
void ASurvivalGameMode::StartPlay()
{
    Super::StartPlay();FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::Intro,0.3f,false);
    if (FParse::Param(FCommandLine::Get(),TEXT("SurvivalSmokeScreenshot"))) {
        FTimerHandle Capture,MoveStart,MoveEnd;
        GetWorldTimerManager().SetTimer(MoveStart,this,&ASurvivalGameMode::BeginMovementProof,4.7f,false);
        GetWorldTimerManager().SetTimer(MoveEnd,this,&ASurvivalGameMode::EndMovementProof,6.0f,false);
        GetWorldTimerManager().SetTimer(Capture,this,&ASurvivalGameMode::CaptureProof,7.0f,false);
    }
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
    if (auto* PC=GetWorld()->GetFirstPlayerController()) if (auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())) { PC->SetViewTargetWithBlend(Player,0.8f);Player->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->SaveProgress();
    }
}
void ASurvivalGameMode::CaptureProof()
{
    if (auto* PC=GetWorld()->GetFirstPlayerController()) PC->ConsoleCommand(TEXT("HighResShot 1"));
    FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::ExitProof,4.0f,false);
}
void ASurvivalGameMode::ExitProof() { FPlatformMisc::RequestExit(false); }

void ASurvivalGameMode::BeginMovementProof()
{
    if (auto* PC=GetWorld()->GetFirstPlayerController()) if (auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())) {
        MovementProofStart=Player->GetActorLocation();bMovementProofStarted=true;
        PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),EKeys::W,IE_Pressed));
    }
}
void ASurvivalGameMode::EndMovementProof()
{
    float Distance=0;bool Grounded=false;
    if (auto* PC=GetWorld()->GetFirstPlayerController()) {
        PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),EKeys::W,IE_Released));
        if (auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())) {
            Distance=FVector::Dist2D(MovementProofStart,Player->GetActorLocation());
            Grounded=Player->GetCharacterMovement()->IsMovingOnGround();
        }
    }
    const bool Passed=bMovementProofStarted && Distance>100 && Grounded;
    const FString Report=FString::Printf(TEXT("{\"phase\":\"actual-game-mode-input-and-floor-test\",\"passed\":%s,\"walk_distance_cm\":%.2f,\"grounded\":%s,\"touch_device_tested\":false,\"android_tested\":false}\n"),Passed?TEXT("true"):TEXT("false"),Distance,Grounded?TEXT("true"):TEXT("false"));
    FFileHelper::SaveStringToFile(Report,*FPaths::Combine(FPaths::ProjectDir(),TEXT("artifacts/gameplay-scene/runtime-movement.json")));
}
