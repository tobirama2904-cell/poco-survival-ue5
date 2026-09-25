#include "SurvivalGameMode.h"
#include "SurvivalWorldDirector.h"
#include "SurvivalGameInstance.h"
#include "SurvivalCharacter.h"
#include "SurvivalCompanion.h"
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
#include "PixelFormat.h"
#include "EngineUtils.h"
ASurvivalGameMode::ASurvivalGameMode()
{
    DefaultPawnClass=ASurvivalCharacter::StaticClass();PlayerControllerClass=ASurvivalPlayerController::StaticClass();HUDClass=ASurvivalHUD::StaticClass();
}
void ASurvivalGameMode::StartPlay()
{
#if PLATFORM_LINUX && WITH_EDITOR
    // Diagnostic-only workaround for UE 5.7 Vulkan's buffer-only R64 support:
    // velocity fallback tests Supported, although it needs an IMAGE format.
    // Exact engine source confirms PlatformFormat==0 means VK_FORMAT_UNDEFINED.
    // Never changes the shipped Android renderer or claims hardware-GPU coverage.
    if (FParse::Param(FCommandLine::Get(),TEXT("SurvivalSoftwareVulkan")) &&
        FParse::Param(FCommandLine::Get(),TEXT("vulkan")) &&
        GPixelFormats[PF_R64_UINT].Supported && GPixelFormats[PF_R64_UINT].PlatformFormat==0) {
        GPixelFormats[PF_R64_UINT].Supported=false;
        UE_LOG(LogTemp,Warning,TEXT("SOFTWARE_VULKAN_IMAGE_FALLBACK: R64 buffer-only format excluded; renderer selects its R32G32 image fallback"));
    }
#endif
    Super::StartPlay();GetWorld()->SpawnActor<ASurvivalWorldDirector>();FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::Intro,0.3f,false);
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
    FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::BeginCountyProof,1.8f,false);
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
    float Distance=0;bool Grounded=false;FRotator CameraRotation=FRotator::ZeroRotator;bool PlayerView=false;bool HumanLoaded=false;
    if (auto* PC=GetWorld()->GetFirstPlayerController()) {
        PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),EKeys::W,IE_Released));
        FVector CameraLocation;PC->GetPlayerViewPoint(CameraLocation,CameraRotation);
        PlayerView=PC->GetViewTarget()==PC->GetPawn();
        if (auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())) {
            Distance=FVector::Dist2D(MovementProofStart,Player->GetActorLocation());
            Grounded=Player->GetCharacterMovement()->IsMovingOnGround();HumanLoaded=Player->HasHumanAvatar();
        }
    }
    const float CameraPitch=FRotator::NormalizeAxis(CameraRotation.Pitch);
    const bool CameraFramed=PlayerView && CameraPitch>=-60 && CameraPitch<=30;
    const bool Passed=bMovementProofStarted && Distance>100 && Grounded && CameraFramed && HumanLoaded;
    const FString Report=FString::Printf(TEXT("{\"phase\":\"actual-game-mode-input-and-floor-test\",\"passed\":%s,\"walk_distance_cm\":%.2f,\"grounded\":%s,\"camera_pitch_degrees\":%.2f,\"player_view_target\":%s,\"camera_framed\":%s,\"human_avatar_loaded\":%s,\"touch_device_tested\":false,\"android_tested\":false}\n"),Passed?TEXT("true"):TEXT("false"),Distance,Grounded?TEXT("true"):TEXT("false"),CameraPitch,PlayerView?TEXT("true"):TEXT("false"),CameraFramed?TEXT("true"):TEXT("false"),HumanLoaded?TEXT("true"):TEXT("false"));
    FFileHelper::SaveStringToFile(Report,*FPaths::Combine(FPaths::ProjectDir(),TEXT("artifacts/gameplay-scene/runtime-movement.json")));
}

void ASurvivalGameMode::BeginCountyProof()
{
 auto* PC=GetWorld()->GetFirstPlayerController();auto* Player=PC?Cast<ASurvivalCharacter>(PC->GetPawn()):nullptr;
 FVector Destination=FVector::ZeroVector;
 for(TActorIterator<AActor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("county_proof"))){
  ++CountyAnchors;const FVector P=It->GetActorLocation();FHitResult Hit;FCollisionQueryParams Params;Params.AddIgnoredActor(*It);if(Player)Params.AddIgnoredActor(Player);
  if(GetWorld()->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,50000),FVector(P.X,P.Y,-10000),ECC_Visibility,Params)&&FMath::Abs(Hit.ImpactPoint.Z-(P.Z-400))<180){++CountyFloors;if(It->ActorHasTag(TEXT("ranger_station")))Destination=Hit.ImpactPoint+FVector(0,0,100);}
 }
 if(Player&&Destination!=FVector::ZeroVector){
  if(auto* G=Cast<USurvivalGameInstance>(GetGameInstance())){G->FilmProgress=18;G->FilmDecision=2;} // diagnostic setup, not campaign-completion evidence
  Player->EndStory();Player->SetActorLocation(Destination,false,nullptr,ETeleportType::TeleportPhysics);Player->GetCharacterMovement()->SetMovementMode(MOVE_Walking);PC->SetControlRotation(FRotator(-8,53,0));PC->SetViewTarget(Player);CountyMovementStart=Destination;
  PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),EKeys::W,IE_Pressed));
 }
 FTimerHandle Move,Capture;GetWorldTimerManager().SetTimer(Move,this,&ASurvivalGameMode::EndCountyMovement,1.3f,false);GetWorldTimerManager().SetTimer(Capture,this,&ASurvivalGameMode::CaptureCountyProof,2.3f,false);
}
void ASurvivalGameMode::EndCountyMovement()
{
 float Distance=0;bool Grounded=false;
 if(auto* PC=GetWorld()->GetFirstPlayerController()){
  PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),EKeys::W,IE_Released));
  if(auto* Player=Cast<ASurvivalCharacter>(PC->GetPawn())){Distance=FVector::Dist2D(CountyMovementStart,Player->GetActorLocation());Grounded=Player->GetCharacterMovement()->IsMovingOnGround();}
 }
 const bool Passed=CountyAnchors==6&&CountyFloors==6&&Grounded&&Distance>100&&Distance<2000;
 const FString Report=FString::Printf(TEXT("{\"passed\":%s,\"rural_anchors\":%d,\"valid_collision_floors\":%d,\"walk_distance_cm\":%.2f,\"grounded\":%s,\"physical_device_tested\":false}\n"),Passed?TEXT("true"):TEXT("false"),CountyAnchors,CountyFloors,Distance,Grounded?TEXT("true"):TEXT("false"));
 FFileHelper::SaveStringToFile(Report,*FPaths::Combine(FPaths::ProjectDir(),TEXT("artifacts/gameplay-scene/county-runtime.json")));
}
void ASurvivalGameMode::CaptureCountyProof()
{
 if(auto* PC=GetWorld()->GetFirstPlayerController())PC->ConsoleCommand(TEXT("HighResShot 1"));
 FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::BeginCompanionFilmProof,2.f,false);
}

void ASurvivalGameMode::BeginCompanionFilmProof()
{
 auto* PC=GetWorld()->GetFirstPlayerController();auto* Player=PC?Cast<ASurvivalCharacter>(PC->GetPawn()):nullptr;
 bool Available=false,Human=false,Grounded=false;float Travel=0,Distance=0;
 for(TActorIterator<ASurvivalCompanion> Friend(GetWorld());Friend;++Friend)if(!Friend->RuthRole){
  Available=Friend->IsAvailable();Human=Friend->HasHumanAvatar();Grounded=Friend->GetCharacterMovement()->IsMovingOnGround();Travel=Friend->Travelled;
  if(Player){Distance=FVector::Dist2D(Player->GetActorLocation(),Friend->GetActorLocation());Player->BeginFilm(18,*Friend);}break;
 }
 bCompanionAvailable=Available;bCompanionHuman=Human;bCompanionGrounded=Grounded;CompanionTravel=Travel;CompanionDistance=Distance;
 FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::CaptureCompanionFilmProof,1.1f,false);
}
void ASurvivalGameMode::CaptureCompanionFilmProof()
{
 auto* PC=GetWorld()->GetFirstPlayerController();auto* Player=PC?PC->GetPawn():nullptr;
 const bool View=PC&&PC->GetViewTarget()&&PC->GetViewTarget()!=Player;
 const bool Pass=bCompanionAvailable&&bCompanionHuman&&bCompanionGrounded&&CompanionTravel>30&&CompanionDistance<1600&&View;
 const FString Report=FString::Printf(TEXT("{\"passed\":%s,\"diagnostic_story_state_injected\":true,\"available\":%s,\"human_mesh\":%s,\"grounded\":%s,\"walked_cm\":%.2f,\"distance_to_player_cm\":%.2f,\"cinematic_camera_active\":%s,\"full_campaign_playthrough\":false}\n"),Pass?TEXT("true"):TEXT("false"),bCompanionAvailable?TEXT("true"):TEXT("false"),bCompanionHuman?TEXT("true"):TEXT("false"),bCompanionGrounded?TEXT("true"):TEXT("false"),CompanionTravel,CompanionDistance,View?TEXT("true"):TEXT("false"));
 FFileHelper::SaveStringToFile(Report,*FPaths::Combine(FPaths::ProjectDir(),TEXT("artifacts/gameplay-scene/companion-runtime.json")));
 if(auto* PC=GetWorld()->GetFirstPlayerController())PC->ConsoleCommand(TEXT("HighResShot 1"));
 FTimerHandle Timer;GetWorldTimerManager().SetTimer(Timer,this,&ASurvivalGameMode::ExitProof,4.f,false);
}
