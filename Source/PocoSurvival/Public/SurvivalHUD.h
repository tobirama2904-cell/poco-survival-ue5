#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "SurvivalHUD.generated.h"
class UTexture2D;
UCLASS()
class POCOSURVIVAL_API ASurvivalHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
private:
    UPROPERTY() TObjectPtr<UTexture2D> Portraits;
};
