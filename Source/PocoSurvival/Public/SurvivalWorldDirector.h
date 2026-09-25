#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SurvivalWorldDirector.generated.h"
class ADirectionalLight;
class ASkyLight;
class AExponentialHeightFog;
class UHierarchicalInstancedStaticMeshComponent;
class UMaterialInstanceDynamic;
class UAudioComponent;
UCLASS()
class POCOSURVIVAL_API ASurvivalWorldDirector : public AActor
{
 GENERATED_BODY()
public:
 ASurvivalWorldDirector();
 virtual void BeginPlay() override;
 virtual void Tick(float Delta) override;
 static FString Chapter(class USurvivalGameInstance* Game);
 static FString Intention(class USurvivalGameInstance* Game);
private:
 UPROPERTY() TObjectPtr<ADirectionalLight> Sun;
 UPROPERTY() TObjectPtr<ASkyLight> Fill;
 UPROPERTY() TObjectPtr<AExponentialHeightFog> Fog;
 UPROPERTY() TObjectPtr<AActor> Sky;
 UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> SkyMaterial;
 UPROPERTY() TArray<TObjectPtr<UMaterialInstanceDynamic>> WetMaterials;
 UPROPERTY() TObjectPtr<UHierarchicalInstancedStaticMeshComponent> Rain;
 UPROPERTY() TObjectPtr<UAudioComponent> RainSound;
 float EnvironmentTimer=0,StoryTimer=0;
 float RainPhase=0;
 bool bSheltered=false;
 void AdvanceStory(class ASurvivalCharacter* Player,class USurvivalGameInstance* Game);
};
