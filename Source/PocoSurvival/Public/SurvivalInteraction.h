#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalInteraction.generated.h"
class UStaticMeshComponent;
class APawn;

// Native quest-prop interaction. Mesh assignment and animation require actual
// imported content; no placeholder level or art quality is implied by this actor.
UCLASS()
class POCOSURVIVAL_API ASurvivalInteraction : public AActor
{
    GENERATED_BODY()
public:
    ASurvivalInteraction();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Interaction") TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Interaction") FName ActionId;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Interaction", meta=(ClampMin="1.0", ClampMax="500.0")) float ReachCm = 220.0f;
    UFUNCTION(BlueprintCallable, Category="Interaction") bool Interact(APawn* User, FString& FailureReason);
};
