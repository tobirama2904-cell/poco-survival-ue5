#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "SurvivalPlayerController.generated.h"
class UTouchInterface;
UCLASS()
class POCOSURVIVAL_API ASurvivalPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void Tick(float Delta) override;
    void RefreshTouchLayout(bool Visible=true);
private:
    FIntPoint LastViewport=FIntPoint::ZeroValue;
    UPROPERTY() TObjectPtr<UTouchInterface> MobileStick;
};
