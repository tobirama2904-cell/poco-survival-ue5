#include "SurvivalPoweredLight.h"
#include "SurvivalGameInstance.h"
#include "Components/PointLightComponent.h"
ASurvivalPoweredLight::ASurvivalPoweredLight()
{
    Light=CreateDefaultSubobject<UPointLightComponent>(TEXT("RestoredPowerLight"));SetRootComponent(Light);
    Light->SetMobility(EComponentMobility::Movable);Light->SetIntensity(1600);Light->SetAttenuationRadius(500);
    Light->SetLightColor(FLinearColor(1,.72f,.43f));Light->SetCastShadows(false);Light->SetVisibility(false);
}
void ASurvivalPoweredLight::BeginPlay()
{
    Super::BeginPlay();
    if (auto* Game=Cast<USurvivalGameInstance>(GetGameInstance())) Game->OnWorldStateChanged.AddDynamic(this,&ASurvivalPoweredLight::Refresh);
    Refresh();
}
void ASurvivalPoweredLight::Refresh()
{
    auto* Game=Cast<USurvivalGameInstance>(GetGameInstance());Light->SetVisibility(Game && Game->HasWorldFlag(RequiredFlag));
}
