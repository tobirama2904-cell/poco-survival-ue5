#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "SurvivalHUD.generated.h"
UCLASS()
class POCOSURVIVAL_API ASurvivalHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
