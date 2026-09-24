#include "SurvivalPlayerController.h"
#include "GameFramework/TouchInterface.h"
void ASurvivalPlayerController::BeginPlay()
{
    Super::BeginPlay();
    bEnableTouchEvents=true;
    SetInputMode(FInputModeGameOnly());
    auto* Defaults=LoadObject<UTouchInterface>(nullptr,TEXT("/Engine/MobileResources/HUD/DefaultVirtualJoysticks.DefaultVirtualJoysticks"));
    if (Defaults && Defaults->Controls.Num()>0)
    {
        MobileStick=DuplicateObject<UTouchInterface>(Defaults,this);
        MobileStick->Controls.SetNum(1);
        MobileStick->Controls[0].Center=FVector2D(0.13f,0.80f);
        MobileStick->Controls[0].InteractionSize=FVector2D(0.32f,0.40f);
        MobileStick->bPreventRecenter=true;
        MobileStick->InactiveOpacity=0.45f;
        ActivateTouchInterface(MobileStick);
    }
}
