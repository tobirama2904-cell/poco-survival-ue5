#include "SurvivalControlSettings.h"
USurvivalControlSettings* USurvivalControlSettings::Get() { auto* S=GetMutableDefault<USurvivalControlSettings>();S->Normalize();return S; }
void USurvivalControlSettings::Normalize()
{
 if(Positions.Num()!=static_cast<int32>(survival::Control::Count)) { Positions.Reset();for(auto P:survival::DefaultControls)Positions.Add(FVector2D(P.x,P.y));bLeftHanded=false; }
 Sensitivity=FMath::IsFinite(Sensitivity)?FMath::Clamp(Sensitivity,.35f,2.5f):1;
 ButtonScale=FMath::IsFinite(ButtonScale)?FMath::Clamp(ButtonScale,.75f,1.4f):1;
 Opacity=FMath::IsFinite(Opacity)?FMath::Clamp(Opacity,.2f,.95f):.65f;
 for(int32 I=0;I<Positions.Num();++I)if(Positions[I].ContainsNaN())Positions[I]=FVector2D(survival::DefaultControls[I].x,survival::DefaultControls[I].y);
}
void USurvivalControlSettings::ResetLayout() { Positions.Reset();Sensitivity=1;ButtonScale=1;Opacity=.65f;bInvertY=false;Normalize();Store(); }
void USurvivalControlSettings::MirrorLayout() { for(auto& P:Positions)P.X=1-P.X;bLeftHanded=!bLeftHanded;Store(); }
void USurvivalControlSettings::Store() { Normalize();SaveConfig(); }
float USurvivalControlSettings::Radius(survival::Control Id) const { return (Id==survival::Control::Move?.105f:.052f)*ButtonScale; }
FVector2D USurvivalControlSettings::Position(survival::Control Id,float Aspect) const
{
 const int32 I=static_cast<int32>(Id);const FVector2D P=Positions.IsValidIndex(I)?Positions[I]:FVector2D(.5,.5);
 auto C=survival::ClampControl({static_cast<float>(P.X),static_cast<float>(P.Y)},Radius(Id),Aspect);return FVector2D(C.x,C.y);
}
int32 USurvivalControlSettings::Hit(FVector2D Point,float Aspect,bool Editing) const
{
 for(int32 I=0;I<Positions.Num();++I){const auto Id=static_cast<survival::Control>(I);if(Id==survival::Control::Move&&!Editing)continue;const auto C=Position(Id,Aspect);
 if(survival::ControlHit({static_cast<float>(Point.X),static_cast<float>(Point.Y)},{static_cast<float>(C.X),static_cast<float>(C.Y)},Radius(Id),Aspect))return I;}
 return INDEX_NONE;
}
void USurvivalControlSettings::Move(int32 Id,FVector2D Point,float Aspect) { if(!Positions.IsValidIndex(Id))return;auto C=survival::ClampControl({static_cast<float>(Point.X),static_cast<float>(Point.Y)},Radius(static_cast<survival::Control>(Id)),Aspect);Positions[Id]=FVector2D(C.x,C.y); }
const TCHAR* USurvivalControlSettings::Label(survival::Control Id)
{
 static const TCHAR* Names[]={TEXT("Действие"),TEXT("Удар"),TEXT("Бег"),TEXT("Прыжок"),TEXT("Тише"),TEXT("Зарядить"),TEXT("Бутылка"),TEXT("Оружие"),TEXT("Заметки"),TEXT("Сохранить"),TEXT("Загрузить"),TEXT("Настройки"),TEXT("Фонарь"),TEXT("Движение")};
 const int32 I=static_cast<int32>(Id);return I>=0&&I<14?Names[I]:TEXT("");
}
