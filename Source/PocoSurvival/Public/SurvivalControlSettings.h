#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "Core/Experience.h"
#include "SurvivalControlSettings.generated.h"
UCLASS(Config=GameUserSettings)
class POCOSURVIVAL_API USurvivalControlSettings : public UObject
{
 GENERATED_BODY()
public:
 static USurvivalControlSettings* Get();
 UPROPERTY(Config) TArray<FVector2D> Positions;
 UPROPERTY(Config) float Sensitivity=1;
 UPROPERTY(Config) float ButtonScale=1;
 UPROPERTY(Config) float Opacity=.65f;
 UPROPERTY(Config) bool bInvertY=false;
 UPROPERTY(Config) bool bLeftHanded=false;
 UPROPERTY(Config) bool bPerformanceMode=true;
 void Normalize();
 void ResetLayout();
 void MirrorLayout();
 void Store();
 FVector2D Position(survival::Control Id,float Aspect) const;
 float Radius(survival::Control Id) const;
 int32 Hit(FVector2D Point,float Aspect,bool Editing) const;
 void Move(int32 Id,FVector2D Point,float Aspect);
 static const TCHAR* Label(survival::Control Id);
};
