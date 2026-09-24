#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalPoweredLight.generated.h"
class UPointLightComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalPoweredLight : public AActor
{
    GENERATED_BODY()
public:
    ASurvivalPoweredLight();
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Power") TObjectPtr<UPointLightComponent> Light;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Power") FName RequiredFlag=TEXT("generator_running");
private:
    UFUNCTION() void Refresh();
};
