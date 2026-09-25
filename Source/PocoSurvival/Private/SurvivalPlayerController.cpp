#include "SurvivalPlayerController.h"
#include "SurvivalControlSettings.h"
#include "SurvivalCharacter.h"
#include "GameFramework/TouchInterface.h"
#include "GameFramework/GameUserSettings.h"
#include "Engine/Engine.h"
void ASurvivalPlayerController::BeginPlay()
{
 Super::BeginPlay();bEnableTouchEvents=true;SetInputMode(FInputModeGameOnly());RefreshTouchLayout();
}
void ASurvivalPlayerController::Tick(float Delta)
{
 Super::Tick(Delta);int32 W,H;GetViewportSize(W,H);if(W>0&&H>0&&LastViewport!=FIntPoint(W,H)) { LastViewport=FIntPoint(W,H);auto* P=Cast<ASurvivalCharacter>(GetPawn());RefreshTouchLayout(!P||!P->bEditingControls); }
}
void ASurvivalPlayerController::RefreshTouchLayout(bool Visible)
{
 auto* S=USurvivalControlSettings::Get();int32 W,H;GetViewportSize(W,H);const float Aspect=H>0?static_cast<float>(W)/H:16.f/9;
 if(!MobileStick) { auto* Defaults=LoadObject<UTouchInterface>(nullptr,TEXT("/Engine/MobileResources/HUD/DefaultVirtualJoysticks.DefaultVirtualJoysticks"));if(Defaults)MobileStick=DuplicateObject<UTouchInterface>(Defaults,this); }
 if(MobileStick&&MobileStick->Controls.Num()) {
  MobileStick->Controls.SetNum(1);auto& C=MobileStick->Controls[0];C.Center=S->Position(survival::Control::Move,Aspect);
  C.VisualSize=FVector2D(.2f/Aspect,.2f)*S->ButtonScale;C.ThumbSize=FVector2D(.09f/Aspect,.09f)*S->ButtonScale;C.InteractionSize=FVector2D(.32f/Aspect,.32f)*S->ButtonScale;
  MobileStick->bPreventRecenter=true;MobileStick->InactiveOpacity=S->Opacity;ActivateTouchInterface(Visible?MobileStick.Get():nullptr);
 }
 if(GEngine)if(auto* Settings=GEngine->GetGameUserSettings()) { Settings->SetFrameRateLimit(30);Settings->SetOverallScalabilityLevel(S->bPerformanceMode?1:2);Settings->ApplyNonResolutionSettings();Settings->SaveSettings(); }
}
